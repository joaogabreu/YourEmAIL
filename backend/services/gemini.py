import os
import json
import google.generativeai as genai
from typing import Dict, Optional

# Imports absolutos para funcionar ao rodar `python app.py` dentro de backend/
from utils import nlp  # type: ignore
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# --- Constantes de Prompts ---

CLASSIFICATION_PROMPT = """
Você é um assistente que classifica e-mails para determinar se REQUEREM AÇÃO ou resposta do destinatário.

Definições:
- Produtivo: E-mails que REQUEREM uma ação, resposta ou decisão do destinatário:
  * Solicitações diretas (orçamentos, reuniões, aprovações)
  * Perguntas que esperam resposta
  * Tarefas atribuídas com prazos
  * Cobrança ou pagamentos pendentes
  * Convites que precisam de confirmação
  * Problemas técnicos reportados pelo remetente

- Improdutivo: E-mails que NÃO requerem ação do destinatário:
  * Notificações automáticas (atualizações de sistema, tickets, status)
  * Informativos unidirecionais (newsletters, relatórios, comunicados)
  * Spam, promoções e marketing
  * Confirmações automáticas (recebos, cadastros)
  * Mensagens sociais/pessoais sem solicitação específica
  * Atualizações de progresso sem necessidade de resposta

Analise se o remetente ESPERA uma resposta ou ação específica do destinatário.
Responda APENAS com Produtivo ou Improdutivo.

{guidelines}
Assunto: {subject}
Texto (pré-processado):
{cleaned_content}
"""

EXPLAIN_UNPRODUCTIVE_PROMPT = """
Você é um assistente de e-mail. O e-mail abaixo foi classificado como IMPRODUTIVO.
Sua tarefa é gerar um objeto JSON com duas chaves:
1. "explanation": Uma explicação objetiva (1-2 frases, em PT-BR) do motivo pelo qual o e-mail é improdutivo. Exemplos:
   - Para notificações automáticas: "Este é um email informativo que não requer resposta"
   - Para spam/marketing: "Email promocional - considere usar o link de descadastro se necessário"
   - Para confirmações: "Confirmação automática que não requer ação do destinatário"
2. "suggested_reply": Uma sugestão de resposta curta e educada (1-2 frases, em PT-BR), começando com uma saudação como 'Olá,'. Para notificações automáticas, sugira algo como "Agradecemos a informação" ou "Recebido, obrigado pela atualização". Não inclua uma assinatura.

Regras de saída:
- A saída deve ser um JSON válido e nada mais.
- Não use markdown no conteúdo das chaves.

Assunto: {subject}
Conteúdo:
{content}
"""

GENERATE_PRODUCTIVE_REPLY_PROMPT = """
Você é um assistente de e-mail e precisa redigir uma resposta para o e-mail produtivo abaixo.
Sua resposta deve ser um corpo de e-mail completo e bem formatado em PT-BR.

Regras:
- Não use markdown.
- Inclua uma saudação apropriada.
- Resuma o ponto principal do e-mail original.
- Se houver vários pontos, use bullet points (-) para clareza.
- Termine com um fechamento cordial.
- Inclua a assinatura fornecida.

Assinatura para usar no final:
{signature}

--- E-mail Original ---
Assunto: {subject}
Conteúdo:
{content}
"""

# --- Funções de Serviço ---

def _signature_block() -> str:
    """Monta uma assinatura para o e-mail a partir de variáveis de ambiente."""
    if prebuilt := os.getenv("REPLY_SIGNATURE"):
        return prebuilt.strip()

    parts = [
        os.getenv("REPLY_SENDER_NAME"),
        os.getenv("REPLY_SENDER_ROLE"),
        os.getenv("REPLY_SENDER_COMPANY"),
        f'Tel.: {os.getenv("REPLY_SENDER_PHONE")}' if os.getenv("REPLY_SENDER_PHONE") else None
    ]
    
    return "\n".join(part for part in parts if part)

def _ensure_configured() -> None:
    """Garante que a SDK do Gemini esteja configurada com uma chave válida."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Gemini API key não encontrada. Defina GEMINI_API_KEY no .env da raiz."
        )
    genai.configure(api_key=GEMINI_API_KEY)

def _get_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(GEMINI_MODEL)

def classify_email(content: str, subject: Optional[str] = None, guidelines: Optional[str] = None) -> str:
    """
    Classifica o conteúdo como 'Produtivo' ou 'Improdutivo'.
    Aplica pré-processamento de NLP para reduzir ruído.
    """
    _ensure_configured()
    cleaned = nlp.preprocess_text(content)
    model = _get_model()
    
    guideline_text = (
        "\nDiretrizes do usuário (priorize estas ao classificar):\n" + guidelines.strip() + "\n"
    ) if guidelines else ""

    prompt = CLASSIFICATION_PROMPT.format(
        guidelines=guideline_text,
        subject=subject or '(sem assunto)',
        cleaned_content=cleaned
    )
    
    response = model.generate_content(prompt)
    text_response = (response.text or "").strip().lower()

    # Evita o bug de substring ("produtivo" em "improdutivo")
    if "improdutivo" in text_response:
        return "Improdutivo"
    if "produtivo" in text_response:
        return "Produtivo"
    # fallback seguro
    return "Improdutivo"

def generate_response(classification: str, content: str, subject: str | None = None) -> Dict[str, str]:
    """Gera a saída de assistência conforme a classificação, sempre padronizando o formato.

    Retorno padrão:
    {
        "classification": "Produtivo" | "Improdutivo",
        "suggested_reply": str,
        "explanation": str (opcional para Improdutivo)
    }
    """
    _ensure_configured()
    model = _get_model()
    cls = classification.strip().capitalize()

    if cls == "Improdutivo":
        prompt = EXPLAIN_UNPRODUCTIVE_PROMPT.format(
            subject=subject or '(sem assunto)',
            content=content
        )
        response = model.generate_content(prompt)
        try:
            # Limpa a resposta para garantir que seja um JSON válido
            json_str = (response.text or "{}").strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(json_str)
            return {
                "classification": "Improdutivo",
                "explanation": data.get("explanation", "Não foi possível gerar a explicação."),
                "suggested_reply": data.get("suggested_reply", "Não foi possível gerar a sugestão de resposta.")
            }
        except (json.JSONDecodeError, AttributeError):
            return {
                "classification": "Improdutivo",
                "explanation": "Erro ao processar a resposta do modelo.",
                "suggested_reply": "Tente novamente."
            }
    
    elif cls == "Produtivo":
        signature = _signature_block()
        prompt = GENERATE_PRODUCTIVE_REPLY_PROMPT.format(
            signature=signature,
            subject=subject or '(sem assunto)',
            content=content
        )
        response = model.generate_content(prompt)
        return {
            "classification": "Produtivo",
            "suggested_reply": (response.text or "").strip()
        }

    return {"error": "Classificação inválida."}
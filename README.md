# YourEmAIL — Classificador Inteligente de E-mails

Classifica e-mails (Produtivo vs. Improdutivo), sugere respostas com Gemini e integra com Gmail para listar mensagens e aplicar labels.

## Visão geral

- Backend: Flask (Python) com endpoints para classificar e gerar respostas (Google Gemini) e integrar com Gmail.
- Frontend: React + Vite (TypeScript).
- IA: Google Generative AI (padrão: `gemini-2.5-flash`, configurável via `GEMINI_MODEL`).
- Login/Permissões: Google Identity Services + Gmail API.

## Requisitos

- Python 3.12 (recomendado) e pip
- Node.js 20+ e npm
- Uma conta Google Cloud com:
  - Gmail API habilitada
  - OAuth 2.0 Client ID (tipo Web) para o front
  - API Key para o GAPI
- Uma chave de API do Google Gemini (Geração de conteúdo)

## Configuração de credenciais

1) Gemini API Key
- Crie/recupere em: https://aistudio.google.com/app/apikey
- Guarde a chave para usar na variável `GEMINI_API_KEY` (arquivo `.env` na raiz).

2) Gmail API / Google Cloud
- No Google Cloud Console, crie um projeto.
- Habilite a API: “Gmail API”.
- Crie uma API Key (usada pelo GAPI no navegador): copie para `VITE_GOOGLE_API_KEY`.
- Crie um OAuth 2.0 Client ID (tipo Aplicativo da Web):
  - Authorized JavaScript origins (desenvolvimento):
    - `http://localhost:5173`
    - `http://localhost:4173` (preview do Vite)
  - Copie o Client ID para `VITE_GOOGLE_CLIENT_ID`.

Observação: O front usa o token client (GIS) e precisa apenas dos “JavaScript origins”.

## Variáveis de ambiente

Crie um arquivo `.env` na RAIZ do projeto (não dentro de `backend/`). O backend carrega daqui automaticamente.

Exemplo de `.env` está em .env.example.

## Como rodar localmente

Abra dois terminais (um para o backend e outro para o frontend). Abaixo os comandos para Windows PowerShell.

### 1) Backend (Flask)

- Instalar dependências e iniciar servidor:

```powershell
cd backend
python -m venv .venv; .\.venv\Scripts\Activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

O backend sobe em `http://localhost:5000` por padrão. CORS permite `http://localhost:5173` (ajuste em `CORS_ALLOWED_ORIGINS` se necessário).

Notas:
- No primeiro uso, o backend pode baixar dados do NLTK (stopwords/rslp). Se falhar, ele usa um fallback simples.
- As variáveis de assinatura (REPLY_*) são opcionais, mas deixam a resposta gerada mais completa.

### 2) Frontend (Vite + React)

- Instalar dependências e iniciar o dev server:

```powershell
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173`.

## Fluxo de uso

1) Acesse o frontend e clique para conectar ao Gmail (permissões: `gmail.readonly` e `gmail.modify`).
2) Liste e-mails, classifique (lote ou individual) e gere resposta sugerida com Gemini.
3) Opcionalmente aplique labels via backend nos e-mails do Gmail.

## Endpoints do backend (resumo)

- POST `/api/classify` — classifica e gera resposta em uma chamada.
- POST `/api/classify-only` — apenas “Produtivo” ou “Improdutivo”.
- POST `/api/generate-reply` — gera resposta a partir de uma classificação existente.
- GET `/api/emails` — lista emails do Gmail (requer header `Authorization: Bearer <token>`).
- POST `/api/emails/{message_id}/label` — aplica label no Gmail (Bearer token requerido).

O backend lê `PORT`, `FLASK_DEBUG` e `CORS_ALLOWED_ORIGINS` do `.env` da raiz.
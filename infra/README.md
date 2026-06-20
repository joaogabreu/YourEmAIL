# YourEmAIL

Classifica e-mails inseridos manualmente ou através de conexão com o Gmail como Produtivo ou Improdutivo e sugere respostas com IA.

Repositório original: https://github.com/israelhub/YourEmAIL

## As duas APIs principais

O projeto tem backend em Flask (Python) e frontend em React (TypeScript/Vite). O backend expõe endpoints REST, faz a classificação, acessa o Gmail e persiste diretrizes e histórico no PostgreSQL; por baixo fala com a Gmail API e a Gemini API da Google. O frontend é a interface, faz login Google e só consome o backend.

## 1. API Backend

Classifica e-mails com Gemini, gera sugestão de resposta, busca mensagens no Gmail, aplica labels e salva diretrizes/histórico no Postgres. Antes de mandar pro modelo, o texto passa por um pré-processamento NLP.

**Rotas**

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | / | Health check |
| POST | /api/classify | Classifica e gera resposta |
| POST | /api/classify-only | Só classifica (Produtivo/Improdutivo) |
| POST | /api/generate-reply | Gera resposta pra e-mail já classificado |
| POST | /api/classify-batch | Classifica vários e-mails de uma vez |
| GET | /api/emails | Lista inbox do Gmail (precisa de Authorization: Bearer token) |
| POST | /api/emails/<message_id>/label | Adiciona label no Gmail (precisa de Bearer token) |
| GET | /api/guidelines | Lê diretrizes do usuário (header X-User-Key) |
| PUT | /api/guidelines | Salva diretrizes |
| GET | /api/history | Histórico de classificações (?limit=50, máx. 200) |

Integrações externas: Gmail em backend/services/gmail.py (list/get de mensagens, labels) e Gemini em backend/services/gemini.py (classificação e respostas).

## 2. Frontend Web

Tela de análise manual, fluxo de conexão com Gmail e inbox classificável. Login via OAuth 2.0 (Google Identity Services) com escopos gmail.readonly e gmail.modify. As chamadas HTTP ficam em frontend/src/services/.

**Rotas**

| Rota | Página | Descrição |
|------|--------|-----------|
| / | ManualClassifier | Colar e-mail e analisar |
| /gmail | GmailConnect | Conectar conta Google |
| /gmail/inbox | GmailClassifier | Inbox com classificação e labels |
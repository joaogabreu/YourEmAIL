import os
from dotenv import load_dotenv

# Carrega sempre o .env da RAIZ do projeto
_ROOT_ENV = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '.env'))
load_dotenv(_ROOT_ENV, override=True)

# Variáveis de ambiente (usar apenas GEMINI_API_KEY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# CORS: lista de origens permitidas separadas por vírgula.
# Use "*" para liberar geral (apenas DEV). Ex.: "http://localhost:5173,http://localhost:4173"
_cors_env = (os.getenv("CORS_ALLOWED_ORIGINS") or "http://localhost:5173").strip()
if _cors_env == "*":
    CORS_ALLOWED_ORIGINS: list[str] | str = "*"
else:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]

# Porta e Debug - Render usa a variável PORT
PORT = int(os.getenv("PORT") or os.getenv("BACKEND_PORT") or 10000)
DEBUG = (os.getenv("FLASK_DEBUG") or os.getenv("DEBUG") or "false").lower() in {"1", "true", "yes", "on"}

# Banco de dados (DATABASE_URL ou componentes POSTGRES_*)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    _pg_user = os.getenv("POSTGRES_USER", "youremail")
    _pg_pass = os.getenv("POSTGRES_PASSWORD", "youremail")
    _pg_host = os.getenv("POSTGRES_HOST", "localhost")
    _pg_port = os.getenv("POSTGRES_PORT", "5432")
    _pg_db = os.getenv("POSTGRES_DB", "youremail")
    DATABASE_URL = f"postgresql://{_pg_user}:{_pg_pass}@{_pg_host}:{_pg_port}/{_pg_db}"

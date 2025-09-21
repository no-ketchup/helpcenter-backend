import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env.local only on host, not in Docker
if not os.getenv("DOCKER_ENV"):
    load_dotenv(BASE_DIR / ".env.local")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required.")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEV_EDITOR_KEY = os.getenv("DEV_EDITOR_KEY", "dev-editor-key")
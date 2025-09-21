import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# If running locally (not Docker), load .env files
if not os.getenv("DOCKER_ENV"):
    load_dotenv(BASE_DIR / ".env")
    env = os.getenv("ENVIRONMENT", "development")
    if env == "test":
        load_dotenv(BASE_DIR / ".env.test", override=True)
    elif env == "production":
        load_dotenv(BASE_DIR / ".env.prod", override=True)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required.")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required.")

# API key for dev-editor endpoints
DEV_EDITOR_KEY = os.getenv("DEV_EDITOR_KEY", "dev-editor-key")
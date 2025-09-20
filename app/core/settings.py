import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# If running locally (not Docker), load .env files
if not os.getenv("DOCKER_ENV"):
    load_dotenv(BASE_DIR / ".env")  # base
    env = os.getenv("ENVIRONMENT", "development")
    if env == "test":
        load_dotenv(BASE_DIR / ".env.test", override=True)
    elif env == "production":
        load_dotenv(BASE_DIR / ".env.prod", override=True)

# Otherwise, trust environment variables passed in by Docker Compose
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
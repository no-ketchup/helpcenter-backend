from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import create_engine
from logging.config import fileConfig
import sys, os

# Add app to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlmodel import SQLModel
from app.core import settings

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# DB URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

# Import models so SQLModel.metadata is populated
from app.domain import models  # noqa
target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode (no DB connection)."""
    context.configure(
        url=settings.DATABASE_URL_SYNC,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode (with DB connection)."""
    connectable = create_engine(settings.DATABASE_URL_SYNC, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
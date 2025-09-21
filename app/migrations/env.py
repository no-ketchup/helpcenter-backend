import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, create_engine
from sqlmodel import SQLModel

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import settings
from app.domain import models  # noqa: F401

# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Pick up DB URL from settings (works for SQLite or Postgres)
db_url = settings.DATABASE_URL
config.set_main_option("sqlalchemy.url", db_url)

# Debug print
print(f"[alembic] Using DATABASE_URL = {db_url}", file=sys.stderr)

# Target metadata
target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode (generates SQL)."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode (applies to DB)."""
    connectable = create_engine(db_url, poolclass=pool.NullPool, future=True)

    # Special handling for SQLite (disable FK pragma errors)
    if db_url.startswith("sqlite"):
        connectable = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            future=True,
        )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
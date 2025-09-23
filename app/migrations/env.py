import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Add project root to sys.spath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import settings

# Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Database URL
db_url = settings.ACTIVE_DATABASE_URL
config.set_main_option("sqlalchemy.url", db_url)
print(f"[alembic] Using ACTIVE_DATABASE_URL = {db_url}", file=sys.stderr)

from app.domain import models
target_metadata = models.metadata


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

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
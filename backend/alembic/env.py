from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool


# Backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

# src directory
SRC_DIR = BASE_DIR / "src"

# Allow Alembic to import your application code
sys.path.insert(0, str(SRC_DIR))


from infrastructure.settings import settings


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Get database URL from .env
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)


# No SQLAlchemy models yet in Phase 1
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a database connection."""

    configuration = config.get_section(
        config.config_ini_section
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
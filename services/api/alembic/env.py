import asyncio
import logging
from logging.config import fileConfig

from sqlalchemy import inspect, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from app.core.config import settings
from app.db import models  # noqa: F401
from app.db.base import Base

logger = logging.getLogger("alembic.env")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using an active database connection."""
    inspector = inspect(connection)
    has_alembic_version = inspector.has_table("alembic_version")
    current_rev = None

    if has_alembic_version:
        mig_context = MigrationContext.configure(connection)
        current_rev = mig_context.get_current_revision()

    # If alembic_version has no revision recorded, but database tables already exist
    # (e.g. created via Base.metadata.create_all during initial deployment),
    # stamp to the current head revision so initial migrations do not fail with DuplicateTableError.
    if current_rev is None and inspector.has_table("organizations"):
        script = ScriptDirectory.from_config(config)
        head_rev = script.get_current_head()
        logger.info(
            "Existing database schema detected without alembic tracking. Auto-stamping revision to %s",
            head_rev,
        )
        mig_context = MigrationContext.configure(connection)
        mig_context.stamp(script, head_rev)
        return

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

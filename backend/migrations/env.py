from alembic import context
from sqlalchemy import engine_from_config, pool

from academy.models import Base

configuration = context.config
if context.is_offline_mode():
    context.configure(
        url=configuration.get_main_option("sqlalchemy.url"), target_metadata=Base.metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = engine_from_config(
        configuration.get_section(configuration.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()

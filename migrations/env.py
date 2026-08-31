from logging.config import fileConfig
from shared.config import config as settings
from sqlalchemy import (
    pool, 
    create_engine,
)
from alembic import context
from shared.infrastructure.database.postgres_base import CustomBase
# حتماً تمام مدل‌های ماژول‌ها را اینجا ایمپورت کنید تا شناسایی شوند
from modules.accounts.infrastructure.persistence.models import AccountModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()



def run_migrations_online() -> None:
    # ۱. تبدیل آدرس به حالت Synchronous
    sync_url = str(settings.POSTGRES_URL).replace("postgresql+asyncpg://", "postgresql://")
    
    # ۲. ساخت Engine با NullPool
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool, 
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, MetaData

from alembic import context

from app.models.base import Base
from app.core.config import settings
from app.core.session import engine
from app.core.log_config import logger

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
target_metadata = Base.metadata


def get_url():
    uri = settings.SQLALCHEMY_DATABASE_URI
    return uri

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
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        current_tenant = context.get_x_argument(as_dictionary=True).get("tenant")
        print(">>>", current_tenant)
        #Todo: need to something about all_tenants_121
        if current_tenant == "all_tenants_121":
            #Todo: all schema name list dynamically
            for tenant_schema_name in ["test_t2s"]:
                conn = connection.execution_options(schema_translate_map={None: tenant_schema_name})

                logger.info("Migrating tenant schema %s" % tenant_schema_name)
                context.configure(
                    connection=conn,
                    target_metadata=target_metadata,
                    version_table_schema=tenant_schema_name,
                    include_schemas=True
                )

                with context.begin_transaction():
                    context.execute(f'set search_path to {tenant_schema_name}')
                    context.run_migrations()
        else:
            conn = connection.execution_options(schema_translate_map={None: current_tenant})
            print("<><><>", conn)
            logger.info("Migrating tenant schema %s" % current_tenant)
            context.configure(
                connection=conn,
                target_metadata=target_metadata,
                version_table_schema=current_tenant,
                include_schemas=True
            )

            with context.begin_transaction():
                context.execute(f'set search_path to {current_tenant}')
                context.run_migrations()
    


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

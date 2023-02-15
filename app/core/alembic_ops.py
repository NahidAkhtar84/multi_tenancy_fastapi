
import argparse
import sqlalchemy as sa
from alembic import command
from alembic.config import Config

from app.core.decorator import timer
from app.core.log_config import logger
from app.core.config import settings




@timer
def alembic_upgrade_head(tenant_name: str, revision="head", url: str = None):
    logger.info("🔺 [Schema upgrade] " + tenant_name + " to version: " + revision)
    print("🔺[Schema upgrade] " + tenant_name + " to version: " + revision)
    # set the paths values

    if url is None:
        url = settings.SQLALCHEMY_DATABASE_URI
    try:
        # create Alembic config and feed it with paths
        config = Config("alembic.ini")
        config.set_main_option("script_location", "app/alembic")  # replace("%", "%%")
        config.set_main_option("sqlalchemy.url", url)
        config.cmd_opts = argparse.Namespace()  # arguments stub

        # If it is required to pass -x parameters to alembic
        x_arg = "".join(["tenant=", tenant_name])  # "dry_run=" + "True"
        if not hasattr(config.cmd_opts, "x"):
            if x_arg is not None:
                setattr(config.cmd_opts, "x", [])
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                setattr(config.cmd_opts, "x", None)

        # prepare and run the command
        revision = revision
        sql = False
        tag = None
        # command.stamp(config, revision, sql=sql, tag=tag)

        # upgrade command
        command.upgrade(config, revision, sql=sql, tag=tag)
    except Exception as e:
        logger.error(f">>: {e}")

    logger.info("✅ Schema upgraded for: " + tenant_name + " to version: " + revision)
    print("✅ Schema upgraded for: " + tenant_name + " to version: " + revision)
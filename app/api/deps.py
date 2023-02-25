import argparse
from contextlib import contextmanager
from typing import Generator, Optional

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.log_config import logger
from app.core.session import engine
from app.models.tenant import Tenant

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API}/auth/login-access-token")


@contextmanager
def with_db(tenant_schema: Optional[str]):
    if tenant_schema:
        schema_translate_map = dict(tenant=tenant_schema)
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)

    try:
        db = Session(autocommit=False, autoflush=False, bind=connectable)
        yield db
    finally:
        db.close()


def alembic_update(tenant_name: str, revision: str = "head", url: str = None) -> None:
    logger.info("<Schema upgrade>: [🔼] " + "Upgrading " + tenant_name + " to version: " + revision)

    if url is None:
        url = settings.SQLALCHEMY_DATABASE_URI
    try:
        # create Alembic config and feed it with paths
        config = Config("alembic.ini")
        config.set_main_option("script_location", "app/alembic")
        config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
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

        # upgrade command
        command.upgrade(config, revision, sql=sql, tag=tag)
        logger.info("<Schema upgrade>: [✅]" + "Upgrading" + tenant_name + " to version: " + revision + "completed")
    except Exception as e:
        logger.error(
            "<Schema upgrade>: [❌]" + "Upgrading" + tenant_name + " to version: " + revision + "failed. " + f"Error: {e}")


def alembic_create(tenant_name: str, revision: str = "head") -> None:
    logger.info("<Schema create>: [🛠️] " + "Creating " + tenant_name)
    try:
        config = Config("alembic.ini")
        config.set_main_option("script_location", "app/alembic")
        config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
        config.cmd_opts = argparse.Namespace()

        x_arg = "".join(["tenant=", tenant_name])
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
        # Todo: get the first alembic version dinamically.
        command.stamp(config, revision, purge=True)
        logger.info("<Schema create>: [✅] " + "Creating " + revision + "to " + tenant_name + "completed")
    except Exception as e:
        logger.error(
            "<Schema create>: [❌] " + "Creating " + revision + "to " + tenant_name + "failed. " + f"Error: {e}")


def tenant_create(tenant_name: str, revision: str = "head") -> None:
    logger.info("<Tenant create>: [🛠️] " + "Creating " + tenant_name)
    with with_db(tenant_name) as db:
        tenant = Tenant(
            name=tenant_name,
            host=tenant_name,
            schema=tenant_name,
        )
        db.add(tenant)
        db.execute(sa.schema.CreateSchema(tenant_name))
        db.commit()
    logger.info("<Tenant create>: [✅] " + "Completed " + tenant_name)


def get_tenant(req: Request) -> Tenant:
    host_without_port = req.headers["host"].split(":", 1)[0]

    with with_db(None) as db:
        tenant = db.query(Tenant).filter(Tenant.host == host_without_port).one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant not found",
        )

    return tenant


def get_db(tenant: Tenant = Depends(get_tenant)) -> Generator:
    with with_db(tenant.schema) as db:
        yield db

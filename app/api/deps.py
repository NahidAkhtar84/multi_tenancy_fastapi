import alembic
import argparse
import sqlalchemy as sa

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from contextlib import contextmanager
from alembic.migration import MigrationContext
from alembic.config import Config
from alembic import command

from app.core import const
from app.core.config import settings
from app.crud.user import CRUDUser
from app.core.session import SessionLocal
from app.models import User
from app.core.log_config import logger
from app.core.session import engine
from app.models.base import get_tenant_specific_metadata
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

def tenant_update(tenant_name: str, revision="head", url: str = None):
    logger.info("🔺 [Schema upgrade] " + tenant_name + " to version: " + revision)
    print("🔺[Schema upgrade] " + tenant_name + " to version: " + revision)
    # set the paths values

    if url is None:
        url = settings.SQLALCHEMY_DATABASE_URI
    try:
        # create Alembic config and feed it with paths
        config = Config("alembic.ini")
        config.set_main_option("script_location", "app/alembic") 
        config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
        # config.cmd_opts = argparse.Namespace()  # arguments stub

        # If it is required to pass -x parameters to alembic
        # x_arg = "".join(["tenant=", tenant_name])  # "dry_run=" + "True"
        # if not hasattr(config.cmd_opts, "x"):
        #     if x_arg is not None:
        #         setattr(config.cmd_opts, "x", [])
        #         if isinstance(x_arg, list) or isinstance(x_arg, tuple):
        #             for x in x_arg:
        #                 config.cmd_opts.x.append(x)
        #         else:
        #             config.cmd_opts.x.append(x_arg)
        #     else:
        #         setattr(config.cmd_opts, "x", None)

        # prepare and run the command
        revision = revision
        sql = False
        tag = None
        # command.stamp(config, revision, sql=sql, tag=tag)

        # upgrade command
        # command.stamp(config, "head", purge=True)
        command.upgrade(config, revision, sql=sql, tag=tag)
    except Exception as e:
        logger.error(e)



def tenant_create(name: str, schema: str, host: str) -> None:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "app/alembic") 
    config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
    config.cmd_opts = argparse.Namespace()

    with with_db(schema) as db:
        tenant = Tenant(
            name=name,
            host=host,
            schema=schema,
        )
        db.add(tenant)
        db.execute(sa.schema.CreateSchema(schema))
        db.commit()
        # get_tenant_specific_metadata().create_all(bind=db.connection())

        x_arg = "".join(["tenant=", schema])
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
        #Todo: get the first alembic version dinamically.
        command.stamp(config, "fe69bd1396dc", purge=True)
        

def get_tenant(req: Request) -> Tenant:
    host_without_port = req.headers["host"].split(":", 1)[0]

    with with_db(None) as db:
      tenant = db.query(Tenant).filter(Tenant.host==host_without_port).one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant not found",
        )

    return tenant

def get_db(tenant: Tenant = Depends(get_tenant)) -> Generator:
    with with_db(tenant.schema) as db:
        yield db


# def get_db() -> Generator:
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()


user_crud = CRUDUser(User)
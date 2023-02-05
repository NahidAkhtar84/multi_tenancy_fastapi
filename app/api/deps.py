import alembic
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


def tenant_create(name: str, schema: str, host: str) -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "app/alembic") 
    alembic_cfg.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

    with with_db(schema) as db:
        context = MigrationContext.configure(db.connection())
        script = alembic.script.ScriptDirectory.from_config(alembic_cfg)
        if context.get_current_revision() != script.get_current_head():
            raise RuntimeError(
                "Database is not up-to-date. Execute migrations before adding new tenants."
            )

        tenant = Tenant(
            name=name,
            host=host,
            schema=schema,
        )
        db.add(tenant)

        db.execute(sa.schema.CreateSchema(schema))
        get_tenant_specific_metadata().create_all(bind=db.connection())

        db.commit()

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
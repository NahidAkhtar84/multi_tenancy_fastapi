from typing import Any

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api import deps
from app.crud.user import CRUDUser
from app.models.user import User
from app.core.log_config import logger
from app.api.deps import tenant_create, alembic_create, alembic_update

tenant_router = APIRouter()


@tenant_router.post("/create",)
def create_new_tenant(
    *,
    tenant_name: str
) -> Any:
    """
    Create new tenant.
    """
    tenant_create(tenant_name)
    alembic_create(tenant_name, "623b3ab58a36")
    return {"detail": f"Tenant with name {tenant_name} created successfully"}


@tenant_router.post("/update",)
def update_new_tenant(
    *,
    tenant_name: str
) -> Any:
    """
    Create new tenant.
    """
    alembic_update(tenant_name)
    return {"detail": f"Tenant with name {tenant_name} updated successfully"}


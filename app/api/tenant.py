from typing import Any

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api import deps
from app.crud.user import CRUDUser
from app.models.user import User
from app.core.log_config import logger
from app.api.deps import tenant_create, tenant_update

tenant_router = APIRouter()


@tenant_router.post("/create",)
def create_new_tenant(
    *,
    tenant_name: str
) -> Any:
    """
    Create new tenant.
    """
    tenant_create(tenant_name, tenant_name, tenant_name)

    return {"detail": f"Tenant with name {tenant_name} created successfully"}


@tenant_router.post("/update",)
def update_new_tenant(
    *,
    tenant_name: str
) -> Any:
    """
    Create new tenant.
    """
    tenant_update(tenant_name)

    return {"detail": f"Tenant with name {tenant_name} updated successfully"}


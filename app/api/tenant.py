from typing import Any

from fastapi import APIRouter, Body, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate, LimitOffsetPage

from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from app.api.deps import tenant_create
from app.core.alembic_ops import alembic_upgrade_head



tenant_router = APIRouter()


@tenant_router.post("/create")
def create_tenant(name: str) -> Any:
    """
    Create new user.
    """
    tenant_create(name, name, name)
    return {"message": "tenant created succesfully"}


@tenant_router.post("/update")
def update_tenant(name: str) -> Any:
    """
    Create new user.
    """
    alembic_upgrade_head(f"{name}")
    return {"message": "tenant updated succesfully"}
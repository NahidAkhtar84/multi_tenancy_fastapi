from typing import Any

from fastapi import APIRouter, Body, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate, LimitOffsetPage

from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app.api import deps
from app.core.enums import MailType
from app.crud.user import CRUDUser
from app.models.user import User
from app.schemas.user import (
    UserInDBBase, UserCreate, UserUpdate,
    UserPassUpdate, UserRegister, UserProfileUpdate
)
from app.core.log_config import logger
from app.core.security import get_password_hash, generate_invite_user_token, verify_password
from sqlalchemy import and_, or_, func
from app.core.utils import decode_token

user_crud = CRUDUser(User)

profile_router = APIRouter()

user_router = APIRouter()


@user_router.post("/create", response_model=UserInDBBase)
def create_new_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
) -> Any:
    """
    Create new user.
    """
    user_crud.user_already_exists(db, user_email=user_in.email)

    return user_crud.create(db, obj_in=user_in)


@user_router.get("/{id}", response_model=UserInDBBase)
def get_user_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:

    return user_crud.user_exists(db, user_id=id)



@user_router.put("/{user_id}", response_model=UserInDBBase)
def update_other_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate
) -> Any:
    """
    Update a user.
    """
    user = user_crud.user_exists(db, user_id=user_id)
    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@user_router.delete("/{id}")
def remove_user(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    user_crud.user_exists(db, user_id=id)
    return user_crud.remove(db, id=id)

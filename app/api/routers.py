from fastapi import APIRouter

from app.api import *

api_router = APIRouter()
api_router.include_router(user.user_router, prefix="/user", tags=["User"])

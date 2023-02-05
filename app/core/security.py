import jwt
from app.core.utils import encode_token, decoding_base64_string

from datetime import datetime, timedelta
from typing import Any, Union

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import ValidationError
from fastapi import HTTPException, status

from app import models
from app.core.config import settings
from app.core.log_config import logger
from app.core.const import ALGORITHM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_min: int = None
) -> str:
    if expires_min:
        expire = datetime.utcnow() + timedelta(minutes=expires_min)
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(
    subject: Union[str, Any], expires_min: int = None
) -> str:
    if expires_min:
        expire = datetime.utcnow() + timedelta(minutes=expires_min)
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def get_access_token_from_refresh_token(db: Session, refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.exceptions.ExpiredSignatureError as error:
        logger.error(f"{error}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    except (ValidationError):
        logger.error("Could not validate credentials")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    token_user = db.query(models.User).filter(models.User.id == int(payload['sub'])).first()
    return token_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Todo: change it
def generate_password_reset_token(email: str) -> str:
    data = {"email": email}
    return encode_token(data, settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES, sub=email)


def generate_invite_user_token(email: str) -> str:
    data = {"email": email}
    return encode_token(data, settings.EMAIL_INVITE_TOKEN_EXPIRE_MINUTES)


def verify_password_reset_token(token: str) -> str | None:
    try:
        token_data = jwt.decode(
            str(decoding_base64_string(token)), settings.SECRET_KEY, algorithms=[ALGORITHM])
        dt_object = datetime.fromtimestamp(token_data['exp'])

        if datetime.utcnow() > dt_object:
            logger.error(
                f"Reset token {token} expires {dt_object} hits at {datetime.utcnow()}")
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Token Expires!")

        return token_data["sub"]

    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError) as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")


import base64, jwt
from datetime import datetime, timedelta
from typing import Optional, Any
from fastapi import HTTPException, status

from app.core.const import ALGORITHM
from app.core.config import settings
from app.core.log_config import logger


def encoding_base64_string(value: str) -> str:
    value_bytes = value.encode('ascii')
    base64_bytes = base64.b64encode(value_bytes)
    base64_value = base64_bytes.decode('ascii')
    return base64_value

def decoding_base64_string(base64_value: str) -> str:
    base64_bytes = base64_value.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    value = message_bytes.decode('ascii')
    return value

def encode_token(data: dict, expire_in_minites, sub:Any = None) -> str:
    token_data = data
    expire = datetime.utcnow() + timedelta(minutes=expire_in_minites)
    token_data.update({"exp": expire, 'token_type': 'access'})
    if sub:
        token_data.update({"sub": sub})
    encoded_jwt = jwt.encode(token_data, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoding_base64_string(str(encoded_jwt))

def decode_token(token: str) -> Optional[str]:
    try:
        token_data = jwt.decode(
            str(decoding_base64_string(token)), settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
    except jwt.exceptions.ExpiredSignatureError as error:
        logger.error(f"{error}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    return token_data




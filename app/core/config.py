import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator
from app.core.log_config import logger


class Settings(BaseSettings):
    API: str = "/api"
    PROJECT_DIR = Path(__file__).parent
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 120
    EMAIL_INVITE_TOKEN_EXPIRE_MINUTES: int = 24*60
    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 1*60
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION_NAME: str

    USERS_OPEN_REGISTRATION: bool = False
    PROJECT_NAME: str
    VERSION_TAG: str
    VERSION_COMMIT_HASH: str = ""

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    POSTGRES_PUBLIC_SCHEMA: str

    MAIL_USER: str
    MAIL_PASSWORD: str

    DATA_SEED: int = 0
    REMARK_MENTION_MAIL: bool = False
    APPLICATION_CREATE_MAIL: bool = False

    HOST_URI: str = "http://localhost"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        logger.error(f"{ValueError(v)}")
        raise ValueError(v)

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @property
    def FULL_VERSION(self):
        return settings.VERSION_TAG + ("." + settings.VERSION_COMMIT_HASH if settings.VERSION_COMMIT_HASH else "")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

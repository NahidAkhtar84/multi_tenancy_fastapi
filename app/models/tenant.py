from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column("id", Integer, primary_key=True, nullable=False)
    name = Column("name", String(256), nullable=False, index=True, unique=True)
    schema = Column("schema", String(256), nullable=False, unique=True)
    host = Column("host", String(256), nullable=False, unique=True)

    __table_args__ = ({"schema": "shared"},)
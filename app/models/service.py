from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    test = Column(String)
    status = Column(Integer)

    __table_args__ = ({"schema": "tenant"},)

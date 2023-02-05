import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

if 'pytest' in ','.join(sys.argv):
    DB_URL = f"{settings.SQLALCHEMY_DATABASE_URI}_test"
else:
    DB_URL = settings.SQLALCHEMY_DATABASE_URI

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

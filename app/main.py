from os import path
from alembic import context, command
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import schema
from sqlalchemy.engine import reflection

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.routers import api_router
from app.core.config import settings
from app.core.session import engine, SessionLocal
from app.models.base import Base, get_shared_metadata
from app.core.log_config import logger

app = FastAPI(title=settings.PROJECT_NAME, version=settings.FULL_VERSION)

root_path = path.dirname(path.abspath(__file__))

app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API)

# Pagination Configuration
add_pagination(app)

@app.get("/")
def read_root():
    return "Hello World, ATS is running healthy!"

@app.get("/version")
def read_root():
    return settings.FULL_VERSION

@app.on_event("startup")
def startup():
    logger.info("🚀 [Starting up] Initializing public schema and public revisions...")

    def _has_table(engine, table_name):
        inspector = reflection.Inspector.from_engine(engine)
        tables = inspector.get_table_names()
        return table_name in tables

    with engine.begin() as db:
        #Todo: Need to read public_schema_name from env
        public_schema_name = "shared"
        if not db.dialect.has_schema(engine, public_schema_name):
            db.execute(schema.CreateSchema("shared"))
            get_shared_metadata().create_all(bind=db)

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "app/alembic")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
        alembic_cfg.attributes["connection"] = db
        if _has_table(db, "alembic_version"):
            # command.upgrade(alembic_cfg, "head", sql=False, tag=None)
            pass
        else:
            command.stamp(alembic_cfg, "head", purge=True)
        logger.info("🎽 [Job] Initialization complete.")


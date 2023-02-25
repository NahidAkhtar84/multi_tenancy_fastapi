from os import path
from alembic.config import Config
from sqlalchemy import schema
from sqlalchemy.engine import reflection

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.routers import api_router
from app.core.config import settings
from app.core.session import engine
from app.core.log_config import logger
from app.api.deps import alembic_create, alembic_update

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


@app.get("/health_check")
def read_root():
    return "[🍏] App is running healthy!"


@app.get("/version")
def read_root():
    return settings.FULL_VERSION


@app.on_event("startup")
def startup():
    logger.info("<Startup Event>: [🚀] Initializing public schema and public revisions.")

    def _has_table(engine, table_name):
        inspector = reflection.Inspector.from_engine(engine)
        tables = inspector.get_table_names()
        return table_name in tables

    public_schema_name = settings.POSTGRES_PUBLIC_SCHEMA
    if not engine.dialect.has_schema(engine, public_schema_name):
        engine.execute(schema.CreateSchema(public_schema_name))

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "app/alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
    alembic_cfg.attributes["connection"] = engine

    if _has_table(engine, "alembic_version"):
        alembic_update("public", "623b3ab58a36")
        logger.info("[🆙] Public schema updated with latest alembic version.")
    else:
        alembic_create("public", "fe69bd1396dc")
        logger.info("[🆗] Public schema created.")
    logger.info("<Startup Event>: [🪂] Initialization of public schema and public revisions completed.")

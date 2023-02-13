from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sqlalchemy import schema

from app.api.routers import api_router
from app.core.config import settings
from app.core.session import engine, SessionLocal
from app.models.base import Base, get_shared_metadata
from app.core.log_config import logger
from alembic import context
from alembic.config import Config
from alembic import command
from os import path
from alembic.migration import MigrationContext

app = FastAPI(title=settings.PROJECT_NAME, version=settings.FULL_VERSION)


root_path = path.dirname(path.abspath(__file__))


with engine.begin() as db:
    context = MigrationContext.configure(db)
    if context.get_current_revision() is not None:
        print("Database already exists.")
    else:
        db.execute(schema.CreateSchema("shared"))
        get_shared_metadata().create_all(bind=db)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "app/alembic") 
    alembic_cfg.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

    alembic_cfg.attributes["connection"] = db
    command.stamp(alembic_cfg, "head", purge=True)

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





# @app.on_event("startup")
# def startup():
#     logger.info("🚀 [Starting up] Initializing DB data...")
#     alembic_upgrade_head("public", "d6ba8c13303e")
#     logger.info("🎽 [Job] Running test Job")

# import argparse
# # import sqlalchemy as sa
# from alembic import command
# from alembic.config import Config
# # from loguru import logger
# # from sentry_sdk import capture_exception

# # from app.config import get_settings
# # from app.db import SQLALCHEMY_DATABASE_URL, with_db
# from app.core.decorator import timer

# # settings = get_settings()


# @timer
# def alembic_upgrade_head(tenant_name: str, revision="head", url: str = None):
#     logger.info("🔺 [Schema upgrade] " + tenant_name + " to version: " + revision)
#     print("🔺[Schema upgrade] " + tenant_name + " to version: " + revision)
#     # set the paths values

#     if url is None:
#         url = settings.SQLALCHEMY_DATABASE_URI
#     try:
#         # create Alembic config and feed it with paths
#         config = Config(str("app/alembic.ini"))
#         config.set_main_option("script_location", str("app/alembic"))  # replace("%", "%%")
#         config.set_main_option("sqlalchemy.url", url)
#         config.cmd_opts = argparse.Namespace()  # arguments stub

#         # If it is required to pass -x parameters to alembic
#         x_arg = "".join(["tenant=", tenant_name])  # "dry_run=" + "True"
#         if not hasattr(config.cmd_opts, "x"):
#             if x_arg is not None:
#                 setattr(config.cmd_opts, "x", [])
#                 if isinstance(x_arg, list) or isinstance(x_arg, tuple):
#                     for x in x_arg:
#                         config.cmd_opts.x.append(x)
#                 else:
#                     config.cmd_opts.x.append(x_arg)
#             else:
#                 setattr(config.cmd_opts, "x", None)

#         # prepare and run the command
#         revision = revision
#         sql = False
#         tag = None
#         # command.stamp(config, revision, sql=sql, tag=tag)

#         # upgrade command
#         command.upgrade(config, revision, sql=sql, tag=tag)
#     except Exception as e:
#         logger.error(e)

#     logger.info("✅ Schema upgraded for: " + tenant_name + " to version: " + revision)
#     print("✅ Schema upgraded for: " + tenant_name + " to version: " + revision)

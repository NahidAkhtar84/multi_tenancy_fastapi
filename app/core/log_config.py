import os, datetime, logging
from pydantic import BaseModel

from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

from app.core.const import LOG_RECORDS_PATH


class LogConfig(BaseModel):
    LOGGER_NAME: str = "ats"
    LOG_FORMAT: str = "%(levelprefix)s | %(pathname)s | %(lineno)d | %(levelname)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "ats": {"handlers": ["default"], "level": LOG_LEVEL},
    }


def log_config():
    dictConfig(LogConfig().dict())
    logger = logging.getLogger("ats")
    
    if not os.path.exists(LOG_RECORDS_PATH):
        os.makedirs(LOG_RECORDS_PATH)

    # RotatingFileHandler is used to limit the log file. This setting will allow 300000 bytes per file and it will generate 5 files.
    file_handler = RotatingFileHandler(f'{LOG_RECORDS_PATH}/logs.log', maxBytes=100000, backupCount=5)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s: %(lineno)d (%(funcName)s) %(message)s'))
    logger.addHandler(file_handler)

    return logger


logger = log_config()

# Log Messages types
# info
# warning
# error
# debug
# critical

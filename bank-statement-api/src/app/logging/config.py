import logging.config
import os

from .dynamic_file_handler import DynamicContentFileHandler

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "raw": {"format": "%(message)s"},
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "big_file": {
            "class": "src.app.logging.dynamic_file_handler.DynamicContentFileHandler",
            "level": "DEBUG",
            "formatter": "raw",
            "directory": "logs/files",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "standard",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
        },
    },
    "loggers": {
        "app.llm.big": {"handlers": ["big_file"], "level": "DEBUG", "propagate": False},
        "app": {"handlers": ["console", "file"], "level": "INFO", "propagate": True},
    },
}


def init_logging():
    os.makedirs("logs", exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

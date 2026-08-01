import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.addHandler(stream_handler)
    root.addHandler(file_handler)

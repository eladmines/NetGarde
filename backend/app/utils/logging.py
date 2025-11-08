import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json


def _get_log_level() -> int:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # Include any structured extras
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    """Configure root logging with console and optional rotating file handler.

    Env vars:
      - LOG_LEVEL: logging level (default INFO)
      - LOG_JSON: if "1", use JSON formatter on console (default 0)
      - LOG_TO_FILE: if "0" disable file handler (default 1)
      - LOG_FILE_PATH: path to log file (default logs/app.log)
      - LOG_FILE_MAX_BYTES: rotate size (default 5_000_000)
      - LOG_FILE_BACKUP_COUNT: backups to keep (default 5)
    """

    root_logger = logging.getLogger()
    # Avoid duplicating handlers if called multiple times (e.g., in tests)
    if getattr(root_logger, "_configured", False):
        return

    root_logger.setLevel(_get_log_level())

    use_json = os.getenv("LOG_JSON", "0") == "1"
    to_file = os.getenv("LOG_TO_FILE", "1") != "0"
    file_path = os.getenv("LOG_FILE_PATH", "logs/app.log")
    max_bytes = int(os.getenv("LOG_FILE_MAX_BYTES", "5000000"))
    backup_count = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

    # Console handler
    console_handler = logging.StreamHandler()
    if use_json:
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    root_logger.addHandler(console_handler)

    # Rotating file handler
    if to_file:
        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=str(path_obj), maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(file_handler)

    # Mark configured
    setattr(root_logger, "_configured", True)


def get_logger(name: str) -> logging.Logger:
    """Convenience accessor for module-level loggers."""
    return logging.getLogger(name)



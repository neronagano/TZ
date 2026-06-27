import logging
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter

from core.settings import settings


class JSONFormatter(JsonFormatter):
    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)


def configure_logging(
    log_file: str | None = None,
    include_uvicorn: bool = False,
) -> None:
    log_level = settings.LOG_LEVEL.upper()
    log_format = settings.LOG_FORMAT.lower()
    formatter = _build_formatter(log_format)
    handlers = _build_handlers(formatter, log_file)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    for handler in handlers:
        root_logger.addHandler(handler)

    if include_uvicorn:
        for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            uvicorn_logger = logging.getLogger(logger_name)
            uvicorn_logger.handlers.clear()
            uvicorn_logger.setLevel(log_level)
            for handler in handlers:
                uvicorn_logger.addHandler(handler)
            uvicorn_logger.propagate = False


def _build_formatter(log_format: str) -> logging.Formatter:
    if log_format == "json":
        return JSONFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _build_handlers(
    formatter: logging.Formatter,
    log_file: str | None,
) -> list[logging.Handler]:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    handlers: list[logging.Handler] = [stream_handler]

    if log_file is not None:
        log_file_path = Path(log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    return handlers

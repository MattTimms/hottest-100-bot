import logging
import sys
from types import FrameType
from typing import cast

from loguru import logger


def configure_logging() -> None:
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in ("uvicorn.asgi", "uvicorn.access"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler(level=logging.INFO)]

    logger.configure(handlers=[{"sink": sys.stderr, "level": logging.INFO}])


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )

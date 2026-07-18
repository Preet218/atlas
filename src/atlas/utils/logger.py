import sys

from loguru import logger

from atlas.config.settings import get_settings


def configure_logger():
    settings = get_settings()

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )
    return logger

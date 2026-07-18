"""Atlas configuration."""

from .paths import (
    CACHE_DIR,
    DATA_DIR,
    LOG_DIR,
    PROJECT_ROOT,
    SRC_DIR,
    TESTS_DIR,
)
from .settings import Settings, get_settings

__all__ = [
    "CACHE_DIR",
    "DATA_DIR",
    "LOG_DIR",
    "PROJECT_ROOT",
    "SRC_DIR",
    "TESTS_DIR",
    "Settings",
    "get_settings",
]

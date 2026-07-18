"""Filesystem paths used throughout Atlas."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

SRC_DIR = PROJECT_ROOT / "src"

DATA_DIR = PROJECT_ROOT / "data"

LOG_DIR = PROJECT_ROOT / "logs"

CACHE_DIR = PROJECT_ROOT / ".cache"

TESTS_DIR = PROJECT_ROOT / "tests"


for directory in (
    DATA_DIR,
    LOG_DIR,
    CACHE_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

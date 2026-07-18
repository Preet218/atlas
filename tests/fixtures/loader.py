from __future__ import annotations

import json
from pathlib import Path


def load_json_fixture(*parts: str):
    path = Path(__file__).parent.joinpath(*parts)

    with path.open() as f:
        return json.load(f)

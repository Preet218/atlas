from __future__ import annotations

import json
from pathlib import Path

from atlas.discovery.mappers.greenhouse import GreenhouseJobMapper


FIXTURE_PATH = Path(__file__).parents[2] / "fixtures" / "greenhouse" / "detail.json"


def test_map_greenhouse_job() -> None:
    mapper = GreenhouseJobMapper()

    payload = json.loads(FIXTURE_PATH.read_text())

    job = mapper.map(payload)

    assert job.title == payload["title"]
    assert job.company.name == payload["company_name"]
    assert str(job.application.url) == payload["absolute_url"]
    assert job.metadata.source_job_id == str(payload["id"])

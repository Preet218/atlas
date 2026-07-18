from __future__ import annotations

import json
from pathlib import Path

from atlas.discovery.mappers.lever import LeverJobMapper
from atlas.job.models import JobPosting
from atlas.common.enums import JobPlatform

def load_fixture() -> dict:
    fixture = (
        Path(__file__).parents[2]
        / "fixtures"
        / "lever"
        / "listing.json"
    )

    with fixture.open() as f:
        return json.load(f)[0]


def test_map_returns_job_posting():
    payload = load_fixture()

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.title == payload["text"]
    assert job.description == payload["descriptionPlain"]

    assert job.metadata.source_job_id == payload["id"]

    assert str(job.application.url) == payload["hostedUrl"]

    assert job.application.platform == JobPlatform.LEVER

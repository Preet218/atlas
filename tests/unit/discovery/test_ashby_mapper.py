from __future__ import annotations

import json
from pathlib import Path

from atlas.common.enums import JobPlatform
from atlas.discovery.mappers.ashby import AshbyJobMapper
from atlas.discovery.models import DiscoveryTarget
from atlas.job.enums import Currency, EmploymentType, WorkplaceType


def load_fixture() -> list[dict]:
    fixture = Path(__file__).parents[2] / "fixtures" / "ashby" / "listing.json"

    with fixture.open() as f:
        return json.load(f)["jobs"]


def find_job(title_contains: str) -> dict:
    for job in load_fixture():
        if title_contains in job["title"]:
            return job

    raise AssertionError(f"No fixture job found matching {title_contains!r}")


def test_map_returns_job_posting():
    payload = find_job("Technical Program Manager")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.title == payload["title"]
    assert job.description == payload["descriptionPlain"]
    assert job.metadata.source_job_id == payload["id"]
    assert str(job.application.url) == payload["jobUrl"]
    assert job.application.platform == JobPlatform.ASHBY


def test_map_uses_target_identifier_as_company_name():
    payload = find_job("Technical Program Manager")

    mapper = AshbyJobMapper()

    target = DiscoveryTarget(platform=JobPlatform.ASHBY, identifier="openai")

    job = mapper.map(payload, target)

    assert job.company.name == "openai"


def test_map_defaults_company_name_without_target():
    payload = find_job("Technical Program Manager")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.company.name == "Unknown"


def test_map_parses_location_from_postal_address():
    payload = find_job("Account Director")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.location.city == "Tokyo"
    assert job.location.country == "Japan"
    assert job.location.state is None


def test_map_parses_hybrid_workplace_type():
    payload = find_job("RL Training Infra")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.location.workplace_type == WorkplaceType.HYBRID


def test_map_falls_back_to_is_remote_when_workplace_type_missing():
    payload = dict(find_job("Technical Program Manager"))
    payload["workplaceType"] = None
    payload["isRemote"] = True

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.location.workplace_type == WorkplaceType.REMOTE


def test_map_returns_none_workplace_type_when_unset():
    payload = find_job("Technical Program Manager")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.location.workplace_type is None


def test_map_parses_employment_type():
    payload = find_job("Technical Program Manager")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.employment_type == EmploymentType.FULL_TIME


def test_map_handles_missing_compensation():
    payload = find_job("Technical Program Manager")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.compensation is None


def test_map_parses_compensation_when_present():
    payload = dict(find_job("Technical Program Manager"))
    payload["compensation"] = {
        "compensationTierSummary": "$120K - $150K",
        "summaryComponents": [
            {
                "compensationType": "Salary",
                "interval": "1 YEAR",
                "currencyCode": "USD",
                "minValue": 120000,
                "maxValue": 150000,
            }
        ],
    }

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.compensation is not None
    assert job.compensation.currency == Currency.USD
    assert job.compensation.min_salary == 120000
    assert job.compensation.max_salary == 150000


def test_map_parses_posted_at():
    payload = find_job("Technical Program Manager")

    mapper = AshbyJobMapper()

    job = mapper.map(payload)

    assert job.application.posted_at is not None

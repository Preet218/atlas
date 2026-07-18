from __future__ import annotations

import json
from pathlib import Path

import pytest

from atlas.common.enums import JobPlatform
from atlas.discovery.mappers.lever import LeverJobMapper
from atlas.discovery.models import DiscoveryTarget
from atlas.job.enums import Currency, EmploymentType, WorkplaceType


def load_fixture() -> dict:
    fixture = Path(__file__).parents[2] / "fixtures" / "lever" / "listing.json"

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


def test_map_uses_target_identifier_as_company_name():
    payload = load_fixture()

    mapper = LeverJobMapper()

    target = DiscoveryTarget(platform=JobPlatform.LEVER, identifier="dnb")

    job = mapper.map(payload, target)

    assert job.company.name == "dnb"


def test_map_defaults_company_name_without_target():
    payload = load_fixture()

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.company.name == "Unknown"


def test_map_parses_remote_location():
    payload = load_fixture()

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.location.workplace_type == WorkplaceType.REMOTE
    assert job.location.country == payload["country"]
    assert job.location.city is None


def test_map_parses_onsite_city_state_location():
    payload = load_fixture()
    payload = {**payload, "workplaceType": "onsite"}
    payload["categories"] = {**payload["categories"], "location": "San Francisco, CA"}

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.location.workplace_type == WorkplaceType.ONSITE
    assert job.location.city == "San Francisco"
    assert job.location.state == "CA"


def test_map_parses_employment_type():
    payload = load_fixture()

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.employment_type == EmploymentType.FULL_TIME


@pytest.mark.parametrize(
    "commitment,expected",
    [
        ("Part Time", EmploymentType.PART_TIME),
        ("Contractor", EmploymentType.CONTRACT),
        ("Internship", EmploymentType.INTERN),
        ("Temporary", EmploymentType.TEMPORARY),
        ("Freelance", EmploymentType.FREELANCE),
        ("Unknown Commitment", None),
    ],
)
def test_map_parses_various_employment_types(commitment, expected):
    payload = load_fixture()
    payload["categories"] = {**payload["categories"], "commitment": commitment}

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.employment_type == expected


def test_map_parses_compensation():
    payload = load_fixture()

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.compensation is not None
    assert job.compensation.currency == Currency.USD
    assert job.compensation.min_salary == payload["salaryRange"]["min"]
    assert job.compensation.max_salary == payload["salaryRange"]["max"]


def test_map_handles_missing_compensation():
    payload = load_fixture()
    payload.pop("salaryRange", None)

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.compensation is None


def test_map_parses_posted_at_from_created_at():
    payload = load_fixture()

    mapper = LeverJobMapper()

    job = mapper.map(payload)

    assert job.application.posted_at is not None

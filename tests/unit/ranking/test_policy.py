from __future__ import annotations

import pytest

from atlas.ranking.exceptions import InvalidPolicyError
from atlas.ranking.policy import RankingPolicy


def test_default_policy_is_valid():
    policy = RankingPolicy.default()

    policy.validate()  # should not raise


def test_default_policy_weights_sum_to_one():
    policy = RankingPolicy.default()

    total = (
        policy.skills_weight
        + policy.role_weight
        + policy.location_weight
        + policy.compensation_weight
        + policy.experience_weight
        + policy.recency_weight
    )

    assert total == pytest.approx(1.0)


def test_validate_raises_when_weights_do_not_sum_to_one():
    policy = RankingPolicy(
        skills_weight=0.5,
        role_weight=0.5,
        location_weight=0.5,
        compensation_weight=0.0,
        experience_weight=0.0,
        recency_weight=0.0,
    )

    with pytest.raises(InvalidPolicyError):
        policy.validate()


def test_validate_raises_on_negative_weight():
    policy = RankingPolicy(
        skills_weight=-0.1,
        role_weight=0.3,
        location_weight=0.2,
        compensation_weight=0.2,
        experience_weight=0.2,
        recency_weight=0.2,
    )

    with pytest.raises(InvalidPolicyError):
        policy.validate()


def test_custom_policy_with_valid_weights():
    policy = RankingPolicy(
        skills_weight=0.5,
        role_weight=0.2,
        location_weight=0.1,
        compensation_weight=0.1,
        experience_weight=0.05,
        recency_weight=0.05,
    )

    policy.validate()  # should not raise

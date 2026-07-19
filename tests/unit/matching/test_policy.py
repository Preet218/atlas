from __future__ import annotations

import pytest

from atlas.matching.exceptions import InvalidPolicyError
from atlas.matching.policy import MatchingPolicy


def test_default_policy_is_valid():
    MatchingPolicy.default().validate()  # should not raise


def test_validate_raises_on_invalid_compensation_floor_ratio():
    policy = MatchingPolicy(compensation_floor_ratio=1.5)

    with pytest.raises(InvalidPolicyError):
        policy.validate()


def test_validate_raises_on_negative_compensation_floor_ratio():
    policy = MatchingPolicy(compensation_floor_ratio=-0.1)

    with pytest.raises(InvalidPolicyError):
        policy.validate()


def test_validate_raises_on_invalid_title_similarity_threshold():
    policy = MatchingPolicy(title_similarity_threshold=1.1)

    with pytest.raises(InvalidPolicyError):
        policy.validate()


def test_custom_policy_with_valid_thresholds():
    policy = MatchingPolicy(
        compensation_floor_ratio=0.7,
        title_similarity_threshold=0.9,
        require_country_match_for_dedup=False,
    )

    policy.validate()  # should not raise

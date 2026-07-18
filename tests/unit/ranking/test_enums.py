from __future__ import annotations

import pytest

from atlas.ranking.enums import MatchStrength


@pytest.mark.parametrize(
    "score,expected",
    [
        (100, MatchStrength.STRONG),
        (80, MatchStrength.STRONG),
        (79.9, MatchStrength.GOOD),
        (60, MatchStrength.GOOD),
        (59.9, MatchStrength.FAIR),
        (40, MatchStrength.FAIR),
        (39.9, MatchStrength.WEAK),
        (0, MatchStrength.WEAK),
    ],
)
def test_from_score(score, expected):
    assert MatchStrength.from_score(score) == expected

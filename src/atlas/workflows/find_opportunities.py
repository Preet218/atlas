"""FindOpportunities: the end-to-end discover -> match -> rank pipeline.

Per docs/architecture.md, "Workflows coordinate services. They do not
implement domain rules." All business logic already lives in
DiscoveryService, MatchingService, and RankingService — this workflow
exists purely to call them in the right order, since nothing else in
the codebase did that yet.
"""

from __future__ import annotations

from datetime import datetime

from atlas.candidate.models import Candidate
from atlas.discovery.models import DiscoveryTarget
from atlas.discovery.service import DiscoveryService
from atlas.matching.service import MatchingService
from atlas.ranking.models import RankedJob
from atlas.ranking.service import RankingService


class FindOpportunitiesWorkflow:
    """Coordinates Discovery, Matching, and Ranking end to end."""

    def __init__(
        self,
        discovery: DiscoveryService,
        matching: MatchingService,
        ranking: RankingService,
    ) -> None:
        self._discovery = discovery
        self._matching = matching
        self._ranking = ranking

    async def run(
        self,
        candidate: Candidate,
        targets: list[DiscoveryTarget],
        now: datetime | None = None,
    ) -> list[RankedJob]:
        """Discover jobs across targets, filter for eligibility and
        cross-platform duplicates, then rank the survivors best-match-first.

        `now` may be supplied for deterministic testing of ranking's
        recency scoring; it defaults to the current UTC time.
        """

        discovered = await self._discovery.discover_many(targets)

        eligible = self._matching.filter_eligible(candidate, discovered)

        return self._ranking.rank(candidate, eligible, now=now)

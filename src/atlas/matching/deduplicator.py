"""JobDeduplicator: detects the same underlying role posted across
multiple platforms (e.g. a company cross-posting to both Greenhouse
and Lever, or a role appearing on Ashby and the company's own site).

Deduplication is normalized-company + fuzzy-title based rather than an
exact match, since the same role is rarely worded identically across
platforms. It is intentionally deterministic (difflib.SequenceMatcher
does no randomized sampling) so results never depend on ordering or
timing.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from difflib import SequenceMatcher

from atlas.job.models import JobPosting
from atlas.matching.models import DuplicateGroup
from atlas.matching.policy import MatchingPolicy

_COMPANY_SUFFIXES = re.compile(
    r"\b(inc|llc|ltd|limited|corp|corporation|co|gmbh|plc|pty)\.?\b",
    re.IGNORECASE,
)
_NON_WORD = re.compile(r"[^\w\s]")
_WHITESPACE = re.compile(r"\s+")


def normalize_company(name: str) -> str:
    """Normalize a company name for duplicate comparison."""

    normalized = name.lower()
    normalized = _COMPANY_SUFFIXES.sub("", normalized)
    normalized = _NON_WORD.sub("", normalized)
    normalized = _WHITESPACE.sub(" ", normalized).strip()
    return normalized


def normalize_title(title: str) -> str:
    """Normalize a job title for duplicate comparison."""

    normalized = title.lower()
    normalized = _NON_WORD.sub("", normalized)
    normalized = _WHITESPACE.sub(" ", normalized).strip()
    return normalized


class JobDeduplicator:
    """Groups job postings that represent the same underlying role."""

    def __init__(self, policy: MatchingPolicy | None = None) -> None:
        self._policy = policy or MatchingPolicy.default()
        self._policy.validate()

    def deduplicate(
        self,
        jobs: list[JobPosting],
    ) -> tuple[list[JobPosting], list[DuplicateGroup]]:
        """Deduplicate a batch of jobs.

        Returns the deduplicated list (one entry per unique role, in
        the order first seen) alongside a DuplicateGroup per cluster
        that had more than one posting, for auditability.

        Note: clustering compares each new job against the first
        (representative) member of each existing group rather than
        computing full transitive closure across every pair. This is a
        deliberate MVP simplification — it may occasionally miss a
        duplicate whose title drifted enough from the group's original
        posting even though it closely matches a later member.
        """

        groups: list[list[JobPosting]] = []

        for job in jobs:
            match = next(
                (group for group in groups if self._is_duplicate(group[0], job)),
                None,
            )

            if match is not None:
                match.append(job)
            else:
                groups.append([job])

        deduplicated: list[JobPosting] = []
        duplicate_groups: list[DuplicateGroup] = []

        for group in groups:
            if len(group) == 1:
                deduplicated.append(group[0])
                continue

            canonical, duplicates = self._select_canonical(group)
            deduplicated.append(canonical)
            duplicate_groups.append(
                DuplicateGroup(canonical=canonical, duplicates=duplicates)
            )

        return deduplicated, duplicate_groups

    def _is_duplicate(self, a: JobPosting, b: JobPosting) -> bool:
        if normalize_company(a.company.name) != normalize_company(b.company.name):
            return False

        similarity = SequenceMatcher(
            None,
            normalize_title(a.title),
            normalize_title(b.title),
        ).ratio()

        if similarity < self._policy.title_similarity_threshold:
            return False

        if self._policy.require_country_match_for_dedup:
            country_a = a.location.country
            country_b = b.location.country

            if country_a and country_b and country_a.lower() != country_b.lower():
                return False

        return True

    def _select_canonical(
        self,
        group: list[JobPosting],
    ) -> tuple[JobPosting, list[JobPosting]]:
        """Pick the most complete, most recently discovered posting."""

        def completeness(job: JobPosting) -> int:
            return sum(
                [
                    job.compensation is not None,
                    bool(job.requirements),
                    bool(job.preferred_skills),
                    bool(job.responsibilities),
                    bool(job.benefits),
                    job.experience_level is not None,
                    bool(job.location.city),
                ]
            )

        def discovered_at(job: JobPosting) -> datetime:
            value = job.metadata.discovered_at

            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)

            return value

        ranked = sorted(
            group,
            key=lambda job: (
                -completeness(job),
                -discovered_at(job).timestamp(),
                job.application.platform.value,
                job.title,
            ),
        )

        return ranked[0], ranked[1:]

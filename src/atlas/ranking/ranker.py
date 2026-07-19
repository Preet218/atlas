"""JobRanker: the domain service that scores a job against a candidate.

Scoring is intentionally deterministic (see docs/architecture.md, "Business
rules should remain deterministic wherever possible") and every dimension
carries a human-readable reason (see docs/specification.md PEP-007,
"Explainable Intelligence").
"""

from __future__ import annotations

from datetime import datetime, timezone

from atlas.candidate.enums import WorkMode
from atlas.candidate.models import Candidate
from atlas.job.enums import ExperienceLevel, WorkplaceType
from atlas.job.models import JobPosting
from atlas.ranking.enums import MatchStrength
from atlas.ranking.models import DimensionScore, RankedJob
from atlas.ranking.policy import RankingPolicy

# Neutral score used whenever there isn't enough data on either side to
# make a confident comparison. Neither rewards nor penalizes the job.
_NEUTRAL_SCORE = 50.0

# Approximate years-of-experience range typically expected for each
# ExperienceLevel. Used only to keep experience scoring deterministic;
# real-world ranges vary by company and role.
_EXPERIENCE_RANGES: dict[ExperienceLevel, tuple[float, float]] = {
    ExperienceLevel.INTERN: (0, 1),
    ExperienceLevel.ENTRY: (0, 2),
    ExperienceLevel.ASSOCIATE: (1, 3),
    ExperienceLevel.MID: (2, 5),
    ExperienceLevel.SENIOR: (5, 8),
    ExperienceLevel.STAFF: (7, 12),
    ExperienceLevel.PRINCIPAL: (9, 15),
    ExperienceLevel.DIRECTOR: (10, 20),
    ExperienceLevel.EXECUTIVE: (12, 30),
}

# Maps candidate WorkMode to job WorkplaceType. Both enums represent the
# same concept but live in different domains (see PEP-006 modularity),
# so ranking is one of the few places that legitimately needs to know
# how they relate.
_WORK_MODE_TO_WORKPLACE_TYPE: dict[WorkMode, WorkplaceType] = {
    WorkMode.ONSITE: WorkplaceType.ONSITE,
    WorkMode.HYBRID: WorkplaceType.HYBRID,
    WorkMode.REMOTE: WorkplaceType.REMOTE,
}


class JobRanker:
    """Scores a single job posting against a candidate profile."""

    def __init__(self, policy: RankingPolicy | None = None) -> None:
        self._policy = policy or RankingPolicy.default()
        self._policy.validate()

    def score(
        self,
        candidate: Candidate,
        job: JobPosting,
        now: datetime | None = None,
    ) -> RankedJob:
        """Score a job posting against a candidate profile.

        Assumes the job has already passed hard eligibility checks (see
        atlas.matching.JobMatcher) — this method scores fit, it doesn't
        decide eligibility.

        `now` may be supplied for deterministic testing of recency
        scoring; it defaults to the current UTC time.
        """

        now = now or datetime.now(timezone.utc)

        dimension_scores = [
            self._score_skills(candidate, job),
            self._score_role(candidate, job),
            self._score_location(candidate, job),
            self._score_compensation(candidate, job),
            self._score_experience(candidate, job),
            self._score_recency(job, now),
        ]

        overall_score = round(
            sum(dimension.weighted_score for dimension in dimension_scores),
            1,
        )

        return RankedJob(
            job=job,
            overall_score=overall_score,
            match_strength=MatchStrength.from_score(overall_score),
            dimension_scores=dimension_scores,
            reasons=self._build_reasons(dimension_scores),
        )

    def _score_skills(self, candidate: Candidate, job: JobPosting) -> DimensionScore:
        """Score how many of the job's listed skills the candidate has."""

        job_skills = {
            skill.lower() for skill in [*job.requirements, *job.preferred_skills]
        }

        if not job_skills:
            return DimensionScore(
                name="skills",
                score=_NEUTRAL_SCORE,
                weight=self._policy.skills_weight,
                reason="Job does not list explicit skill requirements.",
            )

        candidate_skills = {skill.name.lower() for skill in candidate.skills}

        matched = sorted(job_skills & candidate_skills)

        score = 100.0 * len(matched) / len(job_skills)

        if matched:
            preview = ", ".join(matched[:5])
            reason = f"Matches {len(matched)} of {len(job_skills)} listed skills ({preview})."
        else:
            reason = f"Matches 0 of {len(job_skills)} listed skills."

        return DimensionScore(
            name="skills",
            score=round(score, 1),
            weight=self._policy.skills_weight,
            reason=reason,
        )

    def _score_role(self, candidate: Candidate, job: JobPosting) -> DimensionScore:
        """Score how well the job title matches preferred roles."""

        preferred_roles = candidate.preferences.preferred_roles

        if not preferred_roles:
            return DimensionScore(
                name="role",
                score=_NEUTRAL_SCORE,
                weight=self._policy.role_weight,
                reason="No preferred roles specified.",
            )

        title = job.title.lower()

        for role in preferred_roles:
            role_lower = role.lower()

            if role_lower in title or title in role_lower:
                return DimensionScore(
                    name="role",
                    score=100.0,
                    weight=self._policy.role_weight,
                    reason=f"Job title aligns with preferred role '{role}'.",
                )

        domains = [
            *candidate.career_dna.primary_domains,
            *candidate.career_dna.secondary_domains,
        ]

        for domain in domains:
            if domain.lower() in title:
                return DimensionScore(
                    name="role",
                    score=60.0,
                    weight=self._policy.role_weight,
                    reason=f"Job title relates to your '{domain}' experience.",
                )

        return DimensionScore(
            name="role",
            score=30.0,
            weight=self._policy.role_weight,
            reason="Job title doesn't match any stated role preference.",
        )

    def _score_location(self, candidate: Candidate, job: JobPosting) -> DimensionScore:
        """Score location fit: preferred country and preferred work mode."""

        country_score, country_reason = self._score_country(candidate, job)
        mode_score, mode_reason = self._score_work_mode(candidate, job)

        score = (country_score + mode_score) / 2

        return DimensionScore(
            name="location",
            score=round(score, 1),
            weight=self._policy.location_weight,
            reason=f"{country_reason} {mode_reason}".strip(),
        )

    def _score_country(
        self,
        candidate: Candidate,
        job: JobPosting,
    ) -> tuple[float, str]:
        preferred_countries = [
            country.lower() for country in candidate.preferences.preferred_countries
        ]

        if not preferred_countries:
            return _NEUTRAL_SCORE, "No preferred country specified."

        job_country = job.location.country

        if not job_country:
            return _NEUTRAL_SCORE, "Job location's country is unspecified."

        if job_country.lower() in preferred_countries:
            return 100.0, f"Located in a preferred country ({job_country})."

        return 0.0, f"Located outside your preferred countries ({job_country})."

    def _score_work_mode(
        self,
        candidate: Candidate,
        job: JobPosting,
    ) -> tuple[float, str]:
        preferred_modes = candidate.preferences.preferred_work_modes

        if not preferred_modes:
            return _NEUTRAL_SCORE, "No preferred work mode specified."

        workplace_type = job.location.workplace_type

        if workplace_type is None:
            return _NEUTRAL_SCORE, "Job's workplace type is unspecified."

        for mode in preferred_modes:
            if _WORK_MODE_TO_WORKPLACE_TYPE.get(mode) == workplace_type:
                return 100.0, f"Matches your preferred work mode ({mode.value})."

        return 0.0, f"Workplace type ({workplace_type.value}) isn't one you prefer."

    def _score_compensation(
        self,
        candidate: Candidate,
        job: JobPosting,
    ) -> DimensionScore:
        """Score compensation against the candidate's minimum expectation.

        Note: this compares raw numeric values and does not currently
        account for currency differences. Cross-currency comparisons are
        a known limitation and should be revisited before this dimension
        is trusted for candidates targeting multiple currency regions.
        """

        minimum_base_salary = candidate.preferences.minimum_base_salary

        if minimum_base_salary is None or job.compensation is None:
            return DimensionScore(
                name="compensation",
                score=_NEUTRAL_SCORE,
                weight=self._policy.compensation_weight,
                reason="Compensation data unavailable for comparison.",
            )

        job_max = job.compensation.max_salary or job.compensation.min_salary

        if job_max is None:
            return DimensionScore(
                name="compensation",
                score=_NEUTRAL_SCORE,
                weight=self._policy.compensation_weight,
                reason="Job does not publish a salary range.",
            )

        if job_max >= minimum_base_salary:
            return DimensionScore(
                name="compensation",
                score=100.0,
                weight=self._policy.compensation_weight,
                reason="Salary range meets your minimum expectation.",
            )

        ratio = max(0.0, job_max / minimum_base_salary)

        return DimensionScore(
            name="compensation",
            score=round(min(100.0, ratio * 100), 1),
            weight=self._policy.compensation_weight,
            reason="Salary range may fall below your minimum expectation.",
        )

    def _score_experience(
        self,
        candidate: Candidate,
        job: JobPosting,
    ) -> DimensionScore:
        """Score how closely candidate experience matches the job's level."""

        if job.experience_level is None:
            return DimensionScore(
                name="experience",
                score=_NEUTRAL_SCORE,
                weight=self._policy.experience_weight,
                reason="Job does not specify an experience level.",
            )

        low, high = _EXPERIENCE_RANGES[job.experience_level]
        years = candidate.personal.years_of_experience

        if low <= years <= high:
            return DimensionScore(
                name="experience",
                score=100.0,
                weight=self._policy.experience_weight,
                reason=f"Your experience ({years}y) fits the {job.experience_level.value} range.",
            )

        distance = min(abs(years - low), abs(years - high))
        score = max(0.0, 100.0 - distance * 15)

        return DimensionScore(
            name="experience",
            score=round(score, 1),
            weight=self._policy.experience_weight,
            reason=(
                f"Your experience ({years}y) differs from the typical "
                f"{job.experience_level.value} range ({low}-{high}y)."
            ),
        )

    def _score_recency(self, job: JobPosting, now: datetime) -> DimensionScore:
        """Score how recently the job was posted or discovered."""

        reference = job.application.posted_at or job.metadata.discovered_at

        now = self._ensure_aware(now)
        reference = self._ensure_aware(reference)

        days_old = max(0, (now - reference).days)

        if days_old <= 2:
            score, freshness = 100.0, "just posted"
        elif days_old <= 7:
            score, freshness = 80.0, "posted this week"
        elif days_old <= 14:
            score, freshness = 60.0, "posted within two weeks"
        elif days_old <= 30:
            score, freshness = 40.0, "posted within the last month"
        else:
            score, freshness = 20.0, "posted over a month ago"

        return DimensionScore(
            name="recency",
            score=score,
            weight=self._policy.recency_weight,
            reason=f"This job was {freshness} ({days_old} days ago).",
        )

    def _ensure_aware(self, value: datetime) -> datetime:
        """Treat naive datetimes as UTC so comparisons never raise."""

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value

    def _build_reasons(self, dimension_scores: list[DimensionScore]) -> list[str]:
        """Build a short, human-readable explanation of the overall score.

        Highlights the strongest contributing factors first, per
        PEP-007's requirement that users understand why an opportunity
        was highly ranked, and surfaces genuine weak points too so the
        explanation isn't one-sided.
        """

        highlights = [d.reason for d in dimension_scores if d.score >= 70][:3]
        concerns = [d.reason for d in dimension_scores if d.score < 30][:2]

        if highlights:
            return [*highlights, *concerns]

        best = max(dimension_scores, key=lambda d: d.score)
        return [best.reason, *concerns]

"""JobMatcher: the hard eligibility gate between discovery and ranking.

Where JobRanker (see atlas.ranking) produces a continuous 0-100 fit
score, JobMatcher answers a categorical question: is this job even
eligible to be shown to this candidate at all? Excluded companies, a
hard visa mismatch, a location the candidate can't work from, and a
compensation range that's drastically below expectations all belong
here rather than in Ranking, per contributing.md's "No duplicated
logic" — each rule lives in exactly one place.
"""

from __future__ import annotations

from atlas.candidate.enums import VisaRequirement
from atlas.candidate.models import Candidate
from atlas.job.enums import WorkplaceType
from atlas.job.models import JobPosting
from atlas.matching.models import MatchResult
from atlas.matching.policy import MatchingPolicy


class JobMatcher:
    """Evaluates whether a job posting is eligible for a candidate."""

    def __init__(self, policy: MatchingPolicy | None = None) -> None:
        self._policy = policy or MatchingPolicy.default()
        self._policy.validate()

    def evaluate(self, candidate: Candidate, job: JobPosting) -> MatchResult:
        """Return the hard eligibility verdict for a single job."""

        checks = (
            self._check_excluded_company,
            self._check_visa,
            self._check_location,
            self._check_compensation_floor,
        )

        for check in checks:
            reason = check(candidate, job)

            if reason is not None:
                return MatchResult(job=job, is_match=False, reasons=[reason])

        return MatchResult(
            job=job,
            is_match=True,
            reasons=["Meets all hard eligibility requirements."],
        )

    def _check_excluded_company(
        self,
        candidate: Candidate,
        job: JobPosting,
    ) -> str | None:
        excluded = {
            company.lower() for company in candidate.preferences.excluded_companies
        }

        if job.company.name.lower() in excluded:
            return f"{job.company.name} is on your excluded companies list."

        return None

    def _check_visa(self, candidate: Candidate, job: JobPosting) -> str | None:
        """Hard-fail only when the candidate needs sponsorship and the job
        explicitly says it doesn't offer it. An unknown sponsorship status
        (the common case today, since no connector populates it yet) is
        treated as insufficient information, not a failure.
        """

        if candidate.preferences.visa_requirement != VisaRequirement.REQUIRED:
            return None

        if job.visa_sponsorship is False:
            return "This role does not offer visa sponsorship, which you require."

        return None

    def _check_location(self, candidate: Candidate, job: JobPosting) -> str | None:
        """Hard-fail only for non-remote roles based outside every
        preferred country. Remote roles are never location-excluded.
        """

        preferred_countries = [
            country.lower() for country in candidate.preferences.preferred_countries
        ]

        if not preferred_countries:
            return None

        job_country = job.location.country

        if not job_country:
            return None

        if job.location.workplace_type == WorkplaceType.REMOTE:
            return None

        if job_country.lower() not in preferred_countries:
            return (
                f"This role is based in {job_country}, outside your preferred "
                "countries, and isn't remote."
            )

        return None

    def _check_compensation_floor(
        self,
        candidate: Candidate,
        job: JobPosting,
    ) -> str | None:
        """Hard-fail only when pay is drastically below the candidate's
        minimum, per MatchingPolicy.compensation_floor_ratio. A range
        that's merely somewhat below minimum is left to Ranking's
        continuous compensation scoring rather than filtered out here.
        """

        minimum_base_salary = candidate.preferences.minimum_base_salary

        if minimum_base_salary is None or job.compensation is None:
            return None

        job_max = job.compensation.max_salary or job.compensation.min_salary

        if job_max is None:
            return None

        floor = minimum_base_salary * self._policy.compensation_floor_ratio

        if job_max < floor:
            return (
                f"Salary range (up to {job_max:,.0f}) falls well below your "
                f"stated minimum ({minimum_base_salary:,.0f})."
            )

        return None

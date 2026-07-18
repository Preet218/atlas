"""
Candidate Builder.

Responsible for constructing a valid Candidate object from
structured input.
"""

from __future__ import annotations

from atlas.candidate.enums import (
    NoticePeriod,
    TravelPreference,
    VisaRequirement,
    WorkMode,
)
from atlas.candidate.models import (
    Candidate,
    CareerDNA,
    PersonalInfo,
    Preferences,
)


class CandidateBuilder:
    """
    Builder responsible for creating Candidate objects.
    """

    def build(self, data: dict) -> Candidate:
        """
        Build a Candidate from a structured dictionary.
        """

        personal = PersonalInfo(
            full_name=data["personal"]["full_name"],
            email=data["personal"].get("email"),
            phone=data["personal"].get("phone"),
            location=data["personal"]["location"],
            nationality=data["personal"]["nationality"],
            current_company=data["personal"]["current_company"],
            current_role=data["personal"]["current_role"],
            years_of_experience=data["personal"]["years_of_experience"],
            notice_period=NoticePeriod(
                data["personal"].get(
                    "notice_period",
                    NoticePeriod.NEGOTIABLE.value,
                )
            ),
            linkedin_url=data["personal"].get("linkedin_url"),
            github_url=data["personal"].get("github_url"),
            portfolio_url=data["personal"].get("portfolio_url"),
        )

        preferences = Preferences(
            preferred_roles=data["preferences"].get(
                "preferred_roles",
                [],
            ),
            preferred_countries=data["preferences"].get(
                "preferred_countries",
                [],
            ),
            preferred_work_modes=[
                WorkMode(mode)
                for mode in data["preferences"].get(
                    "preferred_work_modes",
                    [],
                )
            ],
            minimum_base_salary=data["preferences"].get("minimum_base_salary"),
            target_total_compensation=data["preferences"].get("target_total_compensation"),
            visa_requirement=VisaRequirement(
                data["preferences"].get(
                    "visa_requirement",
                    VisaRequirement.PREFERRED.value,
                )
            ),
            travel_preference=TravelPreference(
                data["preferences"].get(
                    "travel_preference",
                    TravelPreference.NONE.value,
                )
            ),
            excluded_companies=data["preferences"].get(
                "excluded_companies",
                [],
            ),
        )

        career_dna = CareerDNA(
            primary_domains=data.get("career_dna", {}).get(
                "primary_domains",
                [],
            ),
            secondary_domains=data.get("career_dna", {}).get(
                "secondary_domains",
                [],
            ),
            strengths=data.get("career_dna", {}).get(
                "strengths",
                [],
            ),
            target_domains=data.get("career_dna", {}).get(
                "target_domains",
                [],
            ),
        )

        return Candidate(
            personal=personal,
            education=[],
            experience=[],
            skills=[],
            awards=[],
            preferences=preferences,
            career_dna=career_dna,
        )

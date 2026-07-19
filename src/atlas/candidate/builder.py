"""
Candidate Builder.

Responsible for constructing a valid Candidate object from
structured input.
"""

from __future__ import annotations

from datetime import date

from atlas.candidate.enums import (
    EducationLevel,
    EmploymentType,
    NoticePeriod,
    ProficiencyLevel,
    SkillCategory,
    TravelPreference,
    VisaRequirement,
    WorkMode,
)
from atlas.candidate.models import (
    Award,
    Candidate,
    CareerDNA,
    Education,
    Experience,
    PersonalInfo,
    Preferences,
    Project,
    Skill,
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
            location=data["personal"].get("location"),
            nationality=data["personal"].get("nationality"),
            current_company=data["personal"].get("current_company"),
            current_role=data["personal"].get("current_role"),
            years_of_experience=data["personal"].get("years_of_experience") or 0.0,
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
            education=[
                self._build_education(item) for item in data.get("education", [])
            ],
            experience=[
                self._build_experience(item) for item in data.get("experience", [])
            ],
            skills=[self._build_skill(item) for item in data.get("skills", [])],
            awards=[self._build_award(item) for item in data.get("awards", [])],
            projects=[self._build_project(item) for item in data.get("projects", [])],
            preferences=preferences,
            career_dna=career_dna,
        )

    def _parse_date(self, value: str | None) -> date | None:
        """Parse an ISO-8601 date string, passing None through unchanged."""

        if value is None:
            return None

        return date.fromisoformat(value)

    def _build_education(self, item: dict) -> Education:
        return Education(
            degree=EducationLevel(item["degree"]),
            institution=item["institution"],
            specialization=item.get("specialization"),
            cgpa=item.get("cgpa"),
            start_date=self._parse_date(item.get("start_date")),
            end_date=self._parse_date(item.get("end_date")),
        )

    def _build_skill(self, item: dict) -> Skill:
        return Skill(
            name=item["name"],
            category=SkillCategory(item["category"]),
            proficiency=ProficiencyLevel(
                item.get("proficiency", ProficiencyLevel.INTERMEDIATE.value)
            ),
            years_of_experience=item.get("years_of_experience"),
        )

    def _build_award(self, item: dict) -> Award:
        return Award(
            title=item["title"],
            issuer=item["issuer"],
            award_date=self._parse_date(item.get("award_date")),
            description=item.get("description"),
        )

    def _build_project(self, item: dict) -> Project:
        return Project(
            name=item["name"],
            objective=item["objective"],
            description=item["description"],
            technologies=item.get("technologies", []),
            achievements=item.get("achievements", []),
            business_metrics=item.get("business_metrics", []),
        )

    def _build_experience(self, item: dict) -> Experience:
        return Experience(
            company=item["company"],
            title=item["title"],
            employment_type=EmploymentType(
                item.get("employment_type", EmploymentType.FULL_TIME.value)
            ),
            start_date=self._parse_date(item["start_date"]),
            end_date=self._parse_date(item.get("end_date")),
            current=item.get("current", False),
            location=item.get("location"),
            summary=item.get("summary"),
            projects=[
                self._build_project(project) for project in item.get("projects", [])
            ],
        )


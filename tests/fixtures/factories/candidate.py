"""Factory functions for creating Candidate test instances."""

from __future__ import annotations

from atlas.candidate.enums import (
    ProficiencyLevel,
    SkillCategory,
    VisaRequirement,
    WorkMode,
)
from atlas.candidate.models import (
    Candidate,
    CareerDNA,
    PersonalInfo,
    Preferences,
    Skill,
)


def create_candidate(**overrides) -> Candidate:
    """Create a Candidate with sensible defaults."""

    data = {
        "personal": PersonalInfo(
            full_name="Jamie Rivera",
            email="jamie.rivera@example.com",
            location="Bangalore",
            nationality="Indian",
            current_company="Acme Corp",
            current_role="Senior Data Scientist",
            years_of_experience=6,
        ),
        "education": [],
        "experience": [],
        "skills": [
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING,
                proficiency=ProficiencyLevel.EXPERT,
                years_of_experience=6,
            ),
            Skill(
                name="Machine Learning",
                category=SkillCategory.MACHINE_LEARNING,
                proficiency=ProficiencyLevel.ADVANCED,
                years_of_experience=5,
            ),
            Skill(
                name="LLMs",
                category=SkillCategory.GENERATIVE_AI,
                proficiency=ProficiencyLevel.ADVANCED,
                years_of_experience=2,
            ),
        ],
        "awards": [],
        "preferences": Preferences(
            preferred_roles=["Senior Data Scientist", "ML Engineer"],
            preferred_countries=["India"],
            preferred_work_modes=[WorkMode.HYBRID, WorkMode.REMOTE],
            minimum_base_salary=3_500_000,
            target_total_compensation=5_000_000,
            visa_requirement=VisaRequirement.NOT_REQUIRED,
            excluded_companies=[],
        ),
        "career_dna": CareerDNA(
            primary_domains=["Data Science", "Machine Learning"],
            secondary_domains=["MLOps"],
            strengths=["Model Development", "Experimentation"],
            target_domains=["Generative AI"],
        ),
    }

    data.update(overrides)
    return Candidate(**data)

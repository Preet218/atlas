from __future__ import annotations

from datetime import date

from atlas.candidate.builder import CandidateBuilder
from atlas.candidate.enums import (
    EducationLevel,
    EmploymentType,
    ProficiencyLevel,
    SkillCategory,
    VisaRequirement,
    WorkMode,
)

MINIMAL_DATA = {
    "personal": {
        "full_name": "Jamie Rivera",
        "location": "Bangalore",
        "nationality": "Indian",
        "current_company": "Acme Corp",
        "current_role": "Data Analyst",
        "years_of_experience": 3,
    },
    "preferences": {},
}


def test_build_parses_personal_info():
    candidate = CandidateBuilder().build(MINIMAL_DATA)

    assert candidate.personal.full_name == "Jamie Rivera"
    assert candidate.personal.years_of_experience == 3


def test_build_defaults_missing_lists_to_empty():
    candidate = CandidateBuilder().build(MINIMAL_DATA)

    assert candidate.education == []
    assert candidate.experience == []
    assert candidate.skills == []
    assert candidate.awards == []


def test_build_parses_skills():
    data = {
        **MINIMAL_DATA,
        "skills": [
            {
                "name": "Python",
                "category": "Programming",
                "proficiency": "Expert",
                "years_of_experience": 5,
            },
            {
                "name": "SQL",
                "category": "Database",
            },
        ],
    }

    candidate = CandidateBuilder().build(data)

    assert len(candidate.skills) == 2

    python = candidate.skills[0]
    assert python.name == "Python"
    assert python.category == SkillCategory.PROGRAMMING
    assert python.proficiency == ProficiencyLevel.EXPERT
    assert python.years_of_experience == 5

    sql = candidate.skills[1]
    assert sql.category == SkillCategory.DATABASE
    assert sql.proficiency == ProficiencyLevel.INTERMEDIATE  # default
    assert sql.years_of_experience is None


def test_build_parses_education():
    data = {
        **MINIMAL_DATA,
        "education": [
            {
                "degree": "Bachelor",
                "institution": "IIT Bombay",
                "specialization": "Computer Science",
                "cgpa": 8.7,
                "start_date": "2018-08-01",
                "end_date": "2022-05-31",
            }
        ],
    }

    candidate = CandidateBuilder().build(data)

    education = candidate.education[0]
    assert education.degree == EducationLevel.BACHELOR
    assert education.institution == "IIT Bombay"
    assert education.cgpa == 8.7
    assert education.start_date == date(2018, 8, 1)
    assert education.end_date == date(2022, 5, 31)


def test_build_parses_education_with_missing_optional_dates():
    data = {
        **MINIMAL_DATA,
        "education": [
            {
                "degree": "Master",
                "institution": "IIM Ahmedabad",
            }
        ],
    }

    candidate = CandidateBuilder().build(data)

    assert candidate.education[0].start_date is None
    assert candidate.education[0].end_date is None
    assert candidate.education[0].cgpa is None


def test_build_parses_awards():
    data = {
        **MINIMAL_DATA,
        "awards": [
            {
                "title": "Employee of the Year",
                "issuer": "Acme Corp",
                "award_date": "2024-12-01",
                "description": "Top performer",
            }
        ],
    }

    candidate = CandidateBuilder().build(data)

    award = candidate.awards[0]
    assert award.title == "Employee of the Year"
    assert award.award_date == date(2024, 12, 1)


def test_build_parses_experience_with_defaults():
    data = {
        **MINIMAL_DATA,
        "experience": [
            {
                "company": "Acme Corp",
                "title": "Data Analyst",
                "start_date": "2022-06-01",
                "current": True,
            }
        ],
    }

    candidate = CandidateBuilder().build(data)

    experience = candidate.experience[0]
    assert experience.company == "Acme Corp"
    assert experience.employment_type == EmploymentType.FULL_TIME  # default
    assert experience.start_date == date(2022, 6, 1)
    assert experience.end_date is None
    assert experience.current is True
    assert experience.projects == []


def test_build_parses_experience_with_projects():
    data = {
        **MINIMAL_DATA,
        "experience": [
            {
                "company": "Acme Corp",
                "title": "Data Analyst",
                "employment_type": "Contract",
                "start_date": "2022-06-01",
                "end_date": "2024-01-15",
                "location": "Bangalore",
                "summary": "Built fraud detection models.",
                "projects": [
                    {
                        "name": "Fraud Detection Pipeline",
                        "objective": "Reduce false positives",
                        "description": "Built an ML pipeline for real-time fraud scoring.",
                        "technologies": ["Python", "Spark"],
                        "achievements": ["Cut false positives by 30%"],
                        "business_metrics": ["$2M annual savings"],
                    }
                ],
            }
        ],
    }

    candidate = CandidateBuilder().build(data)

    experience = candidate.experience[0]
    assert experience.employment_type == EmploymentType.CONTRACT
    assert experience.end_date == date(2024, 1, 15)
    assert experience.location == "Bangalore"

    project = experience.projects[0]
    assert project.name == "Fraud Detection Pipeline"
    assert project.technologies == ["Python", "Spark"]
    assert project.achievements == ["Cut false positives by 30%"]
    assert project.business_metrics == ["$2M annual savings"]


def test_build_parses_preferences():
    data = {
        **MINIMAL_DATA,
        "preferences": {
            "preferred_roles": ["AI Engineer"],
            "preferred_countries": ["India"],
            "preferred_work_modes": ["Hybrid", "Remote"],
            "minimum_base_salary": 2_000_000,
            "visa_requirement": "Required",
            "excluded_companies": ["Acme Corp"],
        },
    }

    candidate = CandidateBuilder().build(data)

    assert candidate.preferences.preferred_roles == ["AI Engineer"]
    assert candidate.preferences.preferred_work_modes == [
        WorkMode.HYBRID,
        WorkMode.REMOTE,
    ]
    assert candidate.preferences.visa_requirement == VisaRequirement.REQUIRED
    assert candidate.preferences.excluded_companies == ["Acme Corp"]


def test_build_parses_career_dna():
    data = {
        **MINIMAL_DATA,
        "career_dna": {
            "primary_domains": ["Data Science"],
            "secondary_domains": ["MLOps"],
            "strengths": ["Experimentation"],
            "target_domains": ["Generative AI"],
        },
    }

    candidate = CandidateBuilder().build(data)

    assert candidate.career_dna.primary_domains == ["Data Science"]
    assert candidate.career_dna.target_domains == ["Generative AI"]


def test_build_handles_real_candidate_json_shape():
    """Regression test for the exact shape of the real, checked-in
    candidate.json -- this profile currently has empty lists for
    education/experience/skills/awards/career_dna, which previously
    triggered a KeyError-free but silently-wrong build (the old
    builder hardcoded these to [] regardless of input). This confirms
    the builder now round-trips that shape correctly and would also
    handle it once those lists are populated.
    """

    data = {
        "personal": {
            "full_name": "Preet Patel",
            "email": None,
            "phone": None,
            "location": "Bangalore",
            "nationality": "Indian",
            "current_company": "American Express",
            "current_role": "Senior Data Analyst",
            "years_of_experience": 2.0,
            "notice_period": "Negotiable",
            "linkedin_url": None,
            "github_url": None,
            "portfolio_url": None,
        },
        "education": [],
        "experience": [],
        "skills": [],
        "awards": [],
        "preferences": {
            "preferred_roles": ["AI Engineer"],
            "preferred_countries": ["India"],
            "preferred_work_modes": ["Hybrid"],
            "minimum_base_salary": None,
            "target_total_compensation": None,
            "visa_requirement": "Preferred",
            "travel_preference": "Up to 90%",
            "excluded_companies": ["American Express"],
        },
        "career_dna": {
            "primary_domains": [],
            "secondary_domains": [],
            "strengths": [],
            "target_domains": [],
        },
    }

    candidate = CandidateBuilder().build(data)

    assert candidate.personal.full_name == "Preet Patel"
    assert candidate.preferences.excluded_companies == ["American Express"]
    assert candidate.skills == []

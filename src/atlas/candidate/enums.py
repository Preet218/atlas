"""
Candidate domain enumerations.

These enums represent controlled vocabulary used throughout the
Canonical Candidate Profile (CCP). Keeping them centralized ensures
consistent values across resume generation, job matching, ranking,
and future persistence layers.
"""

from enum import Enum


class EmploymentType(str, Enum):
    """Employment types supported by Atlas."""

    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    INTERN = "Internship"
    FREELANCE = "Freelance"


class WorkMode(str, Enum):
    """Preferred work arrangement."""

    ONSITE = "On-site"
    HYBRID = "Hybrid"
    REMOTE = "Remote"


class NoticePeriod(str, Enum):
    """Standard notice periods."""

    IMMEDIATE = "Immediate"
    FIFTEEN_DAYS = "15 Days"
    ONE_MONTH = "1 Month"
    TWO_MONTHS = "2 Months"
    THREE_MONTHS = "3 Months"
    NEGOTIABLE = "Negotiable"


class VisaRequirement(str, Enum):
    """Work authorization preference."""

    REQUIRED = "Required"
    PREFERRED = "Preferred"
    NOT_REQUIRED = "Not Required"


class ProficiencyLevel(str, Enum):
    """Skill proficiency."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class SkillCategory(str, Enum):
    """High-level skill categories."""

    PROGRAMMING = "Programming"

    MACHINE_LEARNING = "Machine Learning"

    DATA_SCIENCE = "Data Science"

    GENERATIVE_AI = "Generative AI"

    NLP = "Natural Language Processing"

    MLOPS = "MLOps"

    CLOUD = "Cloud"

    DATABASE = "Database"

    VISUALIZATION = "Visualization"

    TOOLING = "Tooling"

    SOFT_SKILLS = "Soft Skills"

    OTHER = "Other"


class EducationLevel(str, Enum):
    """Education levels."""

    HIGH_SCHOOL = "High School"

    DIPLOMA = "Diploma"

    BACHELOR = "Bachelor"

    MASTER = "Master"

    PHD = "PhD"

    OTHER = "Other"


class TravelPreference(str, Enum):
    """Travel willingness."""

    NONE = "None"

    OCCASIONAL = "Up to 25%"

    MODERATE = "Up to 50%"

    FREQUENT = "Up to 75%"

    EXTENSIVE = "Up to 90%"


class ProfileStatus(str, Enum):
    """Candidate profile lifecycle."""

    DRAFT = "Draft"

    ACTIVE = "Active"

    ARCHIVED = "Archived"

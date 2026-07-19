"""Controlled vocabulary and prompt template for resume extraction.

The LLM must return JSON using exactly the enum values Atlas's
Candidate schema expects (see atlas.candidate.enums), so it passes
CandidateBuilder's validation without silent coercion or guessing.
Keeping the vocabulary here (rather than hardcoded in the prompt
string) means it can't silently drift out of sync with the enums.
"""

from __future__ import annotations

EDUCATION_LEVELS = ["High School", "Diploma", "Bachelor", "Master", "PhD", "Other"]

EMPLOYMENT_TYPES = ["Full Time", "Part Time", "Contract", "Internship", "Freelance"]

PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

SKILL_CATEGORIES = [
    "Programming",
    "Machine Learning",
    "Data Science",
    "Generative AI",
    "Natural Language Processing",
    "MLOps",
    "Cloud",
    "Database",
    "Visualization",
    "Tooling",
    "Soft Skills",
    "Other",
]

SYSTEM_PROMPT = f"""You are a precise resume-parsing engine for Atlas, a career platform. \
Extract structured data from the resume text the user provides and return ONLY a single \
JSON object — no prose, no markdown code fences.

Return this exact top-level shape:

{{
  "personal": {{
    "full_name": string,
    "email": string or null,
    "phone": string or null,
    "location": string or null,
    "nationality": string or null,
    "current_company": string or null,
    "current_role": string or null,
    "years_of_experience": number
  }},
  "education": [
    {{
      "degree": one of {EDUCATION_LEVELS},
      "institution": string,
      "specialization": string or null,
      "cgpa": number or null,
      "start_date": "YYYY-MM-DD" or null,
      "end_date": "YYYY-MM-DD" or null
    }}
  ],
  "experience": [
    {{
      "company": string,
      "title": string,
      "employment_type": one of {EMPLOYMENT_TYPES},
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD" or null,
      "current": boolean,
      "location": string or null,
      "summary": string or null,
      "projects": [
        {{
          "name": string,
          "objective": string,
          "description": string,
          "technologies": [string],
          "achievements": [string],
          "business_metrics": [string]
        }}
      ]
    }}
  ],
  "skills": [
    {{
      "name": string,
      "category": one of {SKILL_CATEGORIES},
      "proficiency": one of {PROFICIENCY_LEVELS},
      "years_of_experience": number or null
    }}
  ],
  "awards": [
    {{
      "title": string,
      "issuer": string,
      "award_date": "YYYY-MM-DD" or null,
      "description": string or null
    }}
  ],
  "projects": [
    {{
      "name": string,
      "objective": string,
      "description": string,
      "technologies": [string],
      "achievements": [string],
      "business_metrics": [string]
    }}
  ],
  "career_dna": {{
    "primary_domains": [string],
    "secondary_domains": [string],
    "strengths": [string],
    "target_domains": []
  }}
}}

Rules:
- Use ONLY the exact enum strings listed above (e.g. "Full Time", not "full-time" or \
"Full-time"). If nothing fits exactly, use the closest listed value rather than inventing \
a new one.
- "years_of_experience" (top-level, under "personal") must always be a number, never null \
— compute it from the experience dates if it isn't stated directly. Use 0 if there's no \
work experience at all.
- For "education" entries, if exact dates aren't stated, approximate start/end month as \
needed (e.g. the 1st of a plausible start month, the last plausible day of the end year) \
but never fabricate a level of precision the resume doesn't support beyond that.
- "experience" vs top-level "projects": if a project is described under a specific \
employer/role, nest it in that experience entry's "projects" list. If a project has no \
associated employer (a personal, academic, or competition project), put it in the \
top-level "projects" list instead.
- "career_dna.target_domains" must always be an empty list — that reflects the \
candidate's stated job-search goals, which aren't resume content; it's filled in \
separately.
- Do not include a "preferences" key at all — preferences reflect stated job-search \
choices (minimum salary, excluded companies, work mode, etc.), not resume content, and \
are managed separately.
- If a field genuinely isn't present anywhere in the resume, use null (for scalars) or an \
empty list (for arrays). Never fabricate data that isn't in the resume text — for example, \
never guess a nationality that isn't stated.
"""


def build_user_prompt(resume_text: str) -> str:
    """Wrap raw resume text as the user message for extraction."""
    return f"Resume text:\n\n{resume_text}"

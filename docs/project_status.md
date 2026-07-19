# Project Status

## Completed

- Candidate domain
- Resume domain
- Job domain
- Common package
- Discovery base
- Discovery service
- Greenhouse connector
- Greenhouse mapper
- Greenhouse tests
- Lever mapper (location, employment type, compensation)
- Lever connector
- Lever tests
- Ashby mapper (location, employment type, compensation)
- Ashby connector
- Ashby tests
- Fixed job.enums.JobPlatform missing ASHBY/WORKDAY members
- Ranking Engine (JobRanker domain service, RankingPolicy, RankingService)
- Ranking tests
- Fixed deprecated datetime.utcnow() in candidate.Metadata
- Matching Engine (JobMatcher hard eligibility gate, JobDeduplicator, MatchingPolicy, MatchingService)
- Matching tests
- Added JobPosting.visa_sponsorship field (unpopulated by connectors so far)
- Refactored: excluded-company disqualification moved from JobRanker into JobMatcher (single source of truth for hard eligibility). RankingService no longer filters; intended pipeline is discover -> MatchingService.filter_eligible -> RankingService.rank
- Application Engine (application tracking, status lifecycle, recruiter contacts, follow-up reminders)
- Application tests
- Fixed CandidateBuilder: was silently hardcoding education/experience/skills/awards to [] regardless of input (dead code today — CandidateService/CandidateStorage load candidate.json directly via pydantic, bypassing the builder — but a real latent bug for whenever resume-parsing starts feeding it)
- CandidateBuilder tests (previously an empty placeholder file)
- FindOpportunitiesWorkflow: orchestrates Discovery -> Matching -> Ranking end to end (atlas.workflows), matching the "Find Opportunities" workflow named in architecture.md. Wired into Atlas app.
- Workflow tests
- Added docs/user_guide.md
- Fixed stale Makefile `run` target (pointed at a nonexistent apps.api.main:app)
- Populated the real candidate.json from the user's actual resume (education, experience w/ nested projects, skills, awards, standalone projects, career_dna)
- Added Candidate.projects (top-level, for personal/academic projects not tied to an employer) - previously Project only existed nested under Experience
- Loosened PersonalInfo.nationality/current_company/current_role/location from required to optional - resumes frequently omit these (confirmed: this exact resume states none of them), and nothing downstream requires them. years_of_experience defensively defaults to 0.0 in CandidateBuilder if missing.
- Resume ingestion pipeline (atlas.resume + atlas.llm): PDF/DOCX/text extraction, LLM-based structured extraction into a CandidateBuilder-compatible dict (controlled vocabulary matches candidate enums exactly), ResumeService.ingest() that preserves existing preferences across re-uploads. Wired into Atlas app as atlas.resume / atlas.candidate.
- Added pypdf, python-docx, openai dependencies (pyproject.toml) - needs `uv sync`
- Added openai_model setting + OPENAI_MODEL env var
- Resume/LLM tests (all mock the LLM and PDF/DOCX libraries - no real network calls)

IMPORTANT CAVEAT: the LLM-based resume parsing pipeline (atlas.llm.LLMClient,
atlas.resume.parser/service) has NOT been executed against a live OpenAI API
or with the real pypdf/python-docx packages in this environment (no network
access to install/call them). The orchestration logic is unit-tested with
everything mocked, and the OpenAI SDK usage follows their documented stable
pattern, but this needs a real smoke test (upload a real resume with a real
API key) before being trusted.

## Upcoming

Workday

LinkedIn

Resume/cover-letter generation (tailoring content for a specific job - distinct from parsing, which is now built)

Currency-aware compensation comparisons in Ranking/Matching

A dedicated Resume domain model/mapper (tests/unit/resume/test_models.py and
test_mapper.py exist as empty placeholders from the original scaffold; this
round's implementation reused atlas.candidate.builder.CandidateBuilder
directly instead of building a separate resume-specific model/mapper layer)
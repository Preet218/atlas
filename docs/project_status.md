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

## Upcoming

Workday

LinkedIn

Resume/cover-letter generation (blocked on atlas.llm)

Currency-aware compensation comparisons in Ranking/Matching
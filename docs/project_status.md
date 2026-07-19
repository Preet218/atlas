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

Note: Application Engine scope is deliberately narrower than spec 5.3
"Application Intelligence" — resume selection/optimization and cover
letter generation are out of scope for now since they depend on LLM
and Resume-domain integration that doesn't exist yet (atlas.llm is
still an empty scaffold). What's built covers "Applications Domain
owns application history" from architecture.md: tracking, status
transitions, recruiter contacts, follow-up reminders.

## Upcoming

Workday

LinkedIn

Resume/cover-letter generation (blocked on atlas.llm)
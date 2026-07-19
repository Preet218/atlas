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

## Upcoming

Workday

LinkedIn

Application Engine
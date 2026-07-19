# Atlas User Guide

## What is Atlas?

Atlas is an AI-powered Career Operating System. Instead of you manually
browsing job boards and applying one by one, Atlas discovers openings
directly from companies' own applicant-tracking systems, filters out
anything you're not actually eligible for or wouldn't want, scores and
ranks what's left against your real profile, and tracks every
application through to an offer.

The goal isn't "apply to more jobs." It's **apply to the right jobs,
faster** — which is what actually moves the needle on getting
interviews.

This guide covers what's built today, how the pieces fit together, and
how to actually run it.

---

## The mental model

```
Candidate Profile  →  Discovery  →  Matching  →  Ranking  →  Applications
   (your data)      (find jobs)   (filter out    (score &     (track through
                                    bad fits)      order)       to offer)
```

- **Candidate Profile** — your skills, experience, and preferences, in
  one structured place. Everything downstream reads from this.
- **Discovery** — pulls live job postings directly from company
  career pages, via their own public APIs (Greenhouse, Lever, Ashby
  today).
- **Matching** — a hard yes/no filter. Excluded companies, roles you
  can't legally take without sponsorship, locations you can't work
  from, and pay that's drastically below your floor all get removed
  here. It also merges duplicate postings when a company cross-posts
  the same role to multiple platforms.
- **Ranking** — everything that survives Matching gets a 0-100 fit
  score across six dimensions (skills, role, location, compensation,
  experience level, and posting recency), with a plain-English reason
  for each. Best matches first.
- **Applications** — once you apply, Atlas tracks the application
  through its lifecycle (applied → under review → interviewing →
  offer, etc.), logs recruiter contacts, and reminds you about
  follow-ups.

Everything is explainable by design: nothing is filtered or ranked as
a black box. Every decision Atlas makes comes with a reason you can
read.

---

## What's built vs. what isn't (today)

**Built and tested:**
- Candidate profile (`atlas.candidate`)
- Resume ingestion — upload a PDF/DOCX/text resume and have it parsed
  into your profile automatically (`atlas.resume`, `atlas.llm`)
- Job discovery for **Greenhouse, Lever, and Ashby** (`atlas.discovery`)
- Matching / deduplication (`atlas.matching`)
- Ranking (`atlas.ranking`)
- Application tracking (`atlas.application`)
- The `FindOpportunitiesWorkflow` that strings Discovery → Matching →
  Ranking together in one call (`atlas.workflows`)

**Not built yet:**
- Workday and LinkedIn discovery connectors
- Resume tailoring and cover letter *generation* (resume *parsing* is
  built; generating/optimizing a resume or writing a cover letter for
  a specific job is not)
- A CLI or web UI — today, Atlas is used as a Python library. There's
  a FastAPI app (`atlas.api`) but it currently only exposes health
  checks, not the workflows described here
- Interview preparation

If something below isn't working the way you expect, check this list
first — it may genuinely not be built yet, not a bug.

---

## Getting set up

1. Install dependencies:
   ```
   uv sync
   ```
2. Copy `.env.example` to `.env` and fill in `DATABASE_URL` (Postgres,
   via `docker compose up -d` — see `APPLY.md`). Also fill in
   `OPENAI_API_KEY` if you want to use resume upload (Step 1 below) —
   it's not needed for anything else yet.
3. Fill in your candidate profile — see the next section. This is the
   single most important step: every engine below is only as good as
   the data in this file.

---

## Step 1: Build your candidate profile

You have two ways to get your profile populated. Either works — use
whichever fits.

### Option A: Upload your resume (recommended)

```python
from pathlib import Path
from atlas.app import Atlas

atlas = Atlas()
candidate = atlas.resume.ingest(Path("~/Downloads/My_Resume.pdf").expanduser())
```

This extracts the text from your PDF/DOCX/text resume, sends it to an
LLM to pull out structured education, experience, skills, awards, and
projects, and saves it as your profile. Re-uploading a newer resume
later re-runs the same pipeline and **replaces** the resume-derived
fields — but your `preferences` (excluded companies, minimum salary,
preferred work modes, etc.) are always carried over automatically,
since a resume never states those.

This needs a real `OPENAI_API_KEY` in your `.env` — see Getting Set
Up above. Supported formats: `.pdf`, `.docx`, `.txt`, `.md`. Scanned/
image-only PDFs aren't supported (there's no OCR step).

Because LLM extraction can occasionally miss or misjudge something,
**check the result** — `atlas.candidate.show_profile()` prints a quick
summary, or just inspect `src/atlas/candidate/data/candidate.json`
directly.

### Option B: Edit the JSON directly

Your profile lives at `src/atlas/candidate/data/candidate.json` and
follows the `Candidate` model (`atlas.candidate.models`). At minimum,
fill in:

- `personal` — name, location, current role, years of experience
- `skills` — this drives 35% of your ranking score, the single
  largest factor. An empty skills list means every job gets a neutral
  skills score regardless of fit, which makes ranking far less useful.
- `preferences` — preferred roles, countries, work modes, minimum
  base salary, and `excluded_companies` (e.g. your current employer,
  if you don't want it discovered).
- `career_dna` — your primary/secondary domains, used as a fallback
  signal when a job title doesn't exactly match a preferred role.

Load it with:

```python
from pathlib import Path
from atlas.candidate.service import CandidateService

candidate_service = CandidateService(
    storage_path=Path("src/atlas/candidate/data/candidate.json")
)
candidate = candidate_service.load_profile()
```

If you're populating the profile from some other structured source
rather than editing the JSON directly, use
`atlas.candidate.builder.CandidateBuilder().build(data)` — it accepts
a plain dict shaped like the profile (personal / education /
experience / skills / awards / projects / preferences / career_dna)
and validates it into a `Candidate`. This is exactly what
`atlas.resume.ResumeService` uses internally after the LLM extraction
step.

---

## Step 2: Find opportunities

Discovery works against a company's own board, not a search query — you
tell it *which* companies to check, and it pulls every current opening
from that company's board.

```python
import asyncio
from atlas.app import Atlas
from atlas.common.enums import JobPlatform
from atlas.discovery.models import DiscoveryTarget

atlas = Atlas()
candidate = atlas.candidate.load_profile()

targets = [
    DiscoveryTarget(platform=JobPlatform.ASHBY, identifier="openai"),
    DiscoveryTarget(platform=JobPlatform.LEVER, identifier="dnb"),
    DiscoveryTarget(platform=JobPlatform.GREENHOUSE, identifier="stripe"),
]

results = asyncio.run(atlas.find_opportunities.run(candidate, targets))

for ranked in results[:10]:
    print(f"{ranked.overall_score:5.1f}  {ranked.match_strength.value:7s}  "
          f"{ranked.job.title} @ {ranked.job.company.name}")
    for reason in ranked.reasons:
        print(f"       - {reason}")
```

`identifier` is the company's board slug on that platform, not a
free-text company name — it's the last segment of the company's job
board URL:

| Platform   | Where to find the identifier                          | Example |
|------------|---------------------------------------------------------|---------|
| Greenhouse | `job-boards.greenhouse.io/{identifier}`                 | `stripe` |
| Lever      | `jobs.lever.co/{identifier}`                             | `dnb` |
| Ashby      | `jobs.ashbyhq.com/{identifier}`                           | `openai` |

`results` is a list of `RankedJob`, best match first. Each one carries:
- `overall_score` (0-100) and `match_strength` (strong/good/fair/weak)
- `reasons` — a short, human-readable explanation of the score
- `dimension_scores` — the full breakdown (skills, role, location,
  compensation, experience, recency), if you want to see exactly why

Jobs that fail hard eligibility (excluded company, no visa sponsorship
when you require it, wrong location and not remote, pay far below your
floor) or that duplicate another posting already in the list are
filtered out before ranking — you'll never see them in `results`.

### Tuning how ranking and matching behave

Both use a configurable policy object if the defaults don't fit:

```python
from atlas.ranking.policy import RankingPolicy
from atlas.ranking.ranker import JobRanker
from atlas.ranking.service import RankingService

# Weight compensation more heavily than the default
policy = RankingPolicy(
    skills_weight=0.25,
    role_weight=0.10,
    location_weight=0.10,
    compensation_weight=0.35,
    experience_weight=0.10,
    recency_weight=0.10,
)
ranking = RankingService(ranker=JobRanker(policy=policy))
```

The `MatchingPolicy` similarly lets you adjust how lenient the
compensation floor is, or how aggressively duplicate postings get
merged — see `atlas.matching.policy`.

---

## Step 3: Apply and track it

Once you've decided to apply to one of the ranked jobs:

```python
from atlas.application.enums import ApplicationStatus
from datetime import date

application = atlas.applications.create(
    ranked.job,
    resume_reference="resumes/senior-ds-v3.pdf",  # your own file reference
)

# When you actually submit the application:
application = atlas.applications.update_status(
    application, ApplicationStatus.APPLIED, note="Applied via referral"
)

# Schedule a reminder to follow up if you haven't heard back:
application = atlas.applications.schedule_follow_up(
    application, due_date=date(2026, 7, 26), reason="Check in if no response"
)
```

Check what needs following up on:

```python
for app in atlas.applications.list():
    due = atlas.applications.due_follow_ups(app)
    if due:
        print(f"{app.job.title} @ {app.job.company.name}: {len(due)} follow-up(s) due")
```

Status can only move along legal transitions (e.g. you can't jump
straight from `DRAFT` to `OFFER`) — see `atlas.application.transitions`
for the full graph. This exists to keep your application history
honest and traceable, not to get in your way; every real progression
(applied → review → interviewing → offer/rejected, or withdrawn at any
point) is allowed.

---

## Known limitations worth knowing about

- **Compensation comparisons don't convert currencies.** If your
  minimum salary is in INR and a job posts its range in USD, Ranking
  and Matching compare the raw numbers, which isn't meaningful. This
  matters most once non-Workday/LinkedIn connectors expand your search
  outside India.
- **Only Greenhouse, Lever, and Ashby are supported today.** A lot of
  companies use Workday or hire primarily through LinkedIn — those
  openings simply won't show up yet.
- **Visa sponsorship data is essentially always unknown.** None of the
  three connectors' public APIs expose whether a role sponsors visas,
  so `JobPosting.visa_sponsorship` is `None` for virtually every
  discovered job today. Matching only hard-excludes a job on visa
  grounds when it's explicitly `False`, so this mostly means the visa
  check is a no-op in practice right now.
- **No resume tailoring or cover letter generation yet.** Resume
  *parsing* (file → profile) is built; you still bring your own
  resume/cover letter when applying. Atlas tracks which one you used
  per application (`resume_reference`, `cover_letter`) but doesn't
  generate or optimize them.
- **Resume parsing hasn't been run against a live API in this
  environment.** The extraction pipeline (`atlas.resume`,
  `atlas.llm`) was built and unit-tested with the LLM call mocked out
  — it's never actually been executed against OpenAI's API. Treat the
  first real upload as a test: check the resulting profile before
  trusting it, especially dates, categorization of skills, and which
  projects got attached to which employer.
- **No OCR.** Scanned/image-only PDFs won't extract any text and will
  fail with a clear error rather than silently producing an empty
  profile.

---

## Where to go for more detail

- `docs/specification.md` — the full product spec (what Atlas is
  trying to become, stage by stage)
- `docs/architecture.md` — how the codebase is structured and why
- `docs/contributing.md` — coding standards if you're extending Atlas
- `docs/project_status.md` — what's done, in progress, and next

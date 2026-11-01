# DSA implementation and verification

## Additive scope

The sixth DSA track is integrated into the existing Academy dashboard, curricula, Study Room, resources and Interview Preparation. No separate app, sidebar or theme was created. Canonical root research was compared with published research commit `e856dc4` and is unchanged.

Course: 15 modules; 30 original exercises and 75 fixtures; 15 mock definitions; 14/30/60-day plans with 104 total scheduled lessons; 13 new resource selections and two reused senior resources; 38 employer preparation profiles. Research artifacts, limitations and dictionary are under `research\dsa`.

Eight profiles have selected official guidance, two limited anecdotes and 28 unknown processes. Official general guidance does not establish specific coding formats or topic frequency. Source evidence includes 65 public URLs, 60 HTTP 200 observations, and no-key oEmbed titles/publisher for three individual videos. No full-playback, vacancy or Kenyan eligibility claim is made.

## Implemented workflows

- Existing sixth-track selection and 14/30/60-day lessons with examples, videos, reading, fixtures, questions and complexity.
- Dedicated plans or 30/45-minute companion practice reserved inside another track's existing budget.
- Pattern/random/timed/company/mock/blind sessions; 20/30/45/60/90-minute deadlines.
- Explicit draft saving and persistent ordered submissions; saved code, explanations, ratings and checks are inspectable.
- Browser-only JavaScript worker: three-second termination, five-second fallback, opaque-origin iframe, network-none CSP and bounded data.
- Sample comparison plus ten clearly labeled self-rubric dimensions; optional consent-based existing AI feedback.
- Assistance/failed-answer spaced reviews, manual needs-revision marking, topic/difficulty outcomes and recommended question/30-day lesson.
- Mastery requires independent successes on three separate UTC dates. Late/assisted work cannot become independent timed success.
- Sourced company profiles, editable existing Career Intelligence watchlist and prerequisite-safe company plan priorities.

## Persistence and migrations

Alembic `0002` expands the existing personal-record kind check to coding sessions; it does not reset tables or personal progress. Sessions reuse typed personal envelopes. Startup adds only missing DSA documents without replacing user-edited research.

Import/restore validates timestamps, strict assistance/check flags, submission order and recomputed sample results. Legacy `0001` snapshots are fully validated before their candidate database is migrated to `0002`. Current and legacy restore, restart persistence and retention of edited research/private notes have automated tests.

Before updating the running local application, private SQLite/JSON recovery copies were created under ignored `backups`. They are not published.

## Verification

| Suite | Total | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Backend/API/database/research | 45 | 45 | 0 | 0 |
| Frontend/data/proxy/authored references | 42 | 42 | 0 | 0 |
| Real Chromium acceptance | 3 | 3 | 0 | 0 |
| **Application tests** | **90** | **90** | **0** | **0** |

Local verification completed November 1, 2026. All 30 original reference implementations passed their 75 fixtures. TypeScript, ESLint, Ruff, Prettier and the optimized build passed. `pip_audit` found no known dependency vulnerabilities (the local editable application is not a PyPI advisory entry); production npm audit found zero. The full development tree retains 16 moderate upstream advisories.

The running local application was restarted, health/frontend HTTP 200 verified, all six tracks observed, database revision `0002` confirmed, and every pre-existing personal row compared exactly against the pre-upgrade export. No existing rows changed. Hosted CI for this extension is pending publication; the historical five-track CI result is not substituted for a new run.

TypeScript, ESLint and production build have passed during integration. Initial failures were corrected rather than skipped: misnested sandbox header configuration, a test fixture's duplicated SQLite URL, ambiguous test selectors, asynchronous draft reset during a new-session request, and incorrect test assumptions about the existing nested plan contract.

The browser acceptance suite covers DSA lesson/video/exercise rendering, blind draft/reload/deadline persistence, actual JavaScript execution, saved ratings, company study-plan creation, network restrictions, timeout/cleanup, and the original learning/career/recovery/mobile/Host-boundary workflows. The network probe has a controlled CORS-allowed response so an ordinary cross-origin failure is not treated as successful isolation. An initial standalone-startup timeout during concurrent local verification was followed by a successful complete sequential run, without skipping cases or relaxing timeouts.

## Limits and costs

This is not an exhaustive algorithm judge, live interviewer or validated hiring-readiness predictor. Sample outputs do not prove pointer mutation, nonmutation, asymptotic performance or concurrency bounds. The browser has no hard heap quota. Other languages need local testing; blind mode is study UX, not secure proctoring.

Advanced topics have extension labs but not a complete worked bank exercise for every subtopic. Exact video durations/publication/comments, most employer processes and all learner-specific country eligibility remain unknown. Neither a calendar nor solution viewing guarantees mastery.

No new dependencies or paid services are required. Optional configured AI calls can incur provider charges and send explicitly consented code/answers externally; no live paid-provider request was made. YouTube metadata can use an optional backend key, but stored links and course practice work without one. Docker execution and live paid-provider verification remain untested.

## Open locally

Startup is unchanged. In two PowerShell terminals from the repository:

```powershell
Set-Location C:\Users\joanmoturi\engineering-academy
.\scripts\Start-Backend.ps1
```

```powershell
Set-Location C:\Users\joanmoturi\engineering-academy
.\scripts\Start-Frontend.ps1
```

Open `http://127.0.0.1:3000`, select DSA in Learning Tracks and use Interview Preparation's expandable DSA workspace. After an update, back up, stop both servers, run `git pull --ff-only` and `.\scripts\Setup.ps1`, then restart. See `RUN_INSTRUCTIONS.md`.

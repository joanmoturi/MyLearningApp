# Test results

## Sixth-track release verification - November 1, 2026

| Suite/check | Total | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Backend/API/database/research | 45 | 45 | 0 | 0 |
| Frontend/data/proxy/reference solutions | 42 | 42 | 0 | 0 |
| Playwright Chromium acceptance | 3 | 3 | 0 | 0 |
| **Application tests** | **90** | **90** | **0** | **0** |

Includes the unchanged original regression cases, all 30 authored JavaScript reference implementations/75 fixtures, DSA schema/reference validation, three curricula, reserved budgets, blind drafts/deadlines, assistance/late honesty, three-date mastery, manual revision, hostile coding imports, legacy migration/restore and exact existing-data preservation.

Actual Chromium execution passed: lesson/video-link rendering, saved drafts after reload, sample execution and submission, saved-answer inspection, company plan/practice, network denial with a controlled CORS-allowed probe, infinite-loop termination/iframe cleanup and original learning/career/backup/mobile/Host workflows. Latest complete browser run: 24.0 seconds, a single Windows observation.

Type/lint/format/build checks and production dependency scans passed. No cases were skipped. A concurrent local startup timed out once; the complete sequential browser run subsequently passed without changing test timeouts. Historical release results below remain historical; hosted evidence for the sixth-track runtime will be recorded after its run completes.

## Original five-track release - October 31, 2026

| Suite/check | Total | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Pytest application tests | 35 | 35 | 0 | 0 |
| Vitest component/data/proxy tests | 11 | 11 | 0 | 0 |
| Playwright Chromium acceptance | 2 | 2 | 0 | 0 |
| **Application tests** | **48** | **48** | **0** | **0** |

Latest complete backend run: 38.87 seconds. Latest browser run: 14.1 seconds. These are single native Windows observations, not portable performance benchmarks.

Published runtime commit `a2ab3639aa3cc3b8847ecef6aac32ea36231e1e0` passed GitHub Academy CI run `41233814617` on October 31, 2026. The Ubuntu job passed dependency installation, all three test suites, lint/type/format/build checks, Python dependency scanning and the production npm audit. This is executed hosted evidence, not merely a supplied workflow. The preceding release `1c15938` also passed run `41231443196`.

Ruff lint/format, TypeScript checking, ESLint, Prettier and optimized Next.js build passed. One non-failing Starlette warning recommends migrating TestClient's HTTP client dependency; it was not suppressed.

## Coverage

Backend tests cover startup/migrations, all fifteen track/duration combinations at bounded budgets, progress/evidence, preservation of later-started and annotated lessons, track switching, manual moves/custom lessons, notes, employers/jobs, skill extraction/gaps, competencies, projects, interview revision, optional no-key behavior, import/reference validation, stale previews, SQLite snapshots/restores and a new application instance using persisted data.

Provider tests mock status errors (401/403/429/500), timeout, official playlist metadata and persistent stale-cache access after quota failure. They do not use live credentials or incur provider charges.

Component/data tests cover evidence forms, multi-track selection, safe Markdown/links, understandable errors and aggregation of 401 questions across two catalogue pages. Proxy tests cover hostile Host without Origin, hostile Origin, traversal rejection and restore confirmation.

Chromium acceptance executes fresh startup, cloud plan creation, explicit lesson completion, notes, interview answer, employer/manual JD and gaps, project/task persistence across browser reload, snapshot restore and mobile layout. A separate HTTP request verifies hostile-host rejection against the running proxy.

## Earlier failures fixed

Windows snapshot handles remained open; SQLite snapshot size exceeded the original limit; plan custom routes were shadowed; recalculation misplaced retained work; the proxy dropped restore confirmation; frontend type/lint errors and asynchronous task controls failed; one pytest fixture import was removed by Ruff. The final pagination change initially misplaced a helper and a test inside existing functions; both were corrected before the successful complete rerun. Fixes were followed by successful reruns, not skipped tests.

## Not executed

Docker startup/volume restart, actual laptop reboot, live YouTube/OpenAI requests and every original video playback were not tested. Stored link rendering/security and provider fallbacks were tested. Fresh-install and GitHub-hosted CI results are recorded separately; do not infer them from this table.

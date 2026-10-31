# Test results - 2026-10-31

| Suite/check | Total | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Pytest application tests | 35 | 35 | 0 | 0 |
| Vitest component/data/proxy tests | 10 | 10 | 0 | 0 |
| Playwright Chromium acceptance | 2 | 2 | 0 | 0 |
| **Application tests** | **47** | **47** | **0** | **0** |

Latest complete backend run: 33.31 seconds. Latest browser run: 16.2 seconds. These are single native Windows observations, not portable performance benchmarks.

Ruff lint/format, TypeScript checking, ESLint, Prettier and optimized Next.js build passed. One non-failing Starlette warning recommends migrating TestClient's HTTP client dependency; it was not suppressed.

## Coverage

Backend tests cover startup/migrations, all fifteen track/duration combinations at bounded budgets, progress/evidence, preservation of later-started and annotated lessons, track switching, manual moves/custom lessons, notes, employers/jobs, skill extraction/gaps, competencies, projects, interview revision, optional no-key behavior, import/reference validation, stale previews, SQLite snapshots/restores and a new application instance using persisted data.

Provider tests mock status errors (401/403/429/500), timeout, official playlist metadata and persistent stale-cache access after quota failure. They do not use live credentials or incur provider charges.

Component tests cover evidence forms, multi-track selection, safe Markdown/links and understandable errors. Proxy tests cover hostile Host without Origin, hostile Origin, traversal rejection and restore confirmation.

Chromium acceptance executes fresh startup, cloud plan creation, explicit lesson completion, notes, interview answer, employer/manual JD and gaps, project/task persistence across browser reload, snapshot restore and mobile layout. A separate HTTP request verifies hostile-host rejection against the running proxy.

## Earlier failures fixed

Windows snapshot handles remained open; SQLite snapshot size exceeded the original limit; plan custom routes were shadowed; recalculation misplaced retained work; the proxy dropped restore confirmation; frontend type/lint errors and asynchronous task controls failed; one pytest fixture import was removed by Ruff. Fixes were followed by successful reruns, not skipped tests.

## Not executed

Docker startup/volume restart, actual laptop reboot, live YouTube/OpenAI requests and every original video playback were not tested. Stored link rendering/security and provider fallbacks were tested. Fresh-install and GitHub-hosted CI results are recorded separately; do not infer them from this table.

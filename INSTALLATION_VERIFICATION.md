# Installation verification

**Native clean-clone installation succeeded on October 31, 2026.**

Method: a separate `git clone --no-local` of the committed repository into a clean session directory, a new Python virtual environment, `npm ci`, `.env.example` copied without credentials and the documented `Setup.ps1`. No original database or virtual environment is copied.

The initial clean installation used commit `8d6458e`. The same separate checkout was then updated to published `1c15938`, and the documented Setup script and browser acceptance passed. Finally, published runtime `a2ab3639aa3cc3b8847ecef6aac32ea36231e1e0` was pulled into that checkout; its production build and both browser acceptance tests passed (17.0 seconds). This last step verifies updating the independently installed checkout, not another newly created operating-system environment. Dependency installation and production build succeeded using only the README/Setup script.

Verified HTTP 200 frontend, healthy backend, five tracks, a new 14-day cloud plan, explicitly completed lesson evidence, saved notes, timestamped Backup.ps1 snapshot and Restore.ps1 recovery. Both actual server processes were terminated by their identified PIDs and restarted as new processes; completed progress and notes remained. A later synthetic note disappeared after restoring the earlier snapshot, and a pre-restore recovery copy existed.

Both integration configuration flags were false. No original database, virtual environment, optional key or undocumented application setting was copied.

Single warm HTTP observations through the frontend proxy: health 23 ms, bootstrap 155 ms, dashboard 101 ms, paginated question bank 32 ms, plans 44 ms. N=1 per endpoint, five observations total; these are not percentile statistics or cold-start benchmarks.

Scope: native Windows, Python 3.14.7, Node 26.13.0/npm 11.20.0, existing installed toolchains with a new clone/venv/node_modules. This is not a clean operating-system image. Docker is unavailable, so no container installation, Docker restart or laptop reboot success is claimed.

Independent hosted evidence: GitHub Academy CI run `41233814617` checked out published `a2ab363` on Ubuntu, installed dependencies and passed backend/frontend checks, dependency scans and both browser acceptance tests. It does not validate Docker Compose or the Windows scripts.

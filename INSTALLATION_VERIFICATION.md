# Installation verification

**Native clean-clone installation succeeded on October 31, 2026.**

Method: a separate `git clone --no-local` of the committed repository into a clean session directory, a new Python virtual environment, `npm ci`, `.env.example` copied without credentials and the documented `Setup.ps1`. No original database or virtual environment is copied.

The tested runtime code was commit `8d6458e`, followed by additional canonical snapshot-constraint regression hardening. Dependency installation and production build succeeded from the clean checkout using only the README/Setup script.

Verified HTTP 200 frontend, healthy backend, five tracks, a new 14-day cloud plan, explicitly completed lesson evidence, saved notes, timestamped Backup.ps1 snapshot and Restore.ps1 recovery. Both actual server processes were terminated by their identified PIDs and restarted as new processes; completed progress and notes remained. A later synthetic note disappeared after restoring the earlier snapshot, and a pre-restore recovery copy existed.

Both integration configuration flags were false. No original database, virtual environment, optional key or undocumented application setting was copied.

Single warm HTTP observations through the frontend proxy: health 23 ms, bootstrap 155 ms, dashboard 101 ms, paginated question bank 32 ms, plans 44 ms. N=1 per endpoint, five observations total; these are not percentile statistics or cold-start benchmarks.

Scope: native Windows, Python 3.14.7, Node 26.13.0/npm 11.20.0, existing installed toolchains with a new clone/venv/node_modules. This is not a clean operating-system image. Docker is unavailable, so no container installation, Docker restart or laptop reboot success is claimed.

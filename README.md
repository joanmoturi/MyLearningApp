# Engineering Academy

A local-first engineering learning and career workspace for experienced engineers. It combines five independent learning tracks, research-backed curricula, daily study guides, practical projects, interviews, employer/job research, notes and evidence-based competency assessments.

**No API key, cloud subscription or paid service is required for core features.** Videos and documentation open at their original publishers. The included research has explicit limitations; resource scores are not verified hiring predictions.

## Features

- Senior software, cloud, DevOps/platform, AI and agent/MCP tracks.
- Independent 14/30/60-day plans with 180-240 minutes daily, prerequisite ordering, manual adjustments and retained learning evidence.
- Separate video, reading, practical and knowledge-check completion.
- Searchable resources; bookmarks, personal ratings and verification flags.
- 325 questions, detailed answer rubrics, mock scenarios and spaced review.
- Editable employer watchlists, manual job descriptions, reviewable keyword extraction, skill gaps and job-linked plans.
- Multi-track portfolio projects, tasks and Markdown notes.
- Validated research imports, JSON exports, private SQLite snapshots and confirmed restore.
- Dark/light themes and mobile navigation.

## Architecture and prerequisites

Next.js / React / strict TypeScript frontend; FastAPI / Pydantic / SQLAlchemy backend; SQLite with Alembic migrations. The browser uses a same-origin proxy. Plain CSS is the maintainable styling system. See [ARCHITECTURE.md](ARCHITECTURE.md).

The verified native toolchain is **Python 3.14 and Node.js 26/npm 11**, plus Git. Install these from their official distributions; confirm:

```powershell
python --version
node --version
npm --version
git --version
```

Use PowerShell on Windows. No Docker installation is needed for native use. Other supported Python/Node versions must be tested rather than assumed.

## Fresh installation: Windows

```powershell
git clone https://github.com/joanmoturi/MyLearningApp.git engineering-academy
Set-Location engineering-academy
Copy-Item .env.example .env
.\scripts\Setup.ps1
```

The repository is currently private, so cloning requires the owner's GitHub access. Do not make it public without reviewing the research profile and licensing decision.

Start **two separate terminals** in the repository:

```powershell
# Terminal 1
.\scripts\Start-Backend.ps1
```

```powershell
# Terminal 2
.\scripts\Start-Frontend.ps1
```

Open **http://127.0.0.1:3000**. Verify:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

The first backend startup runs migrations, imports validated research, initializes a local learner and creates a software 30-day plan. No lesson is marked complete. Later startups preserve the database.

If PowerShell policy prevents running scripts, use these equivalent commands without changing your security policy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e backend
Set-Location frontend
npm ci --no-fund --no-audit
npm run build
Set-Location ..
# Terminal 1:
.\.venv\Scripts\python.exe -m uvicorn academy.main:app --host 127.0.0.1 --port 8000 --workers 1
# Terminal 2, from the repository:
Set-Location frontend
npm run start
```

Use the default .env values for those manual startup commands. With a customized origin, export `APP_ORIGIN` and `BACKEND_URL` into the frontend terminal too. Do not enter API keys into the frontend.

## Native Linux alternative

```bash
git clone https://github.com/joanmoturi/MyLearningApp.git engineering-academy
cd engineering-academy
cp .env.example .env
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.lock
.venv/bin/python -m pip install --no-deps -e backend
cd frontend && npm ci --no-fund --no-audit && npm run build && cd ..
# Terminal 1:
.venv/bin/python -m uvicorn academy.main:app --host 127.0.0.1 --port 8000 --workers 1
# Terminal 2:
cd frontend && npm run start
```

Linux execution is covered by CI only when a successful run is recorded; the local verification machine is Windows.

## Configuration

Copy `.env.example` to the **repository root** as `.env`. Defaults suffice.

| Variable | Default/source |
|---|---|
| `APP_ORIGIN` | `http://127.0.0.1:3000`; exact browser origin, including port. |
| `BACKEND_URL` | `http://127.0.0.1:8000`; frontend server's fixed upstream. |
| `DATABASE_URL` | Omit to use `<repository>\data\academy.sqlite3`. Optional absolute SQLAlchemy SQLite URL. |
| `RESEARCH_DIR` | Omit to use the repository `research` directory. |
| `YOUTUBE_API_KEY` | Optional key created in your Google Cloud project with YouTube Data API v3 enabled. |
| `YOUTUBE_FETCH_COMMENTS` | `false`; optional official sample of at most five comments on explicit refresh. |
| `OPENAI_API_KEY` | Optional key from your own OpenAI API account. |
| `AI_MODEL` | Optional model ID available to that API account; no model or spending is configured by default. |

Optional keys stay in the backend environment. Restart the backend after changing them. Settings shows availability, not key values. Metadata errors preserve stored research. AI feedback requires explicit answer submission and consent and is not expert grading. Provider quotas, API usage, cloud infrastructure and external project hosting can incur costs. Free learning resources do not imply free cloud execution.

## Database, migrations and updates

`data\academy.sqlite3` holds personal learning data, original research and indexed entities. It is ignored by Git. Opening a lesson never completes it; proficiency is manually assessed with evidence. Dates and streaks use UTC.

Migrations run automatically at backend startup. To run them explicitly:

```powershell
.\.venv\Scripts\python.exe -c "from academy.database import migrate; from academy.main import app; migrate(str(app.state.engine.url))"
```

Back up first, stop both terminals with Ctrl+C, then:

```powershell
git pull --ff-only
.\scripts\Setup.ps1
```

Restart both terminals. Do not remove `data`, `.env` or Docker volumes when updating. Future schema changes require a new migration; never rewrite an already deployed migration. Current restore accepts schema version `0001` only.

## Research and resource imports

Settings accepts either a recognized dataset envelope (such as `RESOURCE_CATALOG.json`) or a `{"datasets": {"RESOURCE_CATALOG.json": ...}}` map. Validate and inspect added/updated counts and versions, then explicitly apply. References, duplicate IDs and JSON schemas are checked. Stale previews are rejected. Imports update the database, **not repository research files or personal progress**.

Keep historical IDs in refreshed packages; flag outdated resources separately rather than removing referenced entities. JSON imports are limited to 20 MB and 10,000 records per backup collection. Missing source files are reported explicitly; no resources are fabricated. The research schema itself is required.

Career Intelligence supports full manual JDs and editable skill suggestions. It intentionally does not scrape arbitrary job URLs. Confirm extraction results before creating a job-specific plan.

## Backup and moving laptops

```powershell
.\scripts\Backup.ps1
.\scripts\Restore.ps1 -Snapshot .\backups\academy-YYYYMMDD-HHMMSS.sqlite3 -Confirm
```

The frontend and backend must be running. Snapshots are timestamped; restores require confirmation and retain a recovery copy. SQLite restores are limited to 64 MB. JSON export includes plans, progress, notes, competencies, projects, employers and jobs; Markdown export includes notes. No configured API secrets are exported.

On the second laptop, perform fresh installation, start the app, then restore your private snapshot. See [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md).

## Docker alternative

Dockerfiles and Compose configuration are included. **Docker execution was not verified on the development machine because Docker is unavailable.** Native installation is the verified alternative.

```powershell
docker compose up --build -d
docker compose ps
docker compose logs -f
docker compose stop
docker compose start
docker compose exec backend python -c "from academy.database import migrate; migrate('sqlite:////app/data/academy.sqlite3')"
docker compose run --rm backend python -m pytest backend/tests -q
```

Only frontend port `127.0.0.1:3000` is published; backend is internal. `academy-data` persists SQLite. Container listeners use their internal network, not a publicly published backend. Back up/restore through the same scripts or Settings. Backend startup loads research when the volume is new. Do not use `docker compose down -v` unless you intentionally want to destroy learning data.

## Testing

From repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m ruff format --check backend
.\.venv\Scripts\python.exe -m pip_audit --progress-spinner off
Set-Location frontend
npm run typecheck
npm run lint
npm run format:check
npm test
npm run build
npx --no-install playwright install chromium
npm run test:e2e
npm audit --omit=dev --audit-level=moderate
npm audit
```

Playwright starts isolated servers on ports 3127/8127 and a separate ignored test database. It does not use your personal API credentials. Keep those ports free; do not kill unrelated processes. CI runs the same checks on Linux.

To generate screenshots without publishing personal data: use the isolated acceptance-test workspace, take browser screenshots at desktop/mobile sizes, and review them before sharing. Failed Playwright tests save local screenshots and traces in ignored test artifacts.

## Security and limitations

This is a **single-learner, loopback-only application, not an authenticated public service**. Host/Origin validation and custom mutation headers protect the local browser boundary, but processes and users with access to your laptop can still access its data. Do not expose either server through public tunnels, reverse proxies or LAN bindings. See [SECURITY.md](SECURITY.md).

Known limitations include unverified Docker execution, evidence-limited research, no live provider credential test, no arbitrary job-site scraper, and unresolved development-only npm advisories. Detailed acceptance evidence is in [TEST_RESULTS.md](TEST_RESULTS.md), [INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md) and [PRODUCTION_READINESS_REPORT.md](PRODUCTION_READINESS_REPORT.md). The license decision remains pending.

Future extension points: real multi-user authentication, tested PostgreSQL support, additional validated tracks/providers and migration-compatible snapshot upgrades. See architecture documentation for the implementation boundaries.

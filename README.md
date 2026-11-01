# Engineering Academy

A local-first engineering learning and career workspace for experienced engineers. It combines six independent learning tracks, research-backed curricula, daily study guides, practical projects, interviews, employer/job research, notes and evidence-based competency assessments.

**No API key, cloud subscription or paid service is required for core features.** Videos and documentation open at their original publishers. The included research has explicit limitations; resource scores are not verified hiring predictions.

For step-by-step Windows startup instructions, see [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md).
Once it is running, follow [How to use the web app](#how-to-use-the-web-app) below.

## Features

- Senior software, cloud, DevOps/platform, AI, agent/MCP and DSA coding-interview tracks.
- Independent 14/30/60-day plans with 180-240 minutes daily, prerequisite ordering, manual adjustments and retained learning evidence.
- Separate video, reading, practical and knowledge-check completion.
- Searchable resources; bookmarks, personal ratings and verification flags.
- 325 original engineering interview questions plus 30 authored DSA exercises, detailed answer rubrics, mock scenarios and spaced review.
- DSA: 15 modules, persistent timed/blind/pattern/company practice, bounded browser-only JavaScript execution and 38 sourced company profiles.
- Editable employer watchlists, manual job descriptions, reviewable keyword extraction, skill gaps and job-linked plans.
- Multi-track portfolio projects, tasks and Markdown notes.
- Validated research imports, JSON exports, private SQLite snapshots and confirmed restore.
- Dark/light themes and mobile navigation.

## How to use the web app

Start both servers using [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md), then open **http://127.0.0.1:3000**. Keep both server terminals running while you study. Use the sidebar to navigate; on a smaller screen, open the navigation menu.

### 1. Choose a track and assess your starting point

Open **Learning Tracks** and choose one of the six tracks:

- Senior Software Engineering.
- Cloud Engineering.
- DevOps and Platform Engineering.
- AI Engineering.
- Agentic AI and MCP Engineering.
- Data Structures and Algorithms - Big Tech Coding Interviews.

Read the track overview and skills. Use **Assess with evidence** on a skill to record your current capability and practical evidence. Leave skills unassessed when you are unsure: past job experience and completed lessons do not automatically demonstrate proficiency.

Use **Activate track** to change your active track. Existing plans and saved progress remain available when you switch tracks.

### 2. Create your learning plan

Open **My Curriculum**. Select the learning track, target role, **Study duration** (14, 30 or 60 days), **Daily study minutes** (180-240), and learning intensity. Optionally select priority skills, a target company or a saved job.

For dedicated DSA study, leave **DSA routine within daily budget** at **No companion routine / dedicated DSA plan**. For another track, you can reserve 30 or 45 minutes of its existing daily budget for DSA; this does not add extra study hours.

Click **Generate study plan**, then use **Study** on a lesson to open it. Saved plans are listed in this section; **Set active plan** selects the plan you want to follow.

To change a plan, choose **Adjust and recalculate**, update the options and click **Recalculate safely**. Started/completed work and annotations are retained; shortening a plan can extend the schedule to preserve that work. Lesson controls also let you adjust days, skip a lesson, replace a resource or add a custom lesson.

### 3. Study and save completion evidence

Open **Dashboard** and click **Continue learning**, or choose a lesson in **My Curriculum**. In **Study Room**:

1. Read **Before the video** and identify the lesson's prerequisites and objectives.
2. Open the recommended video in its original publisher tab. Follow the implementation prompts rather than only watching.
3. Complete the supplementary reading and practical exercise. Run your code/tests locally where the exercise requires it.
4. Answer the knowledge-check questions and do the revision exercise.
5. Under **Capture your learning evidence**, enter actual study minutes, practical submission evidence and knowledge-check answers.
6. Check only the activities you actually completed, then click **Save lesson progress**.

A lesson is fully completed only after video, reading, practical and knowledge-check completion are explicitly saved. Practical and knowledge completion require their evidence/answers. Opening a video, visiting a lesson or revealing a coding solution does not complete it.

Use **Lesson notes** to save Markdown notes alongside your study. Click the relevant save button before navigating away; do not assume unsaved text is automatically stored.

### 4. Practise technical, system-design and DSA interviews

In **Interview Preparation**, filter the question bank by track, skill, difficulty or category. Select a question or use **Quick random question**. Explain your answer before inspecting the expected answer and rubric, then use **Record interview attempt** to save your answer, self-rubric score and confidence. Use the mock-session controls for a sequence of questions.

For system-design practice, select the Senior Software Engineering track and the relevant design category/skills. Work through architecture, reliability and engineering trade-offs rather than only memorizing answers.

For executable coding practice, expand **DSA coding practice, timed assessments and company preparation**:

1. Choose pattern, random, timed, company, mock or blind mode. Pattern mode requires a pattern selection.
2. Choose a duration and number of distinct questions. Write your clarification, approach, JavaScript `solve(input)`, complexity and trade-offs.
3. Click **Save coding draft** to preserve unfinished work, and **Run sample tests** to execute the provided fixtures.
4. Request a hint or reveal a solution only when needed; assistance is recorded.
5. Complete the ten self-ratings and click **Submit coding answer**.
6. Use **Resume or inspect session** to continue a saved session or review its submitted code and results. Use **Mark needs revision** when you need another attempt.

The deadline persists across reloads. Late submissions are saved but do not count as independent timed successes. Sample checks are not a complete correctness judge; other programming languages need local testing. Mastery requires independent successes on three separate UTC dates, not merely viewing a solution.

Select a company preparation profile to inspect its sources, confidence and limitations, start company practice or create a company DSA plan. An unknown process means generic preparation, not verified company questions. See [DSA and coding interviews](#dsa-and-coding-interviews) for further details.

### 5. Use the remaining workspace sections

| Section | How to use it |
|---|---|
| **Dashboard** | Resume your active plan and review upcoming lessons, weak areas, due revisions and active projects. Read readiness indicators as recorded evidence, not a hiring guarantee. |
| **Resource Library** | Search/filter resources, open the original links, bookmark useful material, save personal ratings and flag verification issues. External resources may have separate paid features; use the selected free portions. |
| **Practical Labs** | Inspect a lab's engineering specification, milestones and validation criteria, then use it as the starting point for hands-on implementation and portfolio work. |
| **Career Intelligence** | Add/edit employers and jobs, paste the full job description, and review extracted skill suggestions. Confirm required/preferred skills before saving. Use **Analyze skill gaps**, then **Create job-specific plan** to prepare against your explicit assessments. Job URLs are references, not an automatic scraping service. |
| **My Projects** | Create a project, associate learning tracks/skills, add repository or deployment links, and manage milestones/tasks and completion states. Build and test the actual project outside the learning app. |
| **Notes and Revision** | Create/edit Markdown notes, review the spaced-revision queue and export notes. Failed/assisted interview attempts generate reviews; revisit the problem independently and record your outcome. |
| **Settings** | Save theme, default study time, track priorities and review intervals. Check optional integration availability, export data, preview imports or restore a snapshot. |

Company watchlist entries and preparation priorities are editable; they are not proof of current vacancies or remote-work eligibility. Skill-gap extraction is reviewable keyword matching, not expert assessment of your CV.

### 6. Keep your learning data safe

Your saved progress, notes, interview attempts, projects and jobs live in **`data\academy.sqlite3`**, not only in the browser. Closing the browser or restarting the servers preserves saved data. Do not delete that file or the `data` directory.

Before updating or moving laptops, open **Settings > Export and backup** and download a **SQLite snapshot**. Keep it private. **Full JSON export** provides a portable record of personal data; **Markdown notes** exports your notes.

For research updates or personal JSON imports, select the correct **Import kind**, choose the JSON file, inspect the validated preview, then click **Confirm and apply import**. A personal JSON import merges records; it is not an exact rollback.

To recover an exact snapshot, use **Restore a SQLite snapshot**, confirm that it replaces the current database, and select a compatible backup. Back up your current state first. See [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md) for scripts, limits and moving laptops.

No paid API is needed for these workflows. Optional AI feedback requires backend configuration and explicit consent; it can send your answer/code to the provider and incur charges. Cloud deployments or external hosting for practical projects can also incur costs. Keep API keys out of notes, code submissions and frontend configuration.

### Suggested daily routine

Start with **Dashboard**, complete one scheduled study session in **Study Room**, save progress/notes, practise interview questions, and finish with due reviews in **Notes and Revision**. If you enabled a companion DSA routine, use its reserved time for coding rather than adding another session on top of your daily budget.

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

Restart both terminals. Do not remove `data`, `.env` or Docker volumes when updating. Future schema changes require a new migration; never rewrite an already deployed migration. Current restore validates revisions `0001` and `0002`; validated older snapshots are migrated before replacement.

## DSA and coding interviews

Choose the sixth track in **Learning Tracks**, then create a 14/30/60-day plan in **My Curriculum**. Lessons use the existing Study Room and notes/progress system. In **Interview Preparation**, expand **DSA coding practice, timed assessments and company preparation**; it opens automatically when DSA is active.

Select a pattern or a timed/random/blind/company/mock mode. Implement `solve(input)` in JavaScript, save your draft explicitly, run sample tests, explain complexity and submit the ten self-ratings. Saved sessions can be resumed or inspected; timers do not reset on reload. Reviewing a solution is recorded as assistance, not mastery.

Company profiles show source classification, limits and editable-watchlist guidance. Company plans highlight researched skills without breaking prerequisite order. Unknown formats use generic practice, not invented company questions. For another active track, select a reserved 30/45-minute DSA routine when creating its plan.

The runner is a timed, network-blocked browser worker, not a complete judge or a proctored examination. Other languages require local testing. Topic rates reflect submitted samples and self-assessment; they are not hiring predictions. See [DSA_IMPLEMENTATION_REPORT.md](DSA_IMPLEMENTATION_REPORT.md) and [DSA_RESEARCH_REPORT.md](research/dsa/DSA_RESEARCH_REPORT.md).

## Research and resource imports

Settings accepts either a recognized dataset envelope (such as `RESOURCE_CATALOG.json`) or a `{"datasets": {"RESOURCE_CATALOG.json": ...}}` map. Validate and inspect added/updated counts and versions, then explicitly apply. References, duplicate IDs and JSON schemas are checked. Stale previews are rejected. Imports update the database, **not repository research files or personal progress**.

For DSA updates, use named entries such as `{"datasets":{"dsa/DSA_QUESTION_BANK.json":...}}`. Startup adds missing DSA documents only; it never refreshes already edited research automatically. The DSA schema and dictionary are under `research\dsa`.

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

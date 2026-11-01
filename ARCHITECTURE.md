# Architecture

## Runtime and trust boundaries

Browser -> Next.js same-origin `/api` proxy -> FastAPI -> SQLite. External YouTube/OpenAI APIs are optional backend-only calls. Both native listeners bind to loopback. Docker publishes only the loopback frontend port. One backend worker serializes requests around database transactions and snapshot restore.

The proxy checks the exact configured Host and Origin, bounds bodies, validates path segments and forwards only selected headers to a fixed server-configured upstream. Writes need a custom same-origin header; restore also needs explicit confirmation. These are local access restrictions, **not authentication**.

## Modules

| Location | Responsibility |
|---|---|
| `frontend\app\workspace.tsx` | Eleven workspace views, domain forms and navigation state. |
| `frontend\app\components.tsx` | Accessible field editor, cards, recursive evidence display and safe external links. |
| `frontend\lib\data.ts` | API/error contract and safe research-data narrowing; no `any`. |
| `frontend\app\api\[...path]\route.ts` | Bounded server-only proxy. |
| `backend\academy\main.py` | API wiring, local boundary, lifespan and transaction dependencies. |
| `models.py`, `schemas.py` | Persistence invariants and strict user inputs. |
| `research.py` | Schema validation, reference checking, source documents and indexing. |
| `services.py` | Curriculum preservation, explicit competency, job gaps and spaced reviews. |
| `data_management.py` | Preview/apply, export, validated snapshot/recovery. |
| `integrations.py` | Fixed official provider endpoints, bounded errors and local fallbacks. |
| `backend\academy\dsa.py`, `dsa_content.py` | Typed coding sessions, sample comparison, analytics and additive research contracts. |
| `frontend\app\dsa-practice.tsx` | Existing interview section's DSA workspace, saved attempts and company preparation. |
| `frontend\lib\coding-runner.ts`, `app\coding-sandbox\route.ts` | Opaque-origin iframe and time-bounded browser worker; no server code execution. |

The workspace centralizes orchestration for a personal product; reusable components and backend services avoid separate microservices. As the frontend grows, extract individual sections behind typed props rather than creating a global plugin framework.

## Persistence

Explicit tables: users, research documents/records, plans, ordered plan lessons, progress, daily study activity, personal records and transient import previews. Owner foreign keys, lesson/research foreign keys, unique sequence and personal-reference constraints are enforced. SQLite connections enable foreign keys, trusted-schema restrictions and bounded lock waits.

Personal domain envelopes are typed by Pydantic and database kind checks. This avoids a repetitive table for every small domain while retaining strict input validation. Notes use validated attachments; projects and jobs use explicit parent/research links plus validated JSON fields. Import validation checks table columns, scalar types, foreign references, research indexes, schemas and evidence. Backups exclude transient previews, not personal records.

SQLite is the tested target. SQLAlchemy types allow a later PostgreSQL adapter, but that requires a driver, integration tests, transaction review and native PostgreSQL backups. Do not claim current PostgreSQL production support.

## Learning engine

The canonical repository research remains unchanged. Original JSON envelopes and indexed IDs are stored separately from personal plans and progress. Plans snapshot source lessons so research refreshes do not change recorded work. Recalculation retains started/completed/custom/annotated/adjusted slots, orders prerequisites and may extend shortened schedules. Priority skills are highlighted without unsafe dependency reordering. Explicit demonstrated competencies can waive conceptual slices; this does not complete a lesson or promote proficiency.

Progress stores four independent flags and actual minutes, answers and practical evidence. Daily activity retains UTC streak history. Interview scoring is self-assessment against authored rubrics; optional AI feedback is neither deterministic grading nor hiring advice.

## API and migrations

OpenAPI is available at the loopback backend `/docs`; it defines typed domain inputs. Catalog endpoints support bounded filters/offset/limit. Personal endpoints are ownership-scoped. Imports are previewed, time-limited, digest-checked and explicitly confirmed; stale state requires re-preview.

Migrations run at startup. Add a new Alembic revision for every future schema change, test upgrades from the previous release and preserve personal data. Never edit a deployed revision. Revision `0002` extends the personal-record kind constraint with `coding_session`, preserving existing rows. Restore accepts fully validated `0001`/`0002` snapshots, migrating a verified older candidate before replacement. Downgrade refuses to delete coding evidence.

DSA files are registered separately under `research\dsa`; the original five-track JSON/schema remain unchanged. Startup merges only missing DSA documents into persisted research. Sessions record server deadlines, drafts, self-ratings, assistance and fixture checks. Import/restore recomputes checks and validates ordered evidence. Performance recommendations prioritize due revisions and observed weaknesses, then curriculum order.

User JavaScript executes in a worker owned by an iframe with scripts permitted but no same-origin permission. The dedicated static runner has network-none CSP and narrowly scoped worker/evaluation permissions. The main application still prohibits evaluation; arbitrary code is never sent to a server execution service. This is browser isolation, not a hard memory quota or an accredited coding judge.

## Adding content and providers

1. **Track:** add a stable `track-*` record to the learner dataset, update any schema cardinality constraints, supply curricula/skills/projects/questions/knowledge links and validate all references. The engine derives `curriculum-<track suffix>-<days>` IDs.
2. **Curriculum:** add a validated template to the matching 14/30/60-day dataset with ordered prerequisites and daily budget invariants. Add generation/preservation tests.
3. **Resource provider:** add schema-valid free-status/evidence metadata and stable IDs to the catalogue. Ordinary HTTP(S) resources need no runtime integration.
4. **Interview category:** add schema-valid questions and mock references, with meaningful answer/rubric/follow-up content. Frontend category filters derive from data.
5. **Integration:** implement fixed official endpoints in `integrations.py`, server-side configuration, bounded timeout/errors and mocked tests. Never accept an arbitrary fetch URL or put keys in browser state.
6. **AI provider:** introduce a small provider adapter preserving explicit consent, limited output, error isolation and the local rubric fallback. Review privacy/cost behavior before enabling it.

Plain CSS is intentional: themed tokens and shared layout/components provide maintainable equivalent styling without an additional framework.

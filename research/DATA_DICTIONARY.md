# Data dictionary and consuming-agent instructions

Version **1.0.0**, research date **October 31, 2026**.

## Package layout

| File | Dataset/content | Primary entities |
|---|---|---|
| `EXECUTIVE_RESEARCH_REPORT.md` | Findings, priorities, market interpretation and handoff | Human-readable |
| `LEARNER_PROFILE.json` | Self-reported learner context, track definitions, active-track settings | `tracks` |
| `JOB_MARKET_SKILLS_MATRIX.json` | Skill registry, recomputable frequencies and sampling methodology | `skills`, `track_analyses` |
| `EMPLOYER_RESEARCH.json` | Data-editable watchlist and coded public descriptions | `employers`, `job_postings` |
| `RESOURCE_CATALOG.json` | Single source of resource metadata and evidence-limited rankings | `resources`, `topic_rankings` |
| `RESOURCE_EVALUATION_METHODOLOGY.md` | Free/evidence/scoring/access policy | Human-readable |
| `CURRICULUM_14_DAYS.json` | Five independent intensive plans | `curricula`, nested `lessons` |
| `CURRICULUM_30_DAYS.json` | Five independent comprehensive plans | `curricula`, nested `lessons` |
| `CURRICULUM_60_DAYS.json` | Five independent deeper-practice plans | `curricula`, nested `lessons` |
| `PRACTICAL_PROJECTS.json` | Exercise through capstone specifications | `projects`, nested `milestones` |
| `INTERVIEW_QUESTION_BANK.json` | Original questions, expected reasoning and rubrics | `questions`, `mock_interviews` |
| `LEARNING_DEPENDENCIES.json` | Direct skill DAG and per-plan artifact sequencing | `skill_dependencies`, `lesson_dependencies` |
| `SHARED_KNOWLEDGE_MAP.json` | Concept-assessment reuse and provider comparison | `knowledge_units` |
| `SOURCE_REGISTER.json` | Reviewed source provenance, exclusions and separate URL observations | `sources` |
| `RESEARCH_GAPS.md` | Explicit missing evidence and refresh work | Human-readable |
| `schemas/package.schema.json` | Explicit Draft 2020-12 structural contracts | Ten dataset-type branches and reusable definitions |
| `VALIDATION_RESULTS.json` | Structural/semantic check output | Validation artifact, not a curriculum dataset |
| `URL_CHECK_RESULTS.json` | Ordinary GET/oEmbed availability observations | Validation artifact, not content verification |
| `tools/` | Reproducible evidence, editorial generation, schema and validation utilities | Research tools only, not an application |
| `../RESEARCH_COMPLETE.md` | Deliverables, results, limitations and next action | Root handoff |

Twelve core JSON files use the shared schema. Markdown reports and validation artifacts are intentionally separate from those import datasets. The schema uses `dataset_type` to select the proper strict object contract; unknown fields fail. Its `ValidationResult` and `URLCheckResults` definitions also validate both JSON artifacts. The schema itself is checked against the Draft 2020-12 meta-schema. Entity/reference semantics are enforced separately by `tools/validate.py`.

## Top-level envelope

Every core dataset has `$schema`, `dataset_type`, `research_version` and `research_date`. `$schema` points to the local schema relative to the research directory; a consumer should load it locally rather than resolve the deliberately nonresolving `.invalid` schema identifier over the network. `research_date` is the research snapshot date, **not the publication date of every source**.

The relevant dataset types are `learner`, `skills`, `employers`, `resources`, `curricula`, `projects`, `questions`, `dependencies`, `shared` and `sources`. All three curricula files use `curricula`, distinguished by `plan_days`.

## IDs and joins

IDs are stable ASCII kebab-case strings, unique within their namespace:

| Namespace | Example | Registry |
|---|---|---|
| Track | `track-swe` | Learner profile |
| Skill | `skill-observability` | Skills matrix |
| Resource | `resource-otel` | Resource catalog |
| Lesson | `lesson-swe-30-13` | Nested curriculum day |
| Knowledge unit | `knowledge-observability` | Shared knowledge map |
| Project | `project-agent-08` | Project specifications |
| Milestone | `project-agent-08-m1` | Nested project milestone |
| Question | `question-swe-01-production-debugging` | Interview bank |
| Employer | `employer-mpesa` | Employer watchlist |
| Job | `job-012` | Employer job descriptions |
| Source | `source-doc-mcp-spec` | Source register |

Plural fields contain arrays, even for one reference. References include `track_ids`, `skill_ids`, `resource_ids`, `source_ids`, `verification_sources`, `interview_question_ids`, `lesson_ids`, `requires_skill_ids`, `requires_lesson_ids`, `project_id` and `canonical_lesson_id`. Resolve them through their registry; do not duplicate the resource title/date/score in lessons.

Five tracks map to six target role categories. The DevOps/platform track groups `devops` and `platform`; other tracks map to `senior`, `cloud`, `ai` and `agent`. Job primary categories are disjoint, and the five track denominators sum to the overall sample.

## Resource fields

Core identity: `id`, `title`, `resource_type`, `provider`, `creator`, `url`, `track_ids`, `skill_ids`, `difficulty`.

Access: `free_status`, `free_evidence`, `execution_cost`, `verification_scope`, `verification_sources`. Read these together: “fully free” describes learning access, not unbounded paid infrastructure/inference. Never recommend an excluded candidate just because it exists in the source register.

Time: `duration_minutes` is publisher-stated total material runtime when available; `duration_status` indicates availability. A lesson's `planned_video_minutes` is allocated viewing time. These values are not interchangeable. Resource publication dates are null unless observed exactly; document review timestamps do not automatically become original publication dates.

Engagement: `view_count`, `like_count`, `comment_count`, `playlist_size` are exact values or null, never estimated numeric placeholders. `public_metadata_observations` retains selected rounded/relative public displays with date and interpretation. A display such as “169K” must not be silently coerced into exact 169000. Unknown is not zero.

Quality: `technical_quality_score` is the technical-correctness component out of 25, `relevance_score` out of 20, `score_breakdown` the seven weighted components, `overall_score` the observed conservative total out of 100, and `score_upper_bound` the unresolved-evidence ceiling. `confidence` is low/medium/high. `score_rationale`, `selection_reason`, `technical_relevance`, `limitations` and `implementation_demonstration` qualify the score. Do not show a provisional score without its evidence/confidence.

Chapter metadata: `verified_chapters` contains start seconds and the specific observation method. No exact lesson-specific start/end playback was established. Daily `verified_timestamp_seconds` remains null rather than inventing a time range.

## Curriculum and lesson fields

Each file holds five curricula, one per track. Each plan contains exactly `duration_days` contiguous day records, not one merged five-track calendar.

Curriculum: `id`, `track_id`, `duration_days`, `daily_minutes`, `total_hours`, `scope`, `deliverable_project_id`, `capstone_completion_level`, `adjustment_policy`, `lessons`.

Lesson: `id`, `day`, `topic`, `knowledge_unit_id`, `skill_ids`, objectives, importance, prerequisite checks, recommended YouTube resource ID, viewing allocation, reading IDs/focus, implementation, interview IDs, revision, before/during/after study guide, time breakdown, outcome, completion criteria and project ID.

Default breakdown in minutes: preparation 10, video 35, reading 25, implementation 100, interview 20, revision 20; total 210. Plan totals are 49, 105 and 210 hours **per track** for 14, 30 and 60 days. The learner selects one active plan/track. Completion requires evidence, not a click on a video.

`phase` distinguishes initial slice, comparative implementation, failure/revision and integration. `assessment_status` explicitly says authored/not learner executed. `capstone_completion_level` distinguishes a thin slice from an integrated prototype and a production-shaped local portfolio candidate.

`prerequisites.lesson_ids` captures prior local artifacts in the selected plan. The global DAG records selected direct conceptual dependencies; it does not prove a complete profession-wide prerequisite map. A shorter plan can leave deeper topics out, which is reflected in its limited scope.

## Job and frequency fields

Job descriptions store URL, source authority, collection/publication/closing dates, explicit status, location/remote wording, unverified eligibility, years when stated, required/preferred skills, coded summary and interview evidence.

`live_description` means a role body was accessible at collection, **not confirmed currently accepting applications**. `expired` is used for the October 30, 2026 closing Kenyan role. A null publication date means freshness of posting could not be confirmed.

Skill counts are integers computed from identifiable postings. `sample_required_count` and `sample_preferred_count` reflect separate coding; `sample_mention_count` counts the union once per posting. Track rows use the track's named job IDs and denominator. Alternatives are mentioned options, not all-mandatory requirements. No frequency is an estimate of the worldwide labor market.

`core_skills_in_sample` means observed at least twice in that track's small sample. `niche_skills` means once in the sample, not proven market niche status. `emerging_skills` is a contemporary classification, not measured growth. `declining_skills` is empty because decline could not be established.

Employer `enabled` makes the watchlist configurable without code changes. Add/remove through data edits; preserve historical jobs when disabling an employer. `research_status` distinguishes reviewed posting, secondary evidence, reviewed/searched portal and watchlist-only. Null portal content verification must not be replaced with a GET date.

## Projects, interviews and reuse

Each track has three exercises, two intermediate projects, two advanced projects and one capstone. Projects specify problems, architecture, technologies, requirements, milestones/hours, acceptance checks, testing, security, local deployment, GitHub evidence and interview discussion.

Hours are editorial planning estimates, not timings measured by a learner. Additional production/provider work can exceed the plan. Synthetic fixtures are mandatory by default.

Questions are original educational material, not alleged actual employer questions. Each includes ID, track, skills, difficulty, category, expected elements, explanation, follow-ups, common mistakes and rubric totaling ten points. Mock interviews have timed stages totaling 60 minutes. Daily coding practice is integrated periodically.

Knowledge units join conceptually related lessons across plans/tracks. Use demonstrated evidence and its context to waive **identical conceptual learning**, not all applied security/provider/failure work. The catalog never duplicates resource metadata. A repeated skill ID does not claim two exercises are operationally identical.

## Provenance, unavailable data and validation

Source `content_status`, `method`, `findings_summary` and `collection_date` describe actual earlier review. `http_status`, `final_url` and `url_last_checked_at` are separate network observations. HTTP 200, a redirect or successful oEmbed does not establish full-course playback, hiring status, deployment correctness or free runtime.

`null` means unavailable/not established. Empty arrays mean no entries were identified under the stated methodology; they are not proof no such skills/resources/opportunities exist. Zero numeric counts are used only for actual counts within the identifiable sample.

## Reproduction commands (PowerShell, repository root)

```powershell
python research\tools\build.py
python research\tools\schema.py
python research\tools\validate.py
python -m unittest discover -s research\tools -p 'test_*.py'
```

The validator uses Python `jsonschema` (available in the research environment). If missing in another environment, install that validation dependency through its normal package manager; no application framework is required.

To perform a new dated network-availability check:

```powershell
python research\tools\check_urls.py
python research\tools\validate.py
```

This makes ordinary public GETs and official oEmbed requests; it does not scrape comments, download media, use authentication or retry denied pages through alternative routes. It changes only network-observation fields/reports. Content requires separate human review; never relabel a new URL check as new technical/free verification.

## Consuming-agent order

1. Read the executive report, methodology and gaps; keep this phase research-only.
2. Validate the local schema and semantic checks; inspect both reports rather than assuming all URLs/content are verified equally.
3. Load track/skill/resource/source registries, then employers/jobs, projects/questions and curricula.
4. Resolve all IDs, select the active track/plan, and show confidence/limitations/free-runtime boundaries.
5. Store user progress in a separate future application data store keyed to canonical knowledge ID plus artifact evidence and scope.
6. Add employers/jobs through data-driven records with reviewable provenance and recomputable denominators.
7. Extend the missing evidence before claiming an exhaustive recommendation engine. Do not build the application until a separate instruction authorizes that phase.

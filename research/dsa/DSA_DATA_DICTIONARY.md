# DSA data dictionary

## Research envelope

Each of the nine requested JSON datasets has `$schema`, `dataset_type: "dsa"`, `research_version` (semantic version string), `research_date` (ISO date), and one or more collections. `DSA_PACKAGE_SCHEMA.json` is the standalone JSON Schema; backend Pydantic validation additionally checks collection types and cross-document references.

| File | Collections / role |
|---|---|
| `DSA_SKILL_MATRIX.json` | `tracks`, `skills`, `modules`: sixth-track identity, concepts and invariants |
| `DSA_LEARNING_DEPENDENCIES.json` | `edges`: prerequisite `from`/`to` skill IDs and reason |
| `DSA_RESOURCE_CATALOG.json` | `resources`: 13 new selections with provenance/free-status/unknown metadata |
| `DSA_QUESTION_BANK.json` | `questions`, `mock_interviews`: original exercises, fixtures, rubric and ordered mock definitions |
| `DSA_COMPANY_RESEARCH.json` | `profiles`, `employers`: 38 research profiles and only missing employer additions |
| `DSA_SOURCE_REGISTER.json` | `sources`: URL, publisher/candidate classification, date and HTTP evidence |
| `DSA_CURRICULUM_14_DAYS.json` | `curricula`: 14-day template and lessons |
| `DSA_CURRICULUM_30_DAYS.json` | `curricula`: 30-day template and lessons |
| `DSA_CURRICULUM_60_DAYS.json` | `curricula`: 60-day template and lessons |

`DSA_URL_VERIFICATION.json` is supplementary public HTTP/oEmbed evidence, not an imported research envelope.

## IDs and relationships

IDs use `track-dsa`, `skill-dsa-*`, `knowledge-dsa-*`, `resource-dsa-*`, `question-dsa-01` through `question-dsa-30`, `mock-dsa-*`, `profile-dsa-*`, `source-dsa-*`, `curriculum-dsa-<days>` and `lesson-dsa-<days>-<day>`.

Questions link skills, source IDs and related questions. Mocks link questions. Lessons link knowledge units, skills, questions, prerequisite lessons and resources. Profiles link employers, sources and preparation skills. Microsoft Africa references the original Microsoft employer instead of duplicating it. Existing `resource-system-design` and `resource-api-design` IDs are reused.

Question fields include original statement, JSON input/output contract, constraints, example `test_cases`, hints, expected pattern, reference JavaScript, complexity, ten rubric dimensions, common mistakes, follow-ups, related IDs, recommended minutes and authorship. Difficulty and company relevance are editorial, not observed employer question frequencies.

Resource `null` fields mean unknown, not zero. `selection_label` is the curated label; `title` uses public oEmbed when obtained; `creator` credits the instructor and `publisher_author` records the publishing channel. Skill tags indicate relevance, not exhaustive coverage.

Profile `interview_evidence` is `officially_documented`, `multiple_candidate_reports`, `limited_anecdotal_evidence` or `unknown`. The current package does not use the second classification. Official process information does not automatically establish DSA intensity. `relevant_job_titles` are watchlist search terms, not live vacancies. `remote_from_kenya` remains `unknown`.

## Personal coding sessions

Existing `personal_records` store a typed `coding_session` envelope. No separate application/database is created.

Fields: configuration, distinct question IDs, UTC start/deadline, current index, drafts, revealed hints/solutions, optional manual `needs_revision` IDs, ordered submissions and active/completed state. Drafts contain code, clarification, approach, time/space complexity and trade-offs.

Submissions store answer, bounded JSON outputs, ten 0-5 self-ratings, solved claim, server-observed elapsed seconds, recomputed fixture checks, strict assistance/late flags and timestamp. Imports validate ordered submission relationships and recompute fixture checks. Timers do not reset on saving/reloading. Late work is retained but is not independent timed success.

States are derived: new, attempted, solved independently, solved with assistance, needs revision, mastered. Manual revision preserves prior attempts. A newer independent success clears an older manual revision flag's effective state. Mastery cannot be manufactured by a dropdown or viewing a solution.

Analytics contain actual attempts, latest unique-question outcomes, topic/difficulty performance, explicitly labeled self-ratings, due revisions, a recommended question/30-day lesson and the most recent 20 session records. An unassessed rate is `null`, never a made-up percentage.

## Import and migration

Because DSA envelopes share a dataset type, supply filenames explicitly:

```json
{"datasets":{"dsa/DSA_QUESTION_BANK.json":{"dataset_type":"dsa","research_version":"1.0.0","research_date":"2026-10-31","questions":[]}}}
```

This illustrates the envelope shape, not a runnable replacement catalogue: the real dataset includes `$schema` and all referenced records; historical referenced IDs cannot be removed.

Startup adds missing optional DSA documents without replacing existing edited research. Future updates require explicit preview/apply. Revision `0002` extends the personal-kind constraint to coding sessions. Fully validated `0001` SQLite snapshots are migrated to `0002` before replacement; invalid/unrecognized snapshots are rejected.

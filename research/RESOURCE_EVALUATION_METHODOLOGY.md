# Resource evaluation methodology

Research date: **October 31, 2026**. Version: **1.0.0**.

## What the scores mean

Scores are transparent, evidence-limited **editorial assessments**, not experimentally established correctness, learner satisfaction, or universal rankings. Public documentation, descriptions, chapter lists and official YouTube oEmbed metadata were examined. Videos were **not watched end to end**, code was not executed, and no YouTube comments were retrieved.

| Dimension | Maximum | Evidence needed for full credit |
|---|---:|---|
| Technical correctness | 25 | Current primary-source alignment and successful reproduction, including failure cases |
| Role relevance | 20 | Direct match to explicit employer requirements and the learner's target outcome |
| Depth and completeness | 15 | Covers design, implementation, failure handling, operations and trade-offs |
| Practical implementation | 15 | Demonstrated implementation with reproducible exercises and validation |
| Publisher credibility | 10 | Identifiable original maintainer, practitioner or educational publisher with relevant expertise |
| Community feedback | 10 | Accessible, attributable feedback about correctness, missing explanations and working examples |
| Recency | 5 | Observed publication/revision date and compatibility with current tools |
| **Total** | **100** | |

The current package caps correctness at 12/25 for metadata-only videos and 21/25 for primary-document spot checks. Videos receive modest implementation credit for public descriptions, not a claim that examples work. Topic relevance, scope and publisher credibility are separately assessed. Similar evidence receives similar scores; these are intentionally coarse, not false-precision competitive measurements.

`score_breakdown` holds earned editorial points or `null`. Unknown community feedback and undated publication are **null, not zero**. `overall_score` is the sum of known points on the original 100-point scale: a conservative lower bound. `score_upper_bound` adds the maximum unresolved points. Do not normalize this to a falsely confident 100/100, or interpret lower scores caused by unavailable evidence as proven poor quality.

`score_rationale`, `confidence`, `selection_reason`, `technical_relevance`, `limitations` and source references accompany every resource. Metadata-only video confidence is low; primary-document confidence is medium. No resource receives high confidence from popularity alone.

## Access and free-status policy

| Value | Meaning | Core eligibility |
|---|---|---|
| `fully_free` | Public learning material without a required payment; not a guarantee that all external services are free | Yes, with recorded evidence scope |
| `free_documentation` | Public technical documentation | Yes |
| `free_audit` | A course is auditable without payment; graded work/certification may be excluded | Only after its complete audit path is checked |
| `free_introductory` | Preview, sample or introduction only | Not as a full-course substitute |
| `free_optional_paid_certification` | All learning free, credential payment optional | Only after course-level confirmation |
| `paid` | Payment required for learning | No |

The present core uses public videos, public documentation, and Hugging Face courses whose introduction explicitly identifies them as free. YouTube oEmbed confirms title/channel and public embedding, **not every minute's playback in every country**. Regional, account or age restrictions may still affect access. Record those observations if encountered.

**Free learning is not free cloud compute.** Cloud resources, model inference, GPUs, hosted CI, premium observability and commercial desktop licensing must be considered separately. Default exercises use synthetic fixtures, local open-source runtimes, deterministic model adapters and optional small licensed local models. Optional cloud/model services require explicit opt-in, current pricing and teardown. A fake model validates engineering controls, **not AI model quality**.

Platform catalogs are not blanket course endorsements:

- AWS's checked digital-training page distinguishes free digital courses from subscription Digital Classroom. No subscription classroom is in the core.
- Google Cloud Skills Boost redirected to Google Skills; the observed GEAR credits are limited, not unlimited free labs. The catalog is discovery-only.
- DeepLearning.AI's MCP course returned HTTP 403. Its complete access/free status was not verified and it is excluded.
- Linux Foundation's free-resource catalog was checked, but individual advanced-course completion paths were not established.
- The newer Google SRE bookstore landing is not the free original book. The direct original online book/workbook paths are the recommendations.
- Advertised bootcamps, CBT Nuggets trials and sponsored external platforms are not part of recommended public YouTube lessons.

## YouTube metadata and timestamps

Exact `duration_minutes`, `published_at`, `view_count`, `like_count`, `comment_count` and playlist size are null where unavailable. Some rounded public search displays are preserved under `public_metadata_observations`; they must not become fabricated exact counts or dates. Counts can vary with cache and collection time.

Selected publisher chapter labels were observed through public indexed descriptions. `verified_chapters` records these observations and start seconds. No lesson-specific end time was verified; every daily guide therefore states a 35-minute **allocation**, not a precise chapter runtime. The future UI must distinguish allocation, publisher-stated runtime and missing runtime.

Comments were unavailable. No sentiment, correction history or implementation success rate is inferred. Full technical video review, exact-date verification and lawful community-feedback review remain open research tasks.

## Ranking and freshness

`topic_rankings` orders the checked shortlist by conservative score, with ID as a stable tie-breaker. It is **not** proof that every alternative on the internet was compared. Documentation and demonstration videos have different instructional functions; show both, not only the numerical winner.

Refresh jobs within 14 days and on application day. Re-check fast-moving AI/MCP resources before implementation; review stable conceptual sources quarterly. Check a dated release/specification, not merely a latest alias. Do not rewrite earlier verification dates when refreshing only a URL.

## Changes confirmed during research

- The checked latest MCP alias resolved to **2026-07-28**. Current architecture documents describe stateless, self-contained requests, `server/discover`, per-request metadata, stdio and Streamable HTTP. Older initialization/session assumptions and deprecated sampling are not prescribed as current behavior.
- Both checked OpenAI Evals and Datasets guides state that the older Evals platform becomes read-only **October 31, 2026**, with shutdown scheduled **November 30, 2026**. Neither is used as a required hosted evaluation lab. Default evaluation is local and task-specific.
- Anthropic's Building Effective Agents page retains useful workflow/agent distinctions but explicitly warns that tooling changed since December 2024.
- Current Kafka quickstart uses a local KRaft-based setup. Historical ZooKeeper-dependent tutorials should not control current installation.

See the corresponding `source-doc-*` and `source-excluded-*` entries in `SOURCE_REGISTER.json`; URL observations are separate in `URL_CHECK_RESULTS.json`.

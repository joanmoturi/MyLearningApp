# DSA research and course

Research date: **October 31, 2026**. This is an additive Academy package, not a replacement for the original five-track research.

This is the initial research snapshot date. HTTP refresh timestamps are recorded individually in the verification file; application acceptance was completed November 1, 2026.

## Scope and method

The package contains 15 modules, 30 original exercises with 75 example fixtures, 15 mock definitions, 13 resource selections, 38 company profiles and 104 scheduled lessons across 14/30/60-day plans. Two existing Academy resources are reused for senior API/design preparation rather than duplicated.

Sources were inspected through public search, publisher pages and bounded HTTP observations. `DSA_SOURCE_REGISTER.json` records provenance and access limits; `DSA_URL_VERIFICATION.json` records 65 distinct URL observations, 60 returning HTTP 200. HTTP success is not a guarantee of complete playback, resource correctness, a live vacancy or employment eligibility.

YouTube's public, no-key oEmbed endpoint confirmed the titles and publishing channel of the three individual freeCodeCamp selections: William Fiset's data-structures and graph courses, and Alvin Zablan's dynamic-programming course. Original authors and the publishing channel are distinguished. Playlist/channel listings were checked separately. Exact durations, publication dates, playlist sizes, engagement and comments remain unknown where not established.

## Resource comparison

| Selection | Main use | Trade-off |
|---|---|---|
| MIT 6.006 videos and notes | Invariants, proofs, algorithms and recurrence reasoning | University pacing; select relevant chapters rather than finish whole lectures daily |
| Abdul Bari's public algorithms playlist | Visual derivation, complexity, greedy/backtracking refresh | Foundational examples need independent senior-level extensions |
| Fiset/freeCodeCamp data structures | Linked structures, stacks, heaps and advanced structures | Long course; only a bounded relevant slice is scheduled |
| Fiset/freeCodeCamp graphs | Representation, traversal and graph reasoning | Does not substitute for independently testing every advanced graph algorithm |
| Zablan/freeCodeCamp dynamic programming | Deriving memoization and tabulation from examples | Extend introductory examples with constraints, counterexamples and proofs |
| NeetCode public videos and roadmap | Pattern recognition and topic ordering | Paid Pro material is not required; platform links can have separate paid features |
| Princeton companion site | Sorting, trees, graphs and implementation reference | Linked textbook purchase is not required; this selection is the public site |
| VisuAlgo | Visualizing state changes and invariants | Visualization alone is not an independent implementation |
| MDN, TypeScript and Python documentation | Language contracts and semantics | References, not full algorithm/interview courses |

HackerRank preparation kits and LeetCode Explore were investigated as supplementary practice candidates. They were not selected as the video-first teaching spine: access varies by portion and they do not replace the original guided/independent course. No proprietary problem statements or paid editorial solutions were copied.

Scores are provisional editorial scores, not learner outcomes or hiring predictions. Weights: correctness spot-check 25, coverage 20, demonstrations 20, interview relevance 20, provenance 15. Selected video scores are 76/100 and document/interactive selections 78/100. Missing community evidence is `null`, not invented praise. These scores do not imply fine-grained comparative certainty or an exhaustive audit of every lecture.

## Curriculum

Modules: foundations; arrays/strings; patterns; linked lists/caches; stacks/queues; searching/sorting; trees; heaps; intervals; graphs; backtracking; DP; greedy proofs; advanced structures; senior practical coding.

Each lesson has conceptual explanation, prerequisites, a video selection, reading, an original reference implementation, guided and independent exercises, interview questions, complexity, expected outcomes and evidence-based completion criteria. Broad topic lists include extension labs; they do not imply a separate fully worked reference solution for every subtopic.

- **14 days:** intensive refresh. Day one combines foundations and arrays, allowing all 15 modules within 14 days. Not a mastery guarantee.
- **30 days:** two phases per module: guided derivation and independent implementation.
- **60 days:** four phases: guided derivation, independence, failure/trade-offs, and mock/revision.

Default allocation is 210 minutes/day: preparation 10, video 35, reading 25, implementation 100, interview 20, revision 20. The app supports 180-240 minutes. Companion DSA practice reserves 30 or 45 minutes from another track's existing implementation budget; it does not add extra daily hours.

Senior practical coding emphasizes contracts, idempotency, interfaces, tests, refactoring, concurrency limits and failure handling. This is different from merely identifying an optimal puzzle algorithm. Existing system-design and API-design resources supplement the practical labs.

## Company watchlist and evidence

All profiles contain careers/source URLs, research date, searchable role titles, confidence, location uncertainty, topic priorities and limitations.

| Group | Profiles |
|---|---|
| Big tech | Google, Microsoft, Amazon, Meta, Apple, Netflix, NVIDIA |
| Engineering technology | Stripe, Uber, Airbnb, LinkedIn, Bloomberg, Datadog, Cloudflare, Snowflake, Adobe, Salesforce, Atlassian, Shopify |
| AI | OpenAI, Anthropic, Cohere, Mistral AI, Hugging Face, Google DeepMind |
| African opportunities | Safaricom, M-KOPA, Andela, Flutterwave, Cellulant, PesaPal, Microsoft Africa |
| Development and remote-first | World Bank, UNICEF, UNDP, Canonical, GitLab, Automattic |

Eight profiles have selected official guidance: Google, Microsoft, Microsoft Africa, Amazon, Meta, NVIDIA, OpenAI and Atlassian. **Official guidance does not necessarily establish specific DSA expectations:** Google's selected general page and NVIDIA's process page do not establish topic frequencies. Microsoft Africa reuses Microsoft guidance without claiming identical regional vacancy eligibility.

Microsoft, Amazon, Meta and Atlassian guidance inform coding/design preparation. Amazon's selected material includes Leadership Principles. OpenAI's official guide describes team-dependent assessments; the course does not assume a universal puzzle-only interview.

Stripe and Anthropic are **limited anecdotal evidence**. Stripe reports include a July 2026 report and a February 2026 new-graduate report; these cannot establish a guaranteed senior process. Anthropic's selected candidate-report synthesis is not official policy. Twenty-eight profiles retain unknown interview processes rather than invented company formats.

Tiers are editable editorial preparation priorities, not vacancy, salary or acceptance predictions. Tier 1 emphasizes major coding-interview targets and relevant African opportunities; Tier 2 adds established engineering companies; Tier 3 covers additional AI/development opportunities. The seeded personal watchlist can be edited or deleted in Career Intelligence without rewriting research.

No profile asserts verified remote employment from Kenya, a suitable live vacancy, work authorization or a cross-company seniority equivalence. Confirm all of these against an exact posting and recruiter guidance.

## Reproducibility and limitations

From the repository root:

```powershell
.\.venv\Scripts\python.exe research\dsa\verify_sources.py
.\.venv\Scripts\python.exe research\dsa\build_course.py
.\.venv\Scripts\python.exe -m pytest backend\tests\test_dsa.py -q
```

Observation regenerates public metadata only; it needs internet but no credentials. The generator writes only `research\dsa`. Refreshes of an already imported database require the explicit preview/apply workflow. Preserve stable IDs and personal records.

See `DSA_RESEARCH_GAPS.md` for inaccessible pages, unknown metadata, finite exercise coverage and assessment limits; `DSA_DATA_DICTIONARY.md` defines the application contracts.

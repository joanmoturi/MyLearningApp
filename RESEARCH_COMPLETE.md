# Engineering Academy research handoff

**Research version:** 1.0.0

**Research date:** October 31, 2026

**Status:** Deliverable package complete; evidence coverage explicitly partial. No application development.

## Completed deliverables

All sixteen requested files are in `research\`: executive report, learner profile, job skills matrix, employer research, resource catalog, evaluation methodology, three curriculum files, projects, interview bank, dependency graph, shared knowledge map, source register, gaps and data dictionary.

The package includes five tracks and fifteen independent plans covering 520 study days; 54 checked-access resources including 19 YouTube videos; 40 exercise/project specifications; 325 original interview questions and ten mock interviews; 28 watchlist employers and twelve coded public job descriptions. Explicit Draft 2020-12 schemas and reproducible research-generation/validation tools are included.

## Validation results

- Twelve core datasets passed explicit schema validation, ID/reference checks, dependency ordering/acyclicity and recomputed job-frequency checks.
- All fifteen plans have the correct contiguous day counts, 210-minute daily budgets, integrated interviews/revision and final demonstrable deliverables.
- Each track has at least three exercises, two intermediate projects, two advanced projects and one capstone.
- All question rubrics sum to ten; mock-interview stages sum to their allocated time.
- Three negative integrity tests passed: unresolved references, hidden time/forward prerequisites, and fabricated frequency/unsupported feedback are rejected.
- Ordinary public URL/official YouTube oEmbed checks completed: **100 reachable of 109 unique requests; nine blocked or unavailable**. These include excluded candidates and employer portals; core recommendation endpoints were reachable in this check. No blocked access was bypassed.
- Reports: `research\VALIDATION_RESULTS.json` and `research\URL_CHECK_RESULTS.json`.

## Known limitations

The twelve-posting sample is small and purposive, with only one cloud-category description and one expired Kenyan secondary role. It cannot establish market-wide demand, trends or broad Kenya-remote eligibility; development-organization evidence remains insufficient.

Videos were not watched end to end or reproduced. Exact video metadata, comments and community sentiment were unavailable; selected rounded displays and publicly indexed chapter markers are explicitly qualified. Not every advanced topic has a dedicated reviewed video. Scores are provisional editorial assessments, not tested correctness claims.

Free material does not imply free cloud/API/GPU execution. Default labs use local tools and synthetic fixtures; cloud blueprints/local models are not proof of deployed provider expertise or actual-model quality. Study times are budgeted, not learner-piloted. Current-version and access caveats are preserved in `research\RESEARCH_GAPS.md`.

## Recommended next action

Consume the package using `research\DATA_DICTIONARY.md`, run the validation commands, and pilot the software-engineering 30-day plan. Expand Kenyan/development-organization job evidence and verify high-impact current video implementations before presenting recommendations as exhaustive. **Do not begin application development in this phase.**

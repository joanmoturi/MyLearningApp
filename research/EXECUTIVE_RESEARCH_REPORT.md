# Engineering Academy: executive research report

**Research version:** 1.0.0

**Collection date:** October 31, 2026

**Status:** Versioned, structurally validated research package with explicitly partial market/video evidence. **No application was built.**

## Executive findings

The strongest immediate positioning is **experienced software engineer with production diagnostics, identity, integration and operational judgment**, not beginner cloud developer or unproven AI researcher. The supplied background is self-reported exposure, not certification of mastery. Preserve existing strengths and assess architectural depth, Linux/networking, infrastructure ownership, evaluation and safe agent execution before waiving lessons.

The checked employer descriptions emphasize **building, operating and explaining systems**, not merely recognizing tool names. Senior backend roles ask for distributed systems, maintainable APIs, performance and ownership. Infrastructure roles ask for Kubernetes, infrastructure as code, delivery automation, incident response and identity. AI/agent roles couple retrieval/tool integration with evaluation, observability, safe permissions and demonstrable production delivery.

The package contains five tracks, 15 independent curricula and 520 study-day records, 54 resources including 19 YouTube videos, 40 exercise/project specifications, 325 original interview questions and ten mock interviews. These are **authored learning artifacts**, not completed learner work or guaranteed job readiness. Validation and access reports are separate files.

## Priority recommendation

Retain the initial order:

1. **Senior Software Engineering:** closest fit to existing software ownership, APIs, identity debugging and production context. Prioritize system design, database/concurrency correctness, failure semantics, performance and evidence-backed leadership.
2. **Cloud Engineering:** use Azure exposure as a starting advantage; verify gaps instead of repeating elementary certification material. Develop AWS translation next and GCP literacy through equivalent workload design.
3. **DevOps and Platform Engineering:** share networking, identity, containers, reliability and observability with cloud. Advance beyond pipeline operation into substrate design, recovery, platform interfaces and developer outcomes.
4. **AI Application Engineering:** add Python/data-tooling competence, evaluated retrieval, typed model interfaces and production AI controls. A practical AI overlay can differentiate the software portfolio without claiming research-model expertise.
5. **Agentic AI and MCP Engineering:** build on API/security, AI evaluation and distributed state. Prefer a bounded deterministic workflow or single agent before adding multi-agent coordination.

This ranking is a **career-transition judgment**, not a statistically validated ranking of vacancy volume. The small sample cannot prove that one role is more employable worldwide. If a specific target employer requires AWS infrastructure or evaluated agent delivery, move that employer's missing competency earlier while retaining the shared core.

**Suggested selection:** start the 30-day software track. Choose one active track, not all five concurrently. Reuse demonstrated shared knowledge and add provider-/application-specific labs when changing tracks. Use 14 days for a diagnostic sprint and thin slice; use 60 for repeated implementation, comparative experiments, fault drills and portfolio hardening.

## Job-market evidence and limits

The identifiable sample contains **12 descriptions**, collected on **October 31, 2026**: eleven employer-hosted ATS descriptions and one secondary Kenyan posting. Most publication dates were unavailable, so these are contemporary observed descriptions, **not twelve proven newly posted vacancies**.

| Curriculum track | Sample denominator | Included employers |
|---|---:|---|
| Senior software | 3 | Reddit, Customer.io, M-Pesa Africa through a secondary Safaricom listing |
| Cloud | 1 | Joblogic |
| DevOps/platform | 3 | Sureify, PrivateID, Isar Aerospace |
| AI application | 2 | Typeform, Temus |
| Agentic/MCP | 3 | Everpure/Pure Storage board, Weedmaps, Anthropic |

Each posting has one primary role category. DevOps and platform categories are combined into their curriculum track. Required/preferred coding is explicit; a language or cloud alternative is a **mention**, not a requirement to master every option. Each skill is counted once per posting.

In this sample, AWS, Python and agent-related requirements/preferences appear in **8/12** descriptions each; CI/CD in **7/12**; Kubernetes, observability and security in **6/12** each. These frequencies reflect a deliberately AI/infrastructure-oriented discovery sample and **must not be presented as general-market prevalence**. Exact posting IDs, required/preferred distinctions and recomputable rows are in `JOB_MARKET_SKILLS_MATRIX.json`.

Important posting observations:

- **Customer.io** explicitly describes end-to-end ownership, cloud-native distributed systems, relational database trade-offs, on-call and verification of AI-assisted changes. Its posted interview process includes an ownership discussion/AI-assisted coding, collaborative system design, realistic take-home and review. Source: `job-007`.
- **Reddit** asks for distributed systems experience, maintainable APIs, well-tested code, performance, mentorship and cloud/Kubernetes familiarity. This supports deep software judgment, not a superficial diagram-only system-design track. Source: `job-006`.
- **Sureify/PrivateID** connect Terraform, Kubernetes and CI/CD to Linux, scripting, on-call and root-cause analysis. Existing identity diagnostics is useful adjacent experience, but does not itself establish cluster/state expertise. Sources: `job-001`, `job-002`.
- **Isar Aerospace** explicitly emphasizes cluster topology, upgrades, storage, certificates, GitOps, reusable delivery, Azure identity and ADRs. Platform engineering means owning runtime and supported developer workflows, not simply installing a portal. Source: `job-011`.
- **Typeform** asks for production AI/ML experience, enterprise RAG, automated evaluations, Python, infrastructure and operating trade-offs. Its four-year experience requirement concerns AI/ML specifically, not automatically any four years of software engineering. Source: `job-009`.
- **Weedmaps** asks for shipped LLM features, evaluated retrieval, typed/tool interfaces, cost/latency ownership, permissions and on-call. MCP is among its bonus skills. Source: `job-004`.
- **Everpure** explicitly requests MCP servers, enterprise data models, RAG/agents, REST/OAuth and technical leadership. Integration and identity experience are particularly reusable here. Source: `job-003`.
- **Anthropic Computer Use** emphasizes end-to-end product delivery, agent-harness reliability, usage instrumentation and practical LLM integration; evals and guardrails are preferred. Source: `job-005`.
- **M-Pesa Africa's** secondary listing connects API/event architecture, SDK compatibility, security, ADRs, developer portals and multi-market leadership. It asks for eight-plus years and is a **stretch architecture role**. Posted **October 26, 2026**, it expired **October 30, 2026**; it is skills evidence, **not an open opportunity on October 31**. Source: `job-012`.

Kenya-remote eligibility was not assumed. Typeform specifies US/US Eastern eligibility; Sureify says Americas; Joblogic is onsite; Anthropic describes office attendance. Other remote labels still need country/contract confirmation. There is insufficient development-organization evidence to characterize UNDP/UNICEF/UNOPS/World Bank hiring requirements. The configurable 28-employer watchlist preserves those targets with explicit research status.

No growth, decline, salary or hiring-volume statistics were invented. MCP/agents/evaluation are **contemporary observed competencies**, not proven statistically rising trends. Longitudinal evidence is required to label skills declining; established CI tooling remains relevant where requested.

## Competency strategy by track

### Senior software engineering

**Leverage:** APIs, production investigations, integrations, reviews, migration context and organizational experience.

**Build evidence:** consistency and partial failure; SQL internals, isolation and constraints; idempotent effects/outbox; backpressure, cache stampedes and hot partitions; bounded concurrency; tail-latency profiling; SLO-driven overload handling; authorization; practical testing; reversible migrations; ADRs and influence.

**Portfolio:** a tenant-scoped diagnostics platform with relational persistence, outbox/worker semantics, telemetry, failure fixtures and measured recovery. Keep a modular core until extraction has a documented benefit. Interview practice requires capacity assumptions, invariants, failure handling, alternatives and a specific personal ownership story.

### Cloud engineering

**Leverage:** Azure resource/engineering context and identity debugging.

**Build evidence:** packet paths, DNS/routing/private endpoints, workload identity, resource hierarchy, storage/managed database ownership, serverless duplicates, managed Kubernetes responsibilities, zone/regional failure, restores, RTO/RPO, migration sequencing and unit economics.

**Provider comparison:** use Azure for depth, AWS for transferable breadth, and GCP for selected operational/architecture mapping. Conceptual equivalents are not identical products. Re-check each provider's IAM evaluation, network scope/defaults, limits, prices and service failure behavior. The local free-core produces architecture and recovery evidence, **not verified deployment on three real cloud providers**.

### DevOps and platform engineering

**Leverage:** incidents, deployment context, automation and engineering systems.

**Build evidence:** Linux/systemd, reliable shell, DNS/TLS debugging, non-root reproducible containers, Kubernetes probes/resources/storage/upgrades, Helm, Terraform state/drift, secure immutable-artifact pipelines, Azure Pipelines translation, GitOps, progressive rollout, Prometheus/Grafana/OpenTelemetry and recovery.

**Platform judgment:** a supported golden path includes service contracts, owners, safe defaults, exceptions and adoption outcomes. Backstage is an interface/catalog, not a substitute for a reliable platform. Rehearse changes and incidents instead of counting configured tools.

### AI application engineering

**Leverage:** backend contracts, operational debugging and secure integration.

**Build evidence:** Python engineering, relevant ML generalization/evaluation, model/token budgets, embeddings, hybrid/vector retrieval, ingestion provenance, chunk/reranking ablations, structured/semantic validation, safe tool boundaries, offline evals, privacy, redacted traces and latency/cost experiments.

**Do not overinvest early:** frontier training and fine-tuning are not the default path for application roles. Keep fine-tuning as a bounded hypothesis with clean data and holdouts. Fake providers are useful for control-flow tests but cannot validate model accuracy. Evaluate actual local/opted-in models separately.

### Agentic AI and MCP engineering

**Leverage:** external API integration, OAuth/identity, automation and production ownership.

**Build evidence:** host/client/server boundaries; tools/resources/prompts; current discovery/request semantics; SDK implementation and interoperability; stdio/HTTP differences; HTTP authorization; external throttling; checkpoint/effect ledgers; memory scope/lifecycle; stopping; bound approvals; trajectory evaluation; safe deployment and auditing.

**Architectural progression:** conventional LLM application -> deterministic workflow -> bounded tool-using agent -> multi-agent experiment only when a measured task benefit justifies additional coordination. MCP standardizes context/tool exchange, not planning or general agent memory.

## Strongest checked free shortlist

“Strongest” means preferred within the checked shortlist, not exhaustive internet superiority. Scores are provisional and exact video metadata/community feedback are often unavailable.

| Track | Preferred demonstration | Primary/free companion |
|---|---|---|
| Software | freeCodeCamp System Design Course (`resource-system-design`) and interview overview | PostgreSQL isolation/indexes; API Design; original Google SRE book/workbook |
| Cloud | John Savill AZ-305 orientation; ExamPro/freeCodeCamp AWS and GCP selected chapters | Azure, AWS and GCP Well-Architected frameworks; local Terraform Docker labs |
| DevOps/platform | DevOps Directive Kubernetes and GitHub Actions; Nana Argo CD | Kubernetes/Helm/Argo CD docs; Terraform local lab; OTel/Prometheus/Grafana; Backstage |
| AI | Karpathy GPT implementation orientation; freeCodeCamp RAG from scratch | Explicitly free Hugging Face LLM course; Evaluate guide; structured-output and OWASP docs |
| Agentic/MCP | freeCodeCamp MCP and LangGraph courses; MCP Security Fundamentals | Dated current MCP architecture/spec/server/transport/auth docs; HF Agents/MCP; LangGraph |

Direct URLs, confidence, free evidence, source checks, weaknesses and rankings are normalized in `RESOURCE_CATALOG.json`. Older videos are conceptual companions, not installation authorities. No paid-only course, free trial or subscription classroom is required.

## Current-version findings

The checked current MCP specification is **July 28, 2026**, not a 2025 tutorial revision. It describes stateless requests, `server/discover`, per-request metadata and updated transport bindings; sampling is deprecated. Build to dated docs and record actual SDK/client compatibility before implementation. Sources: `source-doc-mcp-spec`, `source-doc-mcp-architecture`, `source-doc-mcp-transports`.

The checked OpenAI Evals/Datasets guides both state an older-platform read-only transition on **October 31, 2026** and scheduled shutdown on **November 30, 2026**. The curriculum therefore uses local evaluation rather than either required hosted lab. Sources: `source-excluded-2`, `source-excluded-3`.

These observations demonstrate why current primary docs outrank even popular older videos for fast-changing implementation details. A newer title alone does not prove that every example works.

## Daily study design

All day records allocate **210 minutes**: 10 preparation, 35 selected video, 25 reading, 100 implementation, 20 interview and 20 revision. Full multi-hour videos are never assigned for completion in one day. Exact video duration remains separate from allocated time.

At 180 minutes, reduce optional video and reading by 15 minutes each; retain practical/interview/revision work. At 240 minutes, add 30 minutes of implementation/remediation. If the learner cannot finish a milestone, carry it forward or extend the calendar; do not hide additional study hours.

Each plan has prerequisite ordering, before/during/after study guides, comprehension questions, original practical work, interview IDs, revision, outcomes and evidence-based completion criteria. The 60-day plans repeatedly implement and break bounded slices; they do not merely add more passive video. Every plan ends with a publishable demonstrable slice, with the 14-day scope explicitly smaller than the full capstone specification.

Networking, API contracts, security, databases, reliability, observability and delivery are shared once at the conceptual-assessment level. Reuse does not waive new cloud-provider, agent-permission or application-failure tests.

## Handoff

Read `DATA_DICTIONARY.md`, `RESOURCE_EVALUATION_METHODOLOGY.md` and `RESEARCH_GAPS.md` before importing data. Validate locally against `schemas/package.schema.json` plus semantic checks. The future application must render unknown evidence honestly, retain free-learning/runtime distinctions, allow data-driven employer edits, and keep learner completion separate from research verification.

Before presenting this as an exhaustive, fully reviewed recommendation engine, expand the regional/development-organization job sample and verify high-impact video chapters/implementations. **Application development remains out of scope.**

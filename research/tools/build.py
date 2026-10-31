"""Materialize the research-only package from reviewed evidence and authored units."""

import json
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from evidence import CHAPTERS, DATE, DOCS, EMPLOYERS, EXCLUSIONS, JOBS, PUBLIC_DISPLAYS, VERSION, VIDEOS
from topics import TRACKS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "schemas/package.schema.json"
SCOPE = "Research package; no application implementation or real learner lab execution."


def write(name, kind, **data):
    doc = {
        "$schema": SCHEMA,
        "dataset_type": kind,
        "research_version": VERSION,
        "research_date": DATE,
        **data,
    }
    (ROOT / name).write_text(json.dumps(doc, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return doc


def sk(key):
    return "skill-" + key


def tr(key):
    return "track-" + key


def rs(key):
    return "resource-" + key


def split(value):
    return value.split(",") if value else []


units = {}
for key, (title, roles, text) in TRACKS.items():
    rows = [line.split("|") for line in text.strip().splitlines()]
    assert len(rows) == 20 and all(len(row) == 9 for row in rows)
    if key == "ai":
        rows.insert(0, rows.pop(2))
    units[key] = [
        dict(zip(("skill", "title", "concepts", "lab", "success", "question", "reasoning", "doc", "video"), row))
        for row in rows
    ]
    for row in units[key]:
        row["concepts"] = [x.strip() for x in row["concepts"].split(";")]

skill_keys = sorted(
    {u["skill"] for group in units.values() for u in group}
    | {s for row in DOCS for s in split(row[5])}
    | {s for row in VIDEOS for s in split(row[5])}
    | {s for row in JOBS for s in split(row[7]) + split(row[8])}
)
track_list = [
    {
        "id": tr(key),
        "name": title,
        "target_role_categories": split(roles),
        "priority": index + 1,
        "baseline_assessment": "Explain one production system you owned; implement a typed API with tests; diagnose one synthetic failure. Treat claimed experience as self-reported until demonstrated.",
        "skill_ids": [sk(u["skill"]) for u in units[key]],
    }
    for index, (key, (title, roles, _)) in enumerate(TRACKS.items())
]
sources = []
resources = []


def source(sid, url, title, source_type, method, status, findings, published=None):
    entry = {
        "id": sid,
        "url": url,
        "title": title,
        "source_type": source_type,
        "collection_date": DATE,
        "published_at": published,
        "method": method,
        "content_status": status,
        "http_status": None,
        "final_url": None,
        "url_last_checked_at": None,
        "findings_summary": findings,
        "limitations": "Public content checked to stated extent only; no full-course playback, implementation execution or live hiring guarantee.",
    }
    sources.append(entry)
    return sid


def score(video, tracks, practical, dated, stale):
    # Editorial evidence-limited scoring, not a claim of experimentally verified correctness.
    points = {
        "technical_correctness": 12 if video else 21,
        "role_relevance": 18 if tracks else 12,
        "depth_completeness": 9 if video else 12,
        "practical_implementation": practical,
        "publisher_credibility": 8 if video else 10,
        "community_feedback": None,
        "recency": (2 if stale else 5) if dated else None,
    }
    reasons = {
        "technical_correctness": "Provisional: metadata/chapter or primary-document spot-check only; code not executed and full material not reviewed.",
        "role_relevance": "Mapped to the sampled role requirements and the authored unit's deliverable, not a market-wide demand estimate.",
        "depth_completeness": "Document scope or public chapter descriptions reviewed; gaps in production coverage retained.",
        "practical_implementation": "Implementation demonstrated/described in public metadata or tutorial text; working execution not verified.",
        "publisher_credibility": "Identifiable original project publisher, course author or conference channel; credibility does not prove every claim.",
        "community_feedback": "Unavailable: no YouTube comments were obtained; view count does not substitute.",
        "recency": "Awarded only for an observed exact publication date; undated pages and relative search ages remain unknown.",
    }
    observed = sum(v for v in points.values() if v is not None)
    unknown = (10 if points["community_feedback"] is None else 0) + (5 if points["recency"] is None else 0)
    return points, reasons, observed, min(100, observed + unknown)


def resource(key, title, creator, url, track_keys, skills, resource_type, published, finding, source_ids, limitation, duration=None):
    video = resource_type == "youtube_video"
    practical = 8 if video else (14 if key in ("terraform", "docker", "mcp-server") else 8)
    stale = key in ("agent-patterns", "mcp-video", "terraform-video", "azure-cram", "linux", "docker-video", "k8s-nana")
    points, reasons, low, high = score(video, track_keys, practical, published is not None, stale)
    resources.append({
        "id": rs(key),
        "title": title,
        "resource_type": resource_type,
        "provider": "YouTube" if video else creator,
        "creator": creator,
        "url": url,
        "track_ids": [tr(t) for t in split(track_keys)],
        "skill_ids": [sk(s) for s in split(skills)],
        "difficulty": "prerequisite_repair_or_intermediate" if video else "intermediate_to_advanced",
        "duration_minutes": duration,
        "duration_status": "publisher_stated" if duration is not None else "unavailable",
        "free_status": "fully_free" if video or key.startswith("hf-") else "free_documentation",
        "free_evidence": finding if not video else "Publicly indexed YouTube lesson and successful official oEmbed metadata response; no paid lesson gate observed. Full playback and every promoted external service not checked.",
        "execution_cost": "Existing computer/local open-source tools only for default labs; provider inference, cloud resources, hosted runners and optional GPU compute can cost money and are excluded from the free guarantee.",
        "published_at": published,
        "last_verified_at": DATE,
        "verification_scope": "Public metadata/access and available descriptions only" if video else "Public document content/access, not full chapter traversal or lab execution",
        "view_count": None,
        "like_count": None,
        "comment_count": None,
        "playlist_size": None,
        "community_feedback_summary": "Unavailable; no comments retrieved or sentiment inferred. Rounded search popularity displays were not treated as exact counts.",
        "public_metadata_observations": {
            "observed_at": DATE,
            "view_count_display": PUBLIC_DISPLAYS.get(key, {}).get("view_count_display"),
            "like_count_display": PUBLIC_DISPLAYS.get(key, {}).get("like_count_display"),
            "published_age_display": PUBLIC_DISPLAYS.get(key, {}).get("published_age_display"),
            "interpretation": "Rounded/relative public search display only; may be cached. Not an exact count, publication date or community-quality signal.",
        },
        "technical_quality_score": points["technical_correctness"],
        "relevance_score": points["role_relevance"],
        "overall_score": low,
        "score_upper_bound": high,
        "score_breakdown": points,
        "score_rationale": reasons,
        "confidence": "low" if video else "medium",
        "selection_reason": "Preferred original-source coverage of " + ", ".join(split(skills)) + "; use alongside bounded implementation and interview practice.",
        "technical_relevance": "Conceptual value retained; consult dated/current official documentation for APIs and version-sensitive operations." if stale else "Relevant to the named skill outcomes; not a certification of production readiness.",
        "implementation_demonstration": "Described in public chapters/tutorial text; execution not verified",
        "limitations": [limitation, "No independently executed correctness audit or comprehensive community review."],
        "verification_sources": source_ids,
        "verified_chapters": [{"start_seconds": seconds, "label": label, "verification": "Public publisher chapter description observed in web search; not frame-level playback"} for seconds, label in CHAPTERS.get(key, [])],
    })


for key, title, publisher, url, track_keys, skills, finding, published in DOCS:
    sid = source("source-doc-" + key, url, title, "official_documentation", "web_fetch: reviewed public content", "content_reviewed", finding, published)
    resource(key, title, publisher, url, track_keys, skills, "free_course" if key.startswith("hf-") and key != "hf-evaluate" else "official_documentation", published, finding, [sid], finding, {"terraform": 35, "docker": 15}.get(key))

for key, vid, title, creator, track_keys, skills, published, limitation in VIDEOS:
    url = "https://www.youtube.com/watch?v=" + vid
    meta_url = "https://www.youtube.com/oembed?url=" + quote(url, safe="") + "&format=json"
    sid = source("source-video-" + key, url, title, "youtube", "Public web search/watch URL; no restricted scraping", "metadata_only", limitation, published)
    mid = source("source-oembed-" + key, meta_url, title + " metadata", "youtube_oembed", "Official public oEmbed GET", "metadata_reviewed", "Title and channel confirmed; oEmbed does not expose exact runtime, publication date, engagement or comments.")
    resource(key, title, creator, url, track_keys, skills, "youtube_video", published, "", [sid, mid], limitation)

for index, (url, status, reason) in enumerate(EXCLUSIONS, 1):
    source("source-excluded-" + str(index), url, "Excluded or non-core candidate", "candidate", "web_fetch: attempt and observed response", status, reason)

jobs = []
for index, row in enumerate(JOBS, 1):
    employer, title, role, url, location, minimum, maximum, required, preferred, summary, posted, closes, authority, status = row
    jid = "job-" + str(index).zfill(3)
    sid = source("source-" + jid, url, title, "job_posting", "web_fetch: full available technical description reviewed", "content_reviewed", summary, posted)
    jobs.append({
        "id": jid, "employer_id": "employer-" + employer, "title": title,
        "primary_role_category": role, "url": url, "source_id": sid,
        "source_authority": authority, "collected_at": DATE, "posted_at": posted,
        "closes_at": closes, "status": status, "location_and_remote_policy": location,
        "kenya_remote_eligibility": "local_kenya_role" if employer == "mpesa" else "not_verified",
        "minimum_years": minimum, "maximum_years": maximum,
        "required_skill_ids": [sk(s) for s in split(required)],
        "preferred_skill_ids": [sk(s) for s in split(preferred)],
        "requirements_summary": summary,
        "coding_notes": "Language/cloud alternatives count as mentioned requirements, not a requirement to know every listed alternative. Examples are normalized to capabilities; no inferred requirements added.",
        "seniority_basis": "Senior title/ownership scope or explicit experience; nominal years do not substitute for production competence.",
        "interview_evidence": (
            "Posting explicitly describes recruiter call, end-to-end ownership discussion plus AI-assisted coding, collaborative system design, realistic take-home and review."
            if employer == "customerio" else
            "Posting describes screening, online test, team interview, in-house technical assessment and manager interview."
            if employer == "joblogic" else "No role-specific interview sequence available in reviewed body; use mock scenarios as authored preparation, not employer claims."
        ),
    })

employers = []
for key, name, url, status in EMPLOYERS:
    related = [job for job in jobs if job["employer_id"] == "employer-" + key]
    # Do not mark seed portals checked just because a URL looks plausible.
    employers.append({
        "id": "employer-" + key, "name": name, "enabled": True,
        "career_url": url, "watch_keywords": ["senior software", "cloud", "DevOps", "platform", "AI", "MCP", "agent"],
        "target_locations": ["Kenya", "international", "remote"],
        "research_status": status, "portal_content_last_verified_at": DATE if status == "portal_reviewed" else None,
        "job_ids": [job["id"] for job in related],
        "source_ids": [job["source_id"] for job in related],
        "observed_requirements": [job["requirements_summary"] for job in related],
        "limitations": "No reviewed posting" if not related else "Observed role requirements only; role availability and eligibility require employer confirmation.",
    })

learner = write(
    "LEARNER_PROFILE.json", "learner",
    profile={
        "professional_experience_years": {"minimum": 5, "maximum": 7, "evidence": "user_provided"},
        "professional_context": "User reports previous Microsoft software engineering and large-organization production experience; do not equate exposure with expertise.",
        "existing_exposure": [
            "Identity diagnostics and authentication/login debugging", "Microsoft Graph and detector migration",
            "Azure infrastructure and engineering systems", "Production debugging and on-call",
            "Backend APIs, reviews and pull requests", "Integrations, automation and messaging",
            "AI-assisted engineering tools",
        ],
        "assess_before_skipping": ["Distributed consistency", "Linux/networking depth", "Kubernetes cluster operation", "IaC ownership", "Production LLM evaluation", "MCP authorization and agent reliability"],
        "target_roles": ["Senior Software Engineer", "Cloud Engineer / Senior Cloud Engineer", "DevOps Engineer", "Platform Engineer", "AI Engineer", "Agentic AI / MCP Engineer"],
        "target_markets": ["Kenya", "international technology companies", "eligible international remote roles", "international development organizations"],
        "daily_study_minutes": {"minimum": 180, "default": 210, "maximum": 240},
        "learning_preferences": ["YouTube implementation demonstrations", "Official supplementary reading", "Hands-on local exercises", "Daily interview preparation", "GitHub-publishable projects"],
        "assessment_gate": "Use demonstrated artifacts to waive duplicated conceptual units; preserve new-context integration labs and interviews.",
        "privacy": "Self-reported profile only, no confidential employer incidents, identities, tokens, private Graph data or production artifacts in projects.",
    },
    tracks=track_list,
    active_track_configuration={"active_track_id": tr("swe"), "allow_track_switching": True, "default_plan_days": 30, "completion_storage_design": "Persist completion by canonical knowledge-unit ID plus evidence; keep plan/day progress separately."},
    recommendation={"priority_order": [t["id"] for t in track_list], "status": "retain_initial_order_with_shared_core_and_AI_overlay", "rationale": "Closest transition uses software ownership and diagnostics experience. Cloud/DevOps share infrastructure core; add evaluated AI features for differentiation after core foundations. Small biased sample cannot establish relative market demand."},
)

write(
    "EMPLOYER_RESEARCH.json", "employers", employers=employers, job_postings=jobs,
    configuration_contract={
        "operation": "Edit employer records in data, not application code; enabled=false removes from active watchlist without deleting historical job evidence.",
        "add_employer": "Append unique employer ID, name, career URL, keywords and target locations; no hardcoded company switch statements.",
        "add_job_description": "Store supplied description provenance and consent, assign job ID/source ID, code required/preferred skills with human review and update counts using documented denominator.",
        "refresh_interval_days": 14,
        "eligibility_policy": "Never infer worldwide remote eligibility from the word remote; preserve country, time-zone and onsite constraints.",
    },
)

overall_required = Counter(s for j in jobs for s in set(j["required_skill_ids"]))
overall_preferred = Counter(s for j in jobs for s in set(j["preferred_skill_ids"]))
overall_mentions = Counter(s for j in jobs for s in set(j["required_skill_ids"] + j["preferred_skill_ids"]))
skills = []
role_to_track = {"senior": "swe", "cloud": "cloud", "devops": "devops", "platform": "devops", "ai": "ai", "agent": "agent"}
for key in skill_keys:
    sid = sk(key)
    occurrences = [u for group in units.values() for u in group if u["skill"] == key]
    track_ids = sorted(
        {t for r in resources if sid in r["skill_ids"] for t in r["track_ids"]}
        | {tr(t) for t, group in units.items() if any(u["skill"] == key for u in group)}
        | {tr(role_to_track[j["primary_role_category"]]) for j in jobs if sid in j["required_skill_ids"] + j["preferred_skill_ids"]}
    )
    skills.append({
        "id": sid, "name": occurrences[0]["title"] if occurrences else key.replace("-", " ").title(),
        "track_ids": track_ids, "topic_concepts": sorted({c for u in occurrences for c in u["concepts"]}),
        "sample_required_count": overall_required[sid], "sample_preferred_count": overall_preferred[sid],
        "sample_mention_count": overall_mentions[sid],
        "sample_job_ids": [j["id"] for j in jobs if sid in j["required_skill_ids"] + j["preferred_skill_ids"]],
        "learner_leverage": "Self-reported adjacent production/identity/Azure experience; verify using a practical diagnostic." if key in ("identity", "security", "azure", "api", "incident", "observability", "messaging", "migration", "leadership") else "Competence not established by supplied profile; require new practical evidence.",
        "practice_requirement": occurrences[0]["success"] if occurrences else "Select a role-relevant bounded exercise and require reproducible evidence before claiming proficiency.",
    })

analyses = []
for track in track_list:
    role_names = track["target_role_categories"]
    sample = [j for j in jobs if j["primary_role_category"] in role_names]
    counts = Counter(s for j in sample for s in set(j["required_skill_ids"] + j["preferred_skill_ids"]))
    req = Counter(s for j in sample for s in set(j["required_skill_ids"]))
    ranked = sorted(counts, key=lambda s: (-counts[s], s))
    analyses.append({
        "track_id": track["id"], "sample_size": len(sample), "job_ids": [j["id"] for j in sample],
        "frequency_rows": [{"skill_id": s, "mention_count": counts[s], "required_count": req[s], "preferred_only_count": counts[s] - req[s], "denominator": len(sample)} for s in ranked],
        "core_skills_in_sample": [s for s in ranked if counts[s] >= 2],
        "senior_expectations": "Architecture ownership, failure analysis, security and defensible trade-offs; see individual posting scope rather than treating title/years alone as seniority.",
        "emerging_skills": [s for s in ranked if s in {sk(x) for x in ("mcp", "agents", "evaluation", "ai-security", "structured")}],
        "emerging_evidence_status": "Contemporary observed requirements, not statistically demonstrated growth.",
        "niche_skills": [s for s in ranked if counts[s] == 1],
        "niche_interpretation": "Single occurrence in this small sample does not establish market niche status; domain-specific SDK/payment/media expertise separately noted in posting summaries.",
        "declining_skills": [],
        "decline_status": "Not measurable from a one-day cross-sectional sample. Jenkins and established CI tools remain relevant where requested; no invented decline trend.",
        "overlapping_skill_ids": [s for s in track["skill_ids"] if len(next(x["track_ids"] for x in skills if x["id"] == s)) > 1],
        "leverage_skill_ids": [s for s in track["skill_ids"] if s in {sk(x) for x in ("api", "identity", "azure", "incident", "observability", "migration", "messaging")}],
        "new_practice_skill_ids": [s for s in track["skill_ids"] if s not in {sk(x) for x in ("api", "identity", "azure", "incident", "observability", "migration", "messaging")}],
        "limitations": "Purposive sample, not representative. Cloud category has only one posting; senior category includes one expired Kenyan stretch architecture role. Categories are disjoint; alternatives count as mentions, not mandatory mastery of every option.",
    })

write(
    "JOB_MARKET_SKILLS_MATRIX.json", "skills", skills=skills, track_analyses=analyses,
    methodology={
        "sample_size": len(jobs), "collection_start": DATE, "collection_end": DATE,
        "posting_date_range": "Most publication dates unavailable; one observed posting is October 26, 2026. Live descriptions are contemporary observations, not verified recently posted vacancies.",
        "sampling": "Purposive public-source discovery across six role categories; 11 employer-hosted ATS descriptions and one Kenyan secondary-board expired description.",
        "coding": "Manual required/preferred coding; aliases normalized to capabilities; each skill counted once per posting; required alternatives retained as mentions; preferred-only is mention minus required.",
        "denominator_policy": "Overall denominator is all 12 postings; track denominator is disjoint primary categories. Skill absence means not observed, not not-valued.",
        "geographic_limits": "Only one Kenyan posting, no representative development-organization sample and several country-restricted remote roles.",
        "trend_limits": "No salary, hiring-volume, growth, decline or role-demand ranking statistics inferred.",
        "refresh_policy": "Re-check candidate vacancy on application day; refresh sampled roles within 14 days and version snapshots rather than silently replacing history.",
    },
)

rankings = []
for key in skill_keys:
    candidates = [r for r in resources if sk(key) in r["skill_ids"]]
    if candidates:
        ordered = sorted(candidates, key=lambda r: (-r["overall_score"], r["id"]))
        rankings.append({
            "skill_id": sk(key), "resource_ids_in_order": [r["id"] for r in ordered],
            "interpretation": "Evidence-limited editorial shortlist, not a certified best-on-the-internet ranking. Compare documentation and videos within their instructional roles.",
        })

# Direct skill dependencies only. Track/day edges also capture sequencing.
prerequisite_map = {
    "transactions": ["database"], "cache": ["api", "database"], "idempotency": ["messaging", "transactions"],
    "scalability": ["database", "distributed"], "reranking": ["rag", "embeddings"],
    "rag": ["embeddings", "vector"], "vector": ["embeddings"], "finetuning": ["ml", "evaluation"],
    "mcp-client": ["mcp", "mcp-server"], "mcp-server": ["mcp", "tools"],
    "mcp-auth": ["mcp-transport"], "mcp-transport": ["mcp"],
    "approval": ["state", "planning"], "multi-agent": ["orchestration", "planning"],
    "helm": ["kubernetes"], "gitops": ["kubernetes", "cicd"], "cluster-recovery": ["kubernetes"],
}
skill_edges = [
    {"skill_id": sk(key), "requires_skill_ids": [sk(p) for p in values]}
    for key, values in prerequisite_map.items()
]

# Forty independently specifiable exercises/projects: eight per track.
project_seeds = {
    "swe": [
        ("exercise", "Concurrent reservation correctness", "Prevent over-reserving limited diagnostic processing capacity.", "TypeScript API -> PostgreSQL unique constraint/transaction", "TypeScript,PostgreSQL", "transactions,testing"),
        ("exercise", "Cache-stampede experiment", "Protect incident lookup storage during a cold-cache burst.", "API -> bounded single-flight cache -> data store", "TypeScript,Redis,PostgreSQL", "cache,performance"),
        ("exercise", "Outbox crash and replay", "Prevent duplicate notification effects across consumer restarts.", "Transaction/outbox -> Kafka -> idempotent consumer", "TypeScript,PostgreSQL,Kafka", "messaging,idempotency"),
        ("intermediate", "Observable modular diagnostics backend", "Operate tenant-scoped diagnostic ingestion and retrieval with measurable SLOs.", "Modular API -> relational store + async worker -> Collector", "TypeScript,PostgreSQL,Docker Compose,OpenTelemetry", "api,observability,security"),
        ("intermediate", "Notification ingestion and backpressure", "Absorb producer bursts while retaining ordering within one tenant.", "API -> partitioned event stream -> worker/outbox -> delivery stub", "TypeScript,Kafka,PostgreSQL", "messaging,reliability"),
        ("advanced", "Shard migration and failure harness", "Rebalance a skewed tenant workload without losing writes.", "Router -> simulated shard pair -> versioned routing ledger", "TypeScript,PostgreSQL,load generator", "scalability,migration,distributed"),
        ("advanced", "Resilient media-processing pipeline", "Process synthetic media jobs with bounded retries and cancellation.", "Upload metadata -> object-store stub -> queue -> workers -> result API", "TypeScript,Kafka,PostgreSQL,Docker", "concurrency,performance,reliability"),
        ("capstone", "Production-shaped identity diagnostics platform", "Build a secure observable diagnostics service with replayable incident evidence.", "Tenant API -> modular core -> PostgreSQL/outbox -> Kafka worker -> OpenTelemetry", "TypeScript,PostgreSQL,Kafka,Redis,Docker Compose,OpenTelemetry", "architecture,api,transactions,security,incident,adr,leadership"),
    ],
    "cloud": [
        ("exercise", "Cross-cloud packet-path design", "Explain and test the full route from client to private database.", "Client -> edge -> private service -> data subnet; three provider mappings", "Network model,provider architecture docs", "networking,architecture"),
        ("exercise", "Identity permission comparison", "Define minimal workload rights without long-lived embedded keys.", "Federated workload identity -> scoped resource API", "Policy fixtures,Azure/AWS/GCP documentation", "identity,security"),
        ("exercise", "Timed restore drill", "Distinguish backup completion from restored service correctness.", "Backup fixture -> isolated PostgreSQL restore -> integrity check", "PostgreSQL,Docker,Python", "disaster-recovery,database"),
        ("intermediate", "Azure-first cloud workload blueprint", "Design an API/worker/data workload using existing Azure exposure without skipping operational gaps.", "Private API/worker/data services with resource identity and observability", "Azure design,Terraform policy fixtures,local Docker simulation", "azure,identity,reliability"),
        ("intermediate", "AWS/GCP translation blueprint", "Port a workload's capabilities rather than copying service names.", "Equivalent API/queue/database categories across two providers", "AWS/GCP architecture docs,local contract harness", "aws,gcp,architecture"),
        ("advanced", "Regional disaster-recovery rehearsal", "Recover application and data with measured local drill objectives.", "Primary region model -> replicated/backup data -> alternate region model", "Docker,PostgreSQL,failure simulator", "multi-region,disaster-recovery"),
        ("advanced", "Migration and cost decision model", "Plan a reversible migration under egress and capacity constraints.", "Legacy service -> shadow path -> cutover router -> new cloud blueprint", "TypeScript traffic replay,symbolic cost worksheet", "migration,cost,adr"),
        ("capstone", "Secure cross-cloud deployment reference", "Produce an Azure implementation blueprint, AWS alternative and GCP translation with local recovery evidence.", "API/worker -> private data -> workload identity -> telemetry -> recovery environment", "Terraform local Docker,Azure/AWS/GCP design,PostgreSQL,OpenTelemetry", "architecture,identity,networking,reliability,cost,adr"),
    ],
    "devops": [
        ("exercise", "Linux/DNS outage drill", "Locate one infrastructure failure without random configuration changes.", "Lab service -> local resolver -> backend", "Linux,Bash,Docker", "linux,networking,incident"),
        ("exercise", "Hardened container build", "Create a non-root reproducible runtime image.", "Pinned multi-stage build -> minimal runtime -> integration test", "Docker,TypeScript,dependency lock", "docker,secrets"),
        ("exercise", "Kubernetes drift and recovery", "Observe reconciliation and diagnose a broken deployment.", "kind -> Deployment/Service -> GitOps desired state", "kind,kubectl,Argo CD", "kubernetes,gitops"),
        ("intermediate", "Reusable CI/CD delivery pipeline", "Promote tested immutable artifacts through explicit deployment gates.", "PR tests -> trusted build -> artifact -> approved deploy", "GitHub Actions,Azure Pipelines comparison,Docker", "cicd,azure-pipelines,secrets"),
        ("intermediate", "Observable GitOps application platform", "Reconcile application versions and measure reliability in one local cluster.", "Git desired state -> Argo CD -> Helm -> API + metrics", "kind,Argo CD,Helm,Prometheus,Grafana", "gitops,helm,monitoring"),
        ("advanced", "Platform golden path and catalog", "Give developers a supported safe service-creation workflow.", "Template -> service catalog -> reusable CI -> runtime + operational ownership", "Backstage,GitHub Actions,Helm,kind", "platform,automation,leadership"),
        ("advanced", "Cluster lifecycle and recovery toolkit", "Rehearse node drain, workload upgrade and stateful restore safely.", "Disposable cluster -> versioned IaC -> upgrade/recovery orchestrator", "kind,Terraform,Helm,Bash,PostgreSQL", "cluster-recovery,iac,incident"),
        ("capstone", "Self-service observable delivery platform", "Create a paved road for a synthetic diagnostics service with safe rollout and recovery.", "Service template -> CI/artifacts -> GitOps -> kind -> telemetry -> runbook", "GitHub Actions,Helm,Argo CD,kind,OpenTelemetry,Prometheus,Grafana,Backstage optional", "platform,cicd,gitops,secrets,observability,adr,leadership"),
    ],
    "ai": [
        ("exercise", "Retrieval ablation lab", "Measure whether chunking improves evidence retrieval.", "Synthetic runbooks -> local embeddings -> lexical/vector search -> labeled queries", "Python,local embedding model,SQLite or in-memory index", "embeddings,rag,evaluation"),
        ("exercise", "Structured output and refusal harness", "Reject malformed and semantically impossible model responses.", "Fake model -> JSON Schema -> business validator -> typed API response", "Python or TypeScript,JSON Schema", "structured,testing"),
        ("exercise", "Injection-resistant tool boundary", "Keep malicious retrieved text from authorizing external effects.", "Untrusted context -> model proposal -> policy check -> synthetic adapter", "Python,deterministic model fixtures", "ai-security,tools"),
        ("intermediate", "Evaluated runbook RAG assistant", "Answer diagnostics questions with access-scoped evidence and explicit uncertainty.", "Ingestion -> hybrid retrieval -> model adapter -> citations + validation", "Python,local embeddings,PostgreSQL or SQLite,OpenTelemetry", "rag,vector,evaluation"),
        ("intermediate", "Budgeted LLM gateway", "Provide typed responses, timeouts and controlled fallback routing.", "API -> budget/router -> provider adapter -> semantic validator", "TypeScript or Python,fake providers,local model optional", "models,structured,cost"),
        ("advanced", "Multilingual retrieval quality benchmark", "Investigate retrieval failure on realistic English and Swahili synthetic support queries.", "Labeled corpus -> multiple retrieval variants -> calibrated graders -> report", "Python,local embeddings,JSONL eval runner", "reranking,evaluation,privacy"),
        ("advanced", "Production inference optimization study", "Trade latency, memory and quality using measured local experiments.", "Task fixture -> model variants -> batching/cache -> load harness", "Python,small licensed local model,OpenTelemetry", "inference,cost,models"),
        ("capstone", "Secure evaluated diagnostics AI service", "Turn runbook retrieval into an operational API with repeatable evaluation and privacy controls.", "Tenant-scoped ingestion -> hybrid retrieval -> local/fake model -> schema/semantic gates -> traces", "Python,TypeScript API optional,local embeddings,PostgreSQL,Docker,OpenTelemetry", "production-ai,rag,evaluation,ai-security,cost,adr"),
    ],
    "agent": [
        ("exercise", "Current-protocol MCP conformance lab", "Expose validated tools without mixing old and current protocol lifecycle.", "Harness host/client -> dated MCP SDK server -> synthetic diagnostics fixture", "Python or TypeScript MCP SDK,pinned 2026-07-28 protocol,Inspector optional", "mcp,mcp-server,mcp-transport"),
        ("exercise", "Approval replay and mutation binding", "Prevent changed or expired approval from authorizing a write.", "Agent proposal -> scoped approval record -> idempotent synthetic action", "Python,SQLite,deterministic fixtures", "approval,state,security"),
        ("exercise", "Bounded looping-agent experiment", "Halt an agent that repeatedly chooses a failing tool.", "Fake model -> max-step loop -> budget/deadline -> incomplete result", "Python or TypeScript,synthetic tools", "planning,evaluation"),
        ("intermediate", "Read-only diagnostics MCP integration", "Integrate external API-shaped diagnostics with authenticated tenant-scoped access.", "MCP client -> server -> authorization layer -> fake Graph-like API", "MCP SDK,HTTP test harness,synthetic OAuth fixtures", "mcp-auth,integration,mcp-client"),
        ("intermediate", "Durable approval-gated incident workflow", "Recover safely after interruption between proposal and execution.", "Retrieve -> analyze -> approve -> effect ledger -> checkpoint", "Python,LangGraph optional,SQLite,OpenTelemetry", "state,approval,orchestration"),
        ("advanced", "Agent failure and permission evaluation", "Detect unsafe effects, memory poisoning and unreliable task trajectories.", "Adversarial fixtures -> agent -> policy boundary -> trajectory grader", "Python,JSONL suite,MCP server,fake model", "ai-security,evaluation,memory"),
        ("advanced", "Single-versus-multi-agent architecture experiment", "Determine whether planner/reviewer collaboration improves a defined task.", "Task queue -> single baseline or planner/reviewer graph -> shared validated result", "Python,LangGraph optional,model fixtures and optional local inference", "multi-agent,orchestration,evaluation"),
        ("capstone", "Approval-gated MCP incident engineering assistant", "Retrieve synthetic incident context and propose bounded actions without uncontrolled production access.", "Host/client -> authenticated MCP server -> scoped tools/resources -> durable agent -> approval/effect ledger -> audit", "MCP SDK,Python or TypeScript,SQLite,OpenTelemetry,Docker,local/fake model", "mcp,agent-deployment,approval,ai-security,observability,adr"),
    ],
}
projects = []
for track, seeds in project_seeds.items():
    for index, (level, title, problem, architecture, technologies, skill_text) in enumerate(seeds, 1):
        pid = "project-" + track + "-" + str(index).zfill(2)
        milestones = [
            {"id": pid + "-m1", "title": "Contract and threat boundaries", "deliverables": ["Requirements, synthetic fixtures and architecture diagram", "Threat model and baseline acceptance tests"], "estimated_hours": 2},
            {"id": pid + "-m2", "title": "Thin vertical slice", "deliverables": ["Smallest running local flow implementing the problem", "One success and one failure test"], "estimated_hours": 3},
        ]
        if level != "exercise":
            milestones += [
                {"id": pid + "-m3", "title": "Reliability and integration", "deliverables": ["Timeout/idempotency or recovery tests", "Cross-boundary contract and diagnostic evidence"], "estimated_hours": 5},
                {"id": pid + "-m4", "title": "Operational and security hardening", "deliverables": ["Access-denial tests, redacted telemetry and cleanup procedure", "Deployment/recovery runbook and repeatable measurements"], "estimated_hours": 5},
                {"id": pid + "-m5", "title": "Architecture defense", "deliverables": ["ADR with rejected alternatives and remaining gaps", "Recorded demonstration and interview walkthrough"], "estimated_hours": 3},
            ]
        if level in ("advanced", "capstone"):
            milestones += [
                {"id": pid + "-m6", "title": "Measured fault experiment", "deliverables": ["Controlled local failure with baseline and changed results", "Postmortem and evidence of safe recovery"], "estimated_hours": 7},
                {"id": pid + "-m7", "title": "Portfolio evidence and review", "deliverables": ["Fresh-clone reproducibility check", "Limitations and scaling assumptions with no invented production outcomes"], "estimated_hours": 5},
            ]
        projects.append({
            "id": pid, "track_ids": [tr(track)], "level": level, "title": title,
            "problem_statement": problem, "architecture": architecture,
            "technologies": split(technologies), "skill_ids": [sk(x) for x in split(skill_text)],
            "engineering_requirements": [
                "Use synthetic data with explicit API/tool or infrastructure contracts.",
                "Implement the named architecture in a disposable local environment; cloud-track blueprints are explicitly designs, not proof of a real provider deployment.",
                "Bound timeouts, concurrency and side effects; expose meaningful failure outcomes.",
                "Document the problem-specific invariant and validate it using reproducible tests.",
            ],
            "acceptance_criteria": [
                "A reviewer can run the vertical slice from a fresh clone using documented prerequisites.",
                "Success, invalid input and dependency failure cases produce expected results.",
                "Cross-tenant or unauthorized operations fail before protected effects occur where applicable.",
                "A baseline/failure/recovery report states actual dataset, environment and observed result rather than claiming production scale.",
            ],
            "milestones": milestones, "estimated_hours": sum(m["estimated_hours"] for m in milestones),
            "testing_strategy": ["Unit tests for domain decisions", "Integration contracts across real local storage/runtime boundaries", "Deterministic timeout, retry and unauthorized-access fixtures", "One load or fault experiment appropriate to the problem, with evidence"],
            "security_considerations": ["No employer data, credentials or private incident material", "Least-privilege identity and resource access", "Validate untrusted inputs and redact logs", "Approval for destructive or externally mutating actions; local-only fixtures by default"],
            "deployment_requirements": ["Local reproducible deployment is required", "Pin tool and image versions when implementation begins and record them", "Scoped teardown and backup/recovery instructions", "Optional cloud deployment requires explicit learner opt-in and refreshed pricing; never assume free-tier coverage"],
            "github_deliverables": ["README with architecture and runnable commands", "Source/configuration and dependency locks", "Tests and synthetic fixtures", "ADRs, threat model and runbooks", "Measured results and a short demonstration recording reference"],
            "interview_discussion_points": [problem, "Defend one rejected alternative", "Explain one measured failure and mitigation", "State what remains unproven in the local lab"],
            "resource_ids": sorted({rs(u["doc"]) for u in units[track] if u["skill"] in split(skill_text)}),
            "cross_track_extensions": {
                "swe": "Deploy via the DevOps paved road, then add an evaluated read-only AI assistant.",
                "cloud": "Use the software API and DevOps pipeline as the workload; test provider-specific identities only in an opted-in paid/approved sandbox.",
                "devops": "Deploy the software diagnostics API and expose operational context to a read-only MCP server.",
                "ai": "Run behind the secure software API and delivery platform; expose retrieval as a permissioned MCP tool.",
                "agent": "Use the AI retrieval evaluator and software idempotency ledger; deploy through the DevOps platform.",
            }[track],
            "curriculum_scope_note": "14-day plans produce a portfolio candidate thin slice, not this complete specification. 30-day plans integrate core behavior. 60-day plans deepen measured operations; further implementation hours may be needed.",
        })
write("PRACTICAL_PROJECTS.json", "projects", projects=projects)

questions = []
question_map = {}
for track, group in units.items():
    for index, unit in enumerate(group, 1):
        ids = []
        formulations = [
            ("foundational", "conceptual", unit["question"], unit["reasoning"]),
            ("intermediate", "implementation_design",
             "Design a bounded implementation for this task: " + unit["lab"] + ". Explain the invariant and verification strategy.",
             unit["reasoning"] + " Start with the smallest explicit contract, implement the invariant, then test a failure at the boundary. Required evidence: " + unit["success"] + "."),
            ("senior", "production_debugging",
             "During a rollout of " + unit["title"] + ", baseline tests passed but real requests now fail intermittently. Which hypotheses, evidence and safe mitigation would you prioritize?",
             "First establish user impact and rollback/mitigation safety. Compare the last-known-good version, " + ", ".join(unit["concepts"]) + ", and dependency behavior. " + unit["reasoning"] + " Reproduce a bounded failure and verify recovery using: " + unit["success"] + ". Avoid random changes or unjustified certainty."),
        ]
        for difficulty, category, question, explanation in formulations:
            qid = f"question-{track}-{index:02d}-{category.replace('_', '-')}"
            ids.append(qid)
            questions.append({
                "id": qid, "track_id": tr(track), "skill_ids": [sk(unit["skill"])],
                "difficulty": difficulty, "category": category, "question": question,
                "expected_answer_elements": unit["concepts"] + [unit["reasoning"], "Explicit invariant, alternative and reproducible evidence"],
                "detailed_explanation": explanation,
                "follow_up_questions": [
                    "Which assumption would change your decision, and how would you measure it?",
                    "What happens on retry, unauthorized access or partial completion in your proposed design?",
                    "How would you validate this locally without claiming unmeasured production behavior?",
                ],
                "evaluation_rubric": [
                    {"criterion": "Technical reasoning and named concepts", "max_points": 4, "full_credit": unit["reasoning"]},
                    {"criterion": "Invariant, evidence and validation", "max_points": 3, "full_credit": unit["success"]},
                    {"criterion": "Alternatives, failure behavior and communication", "max_points": 3, "full_credit": "Defends a rejected alternative, acknowledges uncertainty and proposes safe operational action."},
                ],
                "common_mistakes": ["Tool-name recitation without explaining " + unit["concepts"][0], "Claiming success without " + unit["success"], "Ignoring identity, failure or operational costs", "Presenting assumptions as observed production facts"],
                "source_ids": ["source-doc-" + unit["doc"]],
                "authorship": "Original curriculum question; not an alleged leaked employer interview question.",
            })
        question_map[(track, unit["skill"])] = ids

coding_tasks = {
    "swe": [
        ("Implement a bounded async work queue with cancellation.", "Use a semaphore/work-queue contract; release permits in finally paths; propagate cancellation and test concurrency bounds.", "A failed task leaks no permit; cancellation does not hang pending work."),
        ("Implement an idempotent event handler using a transactional deduplication ledger.", "Persist effect and event identity atomically, handle retries and define retention/unknown completion behavior.", "Concurrent duplicate events produce one logical effect in a real local database."),
    ],
    "cloud": [
        ("Implement a symbolic RTO/RPO validation tool for a recovery timeline.", "Validate event ordering, distinguish observation versus assumptions and report missing evidence.", "Malformed or incomplete timelines never become a recovery guarantee."),
        ("Implement a policy-fixture checker that rejects overbroad cloud workload permissions.", "Parse explicit fixtures, fail closed on unknown policy semantics and avoid asserting equivalence across providers.", "Allow/deny fixtures and unknown-policy cases return distinct results."),
    ],
    "devops": [
        ("Write an idempotent Bash inventory/health-check script with a deadline.", "Quote inputs, preserve exit status, bound retries, separate read-only discovery from mutation.", "Missing binary, unhealthy endpoint and repeated runs are covered."),
        ("Implement a release promotion decision using error-rate and latency fixtures.", "Compare valid windows, require enough observations, bound thresholds and retain rollback compatibility.", "A regression and insufficient-sample case block promotion."),
    ],
    "ai": [
        ("Implement recall@k evaluation for labeled retrieval query fixtures.", "Deduplicate result IDs, respect k and denominators, handle missing labels and report per-query failures.", "Repeated IDs cannot inflate recall; missing labels are unavailable, not zero."),
        ("Implement structured model response validation with refusal and timeout cases.", "Separate parsing/schema/domain validation, preserve explicit refusal/incomplete states and fail closed.", "Valid JSON with invalid business values fails independently of schema success."),
    ],
    "agent": [
        ("Implement an approval-gated idempotent tool execution ledger.", "Bind actor/resource/action/parameters/expiry, record completion atomically where possible and treat ambiguous completion safely.", "Changed arguments, expired approval and concurrent replay never authorize extra effects."),
        ("Implement a bounded agent loop with durable checkpoint fixtures.", "Define max steps, deadline, checkpoint and safe resume; isolate proposals from authorized execution.", "Repeated failing tools stop; recovered work does not duplicate a mutation."),
    ],
}
for track in units:
    for index, (question, reasoning, success) in enumerate(coding_tasks[track], 1):
        questions.append({
            "id": f"question-{track}-coding-{index}", "track_id": tr(track),
            "skill_ids": [sk(units[track][0]["skill"])], "difficulty": "advanced", "category": "coding",
            "question": question, "expected_answer_elements": [reasoning, success],
            "detailed_explanation": reasoning + " Prefer clear typed contracts and a small number of meaningful tests. " + success,
            "follow_up_questions": ["How does concurrency change correctness?", "What do you persist after partial failure?", "How do you test without unreliable live services?"],
            "evaluation_rubric": [{"criterion": "Correctness", "max_points": 5, "full_credit": success}, {"criterion": "Tests and edge cases", "max_points": 3, "full_credit": "Includes deterministic failures and boundaries."}, {"criterion": "Clarity and trade-offs", "max_points": 2, "full_credit": reasoning}],
            "common_mistakes": ["Happy-path-only implementation", "Unbounded retries or leaked resources", "Hidden assumptions about external effects"],
            "source_ids": [], "authorship": "Original practical exercise.",
        })
    for category, question in [
        ("behavioral", "Describe an anonymized production incident you helped resolve. What did you personally do, what changed and what remains uncertain?"),
        ("leadership", "A team rejects your architecture proposal. How do you establish shared goals, gather evidence, make a decision and preserve trust?"),
        ("senior_architecture", "Defend the track capstone under a tenfold traffic increase, a reduced operating budget and a dependency outage. Which decisions change first?"),
    ]:
        questions.append({
            "id": f"question-{track}-{category.replace('_', '-')}", "track_id": tr(track),
            "skill_ids": [sk("leadership") if category != "senior_architecture" else sk("adr")],
            "difficulty": "senior", "category": category, "question": question,
            "expected_answer_elements": ["Clear situation and own contribution", "Evidence, alternatives and trade-offs", "Stakeholder communication", "Measured outcome or explicit lack of measurement"],
            "detailed_explanation": "Evaluate structured judgment rather than rehearsed jargon. Separate personal action from team results, protect confidential details, explain rejected alternatives and show how new evidence changed the decision. Honest limitations are stronger than invented impact statistics.",
            "follow_up_questions": ["What would you do differently?", "Who disagreed and why?", "How did you know the intervention helped?"],
            "evaluation_rubric": [{"criterion": "Ownership and evidence", "max_points": 4, "full_credit": "Specific own actions, evidence and honest outcomes."}, {"criterion": "Judgment and trade-offs", "max_points": 4, "full_credit": "Explains alternatives and risk-sensitive decisions."}, {"criterion": "Communication", "max_points": 2, "full_credit": "Clear, collaborative and confidential-data-safe."}],
            "common_mistakes": ["Invented metrics or attribution", "Blaming individuals", "No evidence or alternative", "Disclosing employer-confidential incident details"],
            "source_ids": [], "authorship": "Original scenario, not an employer question.",
        })

mock_interviews = []
for track in units:
    cap = next(p for p in projects if p["id"] == "project-" + track + "-08")
    mock_interviews.append({
        "id": "mock-" + track + "-design", "track_id": tr(track), "duration_minutes": 60,
        "scenario": cap["problem_statement"],
        "stages": [{"minutes": 10, "task": "Clarify requirements, invariants and target load"}, {"minutes": 20, "task": "Design the architecture and defend one alternative"}, {"minutes": 15, "task": "Introduce dependency failure and permission constraints"}, {"minutes": 10, "task": "Specify validation, observability and rollback"}, {"minutes": 5, "task": "Summarize assumptions and remaining risks"}],
        "question_ids": [q["id"] for q in questions if q["track_id"] == tr(track) and q["category"] == "senior_architecture"],
        "rubric": "40% judgment/invariants, 30% failure/security analysis, 20% validation, 10% communication; these are authored interview scoring weights, not market statistics.",
    })
    mock_interviews.append({
        "id": "mock-" + track + "-debug", "track_id": tr(track), "duration_minutes": 60,
        "scenario": "A capstone rollout passes unit tests but fails intermittently. Synthetic telemetry and one faulty dependency are supplied; produce mitigation and a tested patch plan.",
        "stages": [{"minutes": 10, "task": "Establish impact and safe mitigation"}, {"minutes": 15, "task": "Generate ranked hypotheses from traces/logs"}, {"minutes": 20, "task": "Implement or sketch the smallest fix with regression test"}, {"minutes": 10, "task": "Re-run failure and recovery checks"}, {"minutes": 5, "task": "Communicate outcome and postmortem actions"}],
        "question_ids": [q["id"] for q in questions if q["track_id"] == tr(track) and q["category"] == "coding"],
        "rubric": "40% diagnostic evidence, 30% correctness, 20% safe operations, 10% communication; authored rubric.",
    })
write("INTERVIEW_QUESTION_BANK.json", "questions", questions=questions, mock_interviews=mock_interviews)

plans = {}
lesson_edges = []
core14 = {
    "swe": [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13],
    "cloud": [0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13],
    "devops": [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 14],
    "ai": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12],
    "agent": [0, 1, 2, 3, 6, 7, 8, 9, 11, 12, 15, 16],
}
stage_names = ["Frame and implement", "Extend and compare", "Fault drill and defend"]
stage_actions = [
    "Implement only the named bounded lab; stop when the stated evidence exists.",
    "Extend the previous local slice with one contrasting configuration or alternative. Keep the original fixture as a baseline and compare behavior.",
    "Inject one invalid-input, timeout, concurrent-replay or denied-access fixture relevant to the named invariant. Reproduce, mitigate and document recovery.",
]
resource_lookup = {r["id"]: r for r in resources}
milestone_titles = [
    "Integrate the smallest capstone flow", "Validate contracts and tenant boundaries",
    "Add safe timeout and replay behavior", "Measure telemetry and one failure",
    "Rehearse recovery and write the ADR", "Publish reproducible portfolio evidence",
]
milestones_by_plan = {
    14: ["Assemble one thin vertical slice", "Publish the slice with tests, limitations and architecture defense"],
    30: [
        "Define integrated acceptance fixtures", "Connect API or protocol contracts",
        "Connect persistence and state boundaries", "Enforce tenant and action permissions",
        "Add bounded retries and safe failure responses", "Instrument traces and structured logs",
        "Run a controlled load or evaluation experiment", "Rehearse recovery and rollback",
        "Write the ADR and conduct a mock architecture review", "Publish reproducible portfolio evidence",
    ],
    60: milestone_titles,
}
for days in (14, 30, 60):
    curricula = []
    for track, group in units.items():
        if days == 14:
            schedule = [(group[i], 0, False) for i in core14[track]] + [(group[-2], 0, True), (group[-1], 2, True)]
        elif days == 30:
            schedule = [(u, 0, False) for u in group] + [(group[10 + i], 1 if i < 6 else 2, True) for i in range(10)]
        else:
            schedule = [(u, phase, False) for u in group[:18] for phase in range(3)] + [(group[18 + i // 3], i % 3, True) for i in range(6)]
        lessons = []
        cap_id = "project-" + track + "-08"
        prior = None
        seen_skills = set()
        for day, (unit, phase, capstone) in enumerate(schedule, 1):
            lid = f"lesson-{track}-{days}-{day:02d}"
            video = resource_lookup[rs(unit["video"])]
            specific_prereqs = [sk(p) for p in prerequisite_map.get(unit["skill"], []) if sk(p) in seen_skills]
            reading_ids = [rs(unit["doc"])]
            if track == "agent" and rs("mcp-spec") not in reading_ids:
                reading_ids.append(rs("mcp-spec"))
            if track == "ai" and unit["skill"] == "evaluation":
                reading_ids = [rs("hf-evaluate")]
            cap_index = max(0, day - (len(schedule) - (2 if days == 14 else 10 if days == 30 else 6)) - 1)
            milestone_title = milestones_by_plan[days][min(cap_index, len(milestones_by_plan[days]) - 1)]
            topic = (milestone_title + ": " + unit["title"]) if capstone else unit["title"] + " - " + stage_names[phase]
            chosen_concepts = ", ".join(unit["concepts"])
            implementation = unit["lab"] + ". " + stage_actions[phase]
            if capstone:
                implementation = "Integrate existing track lab artifacts into " + cap_id + ". " + milestone_title + ". Limit today's change to one contract or operational boundary; retain all prior passing fixtures. Apply " + chosen_concepts + "."
            qids = question_map[(track, unit["skill"])]
            daily = {
                "id": lid, "day": day, "track_id": tr(track), "topic": topic,
                "knowledge_unit_id": "knowledge-" + unit["skill"],
                "skill_ids": [sk(unit["skill"])],
                "learning_objectives": [
                    "Explain " + chosen_concepts + " in the context of the diagnostics capstone.",
                    "Produce this bounded evidence: " + unit["success"] + ".",
                    "Defend the decision: " + unit["question"],
                ],
                "why_it_matters": unit["reasoning"] + " Employers in the source sample emphasize practical ownership rather than course completion; this lesson produces evidence of judgment.",
                "prerequisites": {
                    "lesson_ids": [prior] if prior else [],
                    "skill_ids": specific_prereqs,
                    "baseline_knowledge": ["Working programming experience, Git and basic API/test usage", "A disposable local lab with synthetic data"],
                    "knowledge_to_check": unit["concepts"],
                    "gap_policy": "If a prerequisite concept is not demonstrated, use the current reading or prerequisite-repair video within the budget; carry unfinished work forward rather than silently expanding study time.",
                },
                "recommended_youtube_resource_id": video["id"],
                "video_duration_minutes": video["duration_minutes"],
                "planned_video_minutes": 35,
                "video_selection": {
                    "selection_method": "Choose a relevant publisher-labeled chapter by this lesson's focus; watch up to the 35-minute budget, not the entire course.",
                    "focus": chosen_concepts,
                    "verified_timestamp_seconds": None,
                    "timestamp_status": "No lesson-specific start/end verified; resource-level observed chapter labels are available separately where retrieved.",
                    "coverage_limit": "Related instructional orientation; dedicated coverage of every advanced subtopic not verified. Official reading and original lab carry the lesson when the video lacks depth.",
                },
                "supplementary_reading_resource_ids": reading_ids,
                "reading_focus": "Find the section addressing " + chosen_concepts + "; compare the documented contract with the video and note version-sensitive differences.",
                "practical_implementation_exercise": implementation,
                "interview_question_ids": qids[:1] + ([f"question-{track}-coding-1"] if day % 5 == 0 else [qids[2]]),
                "revision_exercise": "Without notes, redraw today's boundary and explain " + unit["concepts"][0] + ". Re-run one earlier contract/failure fixture and record any changed assumption.",
                "study_guide": {
                    "before_video": [
                        "Recall " + unit["concepts"][0] + " from practical experience; distinguish what you observed from what you only assume.",
                        "Predict the behavior of this lab before watching: " + unit["lab"] + ".",
                        "Look for the invariant, trust boundary and trade-off behind " + unit["title"] + "; do not transcribe commands blindly.",
                    ],
                    "during_video": [
                        "Capture a diagram linking " + chosen_concepts + " to the capstone's data or control flow.",
                        "Write one assumption and one failure mode alongside any demonstrated code or configuration.",
                        "Stop at 35 minutes. Cross-check current SDK/provider behavior in the reading; public chapter markers are not proof the demonstration still runs.",
                    ],
                    "after_video": {
                        "comprehension_questions": [unit["question"], "Which failure would violate the invariant in your implementation?", "Which observed result would cause you to choose a different architecture?"],
                        "practice": implementation,
                        "validate_understanding": [unit["success"], "Explain why the rejected alternative is less suitable under today's assumptions.", "Make one deliberately wrong change and confirm an appropriate test catches it; restore the valid implementation."],
                    },
                },
                "time_budget_minutes": {"preparation": 10, "video": 35, "reading": 25, "implementation": 100, "interview": 20, "revision": 20},
                "estimated_total_study_minutes": 210,
                "expected_outcome": unit["success"] + "; capstone integration checkpoint." if capstone else unit["success"],
                "completion_criteria": [unit["success"], "Passing success and relevant failure checks are recorded.", "Answer the two interview questions using trade-offs and evidence, not memorized definitions.", "Record sources, assumptions and a small GitHub-ready artifact; no private data."],
                "project_id": cap_id,
                "phase": "capstone_integration" if capstone else ("concept_and_slice", "comparative_implementation", "failure_and_revision")[phase],
                "assessment_status": "authored_plan_not_learner_executed",
            }
            lessons.append(daily)
            lesson_edges.append({"lesson_id": lid, "requires_lesson_ids": [prior] if prior else []})
            seen_skills.add(sk(unit["skill"]))
            prior = lid
        curricula.append({
            "id": f"curriculum-{track}-{days}", "track_id": tr(track), "duration_days": days,
            "daily_minutes": 210, "total_hours": days * 3.5,
            "scope": {14: "Intensive diagnostic and thin vertical slice; not mastery of the whole discipline.", 30: "All core units plus integrated project; not a guarantee of job readiness.", 60: "Repeated implementation/failure practice plus portfolio integration; advanced specification may still require additional work."}[days],
            "deliverable_project_id": cap_id,
            "capstone_completion_level": {14: "thin_slice", 30: "integrated_prototype", 60: "production_shaped_local_portfolio_candidate"}[days],
            "adjustment_policy": {
                "180_minutes": "Reduce optional video to 20 minutes and reading to 10; retain 100-minute implementation, interview and revision.",
                "240_minutes": "Add 30 minutes of implementation or remediation, not extra passive watching.",
                "unfinished_work": "Carry forward at a checkpoint or extend calendar; no hidden expectation of production deployment in one study day.",
                "waiver": "Waive demonstrated identical conceptual knowledge only; do not waive new-context failure, security or integration work.",
            },
            "lessons": lessons,
        })
    plans[days] = write(f"CURRICULUM_{days}_DAYS.json", "curricula", plan_days=days, curricula=curricula)

for plan in plans.values():
    for curriculum in plan["curricula"]:
        for lesson in curriculum["lessons"]:
            for resource_id in [lesson["recommended_youtube_resource_id"]] + lesson["supplementary_reading_resource_ids"]:
                referenced = resource_lookup[resource_id]
                referenced["track_ids"] = sorted(set(referenced["track_ids"]) | {curriculum["track_id"]})
write("RESOURCE_CATALOG.json", "resources", resources=resources, topic_rankings=rankings)

write(
    "LEARNING_DEPENDENCIES.json", "dependencies",
    skill_dependencies=skill_edges, lesson_dependencies=lesson_edges,
    sequencing_policy="Within each selected plan, explicit prior-day artifacts are prerequisites; skill DAG expresses selected direct conceptual prerequisites, not all knowledge required for every career.",
    external_prerequisites=["Professional programming, Git, typed API and tests", "Local container/Linux environment if required", "Python bridge unit before AI data/model implementation"],
    reentry_policy="On switching tracks or plans, assess canonical knowledge units and carry relevant artifacts; re-run context-specific access/failure tests.",
)

knowledge_units = []
for key in skill_keys:
    related = [l for p in plans.values() for c in p["curricula"] for l in c["lessons"] if l["knowledge_unit_id"] == "knowledge-" + key]
    if related:
        knowledge_units.append({
            "id": "knowledge-" + key, "skill_id": sk(key),
            "track_ids": sorted({l["track_id"] for l in related}),
            "canonical_lesson_id": related[0]["id"],
            "lesson_ids": [l["id"] for l in related],
            "waiver_criteria": "Learner explains the invariant/trade-off and supplies a passing relevant artifact; course attendance alone does not waive knowledge.",
            "reuse_boundary": "Reuse concept assessment and existing equivalent artifacts; new provider, security or failure-context exercises remain required.",
        })
write(
    "SHARED_KNOWLEDGE_MAP.json", "shared", knowledge_units=knowledge_units,
    shared_core_priority=["skill-api", "skill-networking", "skill-security", "skill-observability", "skill-reliability", "skill-database", "skill-cicd"],
    equivalence_policy="Completion is keyed to knowledge ID plus evidence scope. Resource and skill metadata live only in their catalogs; track-specific applied work is not automatically identical.",
    provider_comparison=[
        {"concept": "Resource hierarchy and IAM", "azure": "Tenant/subscription/resource scopes and Entra/workload identity", "aws": "Organization/account/resource scopes and IAM role/policy design", "gcp": "Organization/folder/project/resource scopes and service accounts", "transfer": "Least privilege and federation transfer; effective permission evaluation must be verified separately", "source_ids": ["source-doc-azure-waf", "source-doc-aws-waf", "source-doc-gcp-waf"]},
        {"concept": "Networking", "azure": "VNet/subnet and provider-specific routing/private endpoint design", "aws": "VPC/subnet and provider-specific routing/endpoint design", "gcp": "VPC/subnet and provider-specific scope/routing design", "transfer": "DNS, packet paths, address planning and trust boundaries transfer; scope/defaults do not", "source_ids": ["source-doc-azure-architecture", "source-doc-aws-waf", "source-doc-gcp-waf"]},
        {"concept": "Resilience, data and cost", "azure": "WAF pillars and workload requirements", "aws": "Well-Architected questions and service-specific behavior", "gcp": "Well-Architected pillars and workload perspectives", "transfer": "SLIs/RTO/RPO, recovery tests and unit economics transfer; price, quotas, SLAs and service behavior require fresh verification", "source_ids": ["source-doc-azure-waf", "source-doc-aws-waf", "source-doc-gcp-waf"]},
    ],
)
url_report_path = ROOT / "URL_CHECK_RESULTS.json"
if url_report_path.exists():
    url_report = json.loads(url_report_path.read_text(encoding="utf-8"))
    prior_checks = {entry["entity_id"]: entry for entry in url_report["results"]}
    for entry in sources:
        if entry["id"] in prior_checks:
            checked = prior_checks[entry["id"]]
            entry["http_status"] = checked["http_status"]
            entry["final_url"] = checked["final_url"]
            entry["url_last_checked_at"] = url_report["checked_at"][:10]
write(
    "SOURCE_REGISTER.json", "sources", sources=sources,
    verification_policy="Content checks are only those recorded in method/content_status. URL checks are separate network observations, not proof a job is live or an entire course/lab is free or correct.",
)
print(f"Materialized {len(resources)} resources, {len(jobs)} postings, {len(skills)} skills, {sum(len(c['lessons']) for p in plans.values() for c in p['curricula'])} study days, {len(projects)} projects and {len(questions)} questions.")

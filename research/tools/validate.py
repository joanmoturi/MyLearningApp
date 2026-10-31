"""Validate structure and research-specific referential/coverage constraints."""

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = [
    "LEARNER_PROFILE.json", "JOB_MARKET_SKILLS_MATRIX.json", "EMPLOYER_RESEARCH.json",
    "RESOURCE_CATALOG.json", "CURRICULUM_14_DAYS.json", "CURRICULUM_30_DAYS.json",
    "CURRICULUM_60_DAYS.json", "PRACTICAL_PROJECTS.json", "INTERVIEW_QUESTION_BANK.json",
    "LEARNING_DEPENDENCIES.json", "SHARED_KNOWLEDGE_MAP.json", "SOURCE_REGISTER.json",
]


def validate(root=ROOT):
    problems = []
    docs = {name: json.loads((root / name).read_text(encoding="utf-8")) for name in DATA_FILES}
    schema = json.loads((root / "schemas" / "package.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for name, doc in docs.items():
        for error in validator.iter_errors(doc):
            problems.append(f"{name}: {list(error.path)}: {error.message[:300]}")
    tracks = docs["LEARNER_PROFILE.json"]["tracks"]
    resources = docs["RESOURCE_CATALOG.json"]["resources"]
    skills = docs["JOB_MARKET_SKILLS_MATRIX.json"]["skills"]
    employers = docs["EMPLOYER_RESEARCH.json"]["employers"]
    jobs = docs["EMPLOYER_RESEARCH.json"]["job_postings"]
    projects = docs["PRACTICAL_PROJECTS.json"]["projects"]
    questions = docs["INTERVIEW_QUESTION_BANK.json"]["questions"]
    sources = docs["SOURCE_REGISTER.json"]["sources"]
    knowledge = docs["SHARED_KNOWLEDGE_MAP.json"]["knowledge_units"]
    curricula = [c for d in (14, 30, 60) for c in docs[f"CURRICULUM_{d}_DAYS.json"]["curricula"]]
    lessons = [l for c in curricula for l in c["lessons"]]
    registries = {
        "track": tracks, "resource": resources, "skill": skills, "employer": employers,
        "job": jobs, "project": projects, "question": questions, "source": sources,
        "knowledge": knowledge, "lesson": lessons,
    }
    ids = {kind: {entry["id"] for entry in entries} for kind, entries in registries.items()}
    for kind, entries in registries.items():
        if len(ids[kind]) != len(entries):
            problems.append("Duplicate " + kind + " IDs")
    references = {
        "track_id": "track", "track_ids": "track", "active_track_id": "track", "priority_order": "track",
        "skill_id": "skill", "skill_ids": "skill", "requires_skill_ids": "skill",
        "core_skills_in_sample": "skill", "emerging_skills": "skill", "niche_skills": "skill",
        "declining_skills": "skill", "overlapping_skill_ids": "skill", "leverage_skill_ids": "skill",
        "new_practice_skill_ids": "skill", "required_skill_ids": "skill", "preferred_skill_ids": "skill",
        "shared_core_priority": "skill", "employer_id": "employer",
        "job_ids": "job", "sample_job_ids": "job", "project_id": "project", "deliverable_project_id": "project",
        "question_ids": "question", "interview_question_ids": "question", "source_id": "source",
        "source_ids": "source", "verification_sources": "source", "resource_ids": "resource",
        "resource_ids_in_order": "resource", "recommended_youtube_resource_id": "resource",
        "supplementary_reading_resource_ids": "resource", "knowledge_unit_id": "knowledge",
        "lesson_id": "lesson", "lesson_ids": "lesson", "requires_lesson_ids": "lesson", "canonical_lesson_id": "lesson",
    }

    def walk(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in references:
                    for ref in child if isinstance(child, list) else [child]:
                        if ref not in ids[references[key]]:
                            problems.append(f"Unresolved {path}.{key}: {ref}")
                walk(child, path + "." + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + f"[{index}]")
    for name, doc in docs.items():
        walk(doc, name)

    resource_map = {r["id"]: r for r in resources}
    for r in resources:
        if r["free_status"] not in ("fully_free", "free_documentation"):
            problems.append("Non-free or conditional core resource: " + r["id"])
        if not r["verification_sources"] or not r["free_evidence"]:
            problems.append("Missing resource provenance: " + r["id"])
        actual_score = sum(v for v in r["score_breakdown"].values() if v is not None)
        if r["overall_score"] != actual_score or r["score_upper_bound"] < actual_score:
            problems.append("Score mismatch: " + r["id"])
        if r["score_breakdown"]["community_feedback"] is not None and r["comment_count"] is None:
            problems.append("Unsupported community score: " + r["id"])
        if r["published_at"] is None and r["score_breakdown"]["recency"] is not None:
            problems.append("Unsupported recency score: " + r["id"])
        if r["last_verified_at"] > docs["RESOURCE_CATALOG.json"]["research_date"]:
            problems.append("Future verification: " + r["id"])
    if len({r["url"] for r in resources}) != len(resources):
        problems.append("Duplicate core resource URL")

    dependencies = {e["skill_id"]: e["requires_skill_ids"] for e in docs["LEARNING_DEPENDENCIES.json"]["skill_dependencies"]}
    for c in curricula:
        if len(c["lessons"]) != c["duration_days"] or [l["day"] for l in c["lessons"]] != list(range(1, c["duration_days"] + 1)):
            problems.append("Wrong day count/order: " + c["id"])
        if c["total_hours"] != c["duration_days"] * c["daily_minutes"] / 60:
            problems.append("Wrong curriculum hours: " + c["id"])
        all_plan_skills = {s for l in c["lessons"] for s in l["skill_ids"]}
        seen_lessons, seen_skills = set(), set()
        for lesson in c["lessons"]:
            if sum(lesson["time_budget_minutes"].values()) != lesson["estimated_total_study_minutes"]:
                problems.append("Time sum mismatch: " + lesson["id"])
            if lesson["estimated_total_study_minutes"] != 210:
                problems.append("Daily default mismatch: " + lesson["id"])
            if lesson["time_budget_minutes"]["implementation"] < 90:
                problems.append("Insufficient practical time: " + lesson["id"])
            if not set(lesson["prerequisites"]["lesson_ids"]) <= seen_lessons:
                problems.append("Out-of-order lesson prerequisite: " + lesson["id"])
            if not set(lesson["prerequisites"]["skill_ids"]) <= seen_skills:
                problems.append("Out-of-order declared skill prerequisite: " + lesson["id"])
            for s in lesson["skill_ids"]:
                missing = (set(dependencies.get(s, [])) & all_plan_skills) - seen_skills
                if missing and s not in seen_skills:
                    problems.append(f"Missing conceptual prerequisite for {lesson['id']}: {sorted(missing)}")
            selected_resource = resource_map.get(lesson["recommended_youtube_resource_id"])
            if selected_resource is not None and selected_resource["resource_type"] != "youtube_video":
                problems.append("Lesson video is not YouTube: " + lesson["id"])
            for resource_id in [lesson["recommended_youtube_resource_id"]] + lesson["supplementary_reading_resource_ids"]:
                referenced = resource_map.get(resource_id)
                if referenced is not None and c["track_id"] not in referenced["track_ids"]:
                    problems.append("Resource missing associated track: " + resource_id)
            if not lesson["interview_question_ids"] or not lesson["completion_criteria"] or not lesson["study_guide"]["after_video"]["comprehension_questions"]:
                problems.append("Incomplete lesson: " + lesson["id"])
            seen_lessons.add(lesson["id"])
            seen_skills.update(lesson["skill_ids"])
        if c["lessons"][-1]["phase"] != "capstone_integration" or "Publish" not in c["lessons"][-1]["topic"]:
            problems.append("Final day does not publish deliverable: " + c["id"])
    for track in ids["track"]:
        counts = Counter(p["level"] for p in projects if track in p["track_ids"])
        for level, minimum in {"exercise": 3, "intermediate": 2, "advanced": 2, "capstone": 1}.items():
            if counts[level] < minimum:
                problems.append(f"Insufficient {level} projects for {track}")
        cats = {q["category"] for q in questions if q["track_id"] == track}
        if not {"conceptual", "implementation_design", "production_debugging", "coding", "behavioral", "leadership", "senior_architecture"} <= cats:
            problems.append("Insufficient question coverage: " + track)
    for p in projects:
        if p["estimated_hours"] != sum(m["estimated_hours"] for m in p["milestones"]):
            problems.append("Project hour mismatch: " + p["id"])
    for q in questions:
        if sum(r["max_points"] for r in q["evaluation_rubric"]) != 10:
            problems.append("Question rubric does not sum to ten: " + q["id"])
    for mock in docs["INTERVIEW_QUESTION_BANK.json"]["mock_interviews"]:
        if sum(stage["minutes"] for stage in mock["stages"]) != mock["duration_minutes"]:
            problems.append("Mock interview time mismatch: " + mock["id"])

    def assert_dag(edges, label):
        active, complete = set(), set()
        def visit(node):
            if node in active:
                problems.append(label + " cycle at " + node)
                return
            if node in complete:
                return
            active.add(node)
            for parent in edges.get(node, []):
                visit(parent)
            active.remove(node)
            complete.add(node)
        for node in edges:
            visit(node)
    assert_dag(dependencies, "Skill dependency")
    assert_dag({e["lesson_id"]: e["requires_lesson_ids"] for e in docs["LEARNING_DEPENDENCIES.json"]["lesson_dependencies"]}, "Lesson dependency")

    for skill in skills:
        sid = skill["id"]
        req = sum(sid in j["required_skill_ids"] for j in jobs)
        pref = sum(sid in j["preferred_skill_ids"] for j in jobs)
        mentioned = sum(sid in j["required_skill_ids"] + j["preferred_skill_ids"] for j in jobs)
        if (req, pref, mentioned) != (skill["sample_required_count"], skill["sample_preferred_count"], skill["sample_mention_count"]):
            problems.append("Frequency mismatch: " + sid)
    matrix = docs["JOB_MARKET_SKILLS_MATRIX.json"]
    if matrix["methodology"]["sample_size"] != len(jobs):
        problems.append("Overall sample denominator mismatch")
    for analysis in matrix["track_analyses"]:
        subset = [j for j in jobs if j["id"] in analysis["job_ids"]]
        if len(subset) != analysis["sample_size"]:
            problems.append("Track sample denominator mismatch")
        for row in analysis["frequency_rows"]:
            sid = row["skill_id"]
            count = sum(sid in j["required_skill_ids"] + j["preferred_skill_ids"] for j in subset)
            req = sum(sid in j["required_skill_ids"] for j in subset)
            if (count, req, count - req, len(subset)) != (row["mention_count"], row["required_count"], row["preferred_only_count"], row["denominator"]):
                problems.append("Track frequency mismatch: " + sid)
    url_report_path = root / "URL_CHECK_RESULTS.json"
    if url_report_path.exists():
        url_report = json.loads(url_report_path.read_text(encoding="utf-8"))
        for error in Draft202012Validator(schema["$defs"]["URLCheckResults"], format_checker=FormatChecker()).iter_errors(url_report):
            problems.append("URL report schema: " + error.message[:200])
        if url_report["unique_requests"] != url_report["reachable_count"] + url_report["unavailable_count"]:
            problems.append("URL report count mismatch")
        unique_targets = {r["verification_target"] for r in url_report["results"]}
        if len(unique_targets) != url_report["unique_requests"]:
            problems.append("URL report target denominator mismatch")
    report = {
        "status": "passed" if not problems else "failed",
        "research_date": docs["LEARNER_PROFILE.json"]["research_date"],
        "research_version": docs["LEARNER_PROFILE.json"]["research_version"],
        "validated_dataset_files": len(docs),
        "counts": {kind: len(entries) for kind, entries in registries.items()},
        "curriculum_count": len(curricula), "schema_draft": "2020-12",
        "checks": [
            "Explicit JSON schemas with date/URI formats and no unknown fields",
            "Unique entity IDs and all typed internal references",
            "15 independent plans, contiguous days, 210-minute budgets and final deliverables",
            "Lesson/skill dependency ordering and acyclic graphs",
            "At least 3 exercises, 2 intermediate, 2 advanced and 1 capstone per track",
            "All interview categories, ten-point rubrics and mock-time sums",
            "Free-core labels and provenance, unavailable community/recency scores",
            "Recomputed job frequencies and denominators, duplicate resource URLs",
            "Referenced resource track associations and available validation-artifact schemas",
        ],
        "limitations": [
            "Structural and editorial validation, not learner execution or proof of curriculum timing in practice",
            "URL access results recorded separately; failures never converted into successful content verification",
            "Full video playback, exact metadata and community review unavailable",
        ],
        "errors": problems,
    }
    Draft202012Validator(schema["$defs"]["ValidationResult"], format_checker=FormatChecker()).validate(report)
    (root / "VALIDATION_RESULTS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "passed" else 1)

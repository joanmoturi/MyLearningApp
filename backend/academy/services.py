import copy
import re
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import PersonalRecord, Plan, PlanLesson, Progress, now, uid
from .research import catalogue, get_research
from .schemas import CompanyInput, PlanInput, SettingsInput

LOCAL_USER = "local"
LEVELS = [
    "Not assessed",
    "Unfamiliar",
    "Learning",
    "Basic understanding",
    "Can implement independently",
    "Can troubleshoot in production",
    "Can defend engineering trade-offs",
]


def personal(session: Session, kind: str) -> list[PersonalRecord]:
    return list(
        session.scalars(
            select(PersonalRecord)
            .where(PersonalRecord.user_id == LOCAL_USER, PersonalRecord.kind == kind)
            .order_by(PersonalRecord.created_at.desc())
        )
    )


def get_personal(session: Session, item_id: str, kind: str | None = None):
    item = session.get(PersonalRecord, item_id)
    if not item or item.user_id != LOCAL_USER or kind and item.kind != kind:
        raise HTTPException(404, "Personal item not found.")
    return item


def serialize(item):
    result = {column.name: getattr(item, column.name) for column in item.__table__.columns}
    if isinstance(item, PersonalRecord):
        return {
            **item.data,
            "id": item.id,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "research_ref": item.research_ref,
        }
    return result


def save_personal(
    session: Session, kind: str, data: dict, item_id=None, ref_key=None, research_ref=None, parent_id=None
):
    if item_id:
        item = get_personal(session, item_id, kind)
    elif ref_key:
        item = session.scalar(
            select(PersonalRecord).where(
                PersonalRecord.user_id == LOCAL_USER,
                PersonalRecord.kind == kind,
                PersonalRecord.ref_key == ref_key,
            )
        )
    else:
        item = None
    if item:
        item.data, item.updated_at = data, now()
    else:
        item = PersonalRecord(
            id=uid(),
            user_id=LOCAL_USER,
            kind=kind,
            data=data,
            ref_key=ref_key,
            research_ref=research_ref,
            parent_id=parent_id,
        )
        session.add(item)
    session.flush()
    return item


def settings(session: Session) -> PersonalRecord:
    values = personal(session, "settings")
    return (
        values[0]
        if values
        else save_personal(session, "settings", SettingsInput().model_dump(), ref_key="preferences")
    )


def get_plan(session: Session, plan_id: str) -> Plan:
    plan = session.get(Plan, plan_id)
    if not plan or plan.user_id != LOCAL_USER:
        raise HTTPException(404, "Plan not found.")
    return plan


def get_slot(session: Session, slot_id: str) -> PlanLesson:
    slot = session.get(PlanLesson, slot_id)
    if not slot:
        raise HTTPException(404, "Lesson not found.")
    get_plan(session, slot.plan_id)
    return slot


def progress_data(progress: Progress | None):
    if not progress:
        return {
            "video": False,
            "reading": False,
            "practical": False,
            "knowledge": False,
            "watched_minutes": 0,
            "study_minutes": 0,
            "evidence": "",
            "answers": {},
            "status": "not_started",
        }
    flags = [progress.video, progress.reading, progress.practical, progress.knowledge]
    status = (
        "fully_completed"
        if all(flags)
        else "in_progress"
        if any(flags)
        or progress.watched_minutes
        or progress.study_minutes
        or progress.evidence
        or progress.answers
        else "not_started"
    )
    return {
        **{
            key: getattr(progress, key)
            for key in (
                "video",
                "reading",
                "practical",
                "knowledge",
                "watched_minutes",
                "study_minutes",
                "evidence",
                "answers",
            )
        },
        "status": status,
    }


def slots(session: Session, plan_id: str):
    return list(
        session.scalars(select(PlanLesson).where(PlanLesson.plan_id == plan_id).order_by(PlanLesson.sequence))
    )


def slot_data(session: Session, slot: PlanLesson, full=False):
    data = (
        slot.data
        if full
        else {
            key: slot.data.get(key)
            for key in ("topic", "skill_ids", "knowledge_unit_id", "phase", "estimated_total_study_minutes")
        }
    )
    return {
        **data,
        "id": slot.id,
        "research_id": slot.research_id,
        "plan_id": slot.plan_id,
        "day": slot.day,
        "skipped": slot.skipped,
        "progress": progress_data(session.get(Progress, slot.id)),
    }


def plan_data(session: Session, plan: Plan, full=False):
    items = slots(session, plan.id)
    complete = sum(
        progress_data(session.get(Progress, slot.id))["status"] == "fully_completed" for slot in items
    )
    return {
        **serialize(plan),
        "lesson_count": len(items),
        "completed_count": complete,
        "scheduled_days": max((slot.day for slot in items), default=0),
        **({"lessons": [slot_data(session, slot) for slot in items]} if full else {}),
    }


def adjusted_lesson(lesson: dict, config: PlanInput):
    data = copy.deepcopy(lesson)
    budget = data["time_budget_minutes"]
    if config.daily_minutes < 210:
        reduction = 210 - config.daily_minutes
        budget["video"] -= min(15, reduction)
        budget["reading"] -= max(0, reduction - 15)
    else:
        budget["implementation"] += config.daily_minutes - 210
    if config.intensity == "practical":
        budget["video"] -= 10
        budget["implementation"] += 10
    elif config.intensity == "interview":
        budget["video"] -= 10
        budget["interview"] += 10
    if config.dsa_practice_minutes:
        budget["implementation"] -= config.dsa_practice_minutes
        budget["coding_practice"] = config.dsa_practice_minutes
    data["dsa_practice_minutes"] = config.dsa_practice_minutes
    data["estimated_total_study_minutes"] = sum(budget.values())
    data["planned_video_minutes"] = budget["video"]
    data["target_role"] = config.target_role
    data["priority_focus"] = bool(set(data["skill_ids"]) & set(config.priority_skill_ids))
    return data


def create_plan(session: Session, config: PlanInput, existing: Plan | None = None):
    get_research(session, config.track_id, "track")
    for sid in config.priority_skill_ids:
        get_research(session, sid, "skill")
    if config.company_id:
        get_personal(session, config.company_id, "company")
    if config.job_id:
        job = get_personal(session, config.job_id, "job")
        config.priority_skill_ids = list(set(config.priority_skill_ids + job.data["required_skill_ids"]))
    source = get_research(
        session, f"curriculum-{config.track_id.removeprefix('track-')}-{config.duration_days}", "curriculum"
    ).data
    if existing and existing.track_id != config.track_id:
        raise HTTPException(422, "Create a separate plan when switching tracks; existing work is preserved.")
    plan = existing or Plan(
        id=uid(),
        user_id=LOCAL_USER,
        track_id=config.track_id,
        title=f"{config.target_role} · {config.duration_days} days",
        config=config.model_dump(),
        status="active",
    )
    if not existing:
        session.add(plan)
        session.flush()
    prior = slots(session, plan.id)
    annotated_ids = {
        item.data.get("target_id")
        for item in personal(session, "note")
        if item.data.get("target_type") == "lesson"
    }
    retained = [
        slot
        for slot in prior
        if progress_data(session.get(Progress, slot.id))["status"] != "not_started"
        or slot.research_id is None
        or slot.id in annotated_ids
        or slot.data.get("manual_adjustment")
    ]
    retained_keys = {(slot.data.get("knowledge_unit_id"), slot.data.get("phase")) for slot in retained}
    for slot in prior:
        if slot not in retained:
            session.delete(slot)
    session.flush()
    # Preserve started/completed slot identities and their notes/progress across recalculation.
    for index, slot in enumerate(retained):
        slot.sequence = -index - 1
    session.flush()
    for index, slot in enumerate(retained):
        slot.sequence = index
        slot.day = index + 1
    sequence = len(retained)
    competencies = {item.ref_key: item.data for item in personal(session, "competency")}
    for lesson in source["lessons"]:
        if (lesson.get("knowledge_unit_id"), lesson.get("phase")) in retained_keys:
            continue
        demonstrated = (
            config.reuse_demonstrated
            and lesson["phase"] == "concept_and_slice"
            and all(competencies.get(sid, {}).get("level", 0) >= 4 for sid in lesson["skill_ids"])
        )
        item = PlanLesson(
            id=uid(),
            plan_id=plan.id,
            research_id=lesson["id"],
            sequence=sequence,
            day=sequence + 1,
            skipped=demonstrated,
            data=adjusted_lesson(lesson, config),
        )
        session.add(item)
        sequence += 1
    session.flush()
    rank = {
        (lesson.get("knowledge_unit_id"), lesson.get("phase")): index
        for index, lesson in enumerate(source["lessons"])
    }
    unit_rank = {
        lesson.get("knowledge_unit_id"): index
        for index, lesson in reversed(list(enumerate(source["lessons"])))
    }
    ordered = sorted(
        slots(session, plan.id),
        key=lambda slot: rank.get(
            (slot.data.get("knowledge_unit_id"), slot.data.get("phase")),
            unit_rank.get(slot.data.get("knowledge_unit_id"), len(rank)) + 0.5,
        ),
    )
    for index, slot in enumerate(ordered):
        slot.sequence = -index - 1
    session.flush()
    for index, slot in enumerate(ordered):
        slot.sequence, slot.day = index, index + 1
    plan.config, plan.title = config.model_dump(), f"{config.target_role} · {config.duration_days} days"
    prefs = settings(session)
    prefs.data = {**prefs.data, "active_plan_id": plan.id, "active_track_id": plan.track_id}
    session.flush()
    return plan


ALIASES = {
    "python": ["python"],
    "typescript": ["typescript", "javascript"],
    "go": ["golang", "go"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "api": ["rest", "grpc", "api", "graphql"],
    "database": ["sql", "postgresql", "mysql", "database"],
    "kubernetes": ["kubernetes", "k8s", "aks", "eks", "gke"],
    "docker": ["docker", "containerization"],
    "iac": ["terraform", "infrastructure as code"],
    "cicd": ["ci/cd", "github actions", "jenkins", "pipelines"],
    "gitops": ["gitops", "argocd", "argo cd"],
    "identity": ["oauth", "iam", "entra", "authentication"],
    "rag": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "mcp": ["mcp", "model context protocol"],
    "agents": ["agentic", "ai agents"],
    "observability": ["observability", "opentelemetry", "tracing"],
    "monitoring": ["prometheus", "grafana"],
    "messaging": ["kafka", "message queues"],
    "linux": ["linux"],
    "shell": ["bash", "shell", "powershell"],
    "evaluation": ["evals", "evaluation"],
    "security": ["security", "least privilege"],
}


def analyze_description(text: str, skill_ids: set[str]):
    required, preferred = set(), set()
    section = required
    for line in text.splitlines():
        if re.search(r"nice to have|preferred|bonus|optional", line, re.I):
            section = preferred
        elif re.search(r"required|must have|requirements|minimum qualifications", line, re.I):
            section = required
        for key, aliases in ALIASES.items():
            if "skill-" + key in skill_ids and any(
                re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", line, re.I) for alias in aliases
            ):
                section.add("skill-" + key)
    return {
        "required_skill_ids": sorted(required),
        "preferred_skill_ids": sorted(preferred - required),
        "seniority_expectations": [
            word
            for word in ("senior", "lead", "mentor", "architecture", "ownership", "production", "on-call")
            if word in text.lower()
        ],
        "method": "Reviewable keyword/section suggestions, not expert requirement extraction. Confirm and edit before creating a job-specific plan.",
    }


def gap_report(session: Session, job: PersonalRecord):
    competencies = {item.ref_key: item.data for item in personal(session, "competency")}
    studied = {
        sid
        for slot in session.scalars(select(PlanLesson).join(Plan).where(Plan.user_id == LOCAL_USER))
        if progress_data(session.get(Progress, slot.id))["status"] == "fully_completed"
        for sid in slot.data.get("skill_ids", [])
    }
    resources, lessons = catalogue(session, "resource"), catalogue(session, "lesson")
    rows = []
    for sid in job.data["required_skill_ids"] + job.data["preferred_skill_ids"]:
        level = competencies.get(sid, {}).get("level", 0)
        status = (
            "demonstrated"
            if level >= 4
            else "studied_not_demonstrated"
            if sid in studied
            else "needs_practical_implementation"
            if level >= 1
            else "not_assessed"
        )
        rows.append(
            {
                "skill_id": sid,
                "status": status,
                "competency": LEVELS[level],
                "resource_ids": [r["id"] for r in resources if sid in r["skill_ids"]][:5],
                "lesson_ids": [lesson["id"] for lesson in lessons if sid in lesson["skill_ids"]][:5],
            }
        )
    return {
        "job_id": job.id,
        "rows": rows,
        "limitations": "Self-reported evidence levels and editable keyword suggestions; not a hiring assessment. Studying a skill does not establish independent or production competence.",
    }


def schedule_review(session: Session, question_id: str, successful=False):
    previous = next((item for item in personal(session, "review") if item.ref_key == question_id), None)
    index = min(
        (previous.data["interval_index"] + 1) if previous and successful else 0,
        len(settings(session).data["review_intervals"]) - 1,
    )
    due = now().date() + timedelta(days=settings(session).data["review_intervals"][index])
    return save_personal(
        session,
        "review",
        {"question_id": question_id, "due_date": due.isoformat(), "interval_index": index},
        item_id=previous.id if previous else None,
        ref_key=question_id,
        research_ref=question_id,
    )


def seed_companies(session: Session):
    mapping = {}
    for employer in catalogue(session, "employer"):
        existing = next(
            (item for item in personal(session, "company") if item.research_ref == employer["id"]), None
        )
        if not existing:
            data = CompanyInput(
                name=employer["name"],
                career_url=employer["career_url"],
                target_roles=", ".join(employer["watch_keywords"]),
                notes=employer["limitations"],
                enabled=employer["enabled"],
                priority=employer.get("preparation_tier", 3),
            ).model_dump()
            existing = save_personal(
                session, "company", data, research_ref=employer["id"], ref_key=employer["id"]
            )
        mapping[employer["id"]] = existing.id
    for job in catalogue(session, "job"):
        if any(item.research_ref == job["id"] for item in personal(session, "job")):
            continue
        data = {
            "company_id": mapping[job["employer_id"]],
            "title": job["title"],
            "url": job["url"],
            "description": job["requirements_summary"],
            "location": job["location_and_remote_policy"],
            "employment_type": "Not specified",
            "required_experience": str(job["minimum_years"] or "Not specified"),
            "required_skill_ids": job["required_skill_ids"],
            "preferred_skill_ids": job["preferred_skill_ids"],
            "deadline": job["closes_at"],
            "application_status": "closed" if job["status"] == "expired" else "researching",
            "notes": "Imported research summary, not a full description or verified live vacancy.",
            "interview_feedback": "",
        }
        save_personal(
            session,
            "job",
            data,
            research_ref=job["id"],
            ref_key=job["id"],
            parent_id=mapping[job["employer_id"]],
        )

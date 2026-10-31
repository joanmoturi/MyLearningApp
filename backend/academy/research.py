import hashlib
import json
from pathlib import Path

from fastapi import HTTPException
from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ResearchDocument, ResearchRecord

FILES = {
    "LEARNER_PROFILE.json": {"tracks": "track"},
    "JOB_MARKET_SKILLS_MATRIX.json": {"skills": "skill"},
    "EMPLOYER_RESEARCH.json": {"employers": "employer", "job_postings": "job"},
    "RESOURCE_CATALOG.json": {"resources": "resource"},
    "PRACTICAL_PROJECTS.json": {"projects": "project"},
    "INTERVIEW_QUESTION_BANK.json": {"questions": "question", "mock_interviews": "mock"},
    "SHARED_KNOWLEDGE_MAP.json": {"knowledge_units": "knowledge"},
    "SOURCE_REGISTER.json": {"sources": "source"},
    "LEARNING_DEPENDENCIES.json": {},
    **{f"CURRICULUM_{days}_DAYS.json": {"curricula": "curriculum"} for days in (14, 30, 60)},
}
DATASET_TYPES = {
    "LEARNER_PROFILE.json": "learner",
    "JOB_MARKET_SKILLS_MATRIX.json": "skills",
    "EMPLOYER_RESEARCH.json": "employers",
    "RESOURCE_CATALOG.json": "resources",
    "PRACTICAL_PROJECTS.json": "projects",
    "INTERVIEW_QUESTION_BANK.json": "questions",
    "SHARED_KNOWLEDGE_MAP.json": "shared",
    "SOURCE_REGISTER.json": "sources",
    "LEARNING_DEPENDENCIES.json": "dependencies",
    **{f"CURRICULUM_{days}_DAYS.json": "curricula" for days in (14, 30, 60)},
}


def digest(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def records(documents: dict):
    for name, document in documents.items():
        for field, kind in FILES[name].items():
            for data in document.get(field, []):
                yield name, kind, data
                if kind == "curriculum":
                    for lesson in data["lessons"]:
                        yield name, "lesson", lesson


def validate_documents(documents: dict, research_root: Path, allow_partial: bool = False):
    schema = json.loads((research_root / "schemas" / "package.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if set(documents) - FILES.keys():
        raise HTTPException(422, "Unknown research dataset filename.")
    for name, data in documents.items():
        errors = list(validator.iter_errors(data))
        if errors:
            raise HTTPException(422, f"{name}: schema validation failed. No data was applied.")
        if set(FILES[name]) - set(data) or data.get("dataset_type") != DATASET_TYPES[name]:
            raise HTTPException(422, f"{name}: incorrect dataset type for this filename.")
    indexed = list(records(documents))
    registry: dict[str, set[str]] = {}
    all_ids = set()
    for _, kind, data in indexed:
        if data["id"] in all_ids:
            raise HTTPException(422, "Duplicate research ID: " + data["id"])
        all_ids.add(data["id"])
        registry.setdefault(kind, set()).add(data["id"])
    references = {
        "track_id": "track",
        "track_ids": "track",
        "skill_id": "skill",
        "skill_ids": "skill",
        "required_skill_ids": "skill",
        "preferred_skill_ids": "skill",
        "employer_id": "employer",
        "recommended_youtube_resource_id": "resource",
        "supplementary_reading_resource_ids": "resource",
        "resource_ids": "resource",
        "verification_sources": "source",
        "source_id": "source",
        "source_ids": "source",
        "interview_question_ids": "question",
        "question_ids": "question",
        "project_id": "project",
        "deliverable_project_id": "project",
        "lesson_ids": "lesson",
        "requires_lesson_ids": "lesson",
        "canonical_lesson_id": "lesson",
        "knowledge_unit_id": "knowledge",
        "job_ids": "job",
    }

    def check(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in references:
                    for ref in child if isinstance(child, list) else [child]:
                        if ref not in registry.get(references[key], set()):
                            if allow_partial and not any(
                                references[key] in fields.values()
                                or references[key] == "lesson"
                                and "curriculum" in fields.values()
                                for name, fields in FILES.items()
                                if name in documents
                            ):
                                continue
                            raise HTTPException(422, f"Unresolved {key}: {ref}")
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)

    for document in documents.values():
        check(document)
    for _, kind, data in indexed:
        if kind == "curriculum":
            seen = set()
            if [lesson["day"] for lesson in data["lessons"]] != list(range(1, data["duration_days"] + 1)):
                raise HTTPException(422, "Curriculum day count/order is invalid.")
            for lesson in data["lessons"]:
                if not set(lesson["prerequisites"]["lesson_ids"]) <= seen:
                    raise HTTPException(422, "Curriculum has out-of-order dependencies.")
                if sum(lesson["time_budget_minutes"].values()) != lesson["estimated_total_study_minutes"]:
                    raise HTTPException(422, "Curriculum time budget is inconsistent.")
                seen.add(lesson["id"])
        if kind == "resource":
            from .schemas import safe_url

            safe_url(data["url"])
    return indexed


def load_documents(research_root: Path):
    documents, missing = {}, []
    for name in FILES:
        path = research_root / name
        if path.exists():
            documents[name] = json.loads(path.read_text(encoding="utf-8"))
        else:
            missing.append(name)
    return documents, missing


def apply_documents(session: Session, documents: dict, research_root: Path, allow_partial: bool = False):
    indexed = validate_documents(documents, research_root, allow_partial)
    changed = {"added": 0, "updated": 0, "unchanged": 0}
    for name, data in documents.items():
        existing = session.get(ResearchDocument, name)
        if not existing:
            session.add(
                ResearchDocument(name=name, version=data["research_version"], digest=digest(data), data=data)
            )
        elif existing.digest != digest(data):
            existing.data, existing.digest, existing.version = data, digest(data), data["research_version"]
    session.flush()
    for name, kind, data in indexed:
        existing = session.get(ResearchRecord, data["id"])
        if not existing:
            session.add(ResearchRecord(id=data["id"], kind=kind, document_name=name, data=data))
            changed["added"] += 1
        elif existing.kind != kind:
            raise HTTPException(422, "A research ID cannot change entity type.")
        elif existing.data != data:
            existing.data = data
            changed["updated"] += 1
        else:
            changed["unchanged"] += 1
    return changed


def catalogue(session: Session, kind: str) -> list[dict]:
    return [
        record.data for record in session.scalars(select(ResearchRecord).where(ResearchRecord.kind == kind))
    ]


def get_research(session: Session, rid: str, kind: str | None = None) -> ResearchRecord:
    record = session.get(ResearchRecord, rid)
    if not record or kind and record.kind != kind:
        raise HTTPException(404, "Research item not found.")
    return record

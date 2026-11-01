"""Contracts for additive DSA research; original five-track schema stays unchanged."""

import re
from datetime import date
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .schemas import safe_url


class Entity(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,149}$")


class DsaQuestion(Entity):
    track_id: Literal["track-dsa"]
    title: str
    question: str
    skill_ids: list[str] = Field(min_length=1)
    pattern: str
    difficulty: Literal["easy", "medium", "hard"]
    category: Literal["coding"] = "coding"
    constraints: list[str] = Field(min_length=1)
    test_cases: list[dict] = Field(min_length=2, max_length=12)
    hints: list[str] = Field(min_length=1)
    solution_code: str = Field(min_length=10, max_length=20000)
    detailed_explanation: str
    complexity: dict[str, str]
    expected_answer_elements: list[str]
    evaluation_rubric: list[dict]
    follow_up_questions: list[str]
    common_mistakes: list[str]
    related_question_ids: list[str]
    source_ids: list[str]
    recommended_minutes: int = Field(ge=10, le=90)
    authorship: str

    @field_validator("test_cases")
    @classmethod
    def cases(cls, values):
        if any(set(value) != {"input", "output"} for value in values):
            raise ValueError("Fixtures must contain only input and output.")
        return values


class DsaResource(Entity):
    title: str
    creator: str
    url: str
    resource_type: str
    track_ids: list[str]
    skill_ids: list[str]
    free_status: Literal["fully_free", "free_documentation"]
    free_evidence: str
    last_verified_at: date
    overall_score: int = Field(ge=0, le=100)
    confidence: Literal["low", "medium", "high"]
    verification_sources: list[str] = Field(min_length=1)
    _url = field_validator("url")(safe_url)


class DsaProfile(Entity):
    name: str
    employer_id: str
    category: str
    career_url: str
    preparation_tier: int = Field(ge=1, le=3)
    interview_evidence: Literal[
        "officially_documented", "multiple_candidate_reports", "limited_anecdotal_evidence", "unknown"
    ]
    pattern_skill_ids: list[str]
    source_ids: list[str] = Field(min_length=1)
    research_date: date
    confidence: Literal["low", "medium", "high"]
    limitations: list[str] = Field(min_length=1)
    _url = field_validator("career_url")(safe_url)


class DsaLesson(Entity):
    track_id: Literal["track-dsa"]
    day: int = Field(ge=1, le=60)
    topic: str
    learning_objectives: list[str] = Field(min_length=1)
    prerequisites: dict
    skill_ids: list[str] = Field(min_length=1)
    knowledge_unit_id: str
    recommended_youtube_resource_id: str
    supplementary_reading_resource_ids: list[str] = Field(min_length=1)
    interview_question_ids: list[str] = Field(min_length=1)
    study_guide: dict
    example_implementation: str
    complexity_analysis: dict
    coding_exercises: list[str] = Field(min_length=2)
    completion_criteria: list[str] = Field(min_length=2)
    time_budget_minutes: dict[str, int]
    estimated_total_study_minutes: Literal[210]


def validate_dsa_document(name, document):
    fields = {
        "DSA_SKILL_MATRIX.json": ("skills", "tracks", "modules"),
        "DSA_RESOURCE_CATALOG.json": ("resources",),
        "DSA_QUESTION_BANK.json": ("questions", "mock_interviews"),
        "DSA_COMPANY_RESEARCH.json": ("profiles", "employers"),
        "DSA_SOURCE_REGISTER.json": ("sources",),
        "DSA_LEARNING_DEPENDENCIES.json": ("edges",),
        **{f"DSA_CURRICULUM_{days}_DAYS.json": ("curricula",) for days in (14, 30, 60)},
    }
    basename = name.rsplit("/", 1)[-1]
    try:
        if (
            document.get("dataset_type") != "dsa"
            or not re.fullmatch(r"\d+\.\d+\.\d+", str(document.get("research_version", "")))
            or document.get("$schema") != "DSA_PACKAGE_SCHEMA.json"
            or set(document)
            != {"$schema", "dataset_type", "research_version", "research_date", *fields[basename]}
        ):
            raise ValueError("Unexpected DSA document envelope.")
        date.fromisoformat(document["research_date"])
        contracts = {"questions": DsaQuestion, "resources": DsaResource, "profiles": DsaProfile}
        for field in fields[basename]:
            entries = document[field]
            if not isinstance(entries, list) or len(entries) > 10000:
                raise ValueError("Invalid DSA collection.")
            for entry in entries:
                if field == "curricula":
                    Entity.model_validate(entry)
                    if entry["duration_days"] not in (14, 30, 60) or entry["track_id"] != "track-dsa":
                        raise ValueError("Invalid DSA curriculum.")
                    for lesson in entry["lessons"]:
                        DsaLesson.model_validate(lesson)
                elif field != "edges":
                    contracts.get(field, Entity).model_validate(entry)
    except (ValidationError, ValueError, KeyError, TypeError) as error:
        raise HTTPException(422, f"{basename}: invalid DSA research contract.") from error


def package_schema():
    entity = Entity.model_json_schema()
    contracts = {
        "questions": DsaQuestion.model_json_schema(),
        "resources": DsaResource.model_json_schema(),
        "profiles": DsaProfile.model_json_schema(),
    }
    curriculum = {
        **entity,
        "properties": {
            **entity["properties"],
            "track_id": {"const": "track-dsa"},
            "duration_days": {"enum": [14, 30, 60]},
            "lessons": {
                "type": "array",
                "minItems": 14,
                "maxItems": 60,
                "items": DsaLesson.model_json_schema(),
            },
        },
        "required": ["id", "track_id", "duration_days", "lessons"],
    }
    contracts["curricula"] = curriculum
    collections = [
        ("tracks", "skills", "modules"),
        ("resources",),
        ("questions", "mock_interviews"),
        ("profiles", "employers"),
        ("sources",),
        ("edges",),
        ("curricula",),
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Additive Engineering Academy DSA package",
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "$schema": {"const": "DSA_PACKAGE_SCHEMA.json"},
                    "dataset_type": {"const": "dsa"},
                    "research_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                    "research_date": {"type": "string", "format": "date"},
                    **{
                        field: {
                            "type": "array",
                            "maxItems": 10000,
                            "items": contracts.get(field, {"type": "object"} if field == "edges" else entity),
                        }
                        for field in fields
                    },
                },
                "required": ["$schema", "dataset_type", "research_version", "research_date", *fields],
            }
            for fields in collections
        ],
    }

from datetime import date
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ImportInput(Input):
    kind: Literal["research", "personal"]
    payload: dict


def safe_url(value: str) -> str:
    if not value:
        return value
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an http(s) URL without embedded credentials.")
    return value


class PlanInput(Input):
    track_id: str
    duration_days: Literal[14, 30, 60] = 30
    daily_minutes: int = Field(default=210, ge=180, le=240)
    target_role: str = Field(default="Senior Software Engineer", min_length=2, max_length=200)
    intensity: Literal["balanced", "practical", "interview"] = "balanced"
    existing_competency: str = Field(default="Assess using evidence", max_length=500)
    priority_skill_ids: list[str] = Field(default_factory=list, max_length=80)
    company_id: str | None = None
    job_id: str | None = None
    reuse_demonstrated: bool = False
    dsa_practice_minutes: Literal[0, 30, 45] = 0

    @model_validator(mode="after")
    def dedicated_dsa(self):
        if self.track_id == "track-dsa" and self.dsa_practice_minutes:
            raise ValueError("A dedicated DSA plan already includes coding practice.")
        return self


class ProgressInput(Input):
    video: bool = False
    reading: bool = False
    practical: bool = False
    knowledge: bool = False
    watched_minutes: int = Field(default=0, ge=0, le=1440)
    study_minutes: int = Field(default=0, ge=0, le=1440)
    evidence: str = Field(default="", max_length=20000)
    answers: dict[str, str] = Field(default_factory=dict, max_length=50)

    @model_validator(mode="after")
    def require_evidence(self):
        if self.practical and len(self.evidence) < 10:
            raise ValueError("Practical completion requires submission evidence (at least 10 characters).")
        if self.knowledge and not any(len(answer) >= 5 for answer in self.answers.values()):
            raise ValueError("Knowledge completion requires a recorded answer.")
        return self


class NoteInput(Input):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(default="", max_length=100000)
    target_type: Literal["general", "lesson", "resource", "project", "company"] = "general"
    target_id: str | None = None


class ResourceInput(Input):
    bookmarked: bool = False
    completed: bool = False
    rating: int | None = Field(default=None, ge=1, le=5)
    flag: Literal["none", "needs_verification", "broken_link", "outdated", "unavailable_metadata"] = "none"


class CompetencyInput(Input):
    level: int = Field(ge=0, le=6)
    evidence: str = Field(default="", max_length=20000)
    evidence_url: str = Field(default="", max_length=2000)
    _url = field_validator("evidence_url")(safe_url)

    @model_validator(mode="after")
    def require_evidence(self):
        if self.level >= 4 and len(self.evidence) < 10:
            raise ValueError("Independent implementation or higher requires explicit practical evidence.")
        return self


class CompanyInput(Input):
    name: str = Field(min_length=1, max_length=200)
    website: str = Field(default="", max_length=2000)
    career_url: str = Field(default="", max_length=2000)
    location: str = Field(default="", max_length=200)
    arrangement: str = Field(default="Not verified", max_length=200)
    target_roles: str = Field(default="", max_length=1000)
    notes: str = Field(default="", max_length=20000)
    priority: int = Field(default=3, ge=1, le=5)
    enabled: bool = True
    _urls = field_validator("website", "career_url")(safe_url)


class JobInput(Input):
    company_id: str
    title: str = Field(min_length=1, max_length=200)
    url: str = Field(default="", max_length=2000)
    description: str = Field(min_length=10, max_length=100000)
    location: str = Field(default="", max_length=300)
    employment_type: str = Field(default="Not specified", max_length=100)
    required_experience: str = Field(default="", max_length=500)
    required_skill_ids: list[str] = Field(default_factory=list, max_length=80)
    preferred_skill_ids: list[str] = Field(default_factory=list, max_length=80)
    deadline: date | None = None
    application_status: Literal[
        "researching", "saved", "applied", "interviewing", "offer", "rejected", "closed"
    ] = "saved"
    notes: str = Field(default="", max_length=20000)
    interview_feedback: str = Field(default="", max_length=20000)
    _url = field_validator("url")(safe_url)


class Task(Input):
    id: str
    title: str = Field(min_length=1, max_length=300)
    completed: bool = False
    validation: str = Field(default="", max_length=2000)


class ProjectInput(Input):
    title: str = Field(min_length=1, max_length=200)
    track_ids: list[str] = Field(min_length=1, max_length=6)
    skill_ids: list[str] = Field(default_factory=list, max_length=80)
    overview: str = Field(default="", max_length=20000)
    architecture: str = Field(default="", max_length=20000)
    requirements: str = Field(default="", max_length=20000)
    testing_checklist: str = Field(default="", max_length=20000)
    github_url: str = Field(default="", max_length=2000)
    deployment_url: str = Field(default="", max_length=2000)
    status: Literal["not_started", "active", "paused", "completed"] = "not_started"
    tasks: list[Task] = Field(default_factory=list, max_length=100)
    _urls = field_validator("github_url", "deployment_url")(safe_url)

    @model_validator(mode="after")
    def unique_tasks(self):
        if len({task.id for task in self.tasks}) != len(self.tasks):
            raise ValueError("Task IDs must be unique.")
        return self


class AttemptInput(Input):
    question_id: str
    answer: str = Field(min_length=5, max_length=20000)
    score: int = Field(ge=0, le=10)
    confidence: int = Field(ge=1, le=5)
    dimensions: dict[str, int] = Field(default_factory=dict, max_length=6)
    mode: Literal["quick", "topic", "mock", "senior", "revision"] = "quick"

    @field_validator("dimensions")
    @classmethod
    def dimensions_valid(cls, values):
        allowed = {"correctness", "depth", "clarity", "experience", "tradeoffs", "completeness"}
        if set(values) - allowed or any(not 0 <= value <= 5 for value in values.values()):
            raise ValueError("Assessment dimensions must be named 0-5 self-ratings.")
        return values


class SettingsInput(Input):
    active_track_id: str = "track-swe"
    active_plan_id: str | None = None
    theme: Literal["dark", "light", "system"] = "dark"
    daily_minutes: int = Field(default=210, ge=180, le=240)
    priorities: list[str] = Field(default_factory=list, max_length=6)
    review_intervals: list[int] = Field(
        default_factory=lambda: [1, 3, 7, 14, 30], min_length=1, max_length=15
    )

    @field_validator("review_intervals")
    @classmethod
    def intervals(cls, values):
        if values != sorted(set(values)) or not all(1 <= value <= 365 for value in values):
            raise ValueError("Review intervals must be unique ascending days from 1 to 365.")
        return values


class CustomLessonInput(Input):
    topic: str = Field(min_length=1, max_length=300)
    objectives: str = Field(min_length=5, max_length=5000)
    exercise: str = Field(min_length=5, max_length=10000)
    resource_id: str | None = None
    minutes: int = Field(default=210, ge=180, le=240)


class ReviewInput(Input):
    question_id: str
    due_date: date
    interval_index: int = Field(ge=0, le=14)


PERSONAL_SCHEMAS = {
    "note": NoteInput,
    "resource": ResourceInput,
    "competency": CompetencyInput,
    "company": CompanyInput,
    "job": JobInput,
    "project": ProjectInput,
    "attempt": AttemptInput,
    "settings": SettingsInput,
    "review": ReviewInput,
}

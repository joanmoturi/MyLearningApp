"""Persistent coding practice; user code runs only in the browser's isolated runner."""

import json
import random
from datetime import datetime, timedelta
from typing import Literal

from fastapi import HTTPException
from pydantic import Field, JsonValue, StrictBool, model_validator
from sqlalchemy.orm import Session

from .models import now
from .research import catalogue, get_research
from .schemas import PERSONAL_SCHEMAS, Input
from .services import get_personal, personal, save_personal, schedule_review, serialize

DIMENSIONS = (
    "understanding",
    "pattern",
    "algorithm",
    "correctness",
    "quality",
    "time_complexity",
    "space_complexity",
    "edge_cases",
    "testing",
    "communication",
)


class SessionInput(Input):
    mode: Literal["pattern", "random", "timed", "company", "mock", "blind"] = "pattern"
    minutes: Literal[20, 30, 45, 60, 90] = 30
    count: int = Field(default=1, ge=1, le=5)
    skill_id: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    company_profile_id: str | None = None
    question_id: str | None = None


class Draft(Input):
    code: str = Field(default="function solve(input) {\n  // Implement your approach.\n}", max_length=20000)
    clarification: str = Field(default="", max_length=5000)
    approach: str = Field(default="", max_length=5000)
    time_complexity: str = Field(default="", max_length=500)
    space_complexity: str = Field(default="", max_length=500)
    tradeoffs: str = Field(default="", max_length=5000)


class Submission(Draft):
    question_id: str
    outputs: list[JsonValue] = Field(default_factory=list, max_length=12)
    ratings: dict[str, int]
    solved: bool = False
    elapsed_seconds: int = Field(default=0, ge=0, le=86400)

    @model_validator(mode="after")
    def rating_values(self):
        if set(self.ratings) != set(DIMENSIONS) or any(
            not 0 <= value <= 5 for value in self.ratings.values()
        ):
            raise ValueError("Rate all ten rubric dimensions from 0 to 5.")
        if self.solved and (len(self.approach) < 10 or not self.time_complexity or not self.space_complexity):
            raise ValueError("A solved claim requires an approach and both complexity analyses.")
        return self


class SampleCheck(Input):
    case: int = Field(ge=1, le=12)
    passed: StrictBool


class RecordedSubmission(Input):
    answer: Submission
    sample_checks: list[SampleCheck] = Field(min_length=1, max_length=12)
    hint_used: StrictBool
    solution_used: StrictBool
    submitted_at: datetime
    late: StrictBool


class CodingSession(Input):
    config: SessionInput
    question_ids: list[str] = Field(min_length=1, max_length=5)
    started_at: datetime
    deadline_at: datetime
    current_index: int = Field(ge=0, le=5)
    drafts: dict[str, Draft] = Field(default_factory=dict, max_length=5)
    revealed_hints: list[str] = Field(default_factory=list, max_length=5)
    revealed_solutions: list[str] = Field(default_factory=list, max_length=5)
    needs_revision: list[str] = Field(default_factory=list, max_length=5)
    submissions: list[dict] = Field(default_factory=list, max_length=5)
    status: Literal["active", "completed"] = "active"

    @model_validator(mode="after")
    def consistent(self):
        ids = set(self.question_ids)
        if (
            self.started_at.tzinfo is not None
            or self.deadline_at.tzinfo is not None
            or len(ids) != len(self.question_ids)
            or set(self.drafts) - ids
            or set(self.revealed_hints) - ids
            or set(self.revealed_solutions) - ids
            or set(self.needs_revision) - ids
            or self.current_index > len(ids)
            or self.deadline_at != self.started_at + timedelta(minutes=self.config.minutes)
        ):
            raise ValueError("Invalid coding session relationships.")
        submitted = []
        previous = self.started_at
        for entry in self.submissions:
            record = RecordedSubmission.model_validate(entry)
            submitted.append(record.answer.question_id)
            if (
                record.submitted_at.tzinfo is not None
                or record.submitted_at < previous
                or record.hint_used != (record.answer.question_id in self.revealed_hints)
                or record.solution_used != (record.answer.question_id in self.revealed_solutions)
                or record.late != (record.submitted_at > self.deadline_at)
            ):
                raise ValueError("Invalid coding submission evidence.")
            previous = record.submitted_at
        if submitted != self.question_ids[: len(submitted)] or self.current_index != len(submitted):
            raise ValueError("Coding submissions must advance one question at a time.")
        if (self.status == "completed") != (self.current_index == len(ids)):
            raise ValueError("Invalid session completion state.")
        return self


PERSONAL_SCHEMAS["coding_session"] = CodingSession


def create_session(session: Session, body: SessionInput):
    questions = [q for q in catalogue(session, "question") if q["track_id"] == "track-dsa"]
    if body.mode == "company":
        if not body.company_profile_id:
            raise HTTPException(422, "Choose a researched company profile.")
        profile = get_research(session, body.company_profile_id, "company_profile").data
        focus = set(profile["pattern_skill_ids"])
        if focus:
            questions = [q for q in questions if focus & set(q["skill_ids"])]
    if body.mode == "pattern" and not body.skill_id:
        raise HTTPException(422, "Choose a pattern for pattern practice.")
    if body.skill_id:
        questions = [q for q in questions if body.skill_id in q["skill_ids"]]
    if body.difficulty:
        questions = [q for q in questions if q["difficulty"] == body.difficulty]
    if body.question_id:
        questions = [q for q in questions if q["id"] == body.question_id]
    if len(questions) < body.count:
        raise HTTPException(422, "Not enough distinct questions match this practice configuration.")
    chosen = random.SystemRandom().sample(questions, body.count)
    started = now()
    data = CodingSession(
        config=body,
        question_ids=[q["id"] for q in chosen],
        started_at=started,
        deadline_at=started + timedelta(minutes=body.minutes),
        current_index=0,
    ).model_dump(mode="json")
    return session_view(session, save_personal(session, "coding_session", data))


def session_view(session, item):
    state = CodingSession.model_validate(item.data)
    result = {**serialize(item), "server_now": now().isoformat()}
    if state.current_index < len(state.question_ids):
        qid = state.question_ids[state.current_index]
        question = dict(get_research(session, qid, "question").data)
        if qid not in state.revealed_solutions:
            for key in ("solution_code", "detailed_explanation", "expected_answer_elements", "complexity"):
                question.pop(key, None)
        if qid not in state.revealed_hints:
            question.pop("hints", None)
        if state.config.mode == "blind" and qid not in state.revealed_hints + state.revealed_solutions:
            question.pop("pattern", None)
            question.pop("skill_ids", None)
        result["question"] = question
        result["draft"] = state.drafts.get(qid, Draft()).model_dump()
    else:
        result["question"] = {}
    return result


def save_draft(session, session_id, body: Draft):
    item = get_personal(session, session_id, "coding_session")
    state = CodingSession.model_validate(item.data)
    if state.status != "active":
        raise HTTPException(409, "This interview has finished.")
    state.drafts[state.question_ids[state.current_index]] = body
    item.data = state.model_dump(mode="json")
    item.updated_at = now()
    return session_view(session, item)


def reveal(session, session_id, kind):
    item = get_personal(session, session_id, "coding_session")
    state = CodingSession.model_validate(item.data)
    if state.status != "active":
        raise HTTPException(409, "This interview has finished.")
    qid = state.question_ids[state.current_index]
    target = state.revealed_hints if kind == "hint" else state.revealed_solutions
    if qid not in target:
        target.append(qid)
    item.data = state.model_dump(mode="json")
    return session_view(session, item)


def sample_checks(question, outputs):
    return [
        {
            "case": index + 1,
            "passed": index < len(outputs)
            and json.dumps(outputs[index], sort_keys=True) == json.dumps(case["output"], sort_keys=True),
        }
        for index, case in enumerate(question["test_cases"])
    ]


def submit(session, session_id, body: Submission):
    item = get_personal(session, session_id, "coding_session")
    state = CodingSession.model_validate(item.data)
    if state.status != "active" or body.question_id != state.question_ids[state.current_index]:
        raise HTTPException(409, "Submit the current question only, once.")
    question = get_research(session, body.question_id, "question").data
    checks = sample_checks(question, body.outputs)
    hint_used = body.question_id in state.revealed_hints
    solution_used = body.question_id in state.revealed_solutions
    submitted = now()
    late = submitted > state.deadline_at
    question_started = (
        datetime.fromisoformat(state.submissions[-1]["submitted_at"])
        if state.submissions
        else state.started_at
    )
    body.elapsed_seconds = min(86400, max(0, int((submitted - question_started).total_seconds())))
    state.submissions.append(
        {
            "answer": body.model_dump(mode="json"),
            "sample_checks": checks,
            "hint_used": hint_used,
            "solution_used": solution_used,
            "submitted_at": submitted.isoformat(),
            "late": late,
        }
    )
    state.current_index += 1
    if body.question_id in state.needs_revision:
        state.needs_revision.remove(body.question_id)
    state.status = "completed" if state.current_index == len(state.question_ids) else "active"
    item.data = state.model_dump(mode="json")
    item.updated_at = now()
    if not body.solved or hint_used or solution_used or not all(row["passed"] for row in checks):
        schedule_review(session, body.question_id)
    else:
        existing_review = next(
            (r for r in personal(session, "review") if r.ref_key == body.question_id), None
        )
        if existing_review:
            schedule_review(session, body.question_id, successful=True)
    return {
        **session_view(session, item),
        "feedback": {
            "sample_checks": checks,
            "solution": question["solution_code"],
            "explanation": question["detailed_explanation"],
            "complexity": question["complexity"],
            "method": "Sample output comparison plus learner rubric; not proof of correctness or hiring readiness.",
        },
    }


def analytics(session):
    questions = {q["id"]: q for q in catalogue(session, "question") if q["track_id"] == "track-dsa"}
    entries = []
    history = personal(session, "coding_session")
    for item in history:
        for record in item.data["submissions"]:
            answer = record["answer"]
            if answer["question_id"] in questions:
                entries.append({**record, "question": questions[answer["question_id"]]})
    latest = {}
    for entry in sorted(entries, key=lambda r: r["submitted_at"]):
        latest[entry["answer"]["question_id"]] = entry

    def independent(entry):
        return (
            entry["answer"]["solved"]
            and not entry["hint_used"]
            and not entry["solution_used"]
            and not entry["late"]
            and all(r["passed"] for r in entry["sample_checks"])
        )

    def status(qid):
        attempts = [entry for entry in entries if entry["answer"]["question_id"] == qid]
        if not attempts:
            return (
                "attempted"
                if any(
                    qid in item.data["drafts"] and item.data["drafts"][qid].get("approach")
                    for item in history
                )
                else "new"
            )
        last = latest[qid]
        if any(
            qid in item.data.get("needs_revision", [])
            and item.updated_at >= datetime.fromisoformat(last["submitted_at"])
            for item in history
        ):
            return "needs_revision"
        successes = [entry for entry in attempts if independent(entry)]
        dates = {entry["submitted_at"][:10] for entry in successes}
        if independent(last) and len(dates) >= 3:
            return "mastered"
        if independent(last):
            return "solved_independently"
        if last["answer"]["solved"] and all(row["passed"] for row in last["sample_checks"]):
            return (
                "solved_with_assistance" if last["hint_used"] or last["solution_used"] else "needs_revision"
            )
        return "needs_revision"

    topics = []
    for skill in catalogue(session, "skill"):
        if "track-dsa" not in skill["track_ids"]:
            continue
        matches = [entry for entry in entries if skill["id"] in entry["question"]["skill_ids"]]
        unique = [entry for entry in latest.values() if skill["id"] in entry["question"]["skill_ids"]]
        topics.append(
            {
                "skill_id": skill["id"],
                "name": skill["name"],
                "attempts": len(matches),
                "independent_rate": round(100 * sum(independent(e) for e in unique) / len(unique), 1)
                if unique
                else None,
                "pattern_self_rating": round(
                    sum(e["answer"]["ratings"]["pattern"] for e in matches) / len(matches), 1
                )
                if matches
                else None,
                "complexity_self_rating": round(
                    sum(
                        e["answer"]["ratings"]["time_complexity"] + e["answer"]["ratings"]["space_complexity"]
                        for e in matches
                    )
                    / (2 * len(matches)),
                    1,
                )
                if matches
                else None,
            }
        )
    module_order = {skill["id"]: index for index, skill in enumerate(catalogue(session, "skill"))}
    topics.sort(
        key=lambda row: (
            row["independent_rate"] if row["independent_rate"] is not None else 101,
            module_order[row["skill_id"]],
        )
    )
    due = [
        serialize(r)
        for r in personal(session, "review")
        if r.data["question_id"] in questions and r.data["due_date"] <= now().date().isoformat()
    ]
    next_question = (
        due[0]["question_id"]
        if due
        else next(
            (
                q["id"]
                for topic in topics
                for q in questions.values()
                if topic["skill_id"] in q["skill_ids"] and status(q["id"]) != "mastered"
            ),
            None,
        )
    )
    next_lesson = next(
        (
            {"id": lesson["id"], "topic": lesson["topic"], "curriculum_id": curriculum["id"]}
            for curriculum in catalogue(session, "curriculum")
            if curriculum["track_id"] == "track-dsa" and curriculum["duration_days"] == 30
            for lesson in curriculum["lessons"]
            if next_question in lesson["coding_exercises"]
        ),
        None,
    )
    return {
        "attempts": len(entries),
        "questions_attempted": len(latest),
        "solved": sum(
            e["answer"]["solved"] and all(row["passed"] for row in e["sample_checks"])
            for e in latest.values()
        ),
        "solved_independently": sum(independent(e) for e in latest.values()),
        "with_hints": sum(e["hint_used"] for e in entries),
        "with_solutions": sum(e["solution_used"] for e in entries),
        "elapsed_seconds": sum(e["answer"]["elapsed_seconds"] for e in entries),
        "difficulty": [
            {
                "difficulty": level,
                "attempts": sum(e["question"]["difficulty"] == level for e in entries),
                "independent": sum(
                    e["question"]["difficulty"] == level and independent(e) for e in latest.values()
                ),
            }
            for level in ("easy", "medium", "hard")
        ],
        "topics": topics,
        "revision_due": due,
        "next_question_id": next_question,
        "next_lesson": next_lesson,
        "states": {qid: status(qid) for qid in questions},
        "history": [serialize(item) for item in history[:20]],
        "limitations": "Self-reported solutions and rubric ratings with sample-output checks. Mastery requires independent successes on three separate UTC dates; viewing a solution never establishes mastery.",
    }


def register_routes(app, database):
    from fastapi import Depends

    @app.get("/api/dsa")
    def overview(session=Depends(database, scope="function")):
        return {
            "analytics": analytics(session),
            "companies": catalogue(session, "company_profile"),
            "dimensions": list(DIMENSIONS),
        }

    @app.post("/api/dsa/sessions")
    def start(body: SessionInput, session=Depends(database, scope="function")):
        return create_session(session, body)

    @app.get("/api/dsa/sessions/{session_id}")
    def read(session_id: str, session=Depends(database, scope="function")):
        return session_view(session, get_personal(session, session_id, "coding_session"))

    @app.patch("/api/dsa/sessions/{session_id}")
    def draft(session_id: str, body: Draft, session=Depends(database, scope="function")):
        return save_draft(session, session_id, body)

    @app.post("/api/dsa/sessions/{session_id}/help/{kind}")
    def help(session_id: str, kind: Literal["hint", "solution"], session=Depends(database, scope="function")):
        return reveal(session, session_id, kind)

    @app.post("/api/dsa/sessions/{session_id}/submit")
    def answer(session_id: str, body: Submission, session=Depends(database, scope="function")):
        return submit(session, session_id, body)

    @app.post("/api/dsa/sessions/{session_id}/revision/{question_id}")
    def mark_revision(session_id: str, question_id: str, session=Depends(database, scope="function")):
        item = get_personal(session, session_id, "coding_session")
        state = CodingSession.model_validate(item.data)
        if question_id not in state.question_ids[: state.current_index]:
            raise HTTPException(422, "Mark a submitted question for revision.")
        if question_id not in state.needs_revision:
            state.needs_revision.append(question_id)
        item.data = state.model_dump(mode="json")
        item.updated_at = now()
        schedule_review(session, question_id)
        return session_view(session, item)

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import dsa, integrations
from .data_management import apply_import, export_bundle, preview_import, restore_sqlite, sqlite_backup
from .database import make_database, migrate
from .models import (
    ImportPreview,
    PersonalRecord,
    Plan,
    PlanLesson,
    Progress,
    ResearchDocument,
    ResearchRecord,
    StudyActivity,
    User,
    now,
    uid,
)
from .research import DSA_FILES, apply_documents, catalogue, digest, get_research, load_documents
from .schemas import (
    AttemptInput,
    CompanyInput,
    CompetencyInput,
    CustomLessonInput,
    ImportInput,
    JobInput,
    NoteInput,
    PlanInput,
    ProgressInput,
    ProjectInput,
    ResourceInput,
    SettingsInput,
)
from .services import (
    LOCAL_USER,
    analyze_description,
    create_plan,
    gap_report,
    get_personal,
    get_plan,
    get_slot,
    personal,
    plan_data,
    progress_data,
    save_personal,
    schedule_review,
    seed_companies,
    serialize,
    settings,
    slot_data,
    slots,
)

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
MAX_BODY = 20 * 1024 * 1024
logger = logging.getLogger("academy")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def create_app(database_url: str | None = None, research_root: Path | None = None):
    research_root = research_root or Path(os.getenv("RESEARCH_DIR", str(ROOT / "research")))
    database_url = database_url or os.getenv(
        "DATABASE_URL", "sqlite:///" + str(ROOT / "data" / "academy.sqlite3")
    )
    engine, factory = make_database(database_url)

    @asynccontextmanager
    async def lifespan(app):
        migrate(database_url)
        with factory.begin() as session:
            if not session.get(User, LOCAL_USER):
                session.add(User(id=LOCAL_USER, name="Local learner"))
                session.flush()
            documents, missing = load_documents(research_root)
            app.state.research_issues = missing
            if not session.scalar(select(ResearchDocument)) and documents:
                apply_documents(session, documents, research_root, allow_partial=bool(missing))
            else:
                current = {doc.name: doc.data for doc in session.scalars(select(ResearchDocument))}
                additions = {
                    name: data
                    for name, data in documents.items()
                    if name in DSA_FILES and name not in current
                }
                if additions:
                    apply_documents(
                        session, {**current, **additions}, research_root, allow_partial=bool(missing)
                    )
            settings(session)
            seed_companies(session)
            if not session.scalar(select(Plan).where(Plan.user_id == LOCAL_USER)) and session.get(
                ResearchRecord, "curriculum-swe-30"
            ):
                create_plan(session, PlanInput(track_id="track-swe"))
        yield
        engine.dispose()

    app = FastAPI(title="Engineering Academy", version="1.0.0", lifespan=lifespan)
    app.state.engine, app.state.factory = engine, factory
    app.state.research_issues = []
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "backend", "testserver"]
    )
    gate = asyncio.Lock()

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        started = time.monotonic()
        if request.headers.get("origin") and request.headers["origin"] != os.getenv(
            "APP_ORIGIN", "http://127.0.0.1:3000"
        ):
            return JSONResponse({"detail": "Cross-origin access denied."}, 403)
        if (
            request.method not in ("GET", "HEAD", "OPTIONS")
            and request.headers.get("x-academy-client") != "local-workspace"
        ):
            return JSONResponse({"detail": "Missing same-origin client header."}, 403)
        if request.method not in ("GET", "HEAD"):
            chunks, size = [], 0
            limit = 64 * 1024 * 1024 if request.url.path == "/api/data/restore" else MAX_BODY
            async for chunk in request.stream():
                size += len(chunk)
                if size > limit:
                    return JSONResponse({"detail": "File exceeds the permitted size."}, 413)
                chunks.append(chunk)
            request._body = b"".join(chunks)
        # Single-process local transactions and backup/restore never overlap.
        async with gate:
            response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        logger.info(
            json.dumps(
                {
                    "event": "request",
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000),
                }
            )
        )
        return response

    @app.exception_handler(IntegrityError)
    async def integrity_error(_, error):
        return JSONResponse(
            {"detail": "Conflicting IDs or invalid relationships. No changes were applied."}, 409
        )

    @app.exception_handler(ValueError)
    async def validation_error(_, error):
        return JSONResponse({"detail": str(error)[:500]}, 422)

    def database():
        with factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    dsa.register_routes(app, database)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "local_first": True, "research_issues": app.state.research_issues}

    @app.get("/api/bootstrap")
    def bootstrap(session=Depends(database, scope="function")):
        return {
            "tracks": catalogue(session, "track"),
            "skills": catalogue(session, "skill"),
            "curricula": [
                {k: v for k, v in item.items() if k != "lessons"} for item in catalogue(session, "curriculum")
            ],
            "settings": settings(session).data,
            "integrations": integrations.configuration(),
            "research_issues": app.state.research_issues,
        }

    @app.get("/api/catalog/{kind}")
    def list_catalog(
        kind: Literal["track", "skill", "resource", "question", "project", "mock", "knowledge", "source"],
        q: str = "",
        track: str = "",
        skill: str = "",
        difficulty: str = "",
        category: str = "",
        free_status: str = "",
        min_score: int = 0,
        max_minutes: int | None = None,
        published_after: str = "",
        offset: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=400),
        session=Depends(database, scope="function"),
    ):
        items = catalogue(session, kind)
        items = [
            item
            for item in items
            if (not q or q.lower() in json.dumps(item).lower())
            and (not track or track in item.get("track_ids", [item.get("track_id")]))
            and (not skill or skill in item.get("skill_ids", []))
            and (not difficulty or difficulty == item.get("difficulty"))
            and (not category or category == item.get("category", item.get("resource_type")))
            and (not free_status or item.get("free_status") == free_status)
            and item.get("overall_score", 100) >= min_score
            and (
                max_minutes is None
                or item.get("duration_minutes") is not None
                and item["duration_minutes"] <= max_minutes
            )
            and (
                not published_after
                or item.get("published_at") is not None
                and item["published_at"] >= published_after
            )
        ]
        items.sort(key=lambda item: (item.get("title", item.get("name", "")), item["id"]))
        return {"items": items[offset : offset + limit], "total": len(items), "offset": offset}

    @app.get("/api/catalog/{kind}/{item_id}")
    def catalog_item(kind: str, item_id: str, session=Depends(database, scope="function")):
        return get_research(session, item_id, kind).data

    @app.get("/api/plans")
    def list_plans(session=Depends(database, scope="function")):
        return [
            plan_data(session, plan)
            for plan in session.scalars(
                select(Plan).where(Plan.user_id == LOCAL_USER).order_by(Plan.created_at.desc())
            )
        ]

    @app.post("/api/plans")
    def new_plan(body: PlanInput, session=Depends(database, scope="function")):
        return plan_data(session, create_plan(session, body), True)

    @app.get("/api/plans/{plan_id}")
    def read_plan(plan_id: str, session=Depends(database, scope="function")):
        return plan_data(session, get_plan(session, plan_id), True)

    @app.patch("/api/plans/{plan_id}")
    def recalculate_plan(plan_id: str, body: PlanInput, session=Depends(database, scope="function")):
        return plan_data(session, create_plan(session, body, get_plan(session, plan_id)), True)

    @app.post("/api/plans/{plan_id}/status/{action}")
    def plan_action(
        plan_id: str,
        action: Literal["activate", "pause", "resume"],
        session=Depends(database, scope="function"),
    ):
        plan = get_plan(session, plan_id)
        plan.status = "paused" if action == "pause" else "active"
        if action == "pause" and settings(session).data["active_plan_id"] == plan.id:
            settings(session).data = {**settings(session).data, "active_plan_id": None}
        if action != "pause":
            prefs = settings(session)
            prefs.data = {**prefs.data, "active_plan_id": plan.id, "active_track_id": plan.track_id}
        return plan_data(session, plan)

    @app.post("/api/plans/{plan_id}/custom")
    def custom_lesson(plan_id: str, body: CustomLessonInput, session=Depends(database, scope="function")):
        plan = get_plan(session, plan_id)
        if body.resource_id:
            get_research(session, body.resource_id, "resource")
        current = slots(session, plan.id)
        data = {
            "topic": body.topic,
            "learning_objectives": [body.objectives],
            "why_it_matters": "Learner-authored custom lesson; not verified research.",
            "skill_ids": [],
            "knowledge_unit_id": None,
            "phase": "custom",
            "recommended_youtube_resource_id": body.resource_id,
            "supplementary_reading_resource_ids": [],
            "practical_implementation_exercise": body.exercise,
            "estimated_total_study_minutes": body.minutes,
            "planned_video_minutes": 0,
            "prerequisites": {"baseline_knowledge": ["Check prior plan artifacts"]},
            "study_guide": {
                "before_video": ["Review the objective and prior notes."],
                "during_video": ["Record assumptions if using a resource."],
                "after_video": {
                    "comprehension_questions": ["Explain the result and one trade-off."],
                    "validate_understanding": ["Record practical evidence and the knowledge-check answer."],
                },
            },
            "completion_criteria": ["Record evidence and validate the custom objective."],
        }
        slot = PlanLesson(
            id=uid(),
            plan_id=plan.id,
            sequence=len(current),
            day=max((item.day for item in current), default=0) + 1,
            data=data,
            skipped=False,
        )
        session.add(slot)
        session.flush()
        return slot_data(session, slot, True)

    @app.get("/api/lessons/{slot_id}")
    def lesson(slot_id: str, session=Depends(database, scope="function")):
        return slot_data(session, get_slot(session, slot_id), True)

    @app.patch("/api/lessons/{slot_id}")
    def adjust_slot(slot_id: str, request: dict, session=Depends(database, scope="function")):
        if set(request) - {"day", "skipped", "resource_id"}:
            raise HTTPException(422, "Unknown lesson adjustment.")
        slot = get_slot(session, slot_id)
        current = slots(session, slot.plan_id)
        if "day" in request:
            day = request["day"]
            if not isinstance(day, int) or not 1 <= day <= 365:
                raise HTTPException(422, "Day must be 1-365.")
            before = [item for item in current if item.sequence < slot.sequence]
            if before and day <= before[-1].day:
                raise HTTPException(409, "This move would precede required artifacts.")
            slot.day = day
            for item in current:
                if item.sequence > slot.sequence:
                    item.day = max(item.day, day + 1)
                    day = item.day
        if "skipped" in request:
            if not isinstance(request["skipped"], bool):
                raise HTTPException(422, "Skipped must be Boolean.")
            slot.skipped = request["skipped"]
        if "resource_id" in request:
            resource = get_research(session, request["resource_id"], "resource").data
            if resource["free_status"] not in ("fully_free", "free_documentation"):
                raise HTTPException(422, "Choose a free learning resource.")
            slot.data = {
                **slot.data,
                "recommended_youtube_resource_id": resource["id"],
                "resource_replaced_by_learner": True,
            }
        slot.data = {**slot.data, "manual_adjustment": True}
        return slot_data(session, slot, True)

    @app.patch("/api/progress/{slot_id}")
    def update_progress(slot_id: str, body: ProgressInput, session=Depends(database, scope="function")):
        get_slot(session, slot_id)
        item = session.get(Progress, slot_id)
        previous_minutes = item.watched_minutes + item.study_minutes if item else 0
        if not item:
            item = Progress(slot_id=slot_id)
            session.add(item)
        for key, value in body.model_dump().items():
            setattr(item, key, value)
        item.updated_at = now()
        session.flush()
        day = now().date().isoformat()
        activity = session.get(StudyActivity, (slot_id, day))
        difference = item.watched_minutes + item.study_minutes - previous_minutes
        if activity:
            activity.minutes = max(0, activity.minutes + difference)
        elif difference > 0:
            session.add(StudyActivity(slot_id=slot_id, day=day, minutes=difference))
        return progress_data(item)

    @app.get("/api/personal/{kind}")
    def personal_list(
        kind: Literal["note", "resource", "competency", "company", "job", "project", "attempt", "review"],
        session=Depends(database, scope="function"),
    ):
        return [serialize(item) for item in personal(session, kind)]

    def validate_links(session, kind, body):
        if kind == "job":
            get_personal(session, body.company_id, "company")
            for sid in body.required_skill_ids + body.preferred_skill_ids:
                get_research(session, sid, "skill")
        if kind == "project":
            for tid in body.track_ids:
                get_research(session, tid, "track")
            for sid in body.skill_ids:
                get_research(session, sid, "skill")
        if kind == "note" and body.target_type != "general":
            if not body.target_id:
                raise HTTPException(422, "Choose the note's attachment.")
            if body.target_type == "lesson":
                get_slot(session, body.target_id)
            elif body.target_type == "resource":
                get_research(session, body.target_id, "resource")
            else:
                get_personal(session, body.target_id, body.target_type)

    # Typed endpoint generation shares persistence without exposing arbitrary tables/columns.
    def register_editor(kind, schema):
        def add(body, session=Depends(database, scope="function")):
            validate_links(session, kind, body)
            item = save_personal(
                session,
                kind,
                body.model_dump(mode="json"),
                parent_id=body.company_id if kind == "job" else None,
            )
            return serialize(item)

        def edit(item_id: str, body, session=Depends(database, scope="function")):
            validate_links(session, kind, body)
            item = save_personal(session, kind, body.model_dump(mode="json"), item_id=item_id)
            if kind == "job":
                item.parent_id = body.company_id
            return serialize(item)

        add.__annotations__["body"] = schema
        edit.__annotations__["body"] = schema
        app.add_api_route(f"/api/personal/{kind}", add, methods=["POST"], name=f"create_{kind}")
        app.add_api_route(f"/api/personal/{kind}/{{item_id}}", edit, methods=["PATCH"], name=f"edit_{kind}")

    for kind, schema in {
        "note": NoteInput,
        "company": CompanyInput,
        "job": JobInput,
        "project": ProjectInput,
    }.items():
        register_editor(kind, schema)

    @app.delete("/api/personal/{kind}/{item_id}")
    def remove_personal(
        kind: Literal["note", "company", "job", "project"],
        item_id: str,
        session=Depends(database, scope="function"),
    ):
        item = get_personal(session, item_id, kind)
        if session.scalar(select(PersonalRecord).where(PersonalRecord.parent_id == item_id)):
            raise HTTPException(409, "Remove or reassign linked jobs before removing this company.")
        session.delete(item)
        return {"deleted": item_id}

    @app.patch("/api/resources/{resource_id}/personal")
    def resource_preferences(
        resource_id: str, body: ResourceInput, session=Depends(database, scope="function")
    ):
        get_research(session, resource_id, "resource")
        return serialize(
            save_personal(
                session, "resource", body.model_dump(), ref_key=resource_id, research_ref=resource_id
            )
        )

    @app.patch("/api/skills/{skill_id}")
    def competency(skill_id: str, body: CompetencyInput, session=Depends(database, scope="function")):
        get_research(session, skill_id, "skill")
        return serialize(
            save_personal(session, "competency", body.model_dump(), ref_key=skill_id, research_ref=skill_id)
        )

    @app.post("/api/attempts")
    def attempt(body: AttemptInput, session=Depends(database, scope="function")):
        question = get_research(session, body.question_id, "question").data
        item = save_personal(
            session,
            "attempt",
            {
                **body.model_dump(),
                "track_id": question["track_id"],
                "skill_ids": question["skill_ids"],
                "method": "rubric_self_assessment",
            },
        )
        if body.score < 6 or body.confidence <= 2:
            schedule_review(session, body.question_id)
        return {**serialize(item), "expected_answer": question["detailed_explanation"]}

    @app.post("/api/reviews/{review_id}")
    def review_done(review_id: str, request: dict, session=Depends(database, scope="function")):
        review = get_personal(session, review_id, "review")
        return serialize(
            schedule_review(session, review.data["question_id"], successful=bool(request.get("successful")))
        )

    @app.post("/api/jobs/analyze")
    def analyze(request: dict, session=Depends(database, scope="function")):
        text = request.get("description", "")
        if not isinstance(text, str) or not 10 <= len(text) <= 100000:
            raise HTTPException(422, "Provide a 10-100000 character job description.")
        return analyze_description(text, {item["id"] for item in catalogue(session, "skill")})

    @app.get("/api/jobs/{job_id}/gaps")
    def gaps(job_id: str, session=Depends(database, scope="function")):
        return gap_report(session, get_personal(session, job_id, "job"))

    @app.post("/api/projects/{project_id}/start")
    def start_project(project_id: str, session=Depends(database, scope="function")):
        source = get_research(session, project_id, "project").data
        existing = next(
            (item for item in personal(session, "project") if item.research_ref == project_id), None
        )
        if existing:
            return serialize(existing)
        data = ProjectInput(
            title=source["title"],
            track_ids=source["track_ids"],
            skill_ids=source["skill_ids"],
            overview=source["problem_statement"],
            architecture=source["architecture"],
            requirements="\n".join(source["engineering_requirements"]),
            testing_checklist="\n".join(source["testing_strategy"]),
            status="active",
            tasks=[
                {
                    "id": milestone["id"],
                    "title": milestone["title"],
                    "validation": "; ".join(milestone["deliverables"]),
                    "completed": False,
                }
                for milestone in source["milestones"]
            ],
        ).model_dump(mode="json")
        return serialize(save_personal(session, "project", data, ref_key=project_id, research_ref=project_id))

    @app.get("/api/settings")
    def read_settings(session=Depends(database, scope="function")):
        return settings(session).data

    @app.patch("/api/settings")
    def update_settings(body: SettingsInput, session=Depends(database, scope="function")):
        get_research(session, body.active_track_id, "track")
        for tid in body.priorities:
            get_research(session, tid, "track")
        if body.active_plan_id:
            plan = get_plan(session, body.active_plan_id)
            if plan.track_id != body.active_track_id:
                raise HTTPException(422, "The active plan must belong to the active track.")
        settings(session).data = body.model_dump()
        return body.model_dump()

    @app.get("/api/dashboard")
    def dashboard(session=Depends(database, scope="function")):
        plans = [
            plan_data(session, plan)
            for plan in session.scalars(select(Plan).where(Plan.user_id == LOCAL_USER))
        ]
        all_slots = list(session.scalars(select(PlanLesson).join(Plan).where(Plan.user_id == LOCAL_USER)))
        progresses = [session.get(Progress, slot.id) for slot in all_slots]
        study_minutes = sum(item.study_minutes + item.watched_minutes for item in progresses if item)
        dates = {
            date.fromisoformat(item.day)
            for item in session.scalars(
                select(StudyActivity)
                .join(Progress)
                .join(PlanLesson)
                .join(Plan)
                .where(Plan.user_id == LOCAL_USER, StudyActivity.minutes > 0)
            )
        }
        streak, day = 0, now().date()
        if day not in dates:
            day -= timedelta(days=1)
        while day in dates:
            streak, day = streak + 1, day - timedelta(days=1)
        prefs = settings(session).data
        active_slots = [slot for slot in all_slots if slot.plan_id == prefs["active_plan_id"]]
        active_slots.sort(key=lambda slot: slot.sequence)
        upcoming = [
            slot_data(session, slot)
            for slot in active_slots
            if not slot.skipped
            and progress_data(session.get(Progress, slot.id))["status"] != "fully_completed"
        ]
        attempts = personal(session, "attempt")
        readiness = [
            {
                "track_id": track["id"],
                "attempts": len(
                    answers := [item for item in attempts if item.data["track_id"] == track["id"]]
                ),
                "self_rubric_average": round(sum(item.data["score"] for item in answers) / len(answers), 1)
                if answers
                else None,
            }
            for track in catalogue(session, "track")
        ]
        return {
            "plans": plans,
            "active_track_id": prefs["active_track_id"],
            "active_plan_id": prefs["active_plan_id"],
            "hours_studied": round(study_minutes / 60, 1),
            "completed_lessons": sum(
                progress_data(item)["status"] == "fully_completed" for item in progresses
            ),
            "learning_streak": streak,
            "upcoming": upcoming[:5],
            "outstanding_exercises": len(upcoming),
            "interview_readiness": readiness,
            "weak_areas": [
                serialize(item) for item in personal(session, "competency") if 0 < item.data["level"] < 4
            ],
            "revision_due": [
                serialize(item)
                for item in personal(session, "review")
                if item.data["due_date"] <= now().date().isoformat()
            ],
            "active_projects": [
                serialize(item) for item in personal(session, "project") if item.data["status"] == "active"
            ],
        }

    @app.get("/api/data/export")
    def data_export(
        kind: Literal["research", "personal", "notes"] = "personal",
        session=Depends(database, scope="function"),
    ):
        if kind == "notes":
            text = "\n\n".join(
                f"# {item.data['title']}\n\n{item.data['body']}" for item in personal(session, "note")
            )
            return Response(
                text,
                media_type="text/markdown",
                headers={"Content-Disposition": 'attachment; filename="academy-notes.md"'},
            )
        data = (
            {"datasets": {doc.name: doc.data for doc in session.scalars(select(ResearchDocument))}}
            if kind == "research"
            else export_bundle(session)
        )
        return Response(
            json.dumps(data, ensure_ascii=True),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="academy-{kind}.json"'},
        )

    @app.post("/api/data/preview")
    def import_preview(request: ImportInput, session=Depends(database, scope="function")):
        return preview_import(session, request.kind, request.payload, research_root)

    @app.post("/api/data/apply/{preview_id}")
    def import_apply(preview_id: str, request: dict, session=Depends(database, scope="function")):
        if request.get("confirm") is not True:
            raise HTTPException(422, "Explicit import confirmation required.")
        return apply_import(session, preview_id, research_root)

    @app.get("/api/data/backup")
    def backup():
        if not database_url.startswith("sqlite:///"):
            raise HTTPException(409, "Use the JSON export or your PostgreSQL backup tools.")
        return Response(
            sqlite_backup(Path(database_url.removeprefix("sqlite:///"))),
            media_type="application/octet-stream",
            headers={"Content-Disposition": 'attachment; filename="academy.sqlite3"'},
        )

    @app.post("/api/data/restore")
    async def restore(request: Request):
        if request.headers.get("x-academy-confirm") != "restore":
            raise HTTPException(422, "Explicit restore confirmation required.")
        if not database_url.startswith("sqlite:///"):
            raise HTTPException(409, "SQLite restore is only available for the default local database.")
        restore_sqlite(
            engine, Path(database_url.removeprefix("sqlite:///")), await request.body(), research_root
        )
        return {
            "restored": True,
            "recovery_copy": "A pre-restore backup was retained next to the local database.",
        }

    @app.post("/api/resources/{resource_id}/metadata")
    @app.get("/api/resources/{resource_id}/metadata")
    async def refresh_metadata(
        resource_id: str, request: Request, session=Depends(database, scope="function")
    ):
        record = get_research(session, resource_id, "resource")
        cache = next(
            (
                item
                for item in session.scalars(
                    select(ImportPreview)
                    .where(ImportPreview.user_id == LOCAL_USER, ImportPreview.kind == "youtube_cache")
                    .order_by(ImportPreview.created_at.desc())
                )
                if item.data.get("resource_id") == resource_id
            ),
            None,
        )
        stale = bool(
            cache
            and (
                cache.created_at < now() - timedelta(hours=24) or cache.data.get("url") != record.data["url"]
            )
        )
        if cache and (request.method == "GET" or not stale):
            return {**cache.data["metadata"], "stale": stale}
        if request.method == "GET":
            raise HTTPException(409, "No provider metadata is cached. Stored research remains available.")
        try:
            metadata = await integrations.youtube_metadata(record.data["url"])
        except HTTPException as error:
            if cache:
                return {**cache.data["metadata"], "stale": True, "refresh_error": error.detail}
            raise
        payload = {"resource_id": resource_id, "url": record.data["url"], "metadata": metadata}
        session.add(
            ImportPreview(user_id=LOCAL_USER, kind="youtube_cache", data=payload, digest=digest(payload))
        )
        return metadata

    @app.post("/api/interviews/evaluate")
    async def evaluate(request: dict, session=Depends(database, scope="function")):
        if request.get("consent") is not True:
            raise HTTPException(
                422, "Consent is required before sending your answer to the configured provider."
            )
        answer = request.get("answer", "")
        if not isinstance(answer, str) or not 5 <= len(answer) <= 20000:
            raise HTTPException(422, "Provide a 5-20000 character answer.")
        return await integrations.evaluate_answer(
            get_research(session, request.get("question_id", ""), "question").data, answer
        )

    return app


app = create_app()

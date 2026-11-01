import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    inspect,
    select,
)
from sqlalchemy.orm import Session

from .models import (
    Base,
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
)
from .research import DATASET_TYPES, FILES, apply_documents, digest, records, validate_documents
from .schemas import PERSONAL_SCHEMAS, PlanInput, ProgressInput
from .services import LOCAL_USER

TABLE_MODELS = [
    User,
    ResearchDocument,
    ResearchRecord,
    Plan,
    PlanLesson,
    Progress,
    StudyActivity,
    PersonalRecord,
]


def export_bundle(session: Session):
    tables = {}
    for model in TABLE_MODELS:
        entries = []
        query = select(model)
        if model in (Plan, PersonalRecord):
            query = query.where(model.user_id == LOCAL_USER)
        elif model is User:
            query = query.where(User.id == LOCAL_USER)
        elif model is PlanLesson:
            query = query.join(Plan).where(Plan.user_id == LOCAL_USER)
        elif model is Progress:
            query = query.join(PlanLesson).join(Plan).where(Plan.user_id == LOCAL_USER)
        elif model is StudyActivity:
            query = query.join(Progress).join(PlanLesson).join(Plan).where(Plan.user_id == LOCAL_USER)
        for item in session.scalars(query):
            entries.append(
                {
                    column.name: value.isoformat()
                    if isinstance(value := getattr(item, column.name), datetime)
                    else value
                    for column in model.__table__.columns
                }
            )
        tables[model.__tablename__] = entries
    return {"format": "engineering-academy-backup", "version": 1, "tables": tables}


def validate_backup(payload: dict, research_root: Path):
    from .dsa import CodingSession

    if not isinstance(payload, dict):
        raise HTTPException(422, "Backup must be a JSON object.")
    if (
        payload.get("format") != "engineering-academy-backup"
        or payload.get("version") != 1
        or set(payload) != {"format", "version", "tables"}
    ):
        raise HTTPException(422, "Unsupported backup format.")
    tables = payload["tables"]
    if not isinstance(tables, dict):
        raise HTTPException(422, "Backup tables must be an object.")
    if set(tables) != {model.__tablename__ for model in TABLE_MODELS}:
        raise HTTPException(422, "Backup tables are incomplete or unknown.")
    for model in TABLE_MODELS:
        ids = set()
        if not isinstance(tables[model.__tablename__], list) or len(tables[model.__tablename__]) > 10000:
            raise HTTPException(422, "Backup collection is invalid or exceeds 10000 records.")
        for row in tables[model.__tablename__]:
            if not isinstance(row, dict):
                raise HTTPException(422, "Backup rows must be objects.")
            if set(row) != {column.name for column in model.__table__.columns}:
                raise HTTPException(422, "Backup record columns do not match this schema.")
            for column in model.__table__.columns:
                value = row[column.name]
                if value is None:
                    if not column.nullable:
                        raise HTTPException(422, "Null in required backup field.")
                    continue
                if isinstance(column.type, Boolean) and not isinstance(value, bool):
                    raise HTTPException(422, "Invalid backup Boolean.")
                if isinstance(column.type, Integer) and (
                    not isinstance(value, int) or isinstance(value, bool)
                ):
                    raise HTTPException(422, "Invalid backup integer.")
                if isinstance(column.type, DateTime):
                    datetime.fromisoformat(value)
                if isinstance(column.type, String) and (
                    not isinstance(value, str) or column.type.length and len(value) > column.type.length
                ):
                    raise HTTPException(422, "Invalid backup text field.")
                if isinstance(column.type, JSON) and not isinstance(value, dict):
                    raise HTTPException(422, "Backup data envelopes must be objects.")
            primary_key = tuple(row[column.name] for column in model.__table__.columns if column.primary_key)
            if primary_key in ids:
                raise HTTPException(422, "Duplicate backup ID.")
            ids.add(primary_key)
            if "user_id" in row and row["user_id"] != LOCAL_USER or model is User and row["id"] != LOCAL_USER:
                raise HTTPException(422, "This local workspace cannot import another user's records.")
            if model is PersonalRecord:
                if row["kind"] not in set(PERSONAL_SCHEMAS) | {"review"}:
                    raise HTTPException(422, "Unknown personal record kind.")
                if row["kind"] in PERSONAL_SCHEMAS:
                    data = dict(row["data"])
                    if row["kind"] == "attempt":
                        for key in ("track_id", "skill_ids", "method"):
                            data.pop(key, None)
                    PERSONAL_SCHEMAS[row["kind"]].model_validate(data)
            elif model is Plan:
                PlanInput.model_validate(row["config"])
                if row["status"] not in ("active", "paused") or row["track_id"] != row["config"]["track_id"]:
                    raise HTTPException(422, "Invalid plan configuration.")
            elif model is Progress:
                ProgressInput.model_validate(
                    {key: value for key, value in row.items() if key not in ("slot_id", "updated_at")}
                )
            elif model is StudyActivity:
                datetime.fromisoformat(row["day"])
                if row["minutes"] < 0:
                    raise HTTPException(422, "Negative study activity.")
    if [row["id"] for row in tables["users"]] != [LOCAL_USER]:
        raise HTTPException(422, "Backup must contain exactly the local learner.")
    for model in TABLE_MODELS:
        for column in model.__table__.columns:
            for foreign in column.foreign_keys:
                targets = {row[foreign.column.name] for row in tables[foreign.column.table.name]}
                if any(
                    row[column.name] is not None and row[column.name] not in targets
                    for row in tables[model.__tablename__]
                ):
                    raise HTTPException(422, "Backup contains an unresolved relationship.")
    documents = {row["name"]: row["data"] for row in tables["research_documents"]}
    validate_documents(documents, research_root, allow_partial=bool(set(FILES) - set(documents)))
    expected = {data["id"]: (kind, data) for _, kind, data in records(documents)}
    if {row["id"] for row in tables["research_records"]} != set(expected):
        raise HTTPException(422, "Backup research index is incomplete.")
    for row in tables["research_records"]:
        if row["id"] not in expected or expected[row["id"]] != (row["kind"], row["data"]):
            raise HTTPException(422, "Backup research index is inconsistent with its source documents.")
    for row in tables["research_documents"]:
        if row["digest"] != digest(row["data"]) or row["version"] != row["data"]["research_version"]:
            raise HTTPException(422, "Backup research version or digest is inconsistent.")
    people = {item["id"]: item for item in tables["personal_records"]}
    lesson_ids = {item["id"] for item in tables["plan_lessons"]}

    def research_kind(rid, kind):
        return expected.get(rid, (None,))[0] == kind

    for row in tables["personal_records"]:
        data = row["data"]
        if row["kind"] == "job":
            if (
                people.get(data["company_id"], {}).get("kind") != "company"
                or row["parent_id"] != data["company_id"]
            ):
                raise HTTPException(422, "Backup job employer reference is invalid.")
            if any(
                not research_kind(rid, "skill")
                for rid in data["required_skill_ids"] + data["preferred_skill_ids"]
            ):
                raise HTTPException(422, "Backup job skill reference is invalid.")
        if row["kind"] == "project" and (
            any(not research_kind(rid, "track") for rid in data["track_ids"])
            or any(not research_kind(rid, "skill") for rid in data["skill_ids"])
        ):
            raise HTTPException(422, "Backup project reference is invalid.")
        if row["kind"] == "note" and data["target_type"] != "general":
            valid = (
                data["target_id"] in lesson_ids
                if data["target_type"] == "lesson"
                else research_kind(data["target_id"], "resource")
                if data["target_type"] == "resource"
                else people.get(data["target_id"], {}).get("kind") == data["target_type"]
            )
            if not valid:
                raise HTTPException(422, "Backup note attachment is invalid.")
        if row["kind"] in ("attempt", "review") and data["question_id"] not in {
            rid for rid, (kind, _) in expected.items() if kind == "question"
        }:
            raise HTTPException(422, "Backup question reference is invalid.")
        if row["kind"] == "attempt" and (
            data.get("track_id") != expected[data["question_id"]][1]["track_id"]
            or data.get("skill_ids") != expected[data["question_id"]][1]["skill_ids"]
            or data.get("method") != "rubric_self_assessment"
        ):
            raise HTTPException(422, "Backup attempt metadata is inconsistent.")
        if row["kind"] == "coding_session":
            from .dsa import sample_checks

            state = CodingSession.model_validate(data)
            if any(
                not research_kind(qid, "question") or expected[qid][1].get("track_id") != "track-dsa"
                for qid in state.question_ids
            ):
                raise HTTPException(422, "Backup coding session question reference is invalid.")
            for entry in state.submissions:
                qid = entry["answer"]["question_id"]
                if entry["sample_checks"] != sample_checks(expected[qid][1], entry["answer"]["outputs"]):
                    raise HTTPException(422, "Backup coding sample checks are inconsistent.")
        if row["kind"] in ("resource", "competency") and (
            row["ref_key"] != row["research_ref"]
            or expected.get(row["research_ref"], (None,))[0]
            != ("resource" if row["kind"] == "resource" else "skill")
        ):
            raise HTTPException(422, "Backup assessment reference is invalid.")
    return tables


def preview_import(session: Session, kind: str, payload: dict, research_root: Path):
    if not isinstance(payload, dict):
        raise HTTPException(422, "Import must be a JSON object.")
    pending = [(payload, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > 40:
            raise HTTPException(422, "Import nesting exceeds 40 levels.")
        if isinstance(value, dict):
            pending.extend((child, depth + 1) for child in value.values())
        elif isinstance(value, list):
            pending.extend((child, depth + 1) for child in value)
    if kind == "research":
        updates = payload.get("datasets", {})
        if not updates:
            if payload.get("dataset_type"):
                candidates = [
                    name
                    for name in FILES
                    if payload.get("dataset_type") == DATASET_TYPES[name]
                    and (not name.startswith("CURRICULUM") or str(payload.get("plan_days")) in name)
                ]
                if len(candidates) == 1:
                    updates = {candidates[0]: payload}
            if not updates:
                raise HTTPException(422, "Supply a dataset envelope or a datasets filename map.")
        current_documents = {doc.name: doc.data for doc in session.scalars(select(ResearchDocument))}
        merged = dict(current_documents)
        merged.update(updates)
        indexed = validate_documents(merged, research_root)
        if {item.id for item in session.scalars(select(ResearchRecord))} - {
            record["id"] for _, _, record in indexed
        }:
            raise HTTPException(
                422,
                "Research updates cannot remove historical IDs. Retain existing entities and flag outdated material separately.",
            )
        counts = {"added": 0, "updated": 0, "unchanged": 0}
        for _, _, record in indexed:
            current = session.get(ResearchRecord, record["id"])
            counts["added" if not current else "updated" if current.data != record else "unchanged"] += 1
        data = {"datasets": merged, "base_digest": digest(current_documents)}
    elif kind == "personal":
        tables = validate_backup(payload, research_root)
        counts = {key: len(value) for key, value in tables.items()}
        data = {"payload": payload, "base_digest": digest(export_bundle(session))}
    else:
        raise HTTPException(422, "Import kind must be research or personal.")
    preview = ImportPreview(user_id=LOCAL_USER, kind=kind, data=data, digest=digest(data))
    session.add(preview)
    session.flush()
    return {
        "id": preview.id,
        "counts": counts,
        "kind": kind,
        "versions": {name: value["research_version"] for name, value in data.get("datasets", {}).items()},
        "warning": "Preview only. Apply requires explicit confirmation; research changes do not replace personal progress. Personal backup import merges matching IDs atomically.",
    }


def apply_import(session: Session, preview_id: str, research_root: Path):
    preview = session.get(ImportPreview, preview_id)
    if not preview or preview.user_id != LOCAL_USER:
        raise HTTPException(404, "Import preview not found.")
    if preview.applied or preview.created_at < now() - timedelta(minutes=30):
        raise HTTPException(409, "Preview expired or already applied.")
    if digest(preview.data) != preview.digest:
        raise HTTPException(422, "Import preview integrity check failed.")
    if preview.kind == "research":
        if (
            digest({doc.name: doc.data for doc in session.scalars(select(ResearchDocument))})
            != preview.data["base_digest"]
        ):
            raise HTTPException(409, "Research changed since preview. Generate a new preview.")
        result = apply_documents(session, preview.data["datasets"], research_root)
    else:
        if digest(export_bundle(session)) != preview.data["base_digest"]:
            raise HTTPException(409, "Personal data changed since preview. Generate a new preview.")
        tables = validate_backup(preview.data["payload"], research_root)
        for model in TABLE_MODELS:
            for row in tables[model.__tablename__]:
                values = dict(row)
                for column in model.__table__.columns:
                    if isinstance(column.type, DateTime):
                        values[column.name] = datetime.fromisoformat(values[column.name])
                if model is PersonalRecord and values["parent_id"]:
                    values["parent_id"] = None
                session.merge(model(**values))
            session.flush()
        for row in tables["personal_records"]:
            session.get(PersonalRecord, row["id"]).parent_id = row["parent_id"]
        result = {"merged": sum(map(len, tables.values()))}
    preview.applied = True
    preview.data = {"applied": True}
    return result


def sqlite_backup(path: Path) -> bytes:
    with tempfile.TemporaryDirectory(prefix="academy-backup-") as directory:
        snapshot = Path(directory) / "snapshot.sqlite3"
        with closing(sqlite3.connect(path)) as original, closing(sqlite3.connect(snapshot)) as target:
            original.backup(target)
            target.execute("DELETE FROM import_previews WHERE kind != 'youtube_cache'")
            target.commit()
            target.execute("VACUUM")
        return snapshot.read_bytes()


def restore_sqlite(engine, path: Path, data: bytes, research_root: Path):
    if not data.startswith(b"SQLite format 3\x00"):
        raise HTTPException(422, "Not a SQLite backup.")
    with tempfile.TemporaryDirectory(prefix="academy-restore-") as directory:
        candidate = Path(directory) / "candidate.sqlite3"
        candidate.write_bytes(data)
        try:
            with closing(sqlite3.connect(f"file:{candidate.as_posix()}?mode=ro", uri=True)) as connection:
                connection.execute("PRAGMA trusted_schema=OFF")
                if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise HTTPException(422, "SQLite integrity check failed.")
                objects = connection.execute(
                    "SELECT name, type FROM sqlite_master WHERE type IN ('table','trigger','view')"
                ).fetchall()
                names = {name for name, kind in objects if kind == "table"}
                if names != set(Base.metadata.tables) | {"alembic_version"} or any(
                    kind != "table" for _, kind in objects
                ):
                    raise HTTPException(422, "Unknown schema, trigger or view in backup.")
                revision = connection.execute("SELECT version_num FROM alembic_version").fetchall()
                if revision not in ([("0001",)], [("0002",)]):
                    raise HTTPException(422, "Backup migration version is incompatible.")
                if connection.execute("PRAGMA foreign_key_check").fetchall():
                    raise HTTPException(422, "Backup relationships are inconsistent.")
                for table in Base.metadata.sorted_tables:
                    info = connection.execute(f'PRAGMA table_xinfo("{table.name}")').fetchall()
                    columns = {row[1] for row in info}
                    if columns != set(table.columns.keys()):
                        raise HTTPException(422, "Backup columns differ from the application schema.")
                    primary = list(table.primary_key.columns.keys())
                    for row in info:
                        column = table.columns[row[1]]
                        if (
                            row[2].upper() != column.type.compile(dialect=engine.dialect).upper()
                            or bool(row[3]) != (not column.nullable)
                            or row[6] != 0
                            or row[5] != (primary.index(row[1]) + 1 if row[1] in primary else 0)
                        ):
                            raise HTTPException(422, "Backup column types or primary constraints differ.")
                    actual_foreign = {
                        (row[3], row[2], row[4], row[6])
                        for row in connection.execute(f'PRAGMA foreign_key_list("{table.name}")')
                    }
                    expected_foreign = {
                        (
                            column.name,
                            foreign.column.table.name,
                            foreign.column.name,
                            foreign.ondelete or "NO ACTION",
                        )
                        for column in table.columns
                        for foreign in column.foreign_keys
                    }
                    if actual_foreign != expected_foreign:
                        raise HTTPException(422, "Backup foreign-key constraints differ.")
            from .database import make_database

            candidate_engine, factory = make_database("sqlite:///" + str(candidate))
            try:
                inspector = inspect(candidate_engine)

                def normalize(value):
                    return "".join(value.lower().split()).replace('"', "")

                for table in Base.metadata.sorted_tables:
                    expected_unique = {
                        tuple(constraint.columns.keys())
                        for constraint in table.constraints
                        if isinstance(constraint, UniqueConstraint)
                    }
                    actual_unique = {
                        tuple(constraint["column_names"])
                        for constraint in inspector.get_unique_constraints(table.name)
                    }
                    expected_checks = {
                        normalize(str(constraint.sqltext))
                        for constraint in table.constraints
                        if isinstance(constraint, CheckConstraint)
                    }
                    actual_checks = {
                        normalize(constraint["sqltext"])
                        for constraint in inspector.get_check_constraints(table.name)
                    }
                    if revision == [("0001",)] and table.name == "personal_records":
                        expected_checks = {
                            normalize(
                                "kind IN ('note','resource','competency','company','job','project','attempt','review','settings')"
                            )
                        }
                    if expected_unique != actual_unique or expected_checks != actual_checks:
                        raise HTTPException(422, "Backup uniqueness or check constraints differ.")
                with factory() as session:
                    validate_backup(export_bundle(session), research_root)
            finally:
                candidate_engine.dispose()
            if revision == [("0001",)]:
                from .database import migrate

                migrate("sqlite:///" + str(candidate))
            # Preserve a recovery copy before replacing the active database.
            recovery = path.with_suffix(".pre-restore.sqlite3")
            recovery.write_bytes(sqlite_backup(path))
            engine.dispose()
            with closing(sqlite3.connect(candidate)) as original, closing(sqlite3.connect(path)) as target:
                original.backup(target)
        except (sqlite3.Error, ValueError, KeyError, TypeError, RecursionError) as error:
            raise HTTPException(422, "Invalid or incompatible SQLite backup.") from error

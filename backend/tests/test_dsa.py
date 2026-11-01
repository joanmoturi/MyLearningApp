import copy
import json
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import select
from test_workspace import HEADERS, RESEARCH

from academy.database import migrate
from academy.dsa import DIMENSIONS
from academy.main import create_app
from academy.models import PersonalRecord, ResearchDocument, now

QID = "question-dsa-01"


def start(client, **changes):
    response = client.post(
        "/api/dsa/sessions",
        headers=HEADERS,
        json={"mode": "blind", "minutes": 20, "question_id": QID, **changes},
    )
    assert response.status_code == 200, response.text
    return response.json()


def submission(client, session_id, qid=QID, **changes):
    answer = {
        "question_id": qid,
        "code": "function solve(n) { return n*(n+1)/2; }",
        "clarification": "Nonnegative bounded integers.",
        "approach": "Sum lengths one through n.",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "tradeoffs": "Bounded integer model.",
        "outputs": [0, 10, 55],
        "ratings": dict.fromkeys(DIMENSIONS, 4),
        "solved": True,
        "elapsed_seconds": 15,
        **changes,
    }
    return client.post(f"/api/dsa/sessions/{session_id}/submit", headers=HEADERS, json=answer)


@pytest.mark.parametrize("days", [14, 30, 60])
def test_dsa_curriculum_and_reserved_routine(workspace, days):
    client, _, _ = workspace
    result = client.post(
        "/api/plans",
        headers=HEADERS,
        json={"track_id": "track-dsa", "duration_days": days, "daily_minutes": 180},
    )
    assert result.status_code == 200, result.text
    lessons = result.json()["lessons"]
    assert len(lessons) == days
    lesson = client.get("/api/lessons/" + lessons[0]["id"]).json()
    assert lesson["coding_exercises"] and lesson["example_implementation"]
    assert lesson["progress"]["status"] == "not_started"
    companion = client.post(
        "/api/plans",
        headers=HEADERS,
        json={
            "track_id": "track-cloud",
            "duration_days": days,
            "daily_minutes": 180,
            "dsa_practice_minutes": 45,
        },
    ).json()
    first = client.get("/api/lessons/" + companion["lessons"][0]["id"]).json()
    assert sum(first["time_budget_minutes"].values()) == 180
    assert first["time_budget_minutes"]["coding_practice"] == 45
    assert min(first["time_budget_minutes"].values()) >= 0
    assert (
        client.post(
            "/api/plans",
            headers=HEADERS,
            json={
                "track_id": "track-dsa",
                "dsa_practice_minutes": 30,
            },
        ).status_code
        == 422
    )


def test_blind_draft_submission_and_restore(workspace):
    client, app, url = workspace
    current = start(client)
    assert "hints" not in current["question"] and "solution_code" not in current["question"]
    assert client.get("/api/dsa").json()["analytics"]["questions_attempted"] == 0
    draft = {"code": "function solve(n) { return n*(n+1)/2; }", "approach": "A saved original approach."}
    assert client.patch(f"/api/dsa/sessions/{current['id']}", headers=HEADERS, json=draft).status_code == 200
    assert client.get(f"/api/dsa/sessions/{current['id']}").json()["draft"]["code"] == draft["code"]
    assert client.get("/api/dsa").json()["analytics"]["states"][QID] == "attempted"
    response = submission(client, current["id"])
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "completed"
    assert all(row["passed"] for row in response.json()["feedback"]["sample_checks"])
    assert submission(client, current["id"]).status_code == 409
    metrics = client.get("/api/dsa").json()["analytics"]
    assert metrics["solved_independently"] == 1 and metrics["states"][QID] != "mastered"
    bad = client.get("/api/data/export").json()
    record = next(r for r in bad["tables"]["personal_records"] if r["id"] == current["id"])
    record["data"]["submissions"][0]["sample_checks"][0]["passed"] = False
    assert (
        client.post(
            "/api/data/preview", headers=HEADERS, json={"kind": "personal", "payload": bad}
        ).status_code
        == 422
    )
    record["data"]["submissions"][0]["sample_checks"][0]["passed"] = True
    record["data"]["submissions"][0]["hint_used"] = "false"
    assert (
        client.post(
            "/api/data/preview", headers=HEADERS, json={"kind": "personal", "payload": bad}
        ).status_code
        == 422
    )
    record["data"]["submissions"][0]["hint_used"] = False
    record["data"]["started_at"] += "+00:00"
    record["data"]["deadline_at"] += "+00:00"
    assert (
        client.post(
            "/api/data/preview", headers=HEADERS, json={"kind": "personal", "payload": bad}
        ).status_code
        == 422
    )
    snapshot = client.get("/api/data/backup").content
    extra = start(client)
    restored = client.post(
        "/api/data/restore", content=snapshot, headers={**HEADERS, "X-Academy-Confirm": "restore"}
    )
    assert restored.status_code == 200, restored.text
    assert client.get(f"/api/dsa/sessions/{extra['id']}").status_code == 404
    with TestClient(create_app(url, RESEARCH)) as restarted:
        assert restarted.get("/api/dsa").json()["analytics"]["solved_independently"] == 1
        assert restarted.get(f"/api/dsa/sessions/{current['id']}").json()["status"] == "completed"


def test_help_failed_checks_and_expired_timer_are_honest(workspace):
    client, app, _ = workspace
    assisted = start(client)
    client.post(f"/api/dsa/sessions/{assisted['id']}/help/hint", headers=HEADERS)
    assert submission(client, assisted["id"]).status_code == 200
    assert client.get("/api/dsa").json()["analytics"]["states"][QID] == "solved_with_assistance"
    failed = start(client)
    submission(client, failed["id"], outputs=[False, 10, 55])
    assert client.get("/api/dsa").json()["analytics"]["states"][QID] == "needs_revision"
    expired = start(client)
    with app.state.factory.begin() as session:
        record = session.get(PersonalRecord, expired["id"])
        value = copy.deepcopy(record.data)
        value["started_at"] = (now() - timedelta(minutes=30)).isoformat()
        value["deadline_at"] = (now() - timedelta(minutes=10)).isoformat()
        # Derive the exact deadline from the stored start; no wall-clock drift.
        from datetime import datetime

        value["deadline_at"] = (
            datetime.fromisoformat(value["started_at"]) + timedelta(minutes=20)
        ).isoformat()
        record.data = value
    result = submission(client, expired["id"])
    assert result.json()["submissions"][0]["late"] is True
    assert client.get("/api/dsa").json()["analytics"]["solved_independently"] == 0
    assert client.get("/api/personal/review").json()


def test_company_focus_mock_order_and_unknown_policy(workspace):
    client, _, _ = workspace
    company = client.post(
        "/api/dsa/sessions",
        headers=HEADERS,
        json={
            "mode": "company",
            "minutes": 45,
            "company_profile_id": "profile-dsa-openai",
            "count": 2,
        },
    ).json()
    assert all(
        "senior" in client.get("/api/catalog/question/" + qid).json()["skill_ids"][0]
        for qid in company["question_ids"]
    )
    result = client.post(
        "/api/dsa/sessions",
        headers=HEADERS,
        json={
            "mode": "company",
            "minutes": 30,
            "company_profile_id": "profile-dsa-apple",
        },
    )
    assert result.status_code == 200
    profile = next(c for c in client.get("/api/dsa").json()["companies"] if c["id"] == "profile-dsa-apple")
    assert profile["interview_evidence"] == "unknown"
    mock = start(client, mode="mock", question_id=None, count=2)
    assert len(set(mock["question_ids"])) == 2
    assert submission(client, mock["id"], qid=mock["question_ids"][1]).status_code == 409
    assert submission(client, mock["id"], qid=mock["question_ids"][0], solved=False).status_code == 200
    assert client.get(f"/api/dsa/sessions/{mock['id']}").json()["current_index"] == 1


def test_mastery_requires_independent_success_on_three_dates(workspace, monkeypatch):
    import academy.dsa as dsa

    client, _, _ = workspace
    base = now()
    for _ in range(3):
        attempt = start(client)
        assert submission(client, attempt["id"]).status_code == 200
    assert client.get("/api/dsa").json()["analytics"]["states"][QID] != "mastered"
    for day in (1, 2):
        monkeypatch.setattr(dsa, "now", lambda day=day: base + timedelta(days=day))
        attempt = start(client)
        assert submission(client, attempt["id"]).status_code == 200
    assert client.get("/api/dsa").json()["analytics"]["states"][QID] == "mastered"


def test_manual_revision_preserves_attempt_and_next_lesson(workspace):
    client, _, _ = workspace
    initial = client.get("/api/dsa").json()["analytics"]
    assert initial["next_question_id"] == QID
    assert initial["next_lesson"]["id"] == "lesson-dsa-30-01"
    attempt = start(client)
    assert (
        client.post(f"/api/dsa/sessions/{attempt['id']}/revision/{QID}", headers=HEADERS).status_code == 422
    )
    submission(client, attempt["id"])
    assert (
        client.post(f"/api/dsa/sessions/{attempt['id']}/revision/{QID}", headers=HEADERS).status_code == 200
    )
    analytics = client.get("/api/dsa").json()["analytics"]
    assert analytics["states"][QID] == "needs_revision" and analytics["attempts"] == 1
    new = start(client)
    submission(client, new["id"])
    assert client.get("/api/dsa").json()["analytics"]["states"][QID] == "solved_independently"


def test_dsa_research_contracts_and_original_data_unchanged():
    root = RESEARCH / "dsa"
    schema = json.loads((root / "DSA_PACKAGE_SCHEMA.json").read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for name in (
        "DSA_SKILL_MATRIX",
        "DSA_RESOURCE_CATALOG",
        "DSA_QUESTION_BANK",
        "DSA_COMPANY_RESEARCH",
        "DSA_SOURCE_REGISTER",
        "DSA_LEARNING_DEPENDENCIES",
        "DSA_CURRICULUM_14_DAYS",
        "DSA_CURRICULUM_30_DAYS",
        "DSA_CURRICULUM_60_DAYS",
    ):
        validator.validate(json.loads((root / (name + ".json")).read_text()))
    assert len(json.loads((RESEARCH / "LEARNER_PROFILE.json").read_text())["tracks"]) == 5


def test_upgrade_existing_database_preserves_personal_research_and_notes(tmp_path):
    from alembic import command
    from alembic.config import Config

    from academy.database import BACKEND_ROOT, make_database
    from academy.models import User
    from academy.research import apply_documents, load_documents
    from academy.services import save_personal

    path = tmp_path / "existing.sqlite3"
    configuration = Config(str(BACKEND_ROOT / "alembic.ini"))
    configuration.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
    configuration.set_main_option("sqlalchemy.url", "sqlite:///" + str(path))
    command.upgrade(configuration, "0001")
    engine, factory = make_database("sqlite:///" + str(path))
    original, _ = load_documents(RESEARCH)
    original = {name: data for name, data in original.items() if not name.startswith("dsa/")}
    with factory.begin() as session:
        session.add(User(id="local", name="Local learner"))
        session.flush()
        apply_documents(session, original, RESEARCH)
        save_personal(
            session,
            "note",
            {
                "title": "Kept personal note",
                "body": "Existing private learning data.",
                "target_type": "general",
                "target_id": None,
            },
        )
        employer = next(
            item
            for item in session.scalars(select(ResearchDocument))
            if item.name == "EMPLOYER_RESEARCH.json"
        )
        custom = copy.deepcopy(employer.data)
        custom["research_version"] = "1.0.1"
        employer.data = custom
        from academy.research import digest

        employer.digest = digest(custom)
        employer.version = "1.0.1"
    engine.dispose()
    from academy.data_management import sqlite_backup

    legacy_snapshot = sqlite_backup(path)
    with TestClient(create_app("sqlite:///" + str(path), RESEARCH)) as client:
        assert len(client.get("/api/bootstrap").json()["tracks"]) == 6
        assert client.get("/api/personal/note").json()[0]["title"] == "Kept personal note"
        exported = client.get("/api/data/export?kind=research").json()
        assert exported["datasets"]["EMPLOYER_RESEARCH.json"]["research_version"] == "1.0.1"
        assert start(client)["question"]["id"] == QID
        migrate("sqlite:///" + str(path))
        restored = client.post(
            "/api/data/restore", content=legacy_snapshot, headers={**HEADERS, "X-Academy-Confirm": "restore"}
        )
        assert restored.status_code == 200, restored.text
        assert client.get("/api/personal/note").json()[0]["title"] == "Kept personal note"
    with TestClient(create_app("sqlite:///" + str(path), RESEARCH)) as restarted:
        assert len(restarted.get("/api/bootstrap").json()["tracks"]) == 6
        assert start(restarted)["question"]["id"] == QID

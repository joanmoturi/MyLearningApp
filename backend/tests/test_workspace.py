import copy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from academy.main import create_app
from academy.schemas import CompetencyInput

RESEARCH = Path(__file__).resolve().parents[2] / "research"
HEADERS = {"X-Academy-Client": "local-workspace"}


def first_lesson(client):
    plan = client.get("/api/plans").json()[0]
    return client.get("/api/plans/" + plan["id"]).json()["lessons"][0]["id"]


def test_seed_and_migration(workspace):
    client, app, _ = workspace
    assert client.get("/api/health").json()["status"] == "ok"
    assert len(client.get("/api/bootstrap").json()["tracks"]) == 5
    assert client.get("/api/catalog/resource").json()["total"] == 54
    assert "alembic_version" in inspect(app.state.engine).get_table_names()
    assert client.get("/api/dashboard").json()["completed_lessons"] == 0


def test_lesson_open_never_completes_and_progress_is_evidenced(workspace):
    client, _, _ = workspace
    slot = first_lesson(client)
    assert client.get("/api/lessons/" + slot).json()["progress"]["status"] == "not_started"
    assert client.patch("/api/progress/" + slot, headers=HEADERS, json={"practical": True}).status_code == 422
    payload = {
        "video": True,
        "reading": True,
        "practical": True,
        "knowledge": True,
        "watched_minutes": 35,
        "study_minutes": 100,
        "evidence": "Local invariant tests pass with the failure fixture.",
        "answers": {"0": "The chosen boundary preserves isolation."},
    }
    assert (
        client.patch("/api/progress/" + slot, headers=HEADERS, json=payload).json()["status"]
        == "fully_completed"
    )
    assert client.get("/api/dashboard").json()["hours_studied"] == 2.2
    assert client.get("/api/dashboard").json()["learning_streak"] == 1
    assert client.get("/api/personal/competency").json() == []


def test_plan_recalculation_and_switch_preserve_work(workspace):
    client, _, _ = workspace
    slot = first_lesson(client)
    client.patch("/api/progress/" + slot, headers=HEADERS, json={"video": True, "watched_minutes": 20})
    plan_id = client.get("/api/lessons/" + slot).json()["plan_id"]
    result = client.patch(
        "/api/plans/" + plan_id,
        headers=HEADERS,
        json={"track_id": "track-swe", "duration_days": 14, "daily_minutes": 180},
    ).json()
    assert slot in [item["id"] for item in result["lessons"]]
    assert client.get("/api/lessons/" + slot).json()["progress"]["watched_minutes"] == 20
    result = client.post(
        "/api/plans",
        headers=HEADERS,
        json={"track_id": "track-ai", "duration_days": 14, "daily_minutes": 240},
    ).json()
    assert all(item["estimated_total_study_minutes"] == 240 for item in result["lessons"])
    assert client.get("/api/lessons/" + slot).json()["progress"]["video"] is True


def test_move_cascades_and_rejects_forward_prerequisite(workspace):
    client, _, _ = workspace
    plan = client.get("/api/plans/" + client.get("/api/plans").json()[0]["id"]).json()
    items = plan["lessons"]
    assert client.patch("/api/lessons/" + items[1]["id"], headers=HEADERS, json={"day": 1}).status_code == 409
    assert client.patch("/api/lessons/" + items[1]["id"], headers=HEADERS, json={"day": 5}).status_code == 200
    updated = client.get("/api/plans/" + plan["id"]).json()
    assert updated["lessons"][2]["day"] == 6
    assert (
        client.post(
            "/api/plans/" + plan["id"] + "/custom",
            headers=HEADERS,
            json={
                "topic": "Custom queue drill",
                "objectives": "Understand bounded processing",
                "exercise": "Measure a local queue failure.",
            },
        ).status_code
        == 200
    )


def test_notes_career_analysis_and_competency(workspace):
    client, _, _ = workspace
    note = client.post(
        "/api/personal/note",
        headers=HEADERS,
        json={"title": "Boundary notes", "body": "# Notes\n\n<script>alert(1)</script>"},
    ).json()
    assert note["title"] == "Boundary notes"
    company = client.post(
        "/api/personal/company",
        headers=HEADERS,
        json={"name": "Example employer", "career_url": "https://example.com/careers"},
    ).json()
    description = (
        "Requirements\nSenior Python engineer with AWS and Terraform ownership.\nPreferred\nKubernetes"
    )
    suggestions = client.post("/api/jobs/analyze", headers=HEADERS, json={"description": description}).json()
    assert "skill-python" in suggestions["required_skill_ids"]
    assert "skill-kubernetes" in suggestions["preferred_skill_ids"]
    job = client.post(
        "/api/personal/job",
        headers=HEADERS,
        json={
            "company_id": company["id"],
            "title": "Senior Engineer",
            "description": description,
            "required_skill_ids": suggestions["required_skill_ids"],
            "preferred_skill_ids": suggestions["preferred_skill_ids"],
        },
    ).json()
    assert client.get("/api/jobs/" + job["id"] + "/gaps").json()["rows"][0]["status"] == "not_assessed"
    assert client.patch("/api/skills/skill-python", headers=HEADERS, json={"level": 5}).status_code == 422
    assert (
        client.patch(
            "/api/skills/skill-python",
            headers=HEADERS,
            json={"level": 4, "evidence": "Implemented a tested Python service independently."},
        ).status_code
        == 200
    )
    rows = client.get("/api/jobs/" + job["id"] + "/gaps").json()["rows"]
    assert next(row for row in rows if row["skill_id"] == "skill-python")["status"] == "demonstrated"
    assert client.delete("/api/personal/company/" + company["id"], headers=HEADERS).status_code == 409


def test_interview_revision_project_and_optional_fallback(workspace):
    client, _, _ = workspace
    question = client.get("/api/catalog/question?limit=1").json()["items"][0]
    assert (
        client.post(
            "/api/attempts",
            headers=HEADERS,
            json={
                "question_id": question["id"],
                "answer": "I would measure the invariant before choosing a boundary.",
                "score": 3,
                "confidence": 2,
            },
        ).status_code
        == 200
    )
    assert len(client.get("/api/personal/review").json()) == 1
    assert client.post("/api/projects/project-swe-08/start", headers=HEADERS).json()["status"] == "active"
    assert client.post("/api/resources/resource-system-design/metadata", headers=HEADERS).status_code == 409
    assert (
        client.post(
            "/api/interviews/evaluate",
            headers=HEADERS,
            json={"question_id": question["id"], "answer": "This answer remains local."},
        ).status_code
        == 422
    )


def test_research_preview_atomicity_and_personal_preservation(workspace):
    client, _, _ = workspace
    client.post(
        "/api/personal/note",
        headers=HEADERS,
        json={"title": "Keep me", "body": "Personal notes must survive imports."},
    )
    package = client.get("/api/data/export?kind=research").json()
    package["datasets"]["RESOURCE_CATALOG.json"]["research_version"] = "1.0.1"
    result = client.post("/api/data/preview", headers=HEADERS, json={"kind": "research", "payload": package})
    assert result.status_code == 200, result.text
    assert (
        client.post(
            "/api/data/apply/" + result.json()["id"], headers=HEADERS, json={"confirm": True}
        ).status_code
        == 200
    )
    assert client.get("/api/personal/note").json()[0]["title"] == "Keep me"
    bad = copy.deepcopy(package)
    bad["datasets"]["RESOURCE_CATALOG.json"]["resources"][0]["id"] = "resource-missing-reference"
    assert (
        client.post(
            "/api/data/preview", headers=HEADERS, json={"kind": "research", "payload": bad}
        ).status_code
        == 422
    )


def test_backup_restore_and_restart(workspace):
    client, app, url = workspace
    client.post(
        "/api/personal/note", headers=HEADERS, json={"title": "Persistent note", "body": "Original content."}
    )
    question = client.get("/api/catalog/question?limit=1").json()["items"][0]
    client.post(
        "/api/attempts",
        headers=HEADERS,
        json={
            "question_id": question["id"],
            "answer": "A measured, evidence-backed answer.",
            "score": 5,
            "confidence": 2,
        },
    )
    exported = client.get("/api/data/export").json()
    preview = client.post(
        "/api/data/preview", headers=HEADERS, json={"kind": "personal", "payload": exported}
    )
    assert preview.status_code == 200, preview.text
    backup = client.get("/api/data/backup").content
    client.post(
        "/api/personal/note", headers=HEADERS, json={"title": "Later note", "body": "Not in snapshot."}
    )
    restore = client.post(
        "/api/data/restore",
        content=backup,
        headers={**HEADERS, "X-Academy-Confirm": "restore", "Content-Type": "application/octet-stream"},
    )
    assert restore.status_code == 200, restore.text
    assert len(client.get("/api/personal/note").json()) == 1
    with TestClient(create_app(url, RESEARCH)) as restarted:
        assert restarted.get("/api/personal/note").json()[0]["title"] == "Persistent note"
    assert (
        client.post(
            "/api/data/restore", headers={**HEADERS, "X-Academy-Confirm": "restore"}, content=b"not sqlite"
        ).status_code
        == 422
    )


def test_local_security_boundary(workspace):
    client, _, _ = workspace
    assert client.post("/api/personal/note", json={"title": "No header"}).status_code == 403
    assert client.get("/api/bootstrap", headers={"Origin": "https://evil.example"}).status_code == 403
    assert (
        client.post(
            "/api/personal/company",
            headers=HEADERS,
            json={"name": "Unsafe", "website": "javascript:alert(1)"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/personal/company",
            headers=HEADERS,
            json={"name": "Unsafe", "website": "https://user:password@example.com"},
        ).status_code
        == 422
    )
    assert (
        client.post("/api/data/preview", headers=HEADERS, content=b"x" * (20 * 1024 * 1024 + 1)).status_code
        == 413
    )
    with pytest.raises(ValueError):
        CompetencyInput(level=6, evidence="CV")

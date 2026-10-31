import asyncio
import copy
import shutil
import sqlite3
from contextlib import closing

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from test_workspace import HEADERS, RESEARCH, first_lesson

from academy import integrations
from academy.main import create_app


@pytest.mark.parametrize("track", ["swe", "cloud", "devops", "ai", "agent"])
@pytest.mark.parametrize("days", [14, 30, 60])
def test_every_research_plan_and_budget(workspace, track, days):
    client, _, _ = workspace
    response = client.post(
        "/api/plans",
        headers=HEADERS,
        json={
            "track_id": "track-" + track,
            "duration_days": days,
            "daily_minutes": 180,
            "intensity": "practical",
        },
    )
    assert response.status_code == 200, response.text
    plan = response.json()
    assert len(plan["lessons"]) == days
    assert all(item["estimated_total_study_minutes"] == 180 for item in plan["lessons"])
    assert len({item["research_id"] for item in plan["lessons"]}) == days


def test_later_started_lesson_and_annotations_survive_recalculation(workspace):
    client, _, _ = workspace
    plan_id = client.get("/api/plans").json()[0]["id"]
    plan = client.get("/api/plans/" + plan_id).json()
    later = plan["lessons"][9]["id"]
    annotated = plan["lessons"][0]["id"]
    client.patch("/api/progress/" + later, headers=HEADERS, json={"video": True, "watched_minutes": 20})
    client.post(
        "/api/personal/note",
        headers=HEADERS,
        json={
            "title": "Attached note",
            "body": "Must survive.",
            "target_type": "lesson",
            "target_id": annotated,
        },
    )
    updated = client.patch(
        "/api/plans/" + plan_id, headers=HEADERS, json={"track_id": "track-swe", "duration_days": 30}
    ).json()
    assert updated["lessons"][9]["id"] == later
    assert updated["lessons"][0]["id"] == annotated
    assert client.get("/api/data/export").status_code == 200


def test_backup_rejects_missing_index_and_stale_personal_preview(workspace):
    client, _, _ = workspace
    original = client.get("/api/data/export").json()
    bad = copy.deepcopy(original)
    bad["tables"]["research_records"].pop()
    assert (
        client.post(
            "/api/data/preview", headers=HEADERS, json={"kind": "personal", "payload": bad}
        ).status_code
        == 422
    )
    result = client.post("/api/data/preview", headers=HEADERS, json={"kind": "personal", "payload": original})
    assert result.status_code == 200, result.text
    client.post("/api/personal/note", headers=HEADERS, json={"title": "New note"})
    assert (
        client.post(
            "/api/data/apply/" + result.json()["id"], headers=HEADERS, json={"confirm": True}
        ).status_code
        == 409
    )


def test_partial_research_startup_is_explicit(tmp_path):
    root = tmp_path / "research"
    root.mkdir()
    (root / "schemas").mkdir()
    shutil.copyfile(RESEARCH / "schemas" / "package.schema.json", root / "schemas" / "package.schema.json")
    shutil.copyfile(RESEARCH / "RESOURCE_CATALOG.json", root / "RESOURCE_CATALOG.json")
    with TestClient(create_app("sqlite:///" + str(tmp_path / "partial.sqlite3"), root)) as client:
        assert client.get("/api/catalog/resource").json()["total"] == 54
        assert "LEARNER_PROFILE.json" in client.get("/api/bootstrap").json()["research_issues"]
        assert client.get("/api/plans").json() == []


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_provider_failures_remain_understandable(monkeypatch, status):
    original = httpx.AsyncClient
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status, json={"error": "provider failure"})
    )
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    monkeypatch.setenv("OPENAI_API_KEY", "test-not-a-real-key")
    monkeypatch.setenv("AI_MODEL", "test-model")
    with pytest.raises(HTTPException) as caught:
        asyncio.run(
            integrations.evaluate_answer(
                {"question": "Why?", "evaluation_rubric": "Explain evidence"}, "My local answer."
            )
        )
    assert caught.value.status_code == 502
    assert "test-not-a-real-key" not in caught.value.detail


def test_provider_timeout_and_youtube_playlist(monkeypatch):
    original = httpx.AsyncClient

    def timeout(request):
        raise httpx.ReadTimeout("not returned to the user", request=request)

    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(timeout), **kwargs)
    )
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-not-a-real-key")
    with pytest.raises(HTTPException) as caught:
        asyncio.run(integrations.youtube_metadata("https://www.youtube.com/watch?v=abcdefghijk"))
    assert caught.value.status_code == 502
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200, json={"items": [{"snippet": {"title": "Playlist"}, "contentDetails": {"itemCount": 3}}]}
        )
    )
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    result = asyncio.run(integrations.youtube_metadata("https://www.youtube.com/playlist?list=PL-example"))
    assert result["playlist_id"] == "PL-example"
    assert result["comments"] is None


def test_backup_restores_into_a_fresh_database(workspace, tmp_path):
    client, _, _ = workspace
    slot = first_lesson(client)
    client.patch("/api/progress/" + slot, headers=HEADERS, json={"video": True, "watched_minutes": 10})
    client.post("/api/personal/note", headers=HEADERS, json={"title": "Move laptops"})
    snapshot = client.get("/api/data/backup").content
    with TestClient(create_app("sqlite:///" + str(tmp_path / "fresh.sqlite3"), RESEARCH)) as fresh:
        response = fresh.post(
            "/api/data/restore", content=snapshot, headers={**HEADERS, "X-Academy-Confirm": "restore"}
        )
        assert response.status_code == 200, response.text
        assert fresh.get("/api/lessons/" + slot).json()["progress"]["watched_minutes"] == 10
        assert fresh.get("/api/personal/note").json()[0]["title"] == "Move laptops"


def test_restore_rejects_removed_database_constraints(workspace, tmp_path):
    client, _, _ = workspace
    candidate = tmp_path / "missing-constraint.sqlite3"
    candidate.write_bytes(client.get("/api/data/backup").content)
    with closing(sqlite3.connect(candidate)) as connection:
        connection.executescript(
            "DROP TABLE study_activity; CREATE TABLE study_activity(slot_id VARCHAR(100) NOT NULL,day VARCHAR(10) NOT NULL,minutes INTEGER NOT NULL,PRIMARY KEY(slot_id,day));"
        )
    response = client.post(
        "/api/data/restore",
        content=candidate.read_bytes(),
        headers={**HEADERS, "X-Academy-Confirm": "restore"},
    )
    assert response.status_code == 422
    assert "foreign-key constraints" in response.json()["detail"]


def test_metadata_cache_survives_provider_failure(workspace, monkeypatch):
    from datetime import timedelta

    from sqlalchemy import select

    from academy.models import ImportPreview, now

    client, app, _ = workspace
    rid = next(
        item["id"]
        for item in client.get("/api/catalog/resource").json()["items"]
        if item["resource_type"] == "youtube_video"
    )
    calls = []

    async def success(url):
        calls.append(url)
        return {"title": "Mocked official response", "comments": None}

    monkeypatch.setattr(integrations, "youtube_metadata", success)
    assert client.post(f"/api/resources/{rid}/metadata", headers=HEADERS).status_code == 200
    assert client.post(f"/api/resources/{rid}/metadata", headers=HEADERS).json()["stale"] is False
    assert len(calls) == 1
    with app.state.factory.begin() as session:
        session.scalar(select(ImportPreview).where(ImportPreview.kind == "youtube_cache")).created_at = (
            now() - timedelta(days=2)
        )

    async def failure(url):
        raise HTTPException(502, "Quota exhausted")

    monkeypatch.setattr(integrations, "youtube_metadata", failure)
    assert client.get(f"/api/resources/{rid}/metadata").json()["stale"] is True
    assert (
        client.post(f"/api/resources/{rid}/metadata", headers=HEADERS).json()["refresh_error"]
        == "Quota exhausted"
    )

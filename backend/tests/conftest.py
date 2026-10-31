from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from academy.main import create_app


@pytest.fixture
def workspace(tmp_path):
    research = Path(__file__).resolve().parents[2] / "research"
    url = "sqlite:///" + str(tmp_path / "academy.sqlite3")
    app = create_app(url, research)
    with TestClient(app) as client:
        yield client, app, url

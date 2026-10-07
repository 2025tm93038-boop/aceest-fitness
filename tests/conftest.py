import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import db  # noqa: E402
import app as app_module  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Flask test client wired to a fresh, isolated SQLite DB per test."""
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_db()

    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def logged_in_client(client):
    client.post("/login", data={"username": "admin", "password": "admin123"})
    return client

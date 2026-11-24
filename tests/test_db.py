import db


def test_add_and_get_client(tmp_path):
    path = tmp_path / "t.db"
    db.init_db(path)
    db.add_client("Zed", "Beginner", db_path=path)
    assert db.get_client("Zed", db_path=path)["program"] == "Beginner"
    assert db.get_client("Nobody", db_path=path) is None


def test_progress_validation_rejects_bad_values(tmp_path):
    import pytest
    path = tmp_path / "t.db"
    db.init_db(path)
    with pytest.raises(ValueError):
        db.add_progress("Zed", "2026-W01", 101, db_path=path)
    db.add_progress("Zed", "2026-W01", 70, db_path=path)
    assert db.list_progress("Zed", db_path=path)[0]["adherence"] == 70


def test_verify_user(tmp_path):
    path = tmp_path / "t.db"
    db.init_db(path)
    assert db.verify_user("admin", "admin123", db_path=path)
    assert db.verify_user("admin", "bad", db_path=path) is None

def test_home_page_lists_programs(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Fat Loss" in resp.data


def test_api_list_programs(client):
    resp = client.get("/api/programs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) == {"Fat Loss", "Muscle Gain", "Beginner"}


def test_api_get_known_program(client):
    resp = client.get("/api/programs/Fat Loss")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["program"] == "Fat Loss"
    assert "workout" in data and "diet" in data


def test_api_get_unknown_program_returns_404(client):
    resp = client.get("/api/programs/Nonexistent")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_plan_page_renders_selected_program(client):
    resp = client.get("/plan?program=Muscle Gain")
    assert resp.status_code == 200
    assert b"Muscle Gain" in resp.data


def test_clients_page_requires_login(client):
    resp = client.get("/clients", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_login_with_valid_credentials_succeeds(client):
    resp = client.post(
        "/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True
    )
    assert resp.status_code == 200
    assert resp.request.path == "/clients"


def test_login_with_invalid_credentials_fails(client):
    resp = client.post("/login", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data


def test_add_and_view_client(logged_in_client):
    resp = logged_in_client.post("/clients", data={"name": "Alice", "program": "Fat Loss"})
    assert resp.status_code == 200
    assert b"Alice" in resp.data

    detail = logged_in_client.get("/clients/Alice")
    assert detail.status_code == 200
    assert b"Fat Loss" in detail.data


def test_add_client_with_invalid_program_rejected(logged_in_client):
    resp = logged_in_client.post("/clients", data={"name": "Bob", "program": "Not A Program"})
    assert resp.status_code == 400


def test_client_detail_for_unknown_client_404s(logged_in_client):
    resp = logged_in_client.get("/clients/Ghost")
    assert resp.status_code == 404


def test_log_workout_for_existing_client(logged_in_client):
    logged_in_client.post("/clients", data={"name": "Alice", "program": "Fat Loss"})
    resp = logged_in_client.post(
        "/clients/Alice/workouts",
        data={"date": "2026-09-01", "workout_type": "Strength", "duration_min": "45", "notes": "Good session"},
    )
    assert resp.status_code == 200
    assert b"Strength" in resp.data


def test_log_workout_missing_fields_rejected(logged_in_client):
    logged_in_client.post("/clients", data={"name": "Alice", "program": "Fat Loss"})
    resp = logged_in_client.post(
        "/clients/Alice/workouts", data={"date": "", "workout_type": "", "duration_min": "abc"}
    )
    assert resp.status_code == 400


def test_log_progress_within_bounds(logged_in_client):
    logged_in_client.post("/clients", data={"name": "Alice", "program": "Fat Loss"})
    resp = logged_in_client.post(
        "/clients/Alice/progress", data={"week": "2026-W35", "adherence": "80"}
    )
    assert resp.status_code == 200
    assert b"80%" in resp.data


def test_log_progress_out_of_bounds_rejected(logged_in_client):
    logged_in_client.post("/clients", data={"name": "Alice", "program": "Fat Loss"})
    resp = logged_in_client.post(
        "/clients/Alice/progress", data={"week": "2026-W35", "adherence": "150"}
    )
    assert resp.status_code == 400


def test_pdf_report_generated_for_client(logged_in_client):
    logged_in_client.post("/clients", data={"name": "Alice", "program": "Fat Loss"})
    resp = logged_in_client.get("/clients/Alice/report.pdf")
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"
    assert resp.data[:4] == b"%PDF"


def test_adherence_chart_png_generated(logged_in_client):
    logged_in_client.post("/clients", data={"name": "Alice", "program": "Fat Loss"})
    resp = logged_in_client.get("/clients/Alice/chart.png")
    assert resp.status_code == 200
    assert resp.mimetype == "image/png"


def test_logout_clears_session(logged_in_client):
    logged_in_client.get("/logout")
    resp = logged_in_client.get("/clients", follow_redirects=False)
    assert resp.status_code == 302

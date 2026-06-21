from extensions import db


def test_health_check_returns_ok(client):
    response = client.get("/")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["message"] == "Email Classifier API is running"
    assert payload["database"] == "ok"


def test_health_check_database_failure(mocker, client):
    mocker.patch.object(db.session, "execute", side_effect=RuntimeError("connection refused"))

    response = client.get("/")
    payload = response.get_json()
    assert payload["database"].startswith("error:")

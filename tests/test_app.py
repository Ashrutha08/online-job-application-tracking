import os
import tempfile

import pytest

from app import app as flask_app


@pytest.fixture()
def client():
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config.update(
        TESTING=True,
        DATABASE=db_path,
        SECRET_KEY="test-secret",
    )
    with flask_app.test_client() as client:
        with flask_app.app_context():
            from app import init_db
            init_db()
        yield client
    os.close(db_fd)
    os.unlink(db_path)


def register_and_login(client, email="candidate@example.com"):
    client.post("/register", data={
        "name": "Test Candidate",
        "email": email,
        "password": "safe-password-123",
    }, follow_redirects=True)
    return client.post("/login", data={
        "email": email,
        "password": "safe-password-123",
    }, follow_redirects=True)


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Find your next" in response.data
    assert b"opportunity." in response.data


def test_jobs_page_shows_seeded_jobs(client):
    response = client.get("/jobs")
    assert response.status_code == 200
    assert b"Junior Python Developer" in response.data


def test_registration_and_login(client):
    response = register_and_login(client)
    assert response.status_code == 200
    assert b"Find a role that fits." in response.data


def test_applicant_must_login_to_apply(client):
    response = client.get("/apply/1", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

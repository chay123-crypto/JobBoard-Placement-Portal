import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with flask_app.test_client() as client:
        yield client


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_missing_role(client):
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_register_student_success(client):
    response = client.post("/auth/register", json={"role": "student", "email": "student1@example.com", "contact_no": "9999999999", "password": "password123", "name": "Test Student", "dept": "CSE", "dob": "2004-01-01", "year": 2, "cgpa": 8.5})
    assert response.status_code == 200
    assert "registered successfully" in response.get_json()["message"]


def test_login_wrong_password(client):
    response = client.post("/auth/login", json={"email": "nobody@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_check_auth_requires_login(client):
    response = client.get("/auth/check")
    assert response.status_code in (401, 302)

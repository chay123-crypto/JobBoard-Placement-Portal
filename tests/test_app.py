import io
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from backend.cache import cache
from backend.init_db import (
    DEMO_COMPANY_EMAIL,
    DEMO_PASSWORD,
    DEMO_STUDENT_EMAIL,
    seed_demo,
)
from backend.models.models import (
    Application,
    CompanyProfile,
    PlacementDrive,
    StudentProfile,
    User,
    db,
)

TEST_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SECRET_KEY": "test-secret",
    "ADMIN_PASSWORD": "test-admin-password",
    "CACHE_TYPE": "SimpleCache",
    "RATELIMIT_STORAGE_URI": "memory://",
    "RATELIMIT_ENABLED": False,
    "MAIL_SUPPRESS_SEND": True,
    "WTF_CSRF_ENABLED": False,
}


@pytest.fixture(scope="function")
def app():
    with patch("backend.celeryset.celery_app"):
        application, _mail = create_app(TEST_CONFIG)
    with application.app_context():
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _register_student(client, email="stu@test.com", contact="1111111111"):
    return client.post(
        "/auth/register",
        json={
            "role": "student",
            "email": email,
            "contact_no": contact,
            "password": "pass1234",
            "name": "Test Student",
            "dept": "CSE",
            "dob": "2000-06-15",
            "year": 3,
            "cgpa": 8.5,
        },
    )


def _register_company(client, email="co@test.com", contact="2222222222"):
    return client.post(
        "/auth/register",
        json={
            "role": "company",
            "email": email,
            "contact_no": contact,
            "password": "pass1234",
            "name": "TestCorp",
            "website": "https://testcorp.com",
            "location": "Bangalore",
            "field": "IT",
        },
    )


def _login(client, email, password="pass1234"):
    return client.post("/auth/login", json={"email": email, "password": password})


def _login_admin(client):
    return _login(client, "admin@placement.in", TEST_CONFIG["ADMIN_PASSWORD"])


def _approve_company(app, user_email):
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        company = CompanyProfile.query.filter_by(user_id=user.id).first()
        company.approval_status = "approved"
        db.session.commit()
        return company.id


def _create_drive(app, company_id, deadline="2099-12-31"):
    with app.app_context():
        drive = PlacementDrive(
            company_id=company_id,
            jobtitle="SDE",
            job_desc="Backend dev",
            open_postings=5,
            branches="CSE,IT",
            cgpa_above=7.0,
            salary=800000.0,
            age_cat=30,
            deadline=datetime.strptime(deadline, "%Y-%m-%d"),
            status="approved",
            skills="Python",
        )
        db.session.add(drive)
        db.session.commit()
        return drive.drive_id


def test_demo_seed_is_opt_in_and_idempotent(app, client):
    with app.app_context():
        assert User.query.filter_by(email=DEMO_STUDENT_EMAIL).first() is None
        assert User.query.filter_by(email=DEMO_COMPANY_EMAIL).first() is None

        seed_demo()
        seed_demo()

        student_user = User.query.filter_by(email=DEMO_STUDENT_EMAIL).one()
        company_user = User.query.filter_by(email=DEMO_COMPANY_EMAIL).one()
        student = StudentProfile.query.filter_by(user_id=student_user.id).one()
        company = CompanyProfile.query.filter_by(user_id=company_user.id).one()
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()

        assert student_user.checking_password(DEMO_PASSWORD)
        assert company_user.checking_password(DEMO_PASSWORD)
        assert company.approval_status == "approved"
        assert len(drives) == 1
        assert drives[0].status == "approved"

    assert _login(client, DEMO_STUDENT_EMAIL, DEMO_PASSWORD).status_code == 200
    assert _login(client, DEMO_COMPANY_EMAIL, DEMO_PASSWORD).status_code == 200


# ─── Auth Routes ──────────────────────────────────────────────────────────────


class TestIndex:
    def test_index_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200


class TestRegister:
    def test_register_student_success(self, client):
        response = _register_student(client)
        assert response.status_code == 200
        assert "registered successfully" in response.get_json()["message"]

    def test_register_company_success(self, client):
        response = _register_company(client)
        assert response.status_code == 200
        assert "registered successfully" in response.get_json()["message"]

    def test_register_missing_role(self, client):
        response = client.post("/auth/register", json={"email": "x@x.com", "password": "abc"})
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_register_requires_json_object(self, client):
        assert client.post("/auth/register").status_code == 400
        assert client.post("/auth/register", data="not json").status_code == 400

    def test_register_invalid_role(self, client):
        response = client.post("/auth/register", json={"role": "superuser", "email": "x@x.com", "password": "abc"})
        assert response.status_code == 400

    def test_register_duplicate_email(self, client):
        _register_student(client)
        response = _register_student(client, contact="3333333333")
        assert response.status_code == 409
        assert "Email already registered" in response.get_json()["error"]

    def test_register_duplicate_contact(self, client):
        _register_student(client)
        response = _register_student(client, email="other@x.com")
        assert response.status_code == 409
        assert "Contact number already registered" in response.get_json()["error"]

    def test_register_student_bad_dob(self, client, app):
        response = client.post(
            "/auth/register",
            json={
                "role": "student",
                "email": "bad@x.com",
                "contact_no": "9876543210",
                "password": "pass1234",
                "name": "Bad DOB",
                "dept": "CSE",
                "dob": "not-a-date",
                "year": 2,
                "cgpa": 7.0,
            },
        )
        assert response.status_code == 400
        with app.app_context():
            assert User.query.filter_by(email="bad@x.com").first() is None


class TestLogin:
    def test_login_success(self, client):
        _register_student(client)
        response = _login(client, "stu@test.com")
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "stu@test.com"
        assert data["role"] == "student"

    def test_login_wrong_password(self, client):
        _register_student(client)
        response = _login(client, "stu@test.com", "wrongpass")
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = _login(client, "ghost@x.com")
        assert response.status_code == 401

    def test_login_requires_json_object(self, client):
        assert client.post("/auth/login").status_code == 400
        assert client.post("/auth/login", data="not json").status_code == 400

    def test_login_is_rate_limited(self):
        limited_app, _mail = create_app({**TEST_CONFIG, "RATELIMIT_ENABLED": True})
        client = limited_app.test_client()
        for _ in range(5):
            assert _login(client, "missing@example.com").status_code == 401
        assert _login(client, "missing@example.com").status_code == 429


def test_create_app_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY must be configured"):
        create_app({"ADMIN_PASSWORD": "test-admin-password"})


def test_create_app_requires_admin_password(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    with pytest.raises(RuntimeError, match="ADMIN_PASSWORD must be configured"):
        create_app({"SECRET_KEY": "test-secret"})


class TestCheckAuth:
    def test_check_auth_unauthenticated(self, client):
        response = client.get("/auth/check")
        assert response.status_code == 401

    def test_check_auth_authenticated(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.get("/auth/check")
        assert response.status_code == 200
        assert response.get_json()["email"] == "stu@test.com"


class TestLogout:
    def test_logout_requires_login(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 401

    def test_logout_success(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert "Logged out" in response.get_json()["message"]


# ─── Admin Routes ─────────────────────────────────────────────────────────────


class TestAdminDashboard:
    def test_dashboard_requires_admin(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.get("/admin/admin_dashboard")
        assert response.status_code == 403

    def test_dashboard_unauthenticated(self, client):
        response = client.get("/admin/admin_dashboard")
        assert response.status_code == 401

    def test_dashboard_admin_success(self, client):
        _login_admin(client)
        response = client.get("/admin/admin_dashboard")
        assert response.status_code == 200
        data = response.get_json()
        assert "num_students" in data
        assert "num_companies" in data


class TestAdminSearchStudent:
    def test_search_student_found(self, client, app):
        _register_student(client)
        _login_admin(client)
        response = client.get("/admin/search_student?query=Test")
        assert response.status_code == 200
        assert "students" in response.get_json()

    def test_search_student_not_found(self, client):
        _login_admin(client)
        response = client.get("/admin/search_student?query=NoSuchPerson")
        assert response.status_code == 404

    def test_search_student_requires_admin(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.get("/admin/search_student?query=Test")
        assert response.status_code == 403


class TestAdminSearchCompany:
    def test_search_company_found(self, client):
        _register_company(client)
        _login_admin(client)
        response = client.get("/admin/search_company?query=TestCorp")
        assert response.status_code == 200
        assert "companies" in response.get_json()

    def test_search_company_not_found(self, client):
        _login_admin(client)
        response = client.get("/admin/search_company?query=NoSuchCorp")
        assert response.status_code == 404


class TestAdminViewStudents:
    def test_view_students(self, client):
        _register_student(client)
        _login_admin(client)
        response = client.get("/admin/view_students")
        assert response.status_code == 200
        assert "students" in response.get_json()


class TestAdminViewCompanies:
    def test_view_companies(self, client):
        _register_company(client)
        _login_admin(client)
        response = client.get("/admin/view_companies")
        assert response.status_code == 200
        assert "companies" in response.get_json()


class TestAdminAllDrives:
    def test_all_drives(self, client, app):
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        _create_drive(app, cid)
        _login_admin(client)
        response = client.get("/admin/all_drives")
        assert response.status_code == 200
        data = response.get_json()
        assert "drives" in data
        assert "applications" in data


class TestAdminGetApplicants:
    def test_get_applicants_drive_not_found(self, client):
        _login_admin(client)
        response = client.get("/admin/drives/9999/applicants")
        assert response.status_code == 404

    def test_get_applicants_success(self, client, app):
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login_admin(client)
        response = client.get(f"/admin/drives/{drive_id}/applicants")
        assert response.status_code == 200
        assert "applicants" in response.get_json()


class TestAdminUpdateCompanyStatus:
    def test_approve_company(self, client, app):
        _register_company(client)
        with app.app_context():
            user = User.query.filter_by(email="co@test.com").first()
            company = CompanyProfile.query.filter_by(user_id=user.id).first()
            cid = company.id
        _login_admin(client)
        response = client.patch(f"/admin/company/{cid}/status", json={"action": "approve"})
        assert response.status_code == 200
        assert "approved" in response.get_json()["message"]

    def test_reject_company(self, client, app):
        _register_company(client)
        with app.app_context():
            user = User.query.filter_by(email="co@test.com").first()
            company = CompanyProfile.query.filter_by(user_id=user.id).first()
            cid = company.id
        _login_admin(client)
        response = client.patch(f"/admin/company/{cid}/status", json={"action": "reject"})
        assert response.status_code == 200
        assert "rejected" in response.get_json()["message"]

    def test_invalid_action(self, client, app):
        _register_company(client)
        with app.app_context():
            user = User.query.filter_by(email="co@test.com").first()
            company = CompanyProfile.query.filter_by(user_id=user.id).first()
            cid = company.id
        _login_admin(client)
        response = client.patch(f"/admin/company/{cid}/status", json={"action": "delete"})
        assert response.status_code == 400

    def test_company_not_found(self, client):
        _login_admin(client)
        response = client.patch("/admin/company/9999/status", json={"action": "approve"})
        assert response.status_code == 404


class TestAdminUpdateDriveStatus:
    def test_approve_drive(self, client, app):
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login_admin(client)
        response = client.patch(f"/admin/drive/{drive_id}/status", json={"action": "approve"})
        assert response.status_code == 200

    def test_drive_not_found(self, client):
        _login_admin(client)
        response = client.patch("/admin/drive/9999/status", json={"action": "approve"})
        assert response.status_code == 404

    def test_drive_invalid_action(self, client, app):
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login_admin(client)
        response = client.patch(f"/admin/drive/{drive_id}/status", json={"action": "close"})
        assert response.status_code == 400


class TestAdminDeactivateUser:
    def test_deactivate_student(self, client, app):
        _register_student(client)
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        _login_admin(client)
        response = client.patch(f"/admin/user/{uid}/deactivate")
        assert response.status_code == 200
        assert "deactivated" in response.get_json()["message"]

    def test_reactivate_user(self, client, app):
        _register_student(client)
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        _login_admin(client)
        client.patch(f"/admin/user/{uid}/deactivate")
        response = client.patch(f"/admin/user/{uid}/deactivate")
        assert response.status_code == 200
        assert "activated" in response.get_json()["message"]

    def test_cannot_deactivate_admin(self, client, app):
        with app.app_context():
            admin = User.query.filter_by(role="admin").first()
            aid = admin.id
        _login_admin(client)
        response = client.patch(f"/admin/user/{aid}/deactivate")
        assert response.status_code == 403

    def test_user_not_found(self, client):
        _login_admin(client)
        response = client.patch("/admin/user/9999/deactivate")
        assert response.status_code == 404


class TestAdminPlacement:
    def test_placement_empty(self, client):
        _login_admin(client)
        response = client.get("/admin/placement")
        assert response.status_code == 200

    def test_placement_with_data(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            appl = Application(student_id=student.id, drive_id=drive_id, status="selected")
            db.session.add(appl)
            db.session.commit()
        _login_admin(client)
        response = client.get("/admin/placement")
        assert response.status_code == 200
        assert "placement_history" in response.get_json()


class TestAdminScheduleInterview:
    def test_interview_not_found(self, client):
        _login_admin(client)
        response = client.post("/admin/remind_interview/9999")
        assert response.status_code == 404


# ─── Company Routes ───────────────────────────────────────────────────────────


class TestCompanyDashboard:
    def test_dashboard_unauthenticated(self, client):
        response = client.get("/company/dashboard")
        assert response.status_code == 401

    def test_dashboard_not_approved(self, client):
        _register_company(client)
        _login(client, "co@test.com")
        response = client.get("/company/dashboard")
        assert response.status_code == 403

    def test_dashboard_approved(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.get("/company/dashboard")
        assert response.status_code == 200
        data = response.get_json()
        assert data["company_name"] == "TestCorp"


class TestCompanyCreateDrive:
    def test_create_drive_success(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.post(
            "/company/create_drive",
            json={
                "jobtitle": "SDE",
                "branches": "CSE,IT",
                "cgpa_above": 7.0,
                "deadline": "2099-12-31",
                "open_postings": 10,
                "salary": 900000,
                "skills": "Python",
            },
        )
        assert response.status_code == 200
        assert "Successfully applied drive" in response.get_json()["message"]

    def test_create_drive_missing_field(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.post("/company/create_drive", json={"jobtitle": "SDE"})
        assert response.status_code == 400

    def test_create_drive_past_deadline(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.post(
            "/company/create_drive",
            json={
                "jobtitle": "SDE",
                "branches": "CSE",
                "cgpa_above": 7.0,
                "deadline": "2000-01-01",
                "open_postings": 5,
                "salary": 500000,
            },
        )
        assert response.status_code == 400
        assert response.get_json()["error"] == "Deadline must be in the future"

    def test_create_drive_invalid_deadline_format(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.post(
            "/company/create_drive",
            json={
                "jobtitle": "SDE",
                "branches": "CSE",
                "cgpa_above": 7.0,
                "deadline": "not-a-date",
                "open_postings": 5,
                "salary": 500000,
            },
        )
        assert response.status_code == 400
        assert response.get_json()["error"] == "Deadline must use YYYY-MM-DD format"

    def test_create_drive_accepts_zero_values(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.post(
            "/company/create_drive",
            json={
                "jobtitle": "SDE",
                "branches": "CSE",
                "cgpa_above": 0,
                "deadline": "2099-12-31",
                "open_postings": 0,
                "salary": 0,
                "age_cat": 30,
            },
        )
        assert response.status_code == 200

    def test_create_drive_not_approved(self, client):
        _register_company(client)
        _login(client, "co@test.com")
        response = client.post(
            "/company/create_drive",
            json={
                "jobtitle": "SDE",
                "branches": "CSE",
                "cgpa_above": 7.0,
                "deadline": "2099-12-31",
                "open_postings": 5,
                "salary": 500000,
            },
        )
        assert response.status_code == 403


class TestCompanyGetAllApplicants:
    def test_get_all_applicants_empty(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.get("/company/drives/applicants")
        assert response.status_code == 200
        assert response.get_json()["applicants"] == []


class TestCompanyGetStudentInfo:
    def test_student_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.get("/company/student/9999/info")
        assert response.status_code == 404

    def test_get_student_info_requires_company_application(self, client, app):
        _register_student(client)
        _register_company(client)
        _approve_company(app, "co@test.com")
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            sid = student.id
        _login(client, "co@test.com")
        response = client.get(f"/company/student/{sid}/info")
        assert response.status_code == 403

    def test_get_student_info_for_applicant(self, client, app):
        _register_student(client)
        _register_company(client)
        company_id = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, company_id)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            sid = student.id
            db.session.add(Application(student_id=sid, drive_id=drive_id))
            db.session.commit()
        _login(client, "co@test.com")
        response = client.get(f"/company/student/{sid}/info")
        assert response.status_code == 200
        assert "student" in response.get_json()


def test_cached_student_dashboards_are_isolated_by_user(app):
    cache.clear()

    client_one = app.test_client()
    client_two = app.test_client()
    _register_student(client_one, "one@test.com", "1111111111")
    _register_student(client_two, "two@test.com", "3333333333")
    _register_company(client_one)
    company_id = _approve_company(app, "co@test.com")
    drive_id = _create_drive(app, company_id)

    with app.app_context():
        first_student = StudentProfile.query.join(User).filter(User.email == "one@test.com").one()
        second_student = StudentProfile.query.join(User).filter(User.email == "two@test.com").one()
        assert first_student.id != second_student.id
        db.session.add(Application(student_id=second_student.id, drive_id=drive_id))
        db.session.commit()

    first_login = _login(client_one, "one@test.com").get_json()
    second_login = _login(client_two, "two@test.com").get_json()
    assert first_login["id"] != second_login["id"]
    with client_one.session_transaction() as session:
        assert session["_user_id"] == str(first_login["id"])
    with client_two.session_transaction() as session:
        assert session["_user_id"] == str(second_login["id"])
    first_dashboard = client_one.get("/student/student_dashboard")
    second_dashboard = client_two.get("/student/student_dashboard")

    assert first_dashboard.status_code == 200
    assert first_dashboard.get_json()["num_applications"] == 0
    assert second_dashboard.status_code == 200
    assert second_dashboard.get_json()["num_applications"] == 1
    assert app.test_client().get("/student/student_dashboard").status_code == 401


class TestCompanyDriveApplicants:
    def test_drive_applicants_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.get("/company/drives/9999/applicants")
        assert response.status_code == 404

    def test_drive_applicants_success(self, client, app):
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login(client, "co@test.com")
        response = client.get(f"/company/drives/{drive_id}/applicants")
        assert response.status_code == 200
        assert "applicants" in response.get_json()


class TestCompanyUpdateApplicationStatus:
    def test_update_status_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.patch("/company/application/9999/status", json={"action": "selected"})
        assert response.status_code == 404

    def test_update_status_invalid_action(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            appl = Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id = appl.application_id
        _login(client, "co@test.com")
        response = client.patch(f"/company/application/{appl_id}/status", json={"action": "hired"})
        assert response.status_code == 400

    def test_update_status_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            appl = Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id = appl.application_id
        _login(client, "co@test.com")
        response = client.patch(f"/company/application/{appl_id}/status", json={"action": "shortlisted"})
        assert response.status_code == 200
        assert "shortlisted" in response.get_json()["message"]


class TestCompanyCloseDrive:
    def test_close_drive_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.patch("/company/drive/9999/close")
        assert response.status_code == 404

    def test_close_drive_success(self, client, app):
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login(client, "co@test.com")
        response = client.patch(f"/company/drive/{drive_id}/close")
        assert response.status_code == 200
        assert "closed successfully" in response.get_json()["message"]


class TestCompanySeeInfo:
    def test_company_info_unauthorized(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        with app.app_context():
            user = User.query.filter_by(email="co@test.com").first()
            uid = user.id
        _login(client, "co@test.com")
        response = client.get(f"/company/{uid + 999}/info")
        assert response.status_code == 404

    def test_company_info_success(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        with app.app_context():
            user = User.query.filter_by(email="co@test.com").first()
            uid = user.id
        _login(client, "co@test.com")
        response = client.get(f"/company/{uid}/info")
        assert response.status_code == 200
        assert response.get_json()["name"] == "TestCorp"


class TestCompanySeeDrives:
    def test_see_drives_success(self, client, app):
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        _create_drive(app, cid)
        with app.app_context():
            user = User.query.filter_by(email="co@test.com").first()
            uid = user.id
        _login(client, "co@test.com")
        response = client.get(f"/company/{uid}/drives")
        assert response.status_code == 200
        assert "drives" in response.get_json()


class TestCompanyExport:
    def test_export_queued(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        mock_task = MagicMock()
        mock_task.id = "fake-task-id"
        with patch("backend.routes.company.export_csv.delay", return_value=mock_task):
            response = client.post("/company/export")
        assert response.status_code == 202
        assert response.get_json()["task_id"] == "fake-task-id"


class TestCompanyCsvStatus:
    def test_csv_status(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        mock_result = MagicMock()
        mock_result.status = "PENDING"
        mock_result.successful.return_value = False
        mock_result.result = None
        with patch("backend.routes.company.AsyncResult", return_value=mock_result):
            response = client.get("/company/exported_csv_status/fake-id")
        assert response.status_code == 200
        assert response.get_json()["status"] == "PENDING"


class TestCompanyScheduleInterview:
    def test_schedule_interview_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response = client.post(
            "/company/schedule_interview/9999",
            json={
                "interview_date": "2099-11-01",
                "interview_time": "10:00",
                "location": "Online",
            },
        )
        assert response.status_code == 404

    def test_schedule_interview_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            appl = Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id = appl.application_id
        _login(client, "co@test.com")
        mock_task = MagicMock()
        mock_task.id = "reminder-task-id"
        with patch("backend.routes.company.get_reminders.delay", return_value=mock_task):
            response = client.post(
                f"/company/schedule_interview/{appl_id}",
                json={
                    "interview_date": "2099-11-01",
                    "interview_time": "10:00",
                    "location": "Online",
                },
            )
        assert response.status_code == 200
        assert response.get_json()["status"] == "success"


# ─── Student Routes ───────────────────────────────────────────────────────────


class TestStudentDashboard:
    def test_dashboard_unauthenticated(self, client):
        response = client.get("/student/student_dashboard")
        assert response.status_code == 401

    def test_dashboard_success(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.get("/student/student_dashboard")
        assert response.status_code == 200
        data = response.get_json()
        assert "num_applications" in data
        assert "num_companies" in data


class TestStudentViewCompanies:
    def test_view_companies(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.get("/student/view_companies")
        assert response.status_code == 200
        assert "companies" in response.get_json()

    def test_view_companies_requires_login(self, client):
        response = client.get("/student/view_companies")
        assert response.status_code == 401


class TestStudentAllDrives:
    def test_all_drives(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        _create_drive(app, cid)
        _login(client, "stu@test.com")
        response = client.get("/student/all_drives")
        assert response.status_code == 200
        data = response.get_json()
        assert "drives" in data
        assert len(data["drives"]) >= 1


class TestStudentApplications:
    def test_applications_unauthorized(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/student/{uid + 999}/applications")
        assert response.status_code == 403

    def test_applications_success(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/student/{uid}/applications")
        assert response.status_code == 200
        assert "applications" in response.get_json()

    def test_applications_include_match_score(self, client, app):
        _register_student(client)
        _register_company(client)
        company_id = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, company_id)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").one()
            db.session.add(Application(student_id=student.id, drive_id=drive_id))
            db.session.commit()
            user_id = student.user_id

        _login(client, "stu@test.com")
        with patch("backend.routes.student.compute_match_scores", return_value={drive_id: 82.5}):
            response = client.get(f"/student/student/{user_id}/applications")

        assert response.status_code == 200
        application = response.get_json()["applications"][0]
        assert application["match_score"] == 82.5
        assert application["match_category"] == "Great"


class TestStudentApplyDrive:
    def test_apply_drive_not_found(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.post("/student/drive/apply/9999")
        assert response.status_code == 404

    def test_apply_drive_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login(client, "stu@test.com")
        response = client.post(f"/student/drive/apply/{drive_id}")
        assert response.status_code == 200
        assert "Successfully applied" in response.get_json()["message"]

    def test_apply_drive_duplicate(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login(client, "stu@test.com")
        client.post(f"/student/drive/apply/{drive_id}")
        response = client.post(f"/student/drive/apply/{drive_id}")
        assert response.status_code == 400

    def test_apply_drive_low_cgpa(self, client, app):
        _register_student(client, email="lowcgpa@x.com", contact="5555555555")
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        with app.app_context():
            drive = PlacementDrive(
                company_id=cid,
                jobtitle="SDE",
                open_postings=5,
                branches="CSE,IT",
                cgpa_above=9.5,
                salary=800000.0,
                age_cat=30,
                deadline=datetime(2099, 12, 31),
                status="approved",
            )
            db.session.add(drive)
            db.session.commit()
            drive_id = drive.drive_id
            student = StudentProfile.query.filter_by(name="Test Student").first()
            student.cgpa = 6.0
            db.session.commit()
        _login(client, "lowcgpa@x.com")
        response = client.post(f"/student/drive/apply/{drive_id}")
        assert response.status_code == 403


class TestStudentWithdraw:
    def test_withdraw_not_found(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response = client.patch("/student/applications/9999/withdraw")
        assert response.status_code == 404

    def test_withdraw_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            appl = Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id = appl.application_id
        _login(client, "stu@test.com")
        response = client.patch(f"/student/applications/{appl_id}/withdraw")
        assert response.status_code == 200

    def test_withdraw_already_selected(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            appl = Application(student_id=student.id, drive_id=drive_id, status="selected")
            db.session.add(appl)
            db.session.commit()
            appl_id = appl.application_id
        _login(client, "stu@test.com")
        response = client.patch(f"/student/applications/{appl_id}/withdraw")
        assert response.status_code == 400


class TestStudentEligibleDrives:
    def test_eligible_drives(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        _login(client, "stu@test.com")
        with patch("backend.routes.student.compute_match_scores", return_value={drive_id: 50.0}):
            response = client.get("/student/drives/eligible")
        assert response.status_code == 200
        drive = response.get_json()["eligible_drives"][0]
        assert drive["match_score"] == 50.0
        assert drive["match_category"] == "Good"

    def test_eligible_drives_student_not_found(self, client, app):
        _register_student(client)
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            profile = StudentProfile.query.filter_by(user_id=user.id).first()
            db.session.delete(profile)
            db.session.commit()
        _login(client, "stu@test.com")
        response = client.get("/student/drives/eligible")
        assert response.status_code == 404

    def test_eligible_drives_without_pdf_returns_no_match_score(self, client, app):
        _register_student(client)
        _register_company(client)
        company_id = _approve_company(app, "co@test.com")
        _create_drive(app, company_id)
        _login(client, "stu@test.com")

        response = client.get("/student/drives/eligible")

        assert response.status_code == 200
        drive = response.get_json()["eligible_drives"][0]
        assert drive["match_score"] is None
        assert drive["match_category"] is None


class TestStudentPlacement:
    def test_placement_unauthorized(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/student/{uid + 999}/placement")
        assert response.status_code == 400

    def test_placement_empty(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/student/{uid}/placement")
        assert response.status_code == 200

    def test_placement_with_history(self, client, app):
        _register_student(client)
        _register_company(client)
        cid = _approve_company(app, "co@test.com")
        drive_id = _create_drive(app, cid)
        with app.app_context():
            student = StudentProfile.query.filter_by(name="Test Student").first()
            appl = Application(student_id=student.id, drive_id=drive_id, status="selected")
            db.session.add(appl)
            db.session.commit()
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/student/{uid}/placement")
        assert response.status_code == 200
        assert "placement_history" in response.get_json()


class TestStudentGetInfo:
    def test_get_info_unauthorized(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/{uid + 999}/info")
        assert response.status_code == 400

    def test_get_info_success(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/{uid}/info")
        assert response.status_code == 200
        assert "student" in response.get_json()


class TestStudentResume:
    def test_resume_not_found(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.get(f"/student/{uid}/resume")
        assert response.status_code == 404

    def test_pdf_upload_saves_resume_and_returns_extracted_fields(self, client, app, tmp_path):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        app.config["RESUME_UPLOAD_FOLDER"] = str(tmp_path)
        resume_text = "Experienced Python developer with SQL and Flask project work. " "CGPA: 8.5/10. Expected graduation year: 2027. " "Built and maintained several software applications."

        with patch("backend.routes.student.pdf_to_text", return_value=resume_text):
            response = client.patch(
                f"/student/student/{uid}/edit-profile",
                data={"resume": (io.BytesIO(b"%PDF-1.7 test"), "resume.pdf")},
                content_type="multipart/form-data",
            )

        assert response.status_code == 200
        extraction = response.get_json()["resume_extraction"]
        assert extraction == {
            "skills": ["flask", "python", "sql"],
            "cgpa": 8.5,
            "grad_year": 2027,
        }
        with app.app_context():
            student = StudentProfile.query.filter_by(user_id=uid).one()
            assert student.resume_path
            with open(student.resume_path, "rb") as saved_file:
                assert saved_file.read() == b"%PDF-1.7 test"

    def test_pdf_upload_rejects_invalid_pdf(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.patch(
            f"/student/student/{uid}/edit-profile",
            data={"resume": (io.BytesIO(b"not a pdf"), "resume.pdf")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 415

    def test_pdf_upload_rejects_unreadable_pdf_without_saving(self, client, app, tmp_path):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        app.config["RESUME_UPLOAD_FOLDER"] = str(tmp_path)

        with patch("backend.routes.student.pdf_to_text", side_effect=ValueError("Invalid PDF")):
            response = client.patch(
                f"/student/student/{uid}/edit-profile",
                data={"resume": (io.BytesIO(b"%PDF-1.7 invalid"), "resume.pdf")},
                content_type="multipart/form-data",
            )

        assert response.status_code == 422
        with app.app_context():
            student = StudentProfile.query.filter_by(user_id=uid).one()
            assert student.resume_path == ""
        assert list(tmp_path.iterdir()) == []

    def test_docx_upload_still_works_without_pdf_extraction(self, client, app, tmp_path):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        app.config["RESUME_UPLOAD_FOLDER"] = str(tmp_path)

        response = client.patch(
            f"/student/student/{uid}/edit-profile",
            data={"resume": (io.BytesIO(b"docx content"), "resume.docx")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.get_json()["resume_extraction"] is None

    def test_resume_upload_rejects_oversized_file(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user = User.query.filter_by(email="stu@test.com").first()
            uid = user.id
        response = client.patch(
            f"/student/student/{uid}/edit-profile",
            data={"resume": (io.BytesIO(b"x" * 5_000_001), "resume.docx")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 413


class TestStudentExport:
    def test_export_queued(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        mock_task = MagicMock()
        mock_task.id = "student-export-id"
        with patch("backend.routes.student.export_csv.delay", return_value=mock_task):
            response = client.post("/student/export")
        assert response.status_code == 202
        assert response.get_json()["task_id"] == "student-export-id"


class TestStudentCsvStatus:
    def test_csv_status(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.successful.return_value = True
        mock_result.result = "path/to/file.csv"
        with patch("backend.routes.student.AsyncResult", return_value=mock_result):
            response = client.get("/student/export_csv_status/fake-id")
        assert response.status_code == 200
        assert response.get_json()["status"] == "SUCCESS"

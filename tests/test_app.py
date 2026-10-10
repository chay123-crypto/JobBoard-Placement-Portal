import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from models.models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application, Interview
from datetime import datetime, date, timezone


TEST_CONFIG={
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SECRET_KEY": "test-secret",
    "CACHE_TYPE": "SimpleCache",
    "MAIL_SUPPRESS_SEND": True,
    "WTF_CSRF_ENABLED": False,
}


@pytest.fixture(scope="function")
def app():
    with patch("celeryset.celery_app"), patch("cache.Cache.init_app"):
        application, _mail=create_app(TEST_CONFIG)
    application.config["CACHE_TYPE"]="SimpleCache"
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _register_student(client, email="stu@test.com", contact="1111111111"):
    return client.post("/auth/register", json={
        "role": "student",
        "email": email,
        "contact_no": contact,
        "password": "pass1234",
        "name": "Test Student",
        "dept": "CSE",
        "dob": "2000-06-15",
        "year": 3,
        "cgpa": 8.5,
    })


def _register_company(client, email="co@test.com", contact="2222222222"):
    return client.post("/auth/register", json={
        "role": "company",
        "email": email,
        "contact_no": contact,
        "password": "pass1234",
        "name": "TestCorp",
        "website": "https://testcorp.com",
        "location": "Bangalore",
        "field": "IT",
    })


def _login(client, email, password="pass1234"):
    return client.post("/auth/login", json={"email": email, "password": password})


def _login_admin(client):
    return _login(client, "admin@placement.in", "admin@123")


def _approve_company(app, user_email):
    with app.app_context():
        user=User.query.filter_by(email=user_email).first()
        company=CompanyProfile.query.filter_by(user_id=user.id).first()
        company.approval_status="approved"
        db.session.commit()
        return company.id


def _create_drive(app, company_id, deadline="2099-12-31"):
    with app.app_context():
        drive=PlacementDrive(
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


# ─── Auth Routes ──────────────────────────────────────────────────────────────

class TestIndex:
    def test_index_loads(self, client):
        response=client.get("/")
        assert response.status_code==200


class TestRegister:
    def test_register_student_success(self, client):
        response=_register_student(client)
        assert response.status_code==200
        assert "registered successfully" in response.get_json()["message"]

    def test_register_company_success(self, client):
        response=_register_company(client)
        assert response.status_code==200
        assert "registered successfully" in response.get_json()["message"]

    def test_register_missing_role(self, client):
        response=client.post("/auth/register", json={"email": "x@x.com", "password": "abc"})
        assert response.status_code==400
        assert "error" in response.get_json()

    def test_register_invalid_role(self, client):
        response=client.post("/auth/register", json={"role": "superuser", "email": "x@x.com", "password": "abc"})
        assert response.status_code==400

    def test_register_duplicate_email(self, client):
        _register_student(client)
        response=_register_student(client, contact="3333333333")
        assert response.status_code==409
        assert "Email already registered" in response.get_json()["error"]

    def test_register_duplicate_contact(self, client):
        _register_student(client)
        response=_register_student(client, email="other@x.com")
        assert response.status_code==409
        assert "Contact number already registered" in response.get_json()["error"]

    def test_register_student_bad_dob(self, client):
        response=client.post("/auth/register", json={
            "role": "student",
            "email": "bad@x.com",
            "contact_no": "9876543210",
            "password": "pass1234",
            "name": "Bad DOB",
            "dept": "CSE",
            "dob": "not-a-date",
            "year": 2,
            "cgpa": 7.0,
        })
        assert response.status_code==400


class TestLogin:
    def test_login_success(self, client):
        _register_student(client)
        response=_login(client, "stu@test.com")
        assert response.status_code==200
        data=response.get_json()
        assert data["email"]=="stu@test.com"
        assert data["role"]=="student"

    def test_login_wrong_password(self, client):
        _register_student(client)
        response=_login(client, "stu@test.com", "wrongpass")
        assert response.status_code==401

    def test_login_nonexistent_user(self, client):
        response=_login(client, "ghost@x.com")
        assert response.status_code==401


class TestCheckAuth:
    def test_check_auth_unauthenticated(self, client):
        response=client.get("/auth/check")
        assert response.status_code==401

    def test_check_auth_authenticated(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.get("/auth/check")
        assert response.status_code==200
        assert response.get_json()["email"]=="stu@test.com"


class TestLogout:
    def test_logout_requires_login(self, client):
        response=client.post("/auth/logout")
        assert response.status_code==401

    def test_logout_success(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.post("/auth/logout")
        assert response.status_code==200
        assert "Logged out" in response.get_json()["message"]


# ─── Admin Routes ─────────────────────────────────────────────────────────────

class TestAdminDashboard:
    def test_dashboard_requires_admin(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.get("/admin/admin_dashboard")
        assert response.status_code==403

    def test_dashboard_unauthenticated(self, client):
        response=client.get("/admin/admin_dashboard")
        assert response.status_code==401

    def test_dashboard_admin_success(self, client):
        _login_admin(client)
        response=client.get("/admin/admin_dashboard")
        assert response.status_code==200
        data=response.get_json()
        assert "num_students" in data
        assert "num_companies" in data


class TestAdminSearchStudent:
    def test_search_student_found(self, client, app):
        _register_student(client)
        _login_admin(client)
        response=client.get("/admin/search_student?query=Test")
        assert response.status_code==200
        assert "students" in response.get_json()

    def test_search_student_not_found(self, client):
        _login_admin(client)
        response=client.get("/admin/search_student?query=NoSuchPerson")
        assert response.status_code==404

    def test_search_student_requires_admin(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.get("/admin/search_student?query=Test")
        assert response.status_code==403


class TestAdminSearchCompany:
    def test_search_company_found(self, client):
        _register_company(client)
        _login_admin(client)
        response=client.get("/admin/search_company?query=TestCorp")
        assert response.status_code==200
        assert "companies" in response.get_json()

    def test_search_company_not_found(self, client):
        _login_admin(client)
        response=client.get("/admin/search_company?query=NoSuchCorp")
        assert response.status_code==404


class TestAdminViewStudents:
    def test_view_students(self, client):
        _register_student(client)
        _login_admin(client)
        response=client.get("/admin/view_students")
        assert response.status_code==200
        assert "students" in response.get_json()


class TestAdminViewCompanies:
    def test_view_companies(self, client):
        _register_company(client)
        _login_admin(client)
        response=client.get("/admin/view_companies")
        assert response.status_code==200
        assert "companies" in response.get_json()


class TestAdminAllDrives:
    def test_all_drives(self, client, app):
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        _create_drive(app, cid)
        _login_admin(client)
        response=client.get("/admin/all_drives")
        assert response.status_code==200
        data=response.get_json()
        assert "drives" in data
        assert "applications" in data


class TestAdminGetApplicants:
    def test_get_applicants_drive_not_found(self, client):
        _login_admin(client)
        response=client.get("/admin/drives/9999/applicants")
        assert response.status_code==404

    def test_get_applicants_success(self, client, app):
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        _login_admin(client)
        response=client.get(f"/admin/drives/{drive_id}/applicants")
        assert response.status_code==200
        assert "applicants" in response.get_json()


class TestAdminUpdateCompanyStatus:
    def test_approve_company(self, client, app):
        _register_company(client)
        with app.app_context():
            user=User.query.filter_by(email="co@test.com").first()
            company=CompanyProfile.query.filter_by(user_id=user.id).first()
            cid=company.id
        _login_admin(client)
        response=client.patch(f"/admin/company/{cid}/status", json={"action": "approve"})
        assert response.status_code==200
        assert "approved" in response.get_json()["message"]

    def test_reject_company(self, client, app):
        _register_company(client)
        with app.app_context():
            user=User.query.filter_by(email="co@test.com").first()
            company=CompanyProfile.query.filter_by(user_id=user.id).first()
            cid=company.id
        _login_admin(client)
        response=client.patch(f"/admin/company/{cid}/status", json={"action": "reject"})
        assert response.status_code==200
        assert "rejected" in response.get_json()["message"]

    def test_invalid_action(self, client, app):
        _register_company(client)
        with app.app_context():
            user=User.query.filter_by(email="co@test.com").first()
            company=CompanyProfile.query.filter_by(user_id=user.id).first()
            cid=company.id
        _login_admin(client)
        response=client.patch(f"/admin/company/{cid}/status", json={"action": "delete"})
        assert response.status_code==400

    def test_company_not_found(self, client):
        _login_admin(client)
        response=client.patch("/admin/company/9999/status", json={"action": "approve"})
        assert response.status_code==404


class TestAdminUpdateDriveStatus:
    def test_approve_drive(self, client, app):
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        _login_admin(client)
        response=client.patch(f"/admin/drive/{drive_id}/status", json={"action": "approve"})
        assert response.status_code==200

    def test_drive_not_found(self, client):
        _login_admin(client)
        response=client.patch("/admin/drive/9999/status", json={"action": "approve"})
        assert response.status_code==404

    def test_drive_invalid_action(self, client, app):
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        _login_admin(client)
        response=client.patch(f"/admin/drive/{drive_id}/status", json={"action": "close"})
        assert response.status_code==400


class TestAdminDeactivateUser:
    def test_deactivate_student(self, client, app):
        _register_student(client)
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        _login_admin(client)
        response=client.patch(f"/admin/user/{uid}/deactivate")
        assert response.status_code==200
        assert "deactivated" in response.get_json()["message"]

    def test_reactivate_user(self, client, app):
        _register_student(client)
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        _login_admin(client)
        client.patch(f"/admin/user/{uid}/deactivate")
        response=client.patch(f"/admin/user/{uid}/deactivate")
        assert response.status_code==200
        assert "activated" in response.get_json()["message"]

    def test_cannot_deactivate_admin(self, client, app):
        with app.app_context():
            admin=User.query.filter_by(role="admin").first()
            aid=admin.id
        _login_admin(client)
        response=client.patch(f"/admin/user/{aid}/deactivate")
        assert response.status_code==403

    def test_user_not_found(self, client):
        _login_admin(client)
        response=client.patch("/admin/user/9999/deactivate")
        assert response.status_code==404


class TestAdminPlacement:
    def test_placement_empty(self, client):
        _login_admin(client)
        response=client.get("/admin/placement")
        assert response.status_code==200

    def test_placement_with_data(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            appl=Application(student_id=student.id, drive_id=drive_id, status="selected")
            db.session.add(appl)
            db.session.commit()
        _login_admin(client)
        response=client.get("/admin/placement")
        assert response.status_code==200
        assert "placement_history" in response.get_json()


class TestAdminScheduleInterview:
    def test_interview_not_found(self, client):
        _login_admin(client)
        response=client.post("/admin/remind_interview/9999")
        assert response.status_code==404


# ─── Company Routes ───────────────────────────────────────────────────────────

class TestCompanyDashboard:
    def test_dashboard_unauthenticated(self, client):
        response=client.get("/company/dashboard")
        assert response.status_code==401

    def test_dashboard_not_approved(self, client):
        _register_company(client)
        _login(client, "co@test.com")
        response=client.get("/company/dashboard")
        assert response.status_code==403

    def test_dashboard_approved(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.get("/company/dashboard")
        assert response.status_code==200
        data=response.get_json()
        assert data["company_name"]=="TestCorp"


class TestCompanyCreateDrive:
    def test_create_drive_success(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.post("/company/create_drive", json={
            "jobtitle": "SDE",
            "branches": "CSE,IT",
            "cgpa_above": 7.0,
            "deadline": "2099-12-31",
            "open_postings": 10,
            "salary": 900000,
            "skills": "Python",
        })
        assert response.status_code==200
        assert "Successfully applied drive" in response.get_json()["message"]

    def test_create_drive_missing_field(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.post("/company/create_drive", json={"jobtitle": "SDE"})
        assert response.status_code==400

    def test_create_drive_past_deadline(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.post("/company/create_drive", json={
            "jobtitle": "SDE",
            "branches": "CSE",
            "cgpa_above": 7.0,
            "deadline": "2000-01-01",
            "open_postings": 5,
            "salary": 500000,
        })
        assert response.status_code==400

    def test_create_drive_not_approved(self, client):
        _register_company(client)
        _login(client, "co@test.com")
        response=client.post("/company/create_drive", json={
            "jobtitle": "SDE",
            "branches": "CSE",
            "cgpa_above": 7.0,
            "deadline": "2099-12-31",
            "open_postings": 5,
            "salary": 500000,
        })
        assert response.status_code==403


class TestCompanyGetAllApplicants:
    def test_get_all_applicants_empty(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.get("/company/drives/applicants")
        assert response.status_code==200
        assert response.get_json()["applicants"]==[]


class TestCompanyGetStudentInfo:
    def test_student_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.get("/company/student/9999/info")
        assert response.status_code==404

    def test_get_student_info(self, client, app):
        _register_student(client)
        _register_company(client)
        _approve_company(app, "co@test.com")
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            sid=student.id
        _login(client, "co@test.com")
        response=client.get(f"/company/student/{sid}/info")
        assert response.status_code==200
        assert "student" in response.get_json()


class TestCompanyDriveApplicants:
    def test_drive_applicants_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.get("/company/drives/9999/applicants")
        assert response.status_code==404

    def test_drive_applicants_success(self, client, app):
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        _login(client, "co@test.com")
        response=client.get(f"/company/drives/{drive_id}/applicants")
        assert response.status_code==200
        assert "applicants" in response.get_json()


class TestCompanyUpdateApplicationStatus:
    def test_update_status_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.patch("/company/application/9999/status", json={"action": "selected"})
        assert response.status_code==404

    def test_update_status_invalid_action(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            appl=Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id=appl.application_id
        _login(client, "co@test.com")
        response=client.patch(f"/company/application/{appl_id}/status", json={"action": "hired"})
        assert response.status_code==400

    def test_update_status_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            appl=Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id=appl.application_id
        _login(client, "co@test.com")
        response=client.patch(f"/company/application/{appl_id}/status", json={"action": "shortlisted"})
        assert response.status_code==200
        assert "shortlisted" in response.get_json()["message"]


class TestCompanyCloseDrive:
    def test_close_drive_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.patch("/company/drive/9999/close")
        assert response.status_code==404

    def test_close_drive_success(self, client, app):
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        _login(client, "co@test.com")
        response=client.patch(f"/company/drive/{drive_id}/close")
        assert response.status_code==200
        assert "closed successfully" in response.get_json()["message"]


class TestCompanySeeInfo:
    def test_company_info_unauthorized(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        with app.app_context():
            user=User.query.filter_by(email="co@test.com").first()
            uid=user.id
        _login(client, "co@test.com")
        response=client.get(f"/company/{uid + 999}/info")
        assert response.status_code==404

    def test_company_info_success(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        with app.app_context():
            user=User.query.filter_by(email="co@test.com").first()
            uid=user.id
        _login(client, "co@test.com")
        response=client.get(f"/company/{uid}/info")
        assert response.status_code==200
        assert response.get_json()["name"]=="TestCorp"


class TestCompanySeeDrives:
    def test_see_drives_success(self, client, app):
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        _create_drive(app, cid)
        with app.app_context():
            user=User.query.filter_by(email="co@test.com").first()
            uid=user.id
        _login(client, "co@test.com")
        response=client.get(f"/company/{uid}/drives")
        assert response.status_code==200
        assert "drives" in response.get_json()


class TestCompanyExport:
    def test_export_queued(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        mock_task=MagicMock()
        mock_task.id="fake-task-id"
        with patch("routes.company.export_csv.delay", return_value=mock_task):
            response=client.post("/company/export")
        assert response.status_code==202
        assert response.get_json()["task_id"]=="fake-task-id"


class TestCompanyCsvStatus:
    def test_csv_status(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        mock_result=MagicMock()
        mock_result.status="PENDING"
        mock_result.successful.return_value=False
        mock_result.result=None
        with patch("routes.company.AsyncResult", return_value=mock_result):
            response=client.get("/company/exported_csv_status/fake-id")
        assert response.status_code==200
        assert response.get_json()["status"]=="PENDING"


class TestCompanyScheduleInterview:
    def test_schedule_interview_not_found(self, client, app):
        _register_company(client)
        _approve_company(app, "co@test.com")
        _login(client, "co@test.com")
        response=client.post("/company/schedule_interview/9999", json={
            "interview_date": "2099-11-01",
            "interview_time": "10:00",
            "location": "Online",
        })
        assert response.status_code==404

    def test_schedule_interview_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            appl=Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id=appl.application_id
        _login(client, "co@test.com")
        mock_task=MagicMock()
        mock_task.id="reminder-task-id"
        with patch("routes.company.get_reminders.delay", return_value=mock_task):
            response=client.post(f"/company/schedule_interview/{appl_id}", json={
                "interview_date": "2099-11-01",
                "interview_time": "10:00",
                "location": "Online",
            })
        assert response.status_code==200
        assert response.get_json()["status"]=="success"


# ─── Student Routes ───────────────────────────────────────────────────────────

class TestStudentDashboard:
    def test_dashboard_unauthenticated(self, client):
        response=client.get("/student/student_dashboard")
        assert response.status_code==401

    def test_dashboard_success(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.get("/student/student_dashboard")
        assert response.status_code==200
        data=response.get_json()
        assert "num_applications" in data
        assert "num_companies" in data


class TestStudentViewCompanies:
    def test_view_companies(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.get("/student/view_companies")
        assert response.status_code==200
        assert "companies" in response.get_json()

    def test_view_companies_requires_login(self, client):
        response=client.get("/student/view_companies")
        assert response.status_code==401


class TestStudentAllDrives:
    def test_all_drives(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        _create_drive(app, cid)
        _login(client, "stu@test.com")
        response=client.get("/student/all_drives")
        assert response.status_code==200
        data=response.get_json()
        assert "drives" in data
        assert len(data["drives"])>=1


class TestStudentApplications:
    def test_applications_unauthorized(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/student/{uid + 999}/applications")
        assert response.status_code==403

    def test_applications_success(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/student/{uid}/applications")
        assert response.status_code==200
        assert "applications" in response.get_json()


class TestStudentApplyDrive:
    def test_apply_drive_not_found(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.post("/student/drive/apply/9999")
        assert response.status_code==404

    def test_apply_drive_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        _login(client, "stu@test.com")
        response=client.post(f"/student/drive/apply/{drive_id}")
        assert response.status_code==200
        assert "Successfully applied" in response.get_json()["message"]

    def test_apply_drive_duplicate(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        _login(client, "stu@test.com")
        client.post(f"/student/drive/apply/{drive_id}")
        response=client.post(f"/student/drive/apply/{drive_id}")
        assert response.status_code==400

    def test_apply_drive_low_cgpa(self, client, app):
        _register_student(client, email="lowcgpa@x.com", contact="5555555555")
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        with app.app_context():
            drive=PlacementDrive(
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
            drive_id=drive.drive_id
            student=StudentProfile.query.filter_by(name="Test Student").first()
            student.cgpa=6.0
            db.session.commit()
        _login(client, "lowcgpa@x.com")
        response=client.post(f"/student/drive/apply/{drive_id}")
        assert response.status_code==403


class TestStudentWithdraw:
    def test_withdraw_not_found(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        response=client.patch("/student/applications/9999/withdraw")
        assert response.status_code==404

    def test_withdraw_success(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            appl=Application(student_id=student.id, drive_id=drive_id)
            db.session.add(appl)
            db.session.commit()
            appl_id=appl.application_id
        _login(client, "stu@test.com")
        response=client.patch(f"/student/applications/{appl_id}/withdraw")
        assert response.status_code==200

    def test_withdraw_already_selected(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            appl=Application(student_id=student.id, drive_id=drive_id, status="selected")
            db.session.add(appl)
            db.session.commit()
            appl_id=appl.application_id
        _login(client, "stu@test.com")
        response=client.patch(f"/student/applications/{appl_id}/withdraw")
        assert response.status_code==400


class TestStudentEligibleDrives:
    def test_eligible_drives(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        _create_drive(app, cid)
        _login(client, "stu@test.com")
        response=client.get("/student/drives/eligible")
        assert response.status_code==200
        assert "eligible_drives" in response.get_json()

    def test_eligible_drives_student_not_found(self, client, app):
        _register_student(client)
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            profile=StudentProfile.query.filter_by(user_id=user.id).first()
            db.session.delete(profile)
            db.session.commit()
        _login(client, "stu@test.com")
        response=client.get("/student/drives/eligible")
        assert response.status_code==404


class TestStudentPlacement:
    def test_placement_unauthorized(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/student/{uid + 999}/placement")
        assert response.status_code==400

    def test_placement_empty(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/student/{uid}/placement")
        assert response.status_code==200

    def test_placement_with_history(self, client, app):
        _register_student(client)
        _register_company(client)
        cid=_approve_company(app, "co@test.com")
        drive_id=_create_drive(app, cid)
        with app.app_context():
            student=StudentProfile.query.filter_by(name="Test Student").first()
            appl=Application(student_id=student.id, drive_id=drive_id, status="selected")
            db.session.add(appl)
            db.session.commit()
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/student/{uid}/placement")
        assert response.status_code==200
        assert "placement_history" in response.get_json()


class TestStudentGetInfo:
    def test_get_info_unauthorized(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/{uid + 999}/info")
        assert response.status_code==400

    def test_get_info_success(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/{uid}/info")
        assert response.status_code==200
        assert "student" in response.get_json()


class TestStudentResume:
    def test_resume_not_found(self, client, app):
        _register_student(client)
        _login(client, "stu@test.com")
        with app.app_context():
            user=User.query.filter_by(email="stu@test.com").first()
            uid=user.id
        response=client.get(f"/student/{uid}/resume")
        assert response.status_code==404


class TestStudentExport:
    def test_export_queued(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        mock_task=MagicMock()
        mock_task.id="student-export-id"
        with patch("routes.student.export_csv.delay", return_value=mock_task):
            response=client.post("/student/export")
        assert response.status_code==202
        assert response.get_json()["task_id"]=="student-export-id"


class TestStudentCsvStatus:
    def test_csv_status(self, client):
        _register_student(client)
        _login(client, "stu@test.com")
        mock_result=MagicMock()
        mock_result.status="SUCCESS"
        mock_result.successful.return_value=True
        mock_result.result="path/to/file.csv"
        with patch("routes.student.AsyncResult", return_value=mock_result):
            response=client.get("/student/export_csv_status/fake-id")
        assert response.status_code==200
        assert response.get_json()["status"]=="SUCCESS"

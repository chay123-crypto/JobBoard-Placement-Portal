import csv
import sys
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app import create_app
from backend.models.models import CompanyProfile, StudentProfile, User, db
from backend.tasks import export_csv, generate_monthly_reports, get_reminders


@pytest.fixture
def task_app():
    application, email = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
            "ADMIN_PASSWORD": "test-admin-password",
            "CACHE_TYPE": "SimpleCache",
            "MAIL_SUPPRESS_SEND": True,
        }
    )
    with application.app_context():
        db.create_all()
        yield application, email
        db.session.remove()
        db.drop_all()


def _create_student(app):
    with app.app_context():
        user = User(email="student@test.com", role="student", contact_no="1111111111")
        user.set_password("test-password")
        db.session.add(user)
        db.session.flush()
        student = StudentProfile(
            user_id=user.id,
            name="Test Student",
            dept="CSE",
            dob=date(2000, 1, 1),
            year=3,
            cgpa=8.5,
            resume_path="",
        )
        db.session.add(student)
        db.session.commit()
        return user.id, student.id


def test_export_csv_creates_student_export(tmp_path, monkeypatch, task_app):
    app, email = task_app
    user_id, _student_id = _create_student(app)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(sys.modules, "app", SimpleNamespace(app=app, mail=email))

    with patch.object(email, "send") as send:
        result = export_csv.run(user_id, "student")

    assert result["status"] == "success"
    assert result["rows"] == 0
    with open(result["filename"], newline="") as export_file:
        assert next(csv.reader(export_file)) == [
            "Application ID",
            "Company",
            "Job Title",
            "Job Description",
            "Open Postings",
            "Status",
            "Applied Date",
        ]
    send.assert_called_once()


def test_get_reminders_sends_to_student(monkeypatch, task_app):
    app, email = task_app
    _user_id, student_id = _create_student(app)
    monkeypatch.setitem(sys.modules, "app", SimpleNamespace(app=app, mail=email))

    with patch.object(email, "send") as send:
        result = get_reminders.run(
            student_id,
            "2099-01-01",
            "10:00",
            "Test Company",
            "Online",
        )

    assert result == {"status": "success", "student_id": student_id}
    send.assert_called_once()


def test_monthly_report_handles_company_without_drives(monkeypatch, task_app):
    app, email = task_app
    with app.app_context():
        user = User(email="company@test.com", role="company", contact_no="2222222222")
        user.set_password("test-password")
        db.session.add(user)
        db.session.flush()
        db.session.add(
            CompanyProfile(
                user_id=user.id,
                name="Test Company",
                website="https://example.com",
                field="Technology",
                location="Remote",
                approval_status="approved",
            )
        )
        db.session.commit()
    monkeypatch.setitem(sys.modules, "app", SimpleNamespace(app=app, mail=email))

    with patch.object(email, "send") as send:
        result = generate_monthly_reports.run()

    assert result == {
        "status": "success",
        "message": "Sent monthly reports to 1 companies.",
    }
    send.assert_called_once()

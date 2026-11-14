import argparse
from datetime import date, datetime
from getpass import getpass

from backend.models.models import (
    CompanyProfile,
    PlacementDrive,
    StudentProfile,
    User,
    db,
)

DEMO_STUDENT_EMAIL = "demo.student@placement.in"
DEMO_COMPANY_EMAIL = "demo.company@placement.in"
DEMO_STUDENT_CONTACT = "9000000001"
DEMO_COMPANY_CONTACT = "9000000002"


def init():
    db.create_all()
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        new_admin = User(email="admin@placement.in", role="admin", contact_no="0000000000")
        new_admin.set_password("admin@123")
        db.session.add(new_admin)
        db.session.commit()
        print("admin created successfully")
    else:
        print("admin exist already")


def _get_or_create_demo_user(email, role, contact_no, password):
    user = User.query.filter_by(email=email).first()
    contact_owner = User.query.filter_by(contact_no=contact_no).first()

    if user and user.role != role:
        raise ValueError(f"{email} already belongs to a {user.role} account")
    if contact_owner and (user is None or contact_owner.id != user.id):
        raise ValueError(f"Demo contact number {contact_no} is already in use")

    if user is None:
        user = User(email=email, role=role, contact_no=contact_no)
        db.session.add(user)

    user.set_password(password)
    user.is_active = True
    if user.id is None:
        db.session.flush()
    return user


def seed_demo(student_password, company_password):
    if not student_password or not company_password:
        raise ValueError("Both demo account passwords are required")

    db.create_all()
    student_user = _get_or_create_demo_user(
        DEMO_STUDENT_EMAIL,
        "student",
        DEMO_STUDENT_CONTACT,
        student_password,
    )
    company_user = _get_or_create_demo_user(
        DEMO_COMPANY_EMAIL,
        "company",
        DEMO_COMPANY_CONTACT,
        company_password,
    )

    student = StudentProfile.query.filter_by(user_id=student_user.id).first()
    if student is None:
        student = StudentProfile(
            name="Demo Student",
            user_id=student_user.id,
            dept="CSE",
            dob=date(2003, 6, 15),
            year=3,
            cgpa=8.5,
            resume_path="",
        )
        db.session.add(student)

    company = CompanyProfile.query.filter_by(user_id=company_user.id).first()
    if company is None:
        company = CompanyProfile(
            name="Demo Technology Co.",
            user_id=company_user.id,
            website="https://example.com",
            field="Technology",
            location="Remote",
            approval_status="approved",
        )
        db.session.add(company)
        db.session.flush()
    else:
        company.approval_status = "approved"

    drive = PlacementDrive.query.filter_by(
        company_id=company.id,
        jobtitle="Demo Software Engineer",
    ).first()
    if drive is None:
        drive = PlacementDrive(
            company_id=company.id,
            jobtitle="Demo Software Engineer",
            job_desc="Build and maintain web applications with the engineering team.",
            open_postings=3,
            skills="Python, Flask, JavaScript, SQL",
            branches="CSE,IT",
            cgpa_above=7.0,
            salary=800000.0,
            age_cat=30,
            deadline=datetime(2099, 12, 31),
            status="approved",
        )
        db.session.add(drive)
    else:
        drive.status = "approved"
        drive.deadline = datetime(2099, 12, 31)

    db.session.commit()


def _prompt_password(label):
    password = getpass(f"Set password for {label}: ")
    confirmation = getpass(f"Confirm password for {label}: ")
    if not password:
        raise ValueError("Demo account passwords cannot be empty")
    if password != confirmation:
        raise ValueError(f"Passwords for {label} do not match")
    return password


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the placement portal database.")
    parser.add_argument(
        "--seed-demo",
        action="store_true",
        help="Create demo student and company accounts plus an approved job drive.",
    )
    args = parser.parse_args()

    from app import app

    with app.app_context():
        if args.seed_demo:
            student_password = _prompt_password("demo student")
            company_password = _prompt_password("demo company")
            seed_demo(student_password, company_password)
            print("Demo accounts and approved drive are ready.")

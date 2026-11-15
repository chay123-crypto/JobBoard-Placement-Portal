import os
import secrets
from datetime import date, datetime

from celery.result import AsyncResult
from flask import Blueprint, current_app, jsonify, request, send_file
from flask_login import current_user
from pypdf.errors import PdfReadError, PdfStreamError
from sqlalchemy.exc import SQLAlchemyError

from backend.cache import cache
from backend.celeryset import celery_app
from backend.decorator import role_required
from backend.models.models import (
    Application,
    CompanyProfile,
    PlacementDrive,
    StudentProfile,
    db,
)
from backend.resume_parser import (
    extract_cgpa,
    extract_grad_year,
    extract_skills,
    load_vocab,
    pdf_to_text,
)
from backend.tasks import export_csv

student_bp = Blueprint("student", __name__, url_prefix="/student")
upload_folder = "uploads/resumes"
MAX_RESUME_SIZE = 5_000_000


@student_bp.route("/student_dashboard", methods=["GET"])
@cache.cached(timeout=60)
@role_required("student")
def student_dashboard():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    num_applications = Application.query.filter_by(student_id=student.id).count()
    num_companies = CompanyProfile.query.count()
    num_placement_drives = PlacementDrive.query.count()
    return jsonify({"num_applications": num_applications, "num_companies": num_companies, "num_placement_drives": num_placement_drives})


@student_bp.route("/view_companies", methods=["GET"])
@cache.cached(timeout=60)
@role_required("student")
def view_companies():
    companies = CompanyProfile.query.all()
    lis = [{"company_id": c.id, "name": c.name, "website": c.website, "approval_status": c.approval_status, "field": c.field, "location": c.location} for c in companies]
    return jsonify({"companies": lis}), 200


@student_bp.route("/search_company", methods=["GET"])
@role_required("student")
def search_companies():
    query = request.args.get("query", "")
    if CompanyProfile.query.filter(CompanyProfile.name.ilike(f"%{query}%")).first():
        company = CompanyProfile.query.filter(CompanyProfile.name.ilike(f"%{query}%")).all()
    lis = [{"company_id": c.id, "name": c.name, "website": c.website, "approval_status": c.approval_status, "field": c.field, "location": c.location} for c in company]
    if lis:
        return jsonify({"companies": lis}), 200
    else:
        return jsonify({"error": "company not found"}), 404


@student_bp.route("/all_drives", methods=["GET"])
@cache.cached(timeout=60)
@role_required("student")
def all_drives():
    drives = PlacementDrive.query.filter_by(status="approved").all()
    company_ids = [d.company_id for d in drives]
    companies = [c.name for c in CompanyProfile.query.filter(CompanyProfile.id.in_(company_ids)).all()]
    lis = [{"drive_id": p.drive_id, "company_id": p.company_id, "jobtitle": p.jobtitle, "job_desc": p.job_desc, "open_postings": p.open_postings, "branches": p.branches, "cgpa_above": p.cgpa_above, "age_cat": p.age_cat, "deadline": p.deadline.strftime("%d-%m-%Y"), "status": p.status, "skills": p.skills} for p in drives]
    return jsonify({"company_names": companies, "drives": lis}), 200


@student_bp.route("/student/<int:student_id>/applications", methods=["GET"])
@cache.cached(timeout=60)
@role_required("student")
def student_applications(student_id):
    if current_user.id != student_id:
        return jsonify({"error": "Unauthorized access"}), 403
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    applications = Application.query.filter_by(student_id=student.id).all()
    lis = [{"application_id": a.application_id, "drive_id": a.drive_id, "jobtitle": a.drive.jobtitle, "job_desc": a.drive.job_desc, "company_name": a.drive.company.name, "status": a.status} for a in applications]
    return jsonify({"applications": lis}), 200


@student_bp.route("/student/<int:student_id>/edit-profile", methods=["PATCH"])
@role_required("student")
def edit_profile(student_id):
    if current_user.id != student_id:
        return jsonify({"error": "Unauthorized access"}), 403
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    resume_file = request.files.get("resume")
    resume_path = None
    resume_extraction = None
    upload_directory = os.path.abspath(
        current_app.config.get(
            "RESUME_UPLOAD_FOLDER",
            os.path.join(current_app.root_path, upload_folder),
        )
    )
    if resume_file is not None:
        original_filename = resume_file.filename or ""
        if not original_filename:
            return jsonify({"error": "No resume file selected"}), 400
        extension = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
        if extension not in {"pdf", "doc", "docx"}:
            return jsonify({"error": "Only PDF/DOC/DOCX allowed"}), 400

        data = resume_file.stream.read(MAX_RESUME_SIZE + 1)
        if len(data) > MAX_RESUME_SIZE:
            return jsonify({"error": "File too large. Max 5 MB"}), 413
        if not data:
            return jsonify({"error": "The uploaded file is empty"}), 400

        if extension == "pdf":
            if not data.startswith(b"%PDF"):
                return jsonify({"error": "Invalid PDF file"}), 415
            try:
                resume_text = pdf_to_text(data)
            except (PdfReadError, PdfStreamError, ValueError, EOFError):
                return jsonify({"error": "Could not read this PDF"}), 422
            if len(resume_text.strip()) < 50:
                return jsonify({"error": "No text found (scanned PDF?)"}), 422

            skills = extract_skills(resume_text, load_vocab(db.session))
            resume_extraction = {
                "skills": skills,
                "cgpa": extract_cgpa(resume_text),
                "grad_year": extract_grad_year(resume_text),
            }

        os.makedirs(upload_directory, exist_ok=True)
        filename = f"{student.id}_{secrets.token_hex(16)}.{extension}"
        resume_path = os.path.join(upload_directory, filename)
        with open(resume_path, "wb") as saved_file:
            saved_file.write(data)

    inputs = request.form
    if "name" in inputs:
        student.name = inputs["name"]
    if "year" in inputs:
        student.year = inputs["year"]
    if "cgpa" in inputs:
        student.cgpa = inputs["cgpa"]
    if "dept" in inputs:
        student.dept = inputs["dept"]
    old_resume_path = student.resume_path
    if resume_path:
        student.resume_path = resume_path
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        if resume_path and os.path.exists(resume_path):
            try:
                os.remove(resume_path)
            except OSError:
                current_app.logger.warning("Could not remove unsaved resume %s", resume_path)
        return jsonify({"error": "Could not save profile"}), 500

    if resume_path and old_resume_path and os.path.abspath(old_resume_path) != resume_path:
        try:
            old_path = os.path.abspath(old_resume_path)
            if os.path.commonpath([upload_directory, old_path]) == upload_directory and os.path.isfile(old_path):
                os.remove(old_path)
        except (OSError, ValueError):
            current_app.logger.warning("Could not remove replaced resume %s", old_resume_path)

    cache.clear()
    return jsonify({
        "message": f"Profile of {student.name} updated successfully",
        "resume_extraction": resume_extraction,
    }), 200


@student_bp.route("/drive/apply/<int:drive_id>", methods=["POST"])
@role_required("student")
def apply_drive(drive_id):
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({"error": "Drive not found"}), 404
    if not drive.status == "approved":
        return jsonify({"error": "Drive not approved"}), 403
    if student.cgpa < drive.cgpa_above:
        return jsonify({"Message": f"Your CGPA is below the required CGPA of {drive.cgpa_above} for this drive"}), 403
    if student.dept not in drive.branches.split(","):
        return jsonify({"Message": "You are not eligible for this drive"}), 403
    if datetime.now() > drive.deadline:
        return jsonify({"Message": "The deadline for this drive has passed"}), 403
    today = date.today()
    age = today.year - student.dob.year
    if (today.month, today.day) < (student.dob.month, student.dob.day):
        age -= 1
    if drive.age_cat < age:
        return jsonify({"Message": "You are not eligible for this drive"}), 403
    if Application.query.filter_by(student_id=student.id, drive_id=drive.drive_id).first():
        return jsonify({"error": "You have already applied for this drive"}), 400
    application = Application(student_id=student.id, drive_id=drive.drive_id)
    db.session.add(application)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Successfully applied for this drive"}), 200


@student_bp.route("/student/<int:student_id>/placement", methods=["GET"])
@cache.cached(timeout=60)
@role_required("student")
def see_placement(student_id):
    if current_user.id != student_id:
        return jsonify({"error": "Unauthorized access"}), 400
    student = StudentProfile.query.filter_by(user_id=student_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    history = Application.query.filter_by(status="selected", student_id=student.id).all()
    if not history:
        return jsonify({"message": "Sorry you have not been selected for any drives yet..Keep Trying!"}), 200
    lis = [{"application_id": a.application_id, "company": a.drive.company.name, "jobtitle": a.drive.jobtitle, "status": a.status, "application_date": a.appl_date.strftime("%d-%m-%Y"), "salary": a.drive.salary} for a in history]
    return jsonify({"placement_history": lis}), 200


@student_bp.route("/<int:student_id>/resume", methods=["GET"])
@role_required("student", "admin", "company")
def get_resume(student_id):
    if current_user.role not in ("admin", "company") and current_user.id != student_id:
        return jsonify({"error": "Unauthorized access"}), 403
    student = StudentProfile.query.filter_by(user_id=student_id).first()
    if not student or not student.resume_path:
        return jsonify({"error": "No resume uploaded"}), 404
    return send_file(student.resume_path, as_attachment=False)


@student_bp.route("/applications/<int:application_id>/withdraw", methods=["PATCH"])
@role_required("student")
def withdraw(application_id):
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    appl = Application.query.get(application_id)
    if not appl:
        return jsonify({"error": "No application found"}), 404
    if appl.student_id != student.id:
        return jsonify({"error": "Unauthorized"}), 403
    if appl.status in ("rejected", "shortlisted", "selected", "withdrawn"):
        return jsonify({"error": "Cannot withdraw application"}), 400
    appl.status = "withdrawn"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Successfully withdrawn application"})


@student_bp.route("/drives/eligible", methods=["GET"])
@cache.cached(timeout=60)
@role_required("student")
def eligible():
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    drives = PlacementDrive.query.all()
    today = date.today()
    age = today.year - student.dob.year
    if (today.month, today.day) < (student.dob.month, student.dob.day):
        age -= 1
    eligible_drives = []
    for drive in drives:
        if student.cgpa < drive.cgpa_above or student.dept not in drive.branches.split(",") or (drive.age_cat and drive.age_cat < age):
            continue
        eligible_drives.append(drive)
    lis = [{"drive_id": p.drive_id, "company_id": p.company.name, "jobtitle": p.jobtitle, "skills": p.skills, "job_desc": p.job_desc, "open_postings": p.open_postings, "branches": p.branches, "cgpa_above": p.cgpa_above, "age_cat": p.age_cat, "deadline": p.deadline.strftime("%Y-%m-%d"), "status": p.status} for p in eligible_drives]
    return jsonify({"eligible_drives": lis}), 200


@student_bp.route("/<int:student_id>/info", methods=["GET"])
@cache.cached(timeout=60)
@role_required("student")
def get_student(student_id):
    if current_user.id != student_id:
        return jsonify({"error": "Unauthorized access"}), 400
    student = StudentProfile.query.filter_by(user_id=student_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"student": {"id": student.id, "name": student.name, "dept": student.dept, "cgpa": student.cgpa, "year": student.year, "dob": student.dob.strftime("%d-%m-%Y"), "resume_path": student.resume_path}}), 200


@student_bp.route("/export_csv_status/<task_id>", methods=["GET"])
@role_required("student")
def check_csv_status(task_id):
    result = AsyncResult(task_id, app=celery_app)
    return jsonify({"status": result.status, "result": result.result if result.successful() else None}), 200


@student_bp.route("/export", methods=["POST"])
@role_required("student")
def export():
    user_id = current_user.id
    task = export_csv.delay(user_id, "student")
    return jsonify({"status": "success", "task_id": task.id, "message": "Export queued at backend, Check email later.."}), 202

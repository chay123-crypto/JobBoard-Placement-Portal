from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from backend.models.models import CompanyProfile, StudentProfile, User, db
from backend.rate_limit import limiter

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    inputs = request.get_json(silent=True)
    if not isinstance(inputs, dict):
        return jsonify({"error": "A JSON request body is required"}), 400

    role = inputs.get("role")
    if role not in ("student", "company"):
        return jsonify({"error": "Invalid role. Must be student or company."}), 400

    if role == "student":
        required_fields = ("email", "contact_no", "password", "name", "dept", "dob", "year", "cgpa")
    else:
        required_fields = ("email", "contact_no", "password", "name", "website", "location", "field")
    missing_fields = [
        field
        for field in required_fields
        if inputs.get(field) is None or (isinstance(inputs.get(field), str) and not inputs[field].strip())
    ]
    if missing_fields:
        return jsonify({"error": f"Required fields missing: {', '.join(missing_fields)}"}), 400

    dob = None
    if role == "student":
        try:
            dob = datetime.strptime(inputs.get("dob"), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid DOB format"}), 400

    email = inputs.get("email")
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    phone = inputs.get("contact_no")
    if User.query.filter_by(contact_no=phone).first():
        return jsonify({"error": "Contact number already registered"}), 409

    acct = User(role=role, email=email, contact_no=phone)
    acct.set_password(inputs.get("password"))
    db.session.add(acct)

    if role == "student":
        profile = StudentProfile(user=acct, name=inputs.get("name"), dept=inputs.get("dept"), dob=dob, year=inputs.get("year"), cgpa=inputs.get("cgpa"), resume_path="")
    else:
        profile = CompanyProfile(user=acct, name=inputs.get("name"), website=inputs.get("website"), location=inputs.get("location"), field=inputs.get("field"))
    try:
        db.session.add(profile)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return jsonify({"message": f"{role.upper()} registered successfully"}), 200


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    inputs = request.get_json(silent=True)
    if not isinstance(inputs, dict):
        return jsonify({"error": "A JSON request body is required"}), 400
    email = inputs.get("email")
    password = inputs.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.checking_password(password):
        return jsonify({"error": "Invalid password or email. Try again"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated. Contact admin."}), 403
    login_user(user)
    return jsonify({"id": user.id, "email": user.email, "role": user.role, "contact_no": user.contact_no, "is_active": user.is_active}), 200


@auth_bp.route("/check", methods=["GET"])
@login_required
def check_auth():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not logged in"}), 401
    return jsonify({"id": current_user.id, "email": current_user.email, "role": current_user.role, "contact_no": current_user.contact_no, "is_active": current_user.is_active}), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out."}), 200

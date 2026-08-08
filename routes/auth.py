from flask import Blueprint,jsonify,request
from flask_login import login_user,logout_user,login_required,current_user
from models.models import db,User,StudentProfile,CompanyProfile
from datetime import datetime

auth_bp=Blueprint('auth',__name__,url_prefix='/auth')

@auth_bp.route('/register',methods=['POST'])
def register():
    inputs=request.get_json()
    role=inputs.get('role')
    if role not in ('student','company'):
        return jsonify({'error':'Invalid role. Must be student or company.'}), 400

    email=inputs.get('email')
    if User.query.filter_by(email=email).first():
        return jsonify({'error':'Email already registered'}), 409
    
    phone=inputs.get('contact_no')
    if User.query.filter_by(contact_no=phone).first():
        return jsonify({'error':'Contact number already registered'}), 409
    
    acct=User(role=role,email=email,contact_no=phone)
    acct.set_password(inputs.get('password'))
    db.session.add(acct)
    db.session.flush()

    if role=='student':
        profile=StudentProfile(
            user_id=acct.id,
            name=inputs.get('name'),
            dept=inputs.get('dept'),
            dob=datetime.strptime(inputs.get('dob'),'%Y-%m-%d').date(),
            year=inputs.get('year'),
            cgpa=inputs.get('cgpa'),
            resume_path=inputs.get('resume_path','')
        )
    else:
        profile=CompanyProfile(
            user_id=acct.id,
            name=inputs.get('name'),
            website=inputs.get('website'),
            location=inputs.get('location'),
            field=inputs.get('field')
        )
    db.session.add(profile)
    db.session.commit()
    return jsonify({'message':f'{role.upper()} registered successfully'}),200

@auth_bp.route("/login",methods=['POST'])
def login():
    inputs=request.get_json()
    email=inputs.get('email')
    password=inputs.get('password')

    user=User.query.filter_by(email=email).first()

    if not user or not user.checking_password(password):
        return jsonify({'error': 'Invalid password or email. Try again'}),401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Contact admin.'}),403 
    login_user(user)
    return jsonify({'id':user.id,'email':user.email,'role':user.role,'contact_no':user.contact_no,'is_active':user.is_active}),200

@auth_bp.route('/check',methods=['GET'])
@login_required
def check_auth():
    if not current_user.is_authenticated:
        return jsonify({"error":"User not logged in"}),401
    return jsonify({'id':current_user.id,'email':current_user.email,'role':current_user.role,'contact_no':current_user.contact_no,'is_active':current_user.is_active}),200

@auth_bp.route('/logout',methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out.'}),200

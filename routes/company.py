from flask import Blueprint,jsonify,request
from flask_login import login_required,current_user
from decorator import role_required
from cache import cache,init_cache
from datetime import date,datetime
from celeryset import celery_app
from tasks import export_csv, get_reminders
from celery.result import AsyncResult
from models.models import User,StudentProfile,CompanyProfile,db,Application,PlacementDrive,Interview

company_bp=Blueprint('company',__name__,url_prefix='/company')

@company_bp.route('/dashboard',methods=['GET'])
@cache.cached(timeout=60)
@role_required('company')
def company_dashboard():
    company=CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if not company:
        return jsonify({'error':'company not found'}),404
    elif company.approval_status!='approved':
        return jsonify({'error':'company not yet approved by the admin'}),403

    drives=PlacementDrive.query.filter_by(company_id=company.id).all()
    drive_ids=[d.drive_id for d in drives]
    num_applications=Application.query.filter(Application.drive_id.in_(drive_ids)).count()
    num_placement_drives=len(drive_ids)
    lis=[{'drive_id':d.drive_id,'jobtitle':d.jobtitle,'job_desc':d.job_desc,'open_postings':d.open_postings,'branches':d.branches,'cgpa_above':d.cgpa_above,'age_cat':d.age_cat,'deadline':d.deadline.strftime('%Y-%m-%d'),'status':d.status} for d in drives]
    return jsonify(
        {'company_name':company.name,'website':company.website,'approval_status':company.approval_status,'field':company.field,'location':company.location,'num_applications':num_applications,'num_placement_drives':num_placement_drives,'drives':lis}
    )

@company_bp.route('/create_drive',methods=['POST'])
@role_required('company')
def apply_drive():
    company=CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if not company:
        return jsonify({'error':'company not found'}),404
    elif company.approval_status!='approved':
        return jsonify({'error':'company not yet approved by the admin'}),403 
    data=request.get_json()
    required=['jobtitle','branches','cgpa_above','deadline','open_postings','salary']
    for field in required:
        if not data.get(field):
            return jsonify({'error':f'required fields missing. check {field}'}),400
    try:
        deadline=datetime.strptime(data.get('deadline'),'%Y-%m-%d')
    except ValueError:
        return jsonify({'error':'Deadline cannot be in the past'}),400
    drive=PlacementDrive(company_id=company.id,branches=data.get('branches'),status='pending',deadline=deadline,skills=data.get('skills'),jobtitle=data.get('jobtitle'),job_desc=data.get('job_desc'),cgpa_above=data.get('cgpa_above'),open_postings=data.get('open_postings'),age_cat=data.get('age_cat', ''),salary=data.get('salary'))
    db.session.add(drive) 
    db.session.commit()
    cache.clear()
    return jsonify({'message':'Successfully applied drive'}),200

@company_bp.route('/drives/applicants',methods=['GET'])
@cache.cached(timeout=60)
@role_required('company')
def get_all_applicants():
    company=CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if not company:
        return jsonify({'error':'company not found'}),404
    drive_ids=[drive.drive_id for drive in PlacementDrive.query.filter_by(company_id=company.id).all()]
    application=Application.query.filter(Application.drive_id.in_(drive_ids)).all()
    results=[]
    for a in application:
        results.append({'application_id':a.application_id,'student_id':a.student_id,'student_name':a.student.name,'dept': a.student.dept,'cgpa': a.student.cgpa,'year': a.student.year,'status':a.status,'jobtitle':a.drive.jobtitle,'applied_date': a.appl_date.strftime('%Y-%m-%d')})
    return jsonify({'applicants':results}),200

@company_bp.route('/student/<int:student_id>/info',methods=['GET'])
@cache.cached(timeout=60)
@role_required('company')
def get_student(student_id):
    student=StudentProfile.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({"error":"Student not found"}),404
    return jsonify({'student':{'id': student.id, 'user_id': student.user_id, 'name': student.name, 'dept': student.dept, 'cgpa': student.cgpa,'year': student.year,'dob':student.dob.strftime("%d-%m-%Y"), 'resume_path': student.resume_path}}),200
    
@company_bp.route('/drives/<int:drive_id>/applicants',methods=['GET'])
@cache.cached(timeout=60)
@role_required('company')
def get_applicants(drive_id):
    company=CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if not company:
        return jsonify({'error':'company not found'}),404
    drive=PlacementDrive.query.filter_by(drive_id=drive_id,company_id=company.id).first()
    if not drive:
        return jsonify({'error':'no drive found'}),404
    application=Application.query.filter_by(drive_id=drive_id).all()
    results=[]
    for a in application:
        results.append({'application_id':a.application_id,'student_id':a.student_id,'student_name':a.student.name,'dept': a.student.dept,'cgpa': a.student.cgpa,'year': a.student.year,'status':a.status,'applied_date': a.appl_date.strftime('%Y-%m-%d')})
    return jsonify({'jobtitle':drive.jobtitle,'applicants':results}),200

@company_bp.route('/application/<int:application_id>/status',methods=['PATCH'])
@role_required('company')
def update_application_status(application_id):
    appl=Application.query.get(application_id)
    if not appl:
        return jsonify({'error':'Application not found'}),404
    company=CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drive=PlacementDrive.query.filter_by(drive_id=appl.drive_id,company_id=company.id).first()
    if not drive:
        return jsonify({'error':'no drive found'}),404
    action=request.get_json().get('action')
    if action not in ('selected','rejected','shortlisted'):
        return jsonify({'error':'unknown approval action'}),400
    appl.status=action
    db.session.commit()
    cache.clear()
    return jsonify({'message':f"Application {application_id}'s status updated to {appl.status}"}),200

@company_bp.route("/export",methods=['POST'])
@role_required('company')
def export():
    user_id=current_user.id
    task=export_csv.delay(user_id,'company')
    return jsonify({'status':'success','task_id':task.id,'message':'Export queued at backend, Check email later..'}),202

@company_bp.route('/<int:company_id>/drives',methods=['GET'])
@cache.cached(timeout=60)
@role_required('company')
def see_drives(company_id):
    if not company_id==current_user.id:
        return jsonify({'error':'company not found'}),404
    company=CompanyProfile.query.filter_by(user_id=current_user.id).first()
    drive=PlacementDrive.query.filter_by(company_id=company.id).all()
    lis=[{'drive_id':d.drive_id,'jobtitle':d.jobtitle,'job_desc':d.job_desc,'open_postings':d.open_postings,'branches':d.branches,'cgpa_above':d.cgpa_above,'age_cat':d.age_cat,'deadline':d.deadline.strftime('%Y-%m-%d'),'status':d.status,'skills':d.skills} for d in drive]
    return jsonify({'drives':lis}),200

@company_bp.route('/drive/<int:drive_id>/close',methods=['PATCH'])
@role_required('company')
def close_drive(drive_id):
    company=CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if not company:
        return jsonify({'error':'company not found'}),404
    drive=PlacementDrive.query.filter_by(drive_id=drive_id,company_id=company.id).first()
    if not drive:
        return jsonify({'error':'no drive found'}),404
    drive.status='closed'
    db.session.commit()
    cache.clear()
    return jsonify({'message':f'drive {drive_id} closed successfully'}),200

@company_bp.route('/<int:company_id>/info',methods=['GET'])
@role_required('company')
def company(company_id):
    if not company_id==current_user.id:
        return jsonify({'error':'company not found'}),404
    company=CompanyProfile.query.filter_by(user_id=company_id).first()
    if not company:
        return jsonify({'error':'company not found'}),404
    placement_drives=PlacementDrive.query.filter_by(company_id=company.id).all()
    drives=[{'drive_id':d.drive_id,'jobtitle':d.jobtitle,'job_desc':d.job_desc,'open_postings':d.open_postings,'branches':d.branches,'cgpa_above':d.cgpa_above,'age_cat':d.age_cat,'deadline':d.deadline.strftime('%Y-%m-%d'),'status':d.status} for d in placement_drives]
    return jsonify({'company_id':company.id,'name':company.name,'website':company.website,'approval_status':company.approval_status,'drives':drives}),200


@company_bp.route('/schedule_interview/<int:application_id>',methods=['POST'])
@role_required('company')
def invite_interview(application_id):
    try:
        data=request.json
        application=Application.query.get(application_id)
        if not application:
            return jsonify({'error':'No application found'}),404
        interview=Interview(
            student_id=application.student_id,
            company_id=application.drive.company_id,
            application_id=application_id,
            interview_date=data['interview_date'],
            interview_time=data['interview_time'],
            location=data['location'],
            status='scheduled'
        )
        db.session.add(interview)
        db.session.commit()
        cache.clear()
        task=get_reminders.delay(
            interview.student_id,
            interview.interview_date,
            interview.interview_time,
            interview.company.name,
            interview.location
        )
        return jsonify({'status':'success','interview_id':interview.interview_id,'message':'interview scheduled'})
    except Exception as e:
        return jsonify({'error':str(e)}),400
    
@company_bp.route("/exported_csv_status/<task_id>",methods=['GET'])
@role_required('company')
def check_csv_status(task_id):
    result=AsyncResult(task_id, app=celery_app)
    return jsonify({'status': result.status,'result': result.result if result.successful() else None}),200
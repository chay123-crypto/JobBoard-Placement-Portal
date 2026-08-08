from flask import Blueprint,jsonify,request
from flask_login import login_required
from decorator import role_required
from cache import cache,init_cache
from models.models import User,StudentProfile,CompanyProfile,db,Application,PlacementDrive,Interview
import numpy as np
from tasks import get_reminders

admin_bp=Blueprint('admin',__name__,url_prefix='/admin')

@admin_bp.route('/admin_dashboard',methods=['GET'])
@cache.cached(timeout=60)
@role_required('admin')
def admin_dashboard():
    num_students=StudentProfile.query.count()
    num_placedstudents=db.session.query(Application.student_id).filter_by(status='selected').distinct().count()
    selected_apps=Application.query.filter_by(status='selected').all()
    salaries=[a.drive.salary for a in selected_apps if (a.drive and 'intern' not in a.drive.jobtitle.lower())]
    stipends=[a.drive.salary for a in selected_apps if (a.drive and 'intern' in a.drive.jobtitle.lower())]
    if salaries:
        avg_salary=round(np.mean(salaries),2)
        median_salary=round(np.median(salaries),2)
        min_salary=round(np.min(salaries),2)
        max_salary=round(np.max(salaries),2)   
    else:
        avg_salary=0
        median_salary=0
        min_salary=0
        max_salary=0
    if stipends:
        avg_stipend=round(np.mean(stipends),2)
        median_stipend=round(np.median(stipends),2)
    else:
        avg_stipend=0
        median_stipend=0
    num_applications=Application.query.count()
    num_companies=CompanyProfile.query.count()
    num_placement_drives=PlacementDrive.query.count()
    return jsonify({'num_students':num_students,'num_companies':num_companies,'num_placement_drives':num_placement_drives,'num_placed':num_placedstudents,'num_applications':num_applications,'maxSalary':max_salary,'minSalary':min_salary,'avgSalary':avg_salary,'medianSalary':median_salary,'AvgStipend':avg_stipend,'MedianStipend':median_stipend})

@admin_bp.route('/search_student',methods=['GET'])
@role_required('admin')
def search_students():
    query=request.args.get('query','')
    if StudentProfile.query.filter(StudentProfile.name.ilike(f'%{query}%')).first():
        student=StudentProfile.query.filter(StudentProfile.name.ilike(f'%{query}%')).all()
    else:
        return jsonify({'error':'student not found'}),404
    lis=[{'student_id':s.id,'name':s.name,'dept':s.dept,'year':s.year,'cgpa':s.cgpa} for s in student]
    if lis:
        return jsonify({'students':lis}),200
    else:
        return jsonify({'error':'student not found'}),404

@admin_bp.route('/search_company',methods=['GET'])
@role_required('admin')
def search_companies():
    query=request.args.get('query','')
    if CompanyProfile.query.filter(CompanyProfile.name.ilike(f'%{query}%')).first():
        company=CompanyProfile.query.filter(CompanyProfile.name.ilike(f'%{query}%')).all()
    else:
        return jsonify({'error':'company not found'}),404
    lis=[{'company_id':c.id,'name':c.name,'website':c.website,'approval_status':c.approval_status} for c in company]
    if lis:
        return jsonify({'companies':lis}),200
    else:
        return jsonify({'error':'company not found'}),404

@admin_bp.route('/view_students',methods=['GET'])
@cache.cached(timeout=60)
@role_required('admin')
def view_students():
    students=StudentProfile.query.all()
    lis=[{'student_id':s.user_id,'name':s.name,'dept':s.dept,'year':s.year,'cgpa':s.cgpa,'is_active':s.user.is_active} for s in students]
    return jsonify({'students':lis}),200

@admin_bp.route('/view_companies',methods=['GET'])
@cache.cached(timeout=60)
@role_required('admin')
def view_companies():
    companies=CompanyProfile.query.all()
    lis=[{'company_id':c.id,'user_id':c.user_id,'name':c.name,'website':c.website,'approval_status':c.approval_status,'is_active':c.user.is_active,'field':c.field,'location':c.location} for c in companies]
    return jsonify({'companies':lis}),200

@admin_bp.route('/all_drives',methods=['GET'])
@cache.cached(timeout=60)
@role_required('admin')
def all_drives():
    drives=PlacementDrive.query.all()
    company_ids=[d.company_id for d in drives]
    applied=Application.query.all()
    lis2=[{'application_id':a.application_id,'student_id':a.student_id,'drive_id':a.drive_id,'status':a.status} for a in applied]
    companies=[c.name for c in CompanyProfile.query.filter(CompanyProfile.id.in_(company_ids)).all()]
    lis=[{'drive_id':p.drive_id,'company':p.company.name,'jobtitle':p.jobtitle,'job_desc':p.job_desc,'open_postings':p.open_postings,'branches':p.branches,'cgpa_above':p.cgpa_above,'skills':p.skills,'age_cat':p.age_cat,'deadline':p.deadline.strftime('%Y-%m-%d'),'status':p.status} for p in drives]
    return jsonify({'company_names':companies,'drives':lis,'applications':lis2}),200

@admin_bp.route('/drives/<int:drive_id>/applicants',methods=['GET'])
@role_required('admin')
def get_applicants(drive_id):
    drive=PlacementDrive.query.filter_by(drive_id=drive_id).first()
    if not drive:
        return jsonify({'error':'no drive found'}),404
    application=Application.query.filter_by(drive_id=drive_id).all()
    results=[]
    for a in application:
        results.append({'application_id':a.application_id,'user_id':a.student.user_id,'student_id':a.student.id,'name':a.student.name,'dept': a.student.dept,'cgpa': a.student.cgpa,'year': a.student.year,'status':a.status,'resume_path':a.student.resume_path,'applied_date': a.appl_date.strftime('%Y-%m-%d')})
    return jsonify({'jobtitle':drive.jobtitle,'applicants':results}),200

@admin_bp.route('/company/<int:company_id>/status',methods=['PATCH'])
@role_required('admin')
def update_company_status(company_id):
    company=CompanyProfile.query.get(company_id)
    if not company:
        return jsonify({'error':'Company not found'}),404
    action=request.get_json().get('action')
    if action not in ('approve','reject'):
        return jsonify({'error':'unknown approval action'}),400
    company.approval_status='approved' if action=='approve' else "rejected"
    db.session.commit()
    cache.clear()
    return jsonify({'message':f"Company {company_id}'s status updated to {company.approval_status}"}),200

@admin_bp.route('/remind_interview/<int:interview_id>',methods=['POST'])
@role_required('admin')
def schedule_interview(interview_id):
    interview=Interview.query.get(interview_id)
    if not interview:
        return jsonify({'error':'No interview schedule found'}),404
    task=get_reminders.delay(
        interview.student_id,
        interview.interview_date,
        interview.interview_time,
        interview.company.name
    )
    cache.clear()
    return jsonify({
        'status':'success',
        'task_id':task.id,
        'message':'Interview reminder queued'
    }),201

@admin_bp.route('/drive/<int:drive_id>/status',methods=['PATCH'])
@role_required('admin')
def update_drive_status(drive_id):
    drive=PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({'error':'Drive not found'}),404
    action=request.get_json().get('action')
    if action not in ('approve','reject'):
        return jsonify({'error':'unknown approval action'}),400
    drive.status='approved' if action=='approve' else "rejected"
    db.session.commit()
    cache.clear()
    return jsonify({'message':f"Drive {drive_id}'s status updated to {drive.status}"}),200

@admin_bp.route('/user/<int:user_id>/deactivate',methods=['PATCH'])
@role_required('admin')
def deactivate_user(user_id):
    user=User.query.get(user_id)
    if not user:
        return jsonify({'error':'User not found'}),404
    if user.role=='admin':
        return jsonify({'error':'Cannot deactivate admin user'}),403
    user.is_active=not user.is_active
    db.session.commit()
    cache.clear()
    status="activated" if user.is_active else "deactivated"
    return jsonify({'message':f"User {user.id} is {status}"}),200

@admin_bp.route('/placement',methods=['GET'])
@cache.cached(timeout=60)
@role_required('admin')
def see_placement():
    history=Application.query.filter_by(status='selected').all()
    if not history:
        return jsonify({"message":"No placement history found"}),200
    lis=[{'application_id':a.application_id,'company':a.drive.company.name,'jobtitle':a.drive.jobtitle,'status':a.status,'application_date':a.appl_date.strftime("%d-%m-%Y"),'salary':a.drive.salary} for a in history]
    return jsonify({'placement_history':lis}),200

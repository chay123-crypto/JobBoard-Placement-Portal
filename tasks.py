from celeryset import celery_app
from flask_mail import Message
from flask import render_template_string
import csv
import os
import numpy as np
from datetime import datetime,timezone

@celery_app.task
def export_csv(user_id,user_role):
    try:
        from app import mail,app
        from models.models import StudentProfile,Application,CompanyProfile,PlacementDrive
        with app.app_context():
            export_directory='exports'
            os.makedirs(export_directory,exist_ok=True)
            if user_role=='student':
                student=StudentProfile.query.filter_by(user_id=user_id).first()
                if not student:
                    return {'status':'error','message':'Student not found'}
                appl=Application.query.filter_by(student_id=student.id).all()
                filename=f"{export_directory}/student_{user_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

                with open(filename,"w",newline='') as file:
                    buffer=csv.writer(file)
                    buffer.writerow(['Application ID','Company','Job Title','Job Description','Open Postings','Status','Applied Date'])
                    for a in appl:
                        buffer.writerow([
                            a.application_id,
                            a.drive.company.name,
                            a.drive.jobtitle,
                            a.drive.job_desc,
                            a.drive.open_postings,
                            a.status,
                            a.appl_date.strftime("%d-%m-%Y")
                        ])
                mail_body=Message(
                    subject="Your Applications Export",
                    recipients=[student.user.email],
                    body=f"Dear {student.name},\n\n Your cumulative applications till last month is made ready as an export for you.\n\n File:{os.path.basename(filename)}\n\nBest Regards,\nPlacement Team"
                )
                with open(filename,"r") as f:
                    mail_body.attach(filename=os.path.basename(filename),content_type="text/csv",data=f.read())
                mail.send(mail_body)
                return {'status':'success','filename':filename,'rows':len(appl)}
            
            if user_role=='company':
                company=CompanyProfile.query.filter_by(user_id=user_id).first()
                if not company:
                    return {'status': 'error', 'message': 'Company not found'}
                drives=PlacementDrive.query.filter_by(company_id=company.id).all()
                drive_ids=[d.drive_id for d in drives]
                appl=Application.query.filter(Application.drive_id.in_(drive_ids)).all()
                filename=f"{export_directory}/company_{user_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

                with open(filename,"w",newline='') as file:
                    buffer=csv.writer(file)
                    buffer.writerow(['Student ID','Name','Department','CGPA','Job Title','Status','Applied Date'])
                    for a in appl:
                        buffer.writerow([
                            a.student_id,
                            a.student.name,
                            a.student.dept,
                            a.student.cgpa,
                            a.drive.jobtitle,
                            a.status,
                            a.appl_date.strftime("%d-%m-%Y")
                        ])
                mail_body=Message(
                    subject="Your Applications Export",
                    recipients=[company.user.email],
                    body=f"Dear {company.name},\n\n Your cumulative applications till last month is made ready as an export for you.\n\n File:{os.path.basename(filename)}\n\nBest Regards,\nPlacement Team"
                )
                with open(filename,"r") as f:
                    mail_body.attach(filename=os.path.basename(filename),content_type="text/csv",data=f.read())
                mail.send(mail_body)
                return {'status':'success','filename':filename,'rows':len(appl)}
    except Exception as e:
        return {'status':'error','message':str(e)}

@celery_app.task
def get_reminders(student_id,interview_date,interview_time,company_name,interview_location):
    try:
        from app import mail,app
        from models.models import StudentProfile
        with app.app_context():
            student = StudentProfile.query.get(student_id)
            if not student:
                return {'status': 'error', 'message': 'Student not found'}
            
            msg=Message(
                subject=f'Interview Reminder - {company_name}',
                recipients=[student.user.email],
                body=f'''Dear {student.name},

                Your interview is scheduled!

                Company: {company_name}
                Date: {interview_date}
                Time: {interview_time}
                Location: {interview_location}

                Please be ready 10 minutes before the time assigned. Further updates will be disclosed closer to the interview. 
                We wish you all the best!

                Best regards,
                Placement Team'''
                            )
            mail.send(msg)
            return {'status':'success','student_id':student_id}
    
    except Exception as e:
        return {'status':'error','message':str(e)}

@celery_app.task
def generate_monthly_reports():
    from app import app,mail
    from models.models import PlacementDrive,CompanyProfile,User,Application,Interview
    
    try:
        with app.app_context():
            approvedcomp=CompanyProfile.query.filter_by(approval_status='approved').all()
            for comp in approvedcomp:
                user=User.query.get(comp.user_id)
                if not user:
                    continue
                drives=PlacementDrive.query.filter_by(company_id=comp.id).all()
                if drives:
                    numDrives=len(drives)
                    interns=[d for d in drives if 'intern' in d.jobtitle.lower()]
                    jobs=[d for d in drives if 'intern' not in d.jobtitle.lower()]
                    if interns:
                        MedianSalaryIntern=round(np.median([d.salary for d in interns]),2)
                        AvgSalaryIntern=round(np.mean([d.salary for d in interns]),2)
                        numInterns=len(interns)
                    else:
                        numInterns=0
                        MedianSalaryIntern=0
                        AvgSalaryIntern=0
                    if jobs:
                        numInterns=len(interns)
                        numJobs=len(jobs)
                        MaxSalary=round(max([d.salary for d in jobs]),2)
                        MinSalary=round(min([d.salary for d in jobs]),2)
                        MedianSalary=round(np.median([d.salary for d in jobs]),2)
                        AvgSalary=round(np.mean([d.salary for d in jobs]),2)
                    else:
                        MaxSalary=0
                        MinSalary=0
                        MedianSalary=0
                        numJobs=0
                        AvgSalary=0
                else:
                    numDrives=0

                drive_ids=[d.drive_id for d in drives]
                applications=Application.query.filter(Application.drive_id.in_(drive_ids)).all()
                if applications:
                    total_apps=len(applications)
                    shortlisted_counts=len([a for a in applications if a.status=='shortlisted'])
                    selected_counts=len([a for a in applications if a.status=='selected'])
                    rejected_counts=len([a for a in applications if a.status=='rejected'])
                else:
                    total_apps=0
                    shortlisted_counts=0
                    selected_counts=0
                    rejected_counts=0
                numInterviews=len(Interview.query.filter_by(company_id=comp.id).all())
            
                curr_month=datetime.now().strftime("%B")
                curr_year=datetime.now().strftime("%Y")
                if drives:
                    html="""
                    <html>
                    <body style="font-family:Arial;color:#444;">
                    <h2 style="color:#3378cc;">Monthly Placement Report</h2><br>
                    <p>Hello <strong>{{company_name}}</strong>,</p>
                    <p>Here is your placement activity report for the month {{curr_month}} {{curr_year}}. Please acknowledge!</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <div class="card-body">
                    <h4 class="card-title text-dark border-bottom pb-2" style="font-size:30px; color:brown">Drive Statistics</h4>
                    <ul class="list-group list-group-flush mt-3">
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Placement Drives : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ total_drives }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Job Drives : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ total_jobs }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Internship drives : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ total_interns }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Applications Received : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ total_applications }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Students Interviewed : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ total_interviews }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Shortlisted Students : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ shortlisted_counts }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Selected Students : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ selected_counts }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Total Rejected Students : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ rejected_counts }}</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Maximum Salary : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ max_salary }} LPA</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Minimum Salary : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ min_salary }} LPA</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Median Salary : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ median_salary }} PA</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Average Salary : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ avg_salary }} PA</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Median Stipend (For interns) : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ median_stipend }} PM</span>
                    </li>
                    <li style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #eee;">
                    <strong>Average Stipend (For interns) : </strong>
                    <span style="background:#0056b3; color:#fff; padding:2px 10px; border-radius:12px;">{{ avg_stipend }} PM</span>
                    </li>
                    </ul>
                    </div>
                    </div>
                    <div style="background-color: #e9ecef; border-radius: 6px; margin-bottom: 24px; padding: 16px;">
                    <h4 style="color: #212529; border-bottom: 1px solid #ced4da; padding-bottom: 8px; margin: 8px; font-size: 20px;">Applicant Status Breakdown</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 12px;">
                    <tbody>
                    <tr>
                        <td style="padding: 8px 4px; font-weight: bold; color: #212529;">Shortlisted:</td>
                        <td style="padding: 8px 4px; text-align: right;">
                        <span style="background-color: #ffc107; color: #212529; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold;">{{ shortlisted_counts }}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 4px; font-weight: bold; color: #212529;">Selected:</td>
                        <td style="padding: 8px 4px; text-align: right;">
                        <span style="background-color: #198754; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold;">{{ selected_counts }}</span>
                        </td>
                    </tr>
                    <tr>
                    <td style="padding: 8px 4px; font-weight: bold; color: #212529;">Rejected:</td>
                    <td style="padding: 8px 4px; text-align: right;">
                    <span style="background-color: #dc3545; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: bold;">{{ rejected_counts }}</span>
                    </td>
                    </tr>
                    </tbody>
                    </table>
                    </div>
                    </div>
                    </div>
                    <hr class="text-muted"><p class="text-center text-muted-small mt-3">Thank you for partnering with our Placement Cell.</p>
                    <p>Regards</p>
                    </body>
                    </html>
                    """
                    html_body=render_template_string(html,company_name=comp.name,curr_year=curr_year,total_drives=numDrives,total_applications=total_apps,total_jobs=numJobs,total_interns=numInterns,avg_stipend=AvgSalaryIntern,median_stipend=MedianSalaryIntern,max_salary=MaxSalary,min_salary=MinSalary,median_salary=MedianSalary,avg_salary=AvgSalary,total_interviews=numInterviews,shortlisted_counts=shortlisted_counts,selected_counts=selected_counts,rejected_counts=rejected_counts,curr_month=curr_month)
                else:
                    html="""
                    <html>
                    <body style="font-family:Arial;color:#444;">
                    <h2 style="color:#3378cc;">Monthly Placement Report</h2><br>
                    <p>Hello <strong>{{company_name}}</strong>,</p>
                    <p>Here is your placement activity report for the month {{curr_month}} {{curr_year}}. Please acknowledge!</p><br>
                    <div style="background-color: #e9ecef; border-radius: 6px; margin-bottom: 24px; padding: 16px;">
                    <p>No placement activity this month. Looking forward to collaborate with you sooner!</p><br>
                    <p>Regards</p>
                    </div>
                    </body>
                    </html>""" 
                    html_body=render_template_string(html,company_name=comp.name,curr_year=curr_year,curr_month=curr_month)

                msg=Message(subject="Your Monthly Placement Report",sender='noreply@placement-portal.com',recipients=[comp.user.email])
                msg.html=html_body
                mail.send(msg)
        return {'status':'success','message':f'Sent monthly reports to {len(approvedcomp)} companies.'}
    except Exception as e:
        return {'status':'error','message':str(e)}




from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timezone
from flask_login import UserMixin

db=SQLAlchemy()

class User(db.Model,UserMixin):
    __tablename__="userprofile"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(100),nullable=False)
    contact_no=db.Column(db.String(10),unique=True,nullable=False)
    is_active=db.Column(db.Boolean,default=True)
    company_profile=db.relationship('CompanyProfile',backref='user',uselist=False,cascade='all,delete-orphan')
    student_profile=db.relationship('StudentProfile',backref='user',uselist=False,cascade='all,delete-orphan')

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def checking_password(self,password):
        return check_password_hash(self.password_hash,password)

class StudentProfile(db.Model):
    __tablename__="studentprofile"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('userprofile.id'),nullable=False)
    dept=db.Column(db.String(100),nullable=False)
    dob=db.Column(db.Date,nullable=False)
    year=db.Column(db.Integer,nullable=False)
    cgpa=db.Column(db.Float,nullable=False)
    resume_path=db.Column(db.String(255),nullable=False)
    application=db.relationship('Application',backref='student',cascade='all,delete-orphan')

class CompanyProfile(db.Model):
    __tablename__="companyprofile"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('userprofile.id'),nullable=False)
    website=db.Column(db.String(255),nullable=False)
    field=db.Column(db.String(50),nullable=False)
    location=db.Column(db.String(50),nullable=False)
    approval_status=db.Column(db.String(100),nullable=False,default='pending')
    drives=db.relationship('PlacementDrive',backref='company',cascade='all,delete-orphan')

class Application(db.Model):
   __tablename__="applications"
   application_id=db.Column(db.Integer,primary_key=True)
   student_id=db.Column(db.Integer,db.ForeignKey('studentprofile.id'),nullable=False)
   drive_id=db.Column(db.Integer,db.ForeignKey('placementdrives.drive_id'),nullable=False)
   status=db.Column(db.String(100),nullable=False,default='applied')
   appl_date=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
   drive=db.relationship('PlacementDrive',backref='applications')
   __table_args__=(db.UniqueConstraint('student_id','drive_id',name='unique_application'),)

class PlacementDrive(db.Model):
    __tablename__="placementdrives"
    drive_id=db.Column(db.Integer,primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey('companyprofile.id'),nullable=False)
    jobtitle=db.Column(db.String(120),nullable=False)
    job_desc=db.Column(db.String(255))
    open_postings=db.Column(db.Integer,nullable=False)
    skills=db.Column(db.String(255))
    branches=db.Column(db.String(255),nullable=False)
    cgpa_above=db.Column(db.Float,nullable=False)
    salary=db.Column(db.Float,nullable=False)
    age_cat=db.Column(db.Integer)
    deadline=db.Column(db.DateTime,nullable=False)
    status=db.Column(db.String(100),nullable=False,default='pending')

class Interview(db.Model):
    __tablename__="interview"
    interview_id=db.Column(db.Integer,primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey('companyprofile.id'),nullable=False)
    student_id=db.Column(db.Integer,db.ForeignKey('studentprofile.id'),nullable=False)
    application_id=db.Column(db.Integer,db.ForeignKey('applications.application_id'),nullable=False)
    interview_date=db.Column(db.String(50),nullable=False)
    interview_time=db.Column(db.String(50),nullable=False)
    location=db.Column(db.String(255),nullable=False)
    status=db.Column(db.String(50),nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    student=db.relationship('StudentProfile',backref='interview')
    company=db.relationship('CompanyProfile',backref='interview')
    application=db.relationship('Application',backref='interview')

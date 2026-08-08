from celery import Celery
from celery.schedules import crontab
from datetime import datetime,timedelta

celery_app=Celery('placement_portal')
celery_app.conf.broker_url='redis://localhost:6379/0'
celery_app.conf.result_backend='redis://localhost:6379/1'

celery_app.conf.task_serializer='json'
celery_app.conf.accept_content=['json']
celery_app.conf.result_serializer='json'
celery_app.conf.timezone='UTC'
celery_app.conf.enable_utc=True

celery_app.conf.beat_schedule={
    'send-interview-reminders-every-day':{
        'task':'tasks.get_reminders',
        'schedule':crontab(hour=9,minute=0),  
    },
    'generate-placement-reports-monthly':{
        'task':'tasks.generate_monthly_reports',
        'schedule':crontab(day_of_month=1,hour=0,minute=0),
    }
}
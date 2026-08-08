# Placement Portal

A role-based placement management system for colleges.

## Features

- **Admin Dashboard**: Manage companies, postings, applications, and statistics
- **Student Dashboard**: Browse jobs, apply, and track applications
- **Company Dashboard**: Post jobs, review applications, schedule interviews
- **Role-based Access Control**: Secure authentication for Admin, Student, and Company users
- **Background Tasks**: Automated interview reminder emails and CSV exports via Celery
- **Email Notifications**: Interview reminders sent via Flask-Mail (tested locally with MailHog)

## Tech Stack

- **Frontend**: Vue.js, JavaScript, HTML, Bootstrap 5
- **Backend**: Flask
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Task Queue**: Celery + Celery Beat
- **Message Broker**: Redis
- **Caching**: Flask-Caching
- **Email Testing**: MailHog (local SMTP catcher)

## Prerequisites

- Python 3.x
- WSL (or a Linux environment) for Redis and MailHog
- Redis server
- MailHog

## Installation

```bash
git clone <repo-url>
cd placement-portal

# Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# Install backend dependencies
pip install flask flask-sqlalchemy flask-login flask-mail flask-caching celery redis numpy werkzeug
```

## Running the App

This project runs across **5 terminals**: the Flask app, Redis, MailHog, Celery worker, and Celery Beat.

### Terminal 1 — MailHog (WSL)
Catches outgoing emails locally so you can preview them in the browser.
```bash
mailhog
```
View caught emails at: `http://localhost:8025`

### Terminal 2 — Redis (WSL)
Message broker for Celery.
```bash
sudo service redis-server start
```

### Terminal 3 — Flask App
```bash
python app.py
```

### Terminal 4 — Celery Worker
```powershell
$env:PYTHONPATH="."
celery -A tasks.celery_app worker --loglevel=info -P solo
```

### Terminal 5 — Celery Beat (scheduler)
```bash
celery -A celeryset beat -l DEBUG
```
Handles scheduled jobs — e.g. daily interview reminders and monthly placement reports (see `celeryset.py` for the schedule).

## Usage

1. Register as Admin, Student, or Company
2. Log in to access your role-based dashboard
3. Manage placements, applications, and interviews based on your role
4. Check `http://localhost:8025` (MailHog) to view any emails sent by the app

## Project Structure

```
placement-portal/
├── app.py            # Flask app entry point
├── celeryset.py       # Celery app config + beat schedule
├── tasks.py           # Celery background tasks (email reminders, CSV export, reports)
├── cache.py           # Flask-Caching setup
├── decorator.py        # Custom decorators (role-based access, etc.)
├── init_db.py          # Database initialization
├── models/
│   └── models.py       # SQLAlchemy models
├── routes/
│   ├── admin.py
│   ├── auth.py
│   ├── company.py
│   └── student.py
├── templates/
│   └── index.html      # Root HTML shell (renders the Vue app)
└── static/
    └── js/
        ├── main.js
        └── components/
```

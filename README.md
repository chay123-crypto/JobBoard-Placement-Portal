# JobBoard – Full-Stack Placement Portal

A production-ready SPA built with **Vue.js + Flask** demonstrating real-world full-stack development patterns. This project showcases role-based dashboards, RESTful API design, background task processing, component-driven architecture, robust test coverage with pytest, and automated CI/CD workflows.

**Perfect for:** Learning Vue.js through a complete project | Portfolio demonstration | Understanding full-stack architecture | CI/CD implementation basics | Comprehensive Flask testing

Demo Link: https://jobboard-placement-portal.onrender.com/

---

## 🎯 Learning Objectives

By working through this project, I mastered:

- **Vue.js Fundamentals**: Component composition, props/emit patterns, lifecycle hooks, conditional rendering, list management
- **SPA Architecture**: Client-side routing, state management across components, API communication patterns
- **Backend Integration**: RESTful API design, CORS, authentication, role-based access control (RBAC)
- **Async Operations**: Promises, async/await, handling API responses and errors
- **Production Patterns**: Dynamic caching strategies (`Flask-Caching`), background task queues (`Celery`), email notifications (`Flask-Mail`)
- **Database Design**: SQLAlchemy ORM, model relationships, migrations with indexing foreign key attributes
- **Comprehensive Testing**: 90 unit & integration tests using `pytest`, in-memory SQLite, fixture isolation, and Celery/Redis mocking
- **CI/CD Pipeline**: GitHub Actions workflows for automated linting (`Ruff`), auto-formatting (`Black`), and running test suites
- **Full-Stack Debugging**: Browser DevTools + Flask logging to trace issues end-to-end

---

## 📋 Features

| Feature | Technology | Learning Value |
|---------|-----------|-----------------|
| **Multi-role Dashboard** | Vue.js Components | Conditional UI rendering, component reusability |
| **Role-Based Access** | Flask decorators + Auth | Session management, authorization patterns |
| **Job Management** | Vue forms + REST API | Form validation, CRUD operations, API integration |
| **Application Tracking** | Dynamic tables, Vue state | List rendering, filtering, real-time updates |
| **Email Notifications** | Celery + Flask-Mail | Async task processing, scheduled jobs |
| **CSV Export** | Celery background tasks | Long-running operations, progress tracking |
| **Caching Layer** | Flask-Caching | Performance optimization, cache invalidation |
| **Automated Testing** | Pytest | 90 tests covering all routes across all 4 blueprints |
| **CI/CD Pipeline** | GitHub Actions | Automated linting, code formatting, and test execution on push/PR |

---

## 🛠 Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Vue.js, JavaScript (ES6+), HTML5, Bootstrap 5 |
| **Backend** | Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail, Flask-Caching |
| **Database** | SQLite (easily swapped to PostgreSQL) |
| **Task Queue** | Celery + Redis message broker |
| **Scheduling** | Celery Beat (cron-like scheduler) |
| **Email Testing** | MailHog (local SMTP catcher) |
| **Caching** | Flask-Caching (Redis / NullCache for testing) |
| **Testing** | Pytest, Pytest-Flask, Pytest-Cov |
| **Code Quality** | Ruff (linter), Black (formatter) |
| **CI/CD** | GitHub Actions workflows |
| **Containerization** | Docker, Docker Compose |

---

## 📁 Project Structure

Every file in the codebase and its respective responsibility:

```
JobBoard-Placement-Portal/
├── app.py                      # Flask app factory, configuration & blueprint registration
├── models/
│   └── models.py               # SQLAlchemy ORM models (User, StudentProfile, CompanyProfile, Application, PlacementDrive, Interview)
├── routes/
│   ├── auth.py                 # Authentication endpoints (register, login, check auth, logout)
│   ├── admin.py                # Admin dashboard API (stats, company/posting management, status updates)
│   ├── student.py              # Student API (browse jobs, eligible drives, apply, track applications, withdraw, export CSV)
│   └── company.py              # Company API (post drives, review applications, schedule interviews, export CSV)
├── tasks.py                    # Celery background tasks (email reminders, CSV export, monthly reports)
├── celeryset.py                # Celery configuration & beat schedule
├── cache.py                    # Flask-Caching setup (supports Redis / NullCache dynamically)
├── decorator.py                # Custom decorators (@login_required, @role_required)
├── init_db.py                  # Database initialization & seed data (creates default admin)
├── requirements.txt            # Python dependencies (Flask, SQLAlchemy, Celery, pytest, ruff, black, etc.)
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Multi-container setup (App, Redis, Celery worker)
├── .gitignore                  # Git ignore patterns
├── tests/
│   └── test_app.py             # Comprehensive Pytest suite with 90 tests across all route blueprints
├── templates/
│   └── index.html              # Single HTML shell (Vue mounts here)
├── static/
│   ├── background.png          # UI background image asset
│   └── js/
│       ├── main.js             # Vue app entry point, routing, global state
│       └── components/
│           ├── Login.js            # Authentication component
│           ├── Register.js         # Registration form (Student & Company)
│           ├── AdminDashboard.js   # Admin overview (stats, user & drive mgmt)
│           ├── StudentDashboard.js # Student job browse, eligibility & applications
│           └── CompanyDashboard.js # Company job posting, applicant review & interview scheduling
├── .github/
│   └── workflows/
│       ├── integration.yml     # CI pipeline (Ruff linting, Black formatting, Pytest execution)
│       └── main.yml            # Scheduled keep-alive ping workflow
├── specs/
│   └── app.yaml                # App Engine deployment config
└── README.md
```

**Key Insight**: The backend serves as a pure REST API; the frontend is a single-page app that consumes it. This separation makes testing, scaling, and deployment easier.

---

## ⚙️ Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **WSL, Linux, or macOS** (Redis and MailHog run on Unix-like systems)
  - Windows users: Use WSL2 or Docker
- **Git**
- **Redis** (for message broker in live mode)
- **MailHog** (for email testing)

### Quick Check
```bash
python --version    # Should be 3.8+
redis-cli --version
```

---

## 🚀 Installation & Setup

### Step 1: Clone & Enter Directory
```bash
git clone https://github.com/chay123-crypto/JobBoard-Placement-Portal.git
cd JobBoard-Placement-Portal
```

### Step 2: Create Virtual Environment
```bash
# Create
python -m venv venv

# Activate on Windows PowerShell:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python init_db.py
```
This creates `portal.db` / `placement.db` with default seed data:
- Admin user: `admin@placement.in` / `admin@123`

### Step 5: Configure Email Testing (MailHog)

**On WSL/Linux/macOS:**
```bash
# Install MailHog (if not already installed)
go install github.com/mailhog/MailHog@latest

# Or use Docker:
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

**Verify**: Visit `http://localhost:8025` in browser (should be empty initially).

### Step 6: Start Redis
```bash
# On WSL/Linux/macOS:
sudo service redis-server start

# Or with Docker:
docker run -d -p 6379:6379 redis:latest

# Test connection:
redis-cli ping  # Should print "PONG"
```

---

## 🎮 Running the Application

**This project requires 5 terminal windows.** Start them in this order:

### Terminal 1: MailHog (Email Catcher)
```bash
mailhog
```
- Listens on `localhost:1025` (SMTP) and `localhost:8025` (Web UI)
- View caught emails: `http://localhost:8025`

### Terminal 2: Redis (Message Broker)
```bash
redis-server
```

### Terminal 3: Flask App
```bash
python app.py
```
- Output: `Running on http://127.0.0.1:5000`
- Open `http://localhost:5000` in browser

### Terminal 4: Celery Worker (Task Execution)
```bash
# Windows PowerShell:
$env:PYTHONPATH="."
celery -A tasks.celery_app worker --loglevel=info -P solo

# macOS/Linux:
export PYTHONPATH=.
celery -A tasks.celery_app worker --loglevel=info
```
- Watches for background tasks and executes them
- Logs like `[tasks.get_reminders] ... received` will appear

### Terminal 5: Celery Beat (Scheduler)
```bash
celery -A celeryset beat -l DEBUG
```
- Triggers scheduled tasks (e.g., monthly reports)
- Check `celeryset.py` to see the schedule

---

## 🧪 Comprehensive Testing Suite (`tests/test_app.py`)

The project contains a complete **90-test suite** in `tests/test_app.py` covering all routes and edge cases.

### Test Coverage Highlights
* **Auth Tests**: Registration (student, company, missing role, invalid role, duplicate email, duplicate contact, invalid DOB), Login (success, wrong password, non-existent user), Check Auth, Logout.
* **Admin Tests**: Dashboard metrics (unauthenticated, non-admin, admin success), Search Student/Company (found, not found, forbidden), View Students/Companies, All Drives, Applicants per Drive, Approve/Reject Company & Drive (404, invalid action, success), User Activation/Deactivation, Placement Stats.
* **Company Tests**: Dashboard (unauthenticated, not approved, approved), Create Drive (success, missing fields, past deadline, forbidden), All Applicants, Student Info, Drive Applicants, Update Application Status (shortlisted, selected, rejected, invalid action), Close Drive, Company Info, See Drives, Export CSV, CSV Task Status, Schedule Interview.
* **Student Tests**: Dashboard, View Companies, All Drives, Applications (forbidden, success), Apply Drive (success, duplicate application, low CGPA, past deadline), Application Withdrawal (success, already selected, 404), Eligible Drives, Placement History, Student Info, Resume Retrieval, Export CSV, CSV Task Status.

### Running Tests
```bash
# Run the complete suite
python -m pytest tests/test_app.py

# Run with verbose output
python -m pytest tests/test_app.py -v

# Run a specific test class
python -m pytest tests/test_app.py::TestCompanyCreateDrive
```

*Note: The test suite dynamically configures `CACHE_TYPE = "NullCache"` and mocks Celery tasks (`export_csv.delay`, `get_reminders.delay`), enabling rapid, isolated execution in memory without requiring a live Redis server.*

---

## 🔄 CI/CD Pipeline (GitHub Actions)

This project uses **GitHub Actions** for continuous integration. On every `push` or `pull_request` to `main`, `.github/workflows/integration.yml` automatically:

1. Installs Python 3.10 and dependencies from `requirements.txt`
2. Lints code with **Ruff** (`ruff check . --fix --ignore E501,F841`)
3. Auto-formats code with **Black** (`black . --line-length 350`)
4. Runs the **Pytest** test suite (`pytest tests/` with `PYTHONPATH: .`)

Build status for each commit is visible under the repository's **Actions** tab.

---

## 🐳 Docker Setup

Run the entire application stack with Docker Compose:

```bash
# Build and start containers
docker-compose up --build

# Run in background
docker-compose up -d
```

---

## 🎮 Quick Test Flow

1. **Open** `http://localhost:5000`
2. **Register** a new student or company account
3. **Browse drives** posted by companies
4. **Apply** to a drive
5. **Check MailHog** (`http://localhost:8025`) — view confirmation emails
6. **Log in as Admin** (`admin@placement.in` / `admin@123`) to approve companies & view stats
7. **Log in as Company** to review applications and schedule interviews

---

## 🔐 Authentication & Roles

Three user roles control access:

| Role | Access | API Prefix |
|------|--------|-----------|
| **Admin** | Approve companies/drives, view stats, user management | `/admin` |
| **Student** | Browse jobs, view eligible drives, apply, track applications | `/student` |
| **Company** | Post drives, review applications, schedule interviews | `/company` |

**Authentication Flow**:
1. User registers → password hashed via `werkzeug.security`
2. Login creates Flask session (server-side)
3. Each API call includes session cookie
4. Flask `@role_required` decorator enforces access control
5. Frontend renders UI based on logged-in user role

---

## 📚 Vue.js Component Walkthrough

### `main.js` — App Entry Point
- Initializes Vue app
- Sets up client routing (simulated via URL hash)
- Manages global user state
- Fetches auth status from `/auth/check` on load

### `Login.js` — Authentication
- Email + password form
- POST to `/auth/login`
- Redirects to role dashboard on success
- Displays validation errors on failure

### `Register.js` — Registration
- Tabbed registration for Student vs Company
- Client-side validation for date format, CGPA, required fields
- POST to `/auth/register`

### `StudentDashboard.js` — Browse & Apply
- Fetches eligible and approved drives from `/student/all_drives` and `/student/drives/eligible`
- Renders tables with drive requirements
- "Apply" button → POST to `/student/drive/apply/:id`
- Application status tracking & profile resume management

### `CompanyDashboard.js` — Post & Review
- Form to post placement drive (job title, branches, CGPA cutoff, deadline, salary)
- Renders applicants with student details and CGPA
- Status management (Shortlist / Select / Reject)
- Schedule interview modal → POST to `/company/schedule_interview/:app_id`

### `AdminDashboard.js` — Analytics & Management
- Analytics cards (total students, companies, drives, placed count, avg/median salary)
- Company approval/rejection table
- Placement drive status management
- User deactivation toggle

---

## 🔄 API Endpoints Cheat Sheet

### Authentication (`/auth`)
```
POST /auth/register   # Register student or company
POST /auth/login      # Authenticate user session
GET  /auth/check      # Check authentication status
POST /auth/logout     # Terminate user session
```

### Admin API (`/admin`)
```
GET   /admin/admin_dashboard           # Overview analytics
GET   /admin/search_student?query=...  # Search student profiles
GET   /admin/search_company?query=...  # Search company profiles
GET   /admin/view_students             # List all students
GET   /admin/view_companies            # List all companies
GET   /admin/all_drives                # List all placement drives
GET   /admin/drives/:id/applicants     # View drive applicants
PATCH /admin/company/:id/status        # Approve/reject company
PATCH /admin/drive/:id/status          # Approve/reject drive
PATCH /admin/user/:id/deactivate       # Toggle user active status
GET   /admin/placement                 # Placed student history
POST  /admin/remind_interview/:id      # Queue interview reminder task
```

### Company API (`/company`)
```
GET   /company/dashboard                      # Company metrics & drives
POST  /company/create_drive                   # Post a new placement drive
GET   /company/drives/applicants              # Applicants across all drives
GET   /company/student/:id/info               # View student details
GET   /company/drives/:id/applicants          # View drive applicants
PATCH /company/application/:id/status         # Shortlist / select / reject applicant
PATCH /company/drive/:id/close                # Close placement drive
GET   /company/:id/drives                     # Company drives list
GET   /company/:id/info                       # Company profile info
POST  /company/schedule_interview/:app_id     # Schedule student interview
POST  /company/export                         # Queue CSV export task
GET   /company/exported_csv_status/:task_id   # Check CSV task status
```

### Student API (`/student`)
```
GET   /student/student_dashboard              # Student metrics
GET   /student/view_companies                 # Browse companies
GET   /student/search_company?query=...       # Search company by name
GET   /student/all_drives                     # View approved drives
GET   /student/drives/eligible                # View drives student is eligible for
GET   /student/student/:id/applications       # View student's applications
PATCH /student/student/:id/edit-profile       # Update profile & resume
POST  /student/drive/apply/:drive_id          # Apply to a placement drive
PATCH /student/applications/:id/withdraw      # Withdraw pending application
GET   /student/student/:id/placement          # Selected placement history
GET   /student/:id/resume                     # Download/view resume
GET   /student/:id/info                       # Profile info
POST  /student/export                         # Queue CSV export task
GET   /student/export_csv_status/:task_id     # Check CSV task status
```

---

## ⏰ Background Tasks (Celery)

### How It Works
1. Frontend calls API endpoint that triggers asynchronous operation
2. Flask queues a Celery task (returns immediately with a `task_id`)
3. Celery worker executes the task in background
4. Progress / results queried via `/export_csv_status/:task_id`

### Key Tasks
* **`export_csv`** (`tasks.py`): Generates CSV exports of applications for students/companies and sends them via email.
* **`get_reminders`** (`tasks.py`): Sends email reminders to students with interview date, time, and location.
* **`generate_monthly_reports`** (`tasks.py`): Periodic task (Celery Beat) generating monthly placement analytics HTML reports for approved companies.

---

## 🗄️ Database Schema

* **User**: `id`, `email`, `password_hash`, `role`, `contact_no`, `is_active`
* **StudentProfile**: `id`, `name`, `user_id` (FK), `dept`, `dob`, `year`, `cgpa`, `resume_path`
* **CompanyProfile**: `id`, `name`, `user_id` (FK), `website`, `field`, `location`, `approval_status`
* **PlacementDrive**: `drive_id`, `company_id` (FK), `jobtitle`, `job_desc`, `open_postings`, `skills`, `branches`, `cgpa_above`, `salary`, `age_cat`, `deadline`, `status`
* **Application**: `application_id`, `student_id` (FK), `drive_id` (FK), `status`, `appl_date` (Unique constraint on student_id + drive_id)
* **Interview**: `interview_id`, `company_id` (FK), `student_id` (FK), `application_id` (FK), `interview_date`, `interview_time`, `location`, `status`, `created_at`

---

## 🐛 Common Issues & Fixes

### Issue: "Redis connection refused"
```text
Error: ConnectionError: Error connecting to redis://localhost:6379/0
```
**Fix:**
```bash
redis-server  # or: sudo service redis-server start
# Or Docker: docker run -d -p 6379:6379 redis:latest
```

### Issue: "MailHog not catching emails"
**Verify:**
1. MailHog running on `localhost:8025`
2. `MAIL_SERVER = 'localhost'`, `MAIL_PORT = 1025` in `app.py`

### Issue: "Celery worker not picking up tasks"
**Debug:**
1. Ensure Redis is running: `redis-cli ping` → `PONG`
2. Check Celery worker log output
3. Restart worker with `PYTHONPATH=.` set

---

## 📚 Resources

- **Vue.js Docs**: https://vuejs.org/
- **Flask Official**: https://flask.palletsprojects.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **Celery with Flask**: https://celery.io/
- **Bootstrap 5**: https://getbootstrap.com/

---

## 📝 License

This project is open-source and available for educational purposes.

---

## ✨ Summary

**JobBoard – Placement Portal** is a full-featured placement portal demonstrating modern web development patterns:
- ✅ Learn Vue.js component architecture
- ✅ Master Flask REST API design
- ✅ Understand async task processing with Celery
- ✅ 90-test automated testing suite with Pytest
- ✅ CI/CD pipeline automation with GitHub Actions

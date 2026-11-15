# JobBoard – Full-Stack Placement Portal

A full-stack placement portal built with **Vue.js + Flask**. It includes role-based dashboards, placement-drive management, student applications, resume uploads, resume-to-drive similarity scores, background tasks, and automated tests.

**Perfect for:** Learning Vue.js through a complete project | Portfolio demonstration | Understanding full-stack architecture | CI/CD implementation basics | Comprehensive Flask testing

Live demo: https://jobboard-placement-portal.onrender.com/

---

## 🎯 Learning Objectives

By working through this project, I mastered:

- **Vue.js Fundamentals**: Component-driven UI, lifecycle hooks, conditional rendering, and list management
- **SPA Architecture**: Client-side routing, state management across components, API communication patterns
- **Backend Integration**: Flask JSON APIs, session authentication, and role-based access control (RBAC)
- **Async Operations**: Promises, async/await, handling API responses and errors
- **Application Services**: In-process caching (`Flask-Caching`), background task queues (`Celery`), and email notifications (`Flask-Mail`)
- **Database Design**: SQLAlchemy ORM, model relationships, and indexed foreign keys
- **Resume Matching**: PDF text extraction and FastEmbed sentence embeddings using `all-MiniLM-L6-v2`
- **Testing**: 104 unit and integration tests using `pytest`, in-memory SQLite, and mocked background tasks
- **CI/CD Pipeline**: GitHub Actions workflows for automated linting (`Ruff`), auto-formatting (`Black`), and running test suites
- **Full-Stack Debugging**: Browser DevTools + Flask logging to trace issues end-to-end

---

## 📋 Features

| Feature | Technology | Learning Value |
|---------|-----------|-----------------|
| **Multi-role Dashboard** | Vue.js Components | Conditional UI rendering, component reusability |
| **Role-Based Access** | Flask decorators + Auth | Session management, authorization patterns |
| **Placement Drives** | Vue forms + REST API | Drive creation, approval, eligibility, and applications |
| **Application Tracking** | Dynamic tables, Vue state | List rendering, filtering, real-time updates |
| **Resume Matching** | pypdf + FastEmbed | PDF text extraction and semantic similarity estimates |
| **Email Notifications** | Celery + Flask-Mail | Async task processing, scheduled jobs |
| **CSV Export** | Celery background tasks | Long-running operations, progress tracking |
| **Caching Layer** | Flask-Caching | Performance optimization, cache invalidation |
| **Automated Testing** | Pytest | 104 tests covering API routes and resume matching |
| **CI/CD Pipeline** | GitHub Actions | Automated linting, code formatting, and test execution on push/PR |

---

## 🛠 Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Vue.js, JavaScript (ES6+), HTML5, Bootstrap 5 |
| **Backend** | Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail, Flask-Caching |
| **Database** | SQLite |
| **Resume parsing and matching** | pypdf, FastEmbed, all-MiniLM-L6-v2 |
| **Task Queue** | Celery + Redis message broker |
| **Scheduling** | Celery Beat (cron-like scheduler) |
| **Email Testing** | MailHog (local SMTP catcher) |
| **Caching** | Flask-Caching (SimpleCache by default; Redis can be configured) |
| **Testing** | Pytest, Pytest-Flask, Pytest-Cov |
| **Code Quality** | Ruff (linter), Black (formatter) |
| **CI/CD** | GitHub Actions workflows |
| **Containerization** | Docker, Docker Compose |

---

## Project Structure

```
JobBoard-Placement-Portal/
├── app.py
├── backend/
│   ├── cache.py
│   ├── celeryset.py
│   ├── decorator.py
│   ├── init_db.py
│   ├── matching.py
│   ├── resume_parser.py
│   ├── tasks.py
│   ├── models/models.py
│   └── routes/
│       ├── auth.py
│       ├── admin.py
│       ├── student.py
│       └── company.py
├── frontend/
│   ├── templates/index.html
│   └── static/
│       ├── css/app.css
│       └── js/
│           ├── main.js
│           └── components/
├── tests/
│   ├── test_app.py
│   ├── test_cache.py
│   └── test_matching.py
├── Dockerfile
├── requirements.txt
├── .github/
│   └── workflows/
│       ├── integration.yml
│       └── main.yml
└── README.md
```

---

## ⚙️ Prerequisites

- **Python 3.10+**
- **Git**
- **Redis** (optional; required for Celery background tasks)
- **Docker** (optional; for containerized setup)

### Quick Check
```bash
python --version    # Python 3.10 or later
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
python -m backend.init_db
```
The app initializes `portal.db` and creates a default admin account:
- Admin user: `admin@placement.in` / `admin@123`

To optionally add demo student and company accounts with an approved sample drive, run:
```bash
python -m backend.init_db --seed-demo
```
Demo sign-in: `demo.student@placement.in` or `demo.company@placement.in`; both use `DemoAccess123!`. The login page includes one-click demo access. The seed is safe to rerun. The Dockerfile runs this seed command when its container starts, so Docker/Render deployments create the demo accounts automatically. These shared public credentials are public; do not use them with private or production data.

### Optional: Configure Email Testing (MailHog)

**On WSL/Linux/macOS:**
```bash
# Install MailHog (if not already installed)
go install github.com/mailhog/MailHog@latest

# Or use Docker:
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

**Verify**: Visit `http://localhost:8025` in browser (should be empty initially).

### Optional: Start Redis for Background Jobs
```bash
# On WSL/Linux/macOS:
sudo service redis-server start

# Or with Docker:
docker run -d -p 6379:6379 redis:latest

# Test connection:
redis-cli ping  # Should print "PONG"
```

---

## Running the Application

Start the Flask app:
```bash
python app.py
```
Then open `http://localhost:5000`.

The web app uses in-process caching by default and does not require Redis just to start. Redis is required for Celery background jobs. Email delivery requires an SMTP server; MailHog can be used for local testing.

---

## Testing

The suite currently contains **104 tests** across the application, caching, and resume matching.

### Test Coverage Highlights
* **Auth Tests**: Registration (student, company, missing role, invalid role, duplicate email, duplicate contact, invalid DOB), Login (success, wrong password, non-existent user), Check Auth, Logout.
* **Admin Tests**: Dashboard metrics (unauthenticated, non-admin, admin success), Search Student/Company (found, not found, forbidden), View Students/Companies, All Drives, Applicants per Drive, Approve/Reject Company & Drive (404, invalid action, success), User Activation/Deactivation, Placement Stats.
* **Company Tests**: Dashboard (unauthenticated, not approved, approved), Create Drive (success, missing fields, past deadline, forbidden), All Applicants, Student Info, Drive Applicants, Update Application Status (shortlisted, selected, rejected, invalid action), Close Drive, Company Info, See Drives, Export CSV, CSV Task Status, Schedule Interview.
* **Student Tests**: Dashboard, View Companies, All Drives, Applications (forbidden, success), Apply Drive (success, duplicate application, low CGPA, past deadline), Application Withdrawal (success, already selected, 404), Eligible Drives, Placement History, Student Info, Resume Retrieval, Export CSV, CSV Task Status.

### Running Tests
```bash
# Run the complete suite
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run a specific test class
python -m pytest tests/test_app.py::TestCompanyCreateDrive
```

Tests use in-memory SQLite and do not require a live Redis server.

---

## 🔄 CI/CD Pipeline (GitHub Actions)

This project uses **GitHub Actions** for continuous integration. On every `push` or `pull_request` to `main`, `.github/workflows/integration.yml` automatically:

1. Installs Python 3.10 and dependencies from `requirements.txt`
2. Lints code with **Ruff** (`ruff check . --fix --ignore E501,F841`)
3. Auto-formats code with **Black** (`black . --line-length 350`)
4. Runs the **Pytest** test suite (`pytest tests/` with `PYTHONPATH: .`)

Build status for each commit is visible under the repository's **Actions** tab.

---

## Docker and Render Deployment

The repository includes a Dockerfile. Its startup command seeds demo accounts and then starts Gunicorn. On Render, deploy the repository as a Docker web service and leave the **Docker Command** override empty so Render uses the Dockerfile command.

The app currently stores data in SQLite and uploaded resumes on the service filesystem. Render's filesystem is not persistent by default; use a persistent disk or an external database/file store if data must survive service replacement or redeployment. The public demo accounts are shared and must not contain private data.

---

## 🎮 Quick Test Flow

1. **Open** `http://localhost:5000`
2. **Register** a new student or company account
3. **Browse drives** posted by companies
4. **Apply** to a drive
5. **Upload a PDF resume** to see extracted fields and resume-to-drive similarity estimates
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

### `StudentDashboard.js` — Browse, Match & Apply
- Fetches eligible and approved drives from `/student/all_drives` and `/student/drives/eligible`
- Renders tables with drive requirements
- Shows PDF resume-to-drive similarity estimates: Great (>75%), Good (50-75%), and Weak (<50%)
- "Apply" button → POST to `/student/drive/apply/:id`
- Application status tracking and profile resume management

Match scores are calculated from extracted PDF resume text and drive details. They are similarity estimates, not probabilities of getting hired or replacements for the portal's eligibility rules. DOC/DOCX uploads are accepted, but resume text extraction and match scoring currently require a readable PDF. Scanned PDFs without selectable text are not parsed.

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
GET   /student/drives/eligible                # Eligible drives with resume match scores
GET   /student/student/:id/applications       # Applications with resume match scores
PATCH /student/student/:id/edit-profile       # Update profile and upload resume
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
* **`export_csv`** (`backend/tasks.py`): Generates CSV exports of applications for students/companies and sends them via email.
* **`get_reminders`** (`backend/tasks.py`): Sends email reminders to students with interview date, time, and location.
* **`generate_monthly_reports`** (`backend/tasks.py`): Periodic task (Celery Beat) generating monthly placement analytics HTML reports for approved companies.

---

## 🗄️ Database Schema

* **User**: `id`, `email`, `password_hash`, `role`, `contact_no`, `is_active`
* **StudentProfile**: `id`, `name`, `user_id` (FK), `dept`, `dob`, `year`, `cgpa`, `resume_path`
* **CompanyProfile**: `id`, `name`, `user_id` (FK), `website`, `field`, `location`, `approval_status`
* **PlacementDrive**: `drive_id`, `company_id` (FK), `jobtitle`, `job_desc`, `open_postings`, `skills`, `branches`, `cgpa_above`, `salary`, `age_cat`, `deadline`, `status`
* **Application**: `application_id`, `student_id` (FK), `drive_id` (FK), `status`, `appl_date` (Unique constraint on student_id + drive_id)
* **Interview**: `interview_id`, `company_id` (FK), `student_id` (FK), `application_id` (FK), `interview_date`, `interview_time`, `location`, `status`, `created_at`

---

## Troubleshooting

### Redis connection errors
Redis is only needed for Celery background tasks. Flask-Caching uses `SimpleCache` by default. To use Redis for caching, configure `CACHE_TYPE=RedisCache` and set `CACHE_REDIS_URL` or `REDIS_URL`.
```text
Error: ConnectionError: Error connecting to redis://localhost:6379/0
```

### Resume upload or match score fails
Check the Flask/Render service logs for the server traceback. PDF uploads are limited to 5 MB and text extraction reads up to five pages. Scanned/image-only PDFs need OCR, which is not currently included. FastEmbed downloads the MiniLM model the first time a match score is requested.

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

**JobBoard – Placement Portal** is a full-stack placement portal featuring:
- ✅ Learn Vue.js component architecture
- ✅ Master Flask REST API design
- ✅ Understand async task processing with Celery
- ✅ Resume-to-drive semantic similarity scoring
- ✅ 104-test automated testing suite with Pytest
- ✅ CI/CD pipeline automation with GitHub Actions

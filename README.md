# JobBoard – Full-Stack Placement Portal

A production-ready SPA built with **Vue.js + Flask** demonstrating real-world full-stack development patterns. This project showcases role-based dashboards, RESTful API design, background task processing, and component-driven architecture.

**Perfect for:** Learning Vue.js through a complete project | Portfolio demonstration | Understanding full-stack architecture

---

## 🎯 Learning Objectives

By working through this project, I mastered :

- **Vue.js Fundamentals**: Component composition, props/emit patterns, lifecycle hooks, conditional rendering, list management
- **SPA Architecture**: Client-side routing, state management across components, API communication patterns
- **Backend Integration**: RESTful API design, CORS, authentication, role-based access control (RBAC)
- **Async Operations**: Promises, async/await, handling API responses and errors
- **Production Patterns**: Caching strategies (Flask-Caching), background task queues (Celery), email notifications
- **Database Design**: SQLAlchemy ORM, model relationships, migrations
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

---

## 🛠 Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Vue.js, JavaScript (ES6+), HTML5, Bootstrap 5 |
| **Backend** | Flask, Flask-SQLAlchemy, Flask-Login |
| **Database** | SQLite (easily swapped to PostgreSQL) |
| **Task Queue** | Celery + Redis message broker |
| **Scheduling** | Celery Beat (cron-like scheduler) |
| **Email Testing** | MailHog (local SMTP catcher) |
| **Caching** | Flask-Caching (Redis/memory backends) |

---

## 📁 Project Structure

```
PlaceMe/
├── app.py                      # Flask app factory & configuration
├── models/
│   └── models.py               # SQLAlchemy ORM models (User, Company, Job, Application)
├── routes/
│   ├── auth.py                 # Login/Register endpoints
│   ├── admin.py                # Admin dashboard API (stats, company/posting management)
│   ├── student.py              # Student API (browse jobs, apply, track applications)
│   └── company.py              # Company API (post jobs, review applications)
├── tasks.py                    # Celery tasks (email reminders, CSV export, reports)
├── celeryset.py                # Celery configuration & beat schedule
├── cache.py                    # Flask-Caching setup
├── decorator.py                # Custom decorators (@login_required, @role_required)
├── init_db.py                  # Database initialization & seed data
├── templates/
│   └── index.html              # Single HTML shell (Vue mounts here)
├── static/js/
│   ├── main.js                 # Vue app entry point, routing, global state
│   └── components/
│       ├── Login.js            # Authentication component
│       ├── Register.js         # Registration form
│       ├── AdminDashboard.js   # Admin overview (stats, user mgmt)
│       ├── StudentDashboard.js # Student job browse & applications
│       └── CompanyDashboard.js # Company job posting & applicant review
├── app.yaml                    # App Engine deployment config (optional)
└── README.md
```

**Key Insight**: The backend serves as a pure REST API; the frontend is a single-page app that consumes it. This separation makes testing, scaling, and deployment easier.

---

## ⚙️ Prerequisites

- **Python 3.8+**
- **WSL, Linux, or macOS** (Redis and MailHog run on Unix-like systems)
  - Windows users: Use WSL2 or Docker
- **Git**
- **Redis** (for message broker)
- **MailHog** (for email testing)

### Quick Check
```bash
python --version    # Should be 3.8+
redis-cli --version
# mailhog should be in PATH after install
```

---

## 🚀 Installation & Setup

### Step 1: Clone & Enter Directory
```bash
git clone <repo-url>
cd PlaceMe
```

### Step 2: Create Virtual Environment
```bash
# Create
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Or manually:**
```bash
pip install flask==2.3.0 flask-sqlalchemy==3.0.0 flask-login==0.6.2 \
            flask-mail==0.9.1 flask-caching==2.0.2 celery==5.3.0 \
            redis==4.5.0 numpy==1.24.0 werkzeug==2.3.0
```

### Step 4: Initialize Database
```bash
python init_db.py
```
This creates `placement.db` with seed data:
- Admin user: `admin` / `admin123`
- 2 sample companies
- 5 sample students

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
# If installed via apt/brew:
redis-server

# Or Docker (already running):
# (skip this step)
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
- You'll see logs like `[tasks.send_reminder] ... received`

### Terminal 5: Celery Beat (Scheduler)
```bash
celery -A celeryset beat -l DEBUG
```
- Triggers scheduled tasks (e.g., daily email reminders at 9 AM)
- Check `celeryset.py` to see the schedule

---

## 🧪 Quick Test Flow

1. **Open** `http://localhost:5000`
2. **Register** a new student account (or use seed: `student1` / `password123`)
3. **Browse jobs** posted by companies
4. **Apply** to a job
5. **Check MailHog** (`http://localhost:8025`) — you should see confirmation emails
6. **Log in as Admin** and view application stats
7. **Log in as Company** and review applications

---

## 🔐 Authentication & Roles

Three user roles control access:

| Role | Access | API Prefix |
|------|--------|-----------|
| **Admin** | Approve companies, view all stats, manage users | `/api/admin` |
| **Student** | Browse jobs, apply, track applications | `/api/student` |
| **Company** | Post jobs, review applications, schedule interviews | `/api/company` |

**Authentication Flow**:
1. User registers → password hashed via `werkzeug.security`
2. Login creates Flask session (server-side)
3. Each API call includes session cookie
4. Flask decorators enforce role-based access
5. Frontend hides UI elements based on logged-in user role

---

## 📚 Vue.js Component Walkthrough

### `main.js` — App Entry Point
- Initializes Vue app
- Sets up basic routing (simulated via URL hash)
- Manages global user state
- Fetches user role from `/api/auth/user` on load

**Key snippet:**
```javascript
// Fetch current user on app load
fetch('/api/auth/user')
  .then(r => r.json())
  .then(data => app.currentUser = data.user)
  .catch(() => console.log('Not logged in'));
```

### `Login.js` — Authentication
- Form with email + password
- POST to `/api/auth/login`
- Redirects to dashboard on success
- Displays errors if login fails

**Learning points:**
- Form `@submit` event handling
- Async/await with `fetch()`
- Error handling with `.catch()`
- Redirecting user via `window.location.hash`

### `StudentDashboard.js` — Browse & Apply
- Fetches job list from `/api/student/jobs`
- Renders table with job details
- Click "Apply" → POST to `/api/student/apply`
- Shows confirmation or error

**Learning points:**
- `v-for` for list rendering
- Dynamic binding with `:key`
- Conditional rendering with `v-if`
- Calling API methods from Vue methods

### `CompanyDashboard.js` — Post & Review
- Form to post a new job (title, description, deadline)
- Renders applications received with candidate details
- "Accept" / "Reject" buttons update status
- Triggers Celery email task on decision

**Learning points:**
- Two-way binding with `v-model`
- Handling form submission
- Managing component state (`data()`)
- Iterating nested data (`v-for` on arrays of objects)

### `AdminDashboard.js` — Overview & Analytics
- Dashboard showing total users, jobs, applications
- Table of all companies (approve/reject)
- Export statistics as CSV (triggers Celery task)

**Learning points:**
- Reading computed data from API
- Triggering background tasks
- Displaying real-time stats

---

## 🔄 API Endpoints Cheat Sheet

### Authentication
```
POST   /api/auth/register      (email, password, role)
POST   /api/auth/login         (email, password)
POST   /api/auth/logout
GET    /api/auth/user          (returns current user)
```

### Student API
```
GET    /api/student/jobs       (list all job postings)
POST   /api/student/apply      (job_id)
GET    /api/student/applications  (user's applications)
```

### Company API
```
POST   /api/company/job        (title, description, deadline, salary, required_skills)
GET    /api/company/postings   (user's job postings)
GET    /api/company/applications (applications to user's jobs)
POST   /api/company/application/:app_id/accept
POST   /api/company/application/:app_id/reject
```

### Admin API
```
GET    /api/admin/stats        (total users, jobs, applications)
GET    /api/admin/companies    (all companies, pending approval)
POST   /api/admin/company/:id/approve
POST   /api/admin/company/:id/reject
GET    /api/admin/export-csv   (triggers Celery task, returns job_id)
```

---

## ⏰ Background Tasks (Celery)

### How It Works
1. Frontend calls API endpoint that needs long-running task
2. Flask queues a Celery task (returns immediately to user)
3. Celery worker picks up task and executes asynchronously
4. Results stored in Redis or database
5. Frontend can poll for completion status

### Key Tasks

**send_interview_reminder** (`tasks.py:send_interview_reminder`)
- Scheduled daily at 9 AM
- Sends email to students with upcoming interviews
- Example: "Hi John, your interview at TechCorp is on Sept 15 at 2 PM"

**export_placements_csv** (`tasks.py:export_placements_csv`)
- Triggered when admin clicks "Export Stats"
- Generates CSV of all placements
- Saves to `/reports/` folder
- Email sent to admin with attachment

**schedule_interview** (`tasks.py:schedule_interview`)
- Triggered when company schedules an interview
- Sends confirmation to student

### Monitor Tasks
```bash
# In Terminal 4, watch worker logs:
# celery -A tasks.celery_app worker --loglevel=info -P solo

# You'll see:
# [tasks.send_interview_reminder] ... received
# [tasks.send_interview_reminder] ... started
# [tasks.send_interview_reminder] ... succeeded
```

---

## 🗄️ Database Schema

### Users Table
```
id (PK)
email (UNIQUE)
password_hash
role (admin | student | company)
name
created_at
```

### Companies Table
```
id (PK)
user_id (FK → Users)
name
description
website
status (approved | pending | rejected)
created_at
```

### Jobs Table
```
id (PK)
company_id (FK → Companies)
title
description
required_skills
salary
deadline
created_at
```

### Applications Table
```
id (PK)
student_id (FK → Users)
job_id (FK → Jobs)
status (applied | accepted | rejected | interview_scheduled)
applied_at
interview_date (nullable)
interview_time (nullable)
```

**Why this design?**
- Separation of concerns: One user can be admin OR student OR company
- Job postings linked to company via FK
- Applications track both student and job
- Status field allows workflow progression (applied → interview → accepted)

---

## 🐛 Common Issues & Fixes

### Issue: "Redis connection refused"
```
Error: ConnectionError: Error connecting to redis://localhost:6379/0
```
**Fix:**
```bash
# Start Redis:
redis-server  # or: sudo service redis-server start

# Or use Docker:
docker run -d -p 6379:6379 redis:latest
```

### Issue: "MailHog not catching emails"
**Verify:**
1. MailHog running: `http://localhost:8025` loads
2. In Flask app, `MAIL_SERVER` is set to `localhost`, `MAIL_PORT=1025`
3. Check `app.py` for Flask-Mail config:
   ```python
   app.config['MAIL_SERVER'] = 'localhost'
   app.config['MAIL_PORT'] = 1025
   ```

### Issue: "Celery worker not picking up tasks"
**Debug:**
1. Ensure Redis is running: `redis-cli ping` → `PONG`
2. Check Celery worker output for errors
3. Verify `CELERY_BROKER_URL` in `app.py`: `redis://localhost:6379/0`
4. Restart worker: `Ctrl+C` and re-run celery command

### Issue: "CORS errors in browser console"
**Already handled** in `app.py`:
```python
from flask_cors import CORS
CORS(app)
```
If persists, ensure Flask is running on the same machine as frontend.

### Issue: "Login works but dashboard is blank"
**Likely cause:** API call failing silently.
**Debug:**
1. Open browser DevTools → Console tab
2. Look for fetch errors
3. Check Network tab → see if `/api/student/jobs` returns data
4. Verify Flask routes in `routes/student.py` are correct

---

## 📈 Learning Path

### Week 1: Vue Basics
- [ ] Modify `Login.js` to add "Forgot Password?" link (UI only)
- [ ] Add client-side form validation (email format, password strength)
- [ ] Style components with custom CSS classes

### Week 2: Backend Integration
- [ ] Add a new field to Job model (e.g., `company_logo_url`)
- [ ] Update API endpoint to return it
- [ ] Display company logo in StudentDashboard.js

### Week 3: Advanced Features
- [ ] Implement search/filter for jobs (e.g., by salary range)
- [ ] Add pagination to job list (show 10 jobs per page)
- [ ] Create a "Saved Jobs" feature (requires new database table)

### Week 4: Performance & Scaling
- [ ] Implement caching: cache job list for 1 hour
- [ ] Add loading spinners to API calls
- [ ] Measure query performance, optimize slow endpoints

### Week 5: Deployment
- [ ] Deploy backend to Heroku or AWS
- [ ] Deploy frontend to Netlify or Vercel
- [ ] Set up production database (PostgreSQL instead of SQLite)

---

## 🚢 Deployment

### Prepare for Production

1. **Environment variables** (create `.env` file):
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-secure-key>
   SQLALCHEMY_DATABASE_URI=postgresql://<user>:<pass>@<host>/<db>
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   CELERY_BROKER_URL=redis://<redis-host>:6379/0
   ```

2. **Use production server** (not Flask dev server):
   ```bash
   pip install gunicorn
   gunicorn -w 4 app:app  # 4 worker processes
   ```

3. **Heroku Deployment**:
   ```bash
   heroku create my-placement-portal
   git push heroku main
   heroku ps:scale worker=1  # Scale Celery worker
   ```

4. **Database migration** (from SQLite to PostgreSQL):
   ```bash
   # Update SQLALCHEMY_DATABASE_URI to PostgreSQL
   # Dump SQLite: python -c "import init_db; init_db.init_db()"
   # Restore to PostgreSQL: Use SQLAlchemy migration tools
   ```

---

## 📊 Project Metrics

- **Frontend**: 5 Vue components, ~1500 lines of JavaScript
- **Backend**: 4 route modules, ~500 lines of Flask code
- **Database**: 4 tables with relationships
- **Tasks**: 3 Celery tasks (email, CSV export, interview scheduling)
- **Estimated Learning Time**: 20-30 hours (beginner) | 8-12 hours (intermediate)

---

## 🤝 Contributing & Extending

### Ideas for Enhancement
1. **Add interview scheduling UI** (currently backend-only)
2. **Implement job search filters** (location, salary, skills)
3. **Add user profile pages** (view/edit resume)
4. **Notifications dashboard** (in-app notifications, not just email)
5. **Analytics for companies** (view application trends over time)
6. **Mobile-responsive design** (currently desktop-focused)

### Testing Setup (Bonus)
```bash
pip install pytest pytest-flask

# Run tests:
pytest tests/
```

---

## 📚 Resources

- **Vue.js Docs**: https://vuejs.org/
- **Flask Official**: https://flask.palletsprojects.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **Celery with Flask**: https://celery.io/
- **Bootstrap 5**: https://getbootstrap.com/

---

## 📝 License

This project is open source and available for educational purposes.

---

## ✨ Summary

**PlaceMe** is a full-featured placement portal demonstrating modern web development patterns. Use it to:
- ✅ Learn Vue.js component architecture
- ✅ Master Flask API design
- ✅ Understand async task processing with Celery
- ✅ Build a complete, deployable SPA
- ✅ Add to your portfolio with confidence

**Next steps**: Clone the repo, follow the setup, run the app, and start tweaking. Happy coding! 🚀

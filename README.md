# 🎓 University Timetable Management & Academic Scheduling Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?logo=python)](https://python.org)
[![OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT-4285F4.svg?logo=google)](https://developers.google.com/optimization)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker)](https://www.docker.com)

A complete, production-grade university timetable management and automated academic scheduling platform. Engineered with **Google OR-Tools CP-SAT** constraint satisfaction solver, **FastAPI**, **SQLAlchemy 2**, **PostgreSQL**, **WebSockets**, and a modern **Tailwind CSS + Vanilla JavaScript** SaaS frontend.

---

## 🌟 Key Features

### 1. ⚡ Google OR-Tools CP-SAT Timetable Generation Engine
- **Constraint Satisfaction & Optimization (CP-SAT)**:
  - **Hard Constraints**: Strict zero tolerance for teacher double-booking, room double-booking, section class collisions, room capacity violations, lab requirement mismatches, and faculty/room unavailability windows.
  - **Soft Constraints (Optimization Objective)**: Penalizes daily subject clustering, balances faculty daily teaching hours, avoids $>3$ consecutive classes without breaks, and minimizes isolated student idle periods.
  - **Real Mathematical Output**: Produces exact solver metrics: 0 hard conflicts, soft penalty scores, true runtime duration (seconds), and objective values.

### 2. 🛡️ Role-Based Access Control (RBAC) & Security
- **JWT Authentication**: Secure Access and Refresh token lifecycle with `bcrypt` password hashing.
- **Hierarchical Portals**:
  - **Super Admin & University Admin**: Institution-wide management, AI generator, audit logs, facility inventory, analytics.
  - **HOD Portal**: Departmental schedules, teacher workload quotas, absence review, and substitute teacher assignment.
  - **Teacher Portal**: Personal weekly teaching matrix, today's schedule, availability preferences, absence requests.
  - **Student Portal**: Section timetable, today's class schedule with real-time "Current Class" & "Up Next" indicators, campus notices.

### 3. 🔍 Real-Time Conflict Detection & Manual Rescheduler
- Instant hard-constraint audit before moving or placing any class.
- Clear error diagnostics (e.g., *"Cannot move class. Dr. Sharma is already assigned to B.Tech CSE Section B during this period"*).
- Timetable publishing lifecycle: `DRAFT` $\rightarrow$ `PUBLISHED` with automated version increments ($v1, v2, \dots$) and rollback capability.

### 4. 🔄 Substitute Teacher Workflow
- Automated absence notification by faculty.
- Algorithmic candidate recommendation ranking substitute teachers by **Department peer status**, **Subject qualification**, **Slot availability**, and **Lowest active weekly workload**.
- Instant push notifications to substitute teacher, class coordinator, and enrolled students upon approval.

### 5. 🔔 WebSockets & Real-Time Communications
- Bi-directional WebSocket connection (`/api/notifications/ws`).
- Instant bell icon badge updates and animated toast notifications when timetables are published or substitutions are assigned.
- System-wide and department-targeted announcements with priority markers (`URGENT`, `HIGH`, `MEDIUM`).

### 6. 📊 Analytics & Reporting Engine
- Interactive **Chart.js** dashboards:
  - Weekly class distribution by day.
  - Faculty workload vs. maximum target limit.
  - Space and laboratory utilization rates ($0-100\%$).
  - Departmental course volume breakdowns.
- **Exporting Engine**:
  - Export timetable to styled **Excel (.xlsx)** via `openpyxl`.
  - Export timetable to print-ready **PDF (.pdf)** via `ReportLab`.
  - Filter exports by department, teacher, student section, or room.

---

## 🏗️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, Tailwind CSS, Vanilla JavaScript (ES Modules), Chart.js, Font Awesome 6 |
| **Backend API** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2, python-multipart |
| **Database & ORM** | PostgreSQL 16 (production), SQLite (zero-config local dev), SQLAlchemy 2, Alembic |
| **Scheduling Engine** | Google OR-Tools CP-SAT (Constraint Programming - Satisfiability) |
| **Security** | JWT (`python-jose`), `bcrypt` hashing, CORS, RBAC middleware |
| **Real-time** | WebSockets (`websockets`) |
| **Document Export**| `openpyxl` (Excel spreadsheets), `ReportLab` (PDF documents) |
| **DevOps & Containers** | Docker, Docker Compose, Nginx, Redis 7 |

---

## 🗄️ Database Architecture (37 Tables)

```mermaid
erDiagram
    UNIVERSITIES ||--o{ CAMPUSES : contains
    CAMPUSES ||--o{ BUILDINGS : contains
    CAMPUSES ||--o{ DEPARTMENTS : contains
    BUILDINGS ||--o{ ROOMS : has
    ROOMS ||--o| LABS : specializes
    DEPARTMENTS ||--o{ PROGRAMS : offers
    PROGRAMS ||--o{ SECTIONS : divides
    ACADEMIC_YEARS ||--o{ SEMESTERS : spans
    ACADEMIC_YEARS ||--o{ PERIODS : configures
    SEMESTERS ||--o{ SECTIONS : enrolls
    DEPARTMENTS ||--o{ TEACHERS : employs
    SECTIONS ||--o{ STUDENTS : contains
    DEPARTMENTS ||--o{ SUBJECTS : designs
    TEACHERS ||--o{ TEACHER_SUBJECTS : teaches
    SUBJECTS ||--o{ TEACHER_SUBJECTS : taught_by
    TIMETABLE ||--o{ TIMETABLE_ENTRIES : contains
    TIMETABLE_ENTRIES }o--|| TEACHERS : instructs
    TIMETABLE_ENTRIES }o--|| ROOMS : located_at
    TIMETABLE_ENTRIES }o--|| SECTIONS : attends
    TIMETABLE_ENTRIES }o--|| PERIODS : scheduled_in
    TIMETABLE_ENTRIES }o--|| SUBJECTS : studies
```

---

## 🚀 Quick Start & Installation

### Option 1: Instant Local Run (Zero-Configuration)

Requirements: Python 3.12+

1. **Clone repository**:
   ```bash
   git clone <repo-url>
   cd timetable
   ```

2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Populate database with demo data**:
   ```bash
   python seed.py
   ```
   *(This generates 3 departments, 50 teachers, 500 students, 30 subjects, 20 rooms, 5 labs, 10 sections, and a conflict-free timetable generated by CP-SAT!)*

4. **Launch Application**:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```


### Option 2: Docker Compose (Production Environment)

To run the entire multi-service stack with PostgreSQL 16, Redis 7, FastAPI, and Nginx:

```bash
docker compose up --build
```

- Access frontend at: `http://localhost`
- Access backend API directly at: `http://localhost:8000`

---

## 🔑 Demo Login Credentials

The `seed.py` script creates ready-to-test demo accounts across all user roles:

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@university.com` | `AdminPassword123!` | Complete institution authority & system settings |
| **Head of Department (HOD)** | `hod@university.com` | `Password123!` | CSE Department schedules, curriculum & substitutions |
| **Faculty Member** | `teacher@university.com` | `Password123!` | Personal schedule, availability matrix & absences |
| **Student** | `student@university.com` | `Password123!` | Section class schedule, current class & notices |

*(The login screen also features 1-click preset login buttons for instant role switching!)*

---

## 🧪 Automated Testing

The platform includes an automated `pytest` test suite verifying authentication, RBAC, hard conflict detection, and the Google OR-Tools CP-SAT engine:

```bash
python -m pytest -v
```

Output:
```
tests/test_api.py::test_list_departments PASSED
tests/test_api.py::test_list_teachers PASSED
tests/test_api.py::test_list_rooms PASSED
tests/test_api.py::test_analytics_endpoints PASSED
tests/test_auth.py::test_health_endpoint PASSED
tests/test_auth.py::test_admin_login PASSED
tests/test_auth.py::test_invalid_login PASSED
tests/test_auth.py::test_teacher_and_student_demo_logins PASSED
tests/test_conflict_detector.py::test_capacity_conflict_detection PASSED
tests/test_conflict_detector.py::test_break_period_conflict_detection PASSED
tests/test_conflict_detector.py::test_lab_room_requirement_conflict PASSED
tests/test_timetable_generator.py::test_cp_sat_solver_execution PASSED
======================= 12 passed in 7.27s =======================
```

---

## ⚙️ Environment Variables

Create `.env` based on `.env.example`:

```env
PROJECT_NAME="University Timetable Management Platform"
API_V1_STR="/api"
SECRET_KEY="super-secret-production-key-change-in-production-min-32-chars-long"
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM="HS256"

# Database Configuration (PostgreSQL default, falls back to SQLite)
DATABASE_URL="postgresql://postgres:postgrespassword@localhost:5432/university_timetable"

# Redis Cache / WebSocket PubSub
REDIS_URL="redis://localhost:6379/0"

# CORS Origins
BACKEND_CORS_ORIGINS=["*"]

# Solver Parameters
SOLVER_TIME_LIMIT_SECONDS=30
SOLVER_NUM_WORKERS=8
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Authenticate user & issue JWT tokens |
| `POST` | `/api/auth/register` | Register new student or teacher |
| `GET` | `/api/departments` | List academic departments with HODs |
| `GET` | `/api/teachers` | List faculty with workload metrics |
| `GET` | `/api/students` | List student cohorts with section info |
| `GET` | `/api/subjects` | List courses, credits, and lab rules |
| `GET` | `/api/rooms` | List classrooms and specialized laboratories |
| `POST`| `/api/timetable/generate` | Trigger OR-Tools CP-SAT generator |
| `GET` | `/api/timetable/jobs/{id}`| Poll real-time solver progress |
| `POST`| `/api/timetable/{id}/publish`| Publish schedule & broadcast notifications |
| `PUT` | `/api/timetable/entries/{id}/move`| Manual class reschedule with conflict audit |
| `GET` | `/api/substitutions/available-candidates`| Algorithmic substitute teacher finder |
| `GET` | `/api/analytics/charts`| Chart.js data bundle (workload, rooms, days) |
| `GET` | `/api/export/timetable/{id}/excel` | Download openpyxl Excel timetable |
| `GET` | `/api/export/timetable/{id}/pdf` | Download ReportLab PDF timetable |
| `GET` | `/health` | System and database health status |

---

## 📄 License
This project is licensed under the MIT License.

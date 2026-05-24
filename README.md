# UniManager v2 — Enterprise University Management System

[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-green)]()

> **Production-grade** university management platform with role-based access control, TOTP-secured attendance tracking, collision-free scheduling, and audit logging. Built with Clean Architecture, Contract-First API validation (Zod), and Graceful Degradation (Error Boundaries).

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Key Features](#key-features)
- [Security](#security)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [Installation](#installation)
- [Deployment](#deployment)
- [API Overview](#api-overview)
- [Screenshots](#screenshots)
- [Development](#development)
- [License](#license)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                     │
│  React 19 · TypeScript 6 · TanStack Query · Shadcn/UI   │
│  Zod Validation · Error Boundaries · RBAC Sidebar       │
├─────────────────────────────────────────────────────────┤
│                    REST API (Django)                     │
│  DRF 3.17 · SimpleJWT · django-simple-history           │
│  4 apps: users · academic · timetable · dashboard       │
├─────────────────────────────────────────────────────────┤
│                    Data Layer                            │
│  PostgreSQL (prod) / SQLite (dev) · Redis Cache         │
└─────────────────────────────────────────────────────────┘
```

### Backend Layer Flow (per module)

```
models.py  →  services.py  →  serializers.py  →  views.py  →  urls.py
(schema)      (business       (validation)      (routing)     (endpoints)
               logic +
               transaction.
               atomic())
```

> **Key rule:** Business logic lives exclusively in `services.py`. Views never contain logic.

---

## Tech Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2 | UI framework |
| TypeScript | 6.0 | Type safety |
| Vite | 8.0 | Build tool |
| Tailwind CSS | 4.3 | Utility-first CSS |
| TanStack Query | 5.100 | Server state management |
| React Router | 7.15 | Client-side routing |
| Zod | 3.x | Contract-first API validation |
| sonner | 2.x | Toast notifications |
| Recharts | 3.8 | Dashboard charts |
| Lucide React | 1.16 | Icon library |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.14 | Runtime |
| Django | 6.0 | Web framework |
| Django REST Framework | 3.17 | REST API |
| SimpleJWT | 5.x | JWT auth (access 1h / refresh 7d) |
| django-simple-history | 3.x | Audit logging |
| django-redis | 5.x | Caching (5 min TTL) |
| drf-spectacular | 0.x | OpenAPI / Swagger |
| pytotp | 4.x | QR code TOTP generation |

---

## Key Features

### Attendance System
- **TOTP-based QR codes** — dynamic QR that changes every 3 seconds (anti-proxy)
- **Bulk attendance marking** — mark all students Present/Late/Absent with one click
- **Progress tracking** — colored student status table with real-time counters

### Scheduling
- **Auto collision detection** — prevents double-booking classrooms and teachers
- **Week navigation** — browse timetable by week with today highlighting
- **Group filtering** — view timetable per academic group

### Role-Based Access Control
- **4 roles:** Student, Teacher, Admin, Superadmin
- **Hierarchical permissions** — route-level and sidebar-level enforcement
- **Smart redirect** — students land on Timetable, admins on Dashboard

### Data Integrity
- **Zod contract validation** — every API response validated against schema; invalid data returns fallback + console warning (never crashes)
- **Error Boundaries** — per-page crash containment; one broken page never takes down the entire app
- **Graceful Degradation** — toast notifications for 4xx/5xx errors instead of blank screens

### Audit Trail
- **django-simple-history** — tracks every change on User, Lesson, Attendance, Enrollment
- **Audit log UI** — timeline view with search, date grouping, and action type filters

---

## Security

| Layer | Implementation |
|-------|---------------|
| Authentication | JWT (access token + refresh token blacklist) |
| Attendance | TOTP-based QR code (3-second interval; secret derived from lesson ID + date) |
| Role Enforcement | Backend: DRF permissions; Frontend: route guards + sidebar filtering |
| Proxy Prevention | QR code includes timestamp + nonce; expires after interval |
| Input Validation | Zod schemas on frontend; DRF serializers on backend |
| Error Safety | Error Boundaries prevent full-app crashes |

---

## Frontend Architecture

### Directory Structure

```
src/
├── components/
│   ├── layout/          AppLayout, ProtectedRoute, ProtectedPage
│   └── ui/              shadcn/ui components (card, button, toaster)
├── features/
│   ├── auth/            LoginPage
│   ├── dashboard/       DashboardPage, AttendanceChart
│   ├── academic/        AcademicPage (tabs: Faculties/Groups/Subjects)
│   ├── timetable/       TimetablePage, LessonCard
│   ├── attendance/      AttendancePage, AttendanceTable, QRCodeGenerator
│   └── audit/           AuditPage (timeline view)
├── hooks/               useAuth, useAcademic, useTimetable, useAttendance, useAudit, useDashboardStats
├── lib/                 api-client.ts, schemas.ts, auth.ts, utils.ts
└── types/               index.ts
```

### Code Splitting

Each feature page is lazy-loaded via `React.lazy()` + `Suspense`. Build output:

| Chunk | Size |
|-------|------|
| `vendor` (react, react-dom, router) | ~389 kB |
| `ui` (lucide-react, recharts) | sorted with Dashboard |
| DashboardPage | ~338 kB |
| AcademicPage | ~80 kB |
| AttendancePage | ~33 kB |
| TimetablePage | ~7 kB |
| AuditPage | ~7 kB |

### State Management

- **Server state:** TanStack Query (cache-first with stale-while-revalidate)
- **Auth state:** React Context (AuthProvider)
- **Local state:** React useState / useCallback

---

## Backend Architecture

### Apps

```
apps/
├── users/           Custom User model, JWT auth, registration
├── academic/        Faculty → Department → Subject → Group → Enrollment
├── timetable/       Classroom → TimeSlot → Lesson → Attendance + QR generation
└── dashboard/       Aggregated stats endpoint
```

### Data Model

```
Faculty ──< Department ──< Subject
                │
                ├──< Group ──< Lesson ──< Attendance
                │       │        │
                │       │        └── TimeSlot
                │       │        └── Classroom
                │       │        └── Teacher (User)
                │       │
                │       └──< Enrollment ── Student (User)
                │
                └──< Semester ──< AcademicYear
```

### API Endpoints

**Auth** (`/api/users/`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/register/` | Create account |
| POST | `/login/` | Obtain JWT tokens |
| POST | `/refresh/` | Refresh access token |
| POST | `/logout/` | Blacklist token |

**Academic** (`/api/academic/`)
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/faculties/` | Faculties CRUD (nested departments) |
| GET/POST | `/departments/` | Departments CRUD |
| GET/POST | `/subjects/` | Subjects CRUD |
| GET/POST | `/groups/` | Groups CRUD |
| GET/POST | `/enrollments/` | Enrollments CRUD |

**Timetable** (`/api/timetable/`)
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/classrooms/` | Classrooms CRUD |
| GET/POST | `/time-slots/` | Time slots CRUD |
| GET/POST | `/lessons/` | Lessons CRUD (collision-checked) |
| GET | `/lessons/by-group/{id}/` | Group timetable |
| GET | `/lessons/by-teacher/{id}/` | Teacher timetable |
| GET/POST | `/attendances/` | Attendances CRUD |
| POST | `/attendances/bulk/` | Bulk attendance marking |
| GET | `/attendances/by-lesson/{id}/` | Lesson attendance roster |
| GET | `/attendances/by-student/{id}/` | Student attendance history |

**Dashboard** (`/api/dashboard/`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/stats/` | Aggregated dashboard statistics |

---

## Installation

### Prerequisites

- Python 3.14+
- Node.js 22+
- Redis (optional, for caching)

### Backend

```bash
# 1. Clone
git clone https://github.com/hojiakbar-me/UniManager-v2
cd UniManager-v2/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Migrate database
python manage.py migrate

# 4. Seed demo data (20 users, 10 lessons, 150 attendance records)
python manage.py seed_data

# 5. Create superadmin
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/api/docs/** for Swagger UI.

### Frontend

```bash
cd UniManager-v2/frontend

# 1. Install dependencies
npm install

# 2. Create .env file
echo "VITE_API_URL=http://localhost:8000/api" > .env

# 3. Start development server
npm run dev
```

Visit **http://localhost:5173** to use the application.

### Seed Credentials

| Role | Email | Password |
|------|-------|----------|
| Superadmin | `superadmin@uni.com` | `admin123` |
| Admin | `admin@uni.com` | `admin123` |
| Student | `ali.karimov@uni.com` | `admin123` |
| Student | `zarina.akhmedova@uni.com` | `admin123` |
| Student | `bekzod.tursunov@uni.com` | `admin123` |
| Student | `dilnoza.rakhimova@uni.com` | `admin123` |
| Student | `eldor.yusupov@uni.com` | `admin123` |
| Student | `feruza.mamatkulova@uni.com` | `admin123` |
| Student | `gulnara.sadykova@uni.com` | `admin123` |
| Student | `jasur.nazarov@uni.com` | `admin123` |

---

## Deployment

### Frontend (Vercel)

1. Push the frontend directory to a GitHub repository
2. Connect Vercel to the repository
3. Configure:
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Environment Variables:** `VITE_API_URL` → your backend URL
4. Deploy

The `vercel.json` file in the project root handles SPA routing:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

### Backend (Django)

Recommendations:
- **Database:** PostgreSQL (via Railway / AWS RDS)
- **Static/Media:** AWS S3 or DigitalOcean Spaces
- **App hosting:** Railway / Render / DigitalOcean App Platform
- **Cache:** Upstash Redis (serverless) or DigitalOcean Redis

---

## Development

### Build

```bash
# Backend
python manage.py check  # System check (0 issues)
python manage.py test   # Run tests

# Frontend
npm run build           # TypeScript + Vite build (0 errors)
npm run preview         # Preview production build
```

### Coding Conventions

- **Backend:** Models → Services → Serializers → Views → URLs (strict layer separation)
- **Frontend:** Feature-based module structure; generic DataTable + AddDialog patterns
- **TypeScript:** Enable `noUnusedLocals`, `noUnusedParameters`, `verbatimModuleSyntax`
- **Validation:** All API responses validated against Zod schemas; fallback on mismatch

---

## License

MIT

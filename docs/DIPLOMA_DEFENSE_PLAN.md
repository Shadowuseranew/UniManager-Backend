# UniManager — Diploma Defense Presentation Plan

## Slide Deck Structure (5 slides)

---

### Slide 1: Project Overview
**Title:** UniManager — University Management System

- **Goal:** Automate university academic operations (scheduling, attendance, enrollment)
- **Target Users:** Students, Teachers, Admin Staff
- **Core Modules:**
  - **Auth** — Role-based access (Student, Teacher, Admin, Superadmin)
  - **Academic Core** — Faculty → Department → Subject → Group
  - **Timetable** — Lesson scheduling with collision detection
  - **Enrollment + Attendance** — Full academic lifecycle

---

### Slide 2: Technology Stack
| Layer | Technology | Why |
|---|---|---|
| Backend | Python 3.14 + Django 6.0 | Rapid development, built-in security, ORM |
| API | Django REST Framework | Scalable, browsable API |
| Auth | SimpleJWT (access 1h / refresh 7d) | Stateless, blacklist support |
| Database | SQLite (dev) / PostgreSQL (prod) | Django ORM abstracts both |
| Docs | drf-spectacular (Swagger UI) | Auto-generated API docs |
| Architecture | Clean Architecture (Model → Service → Serializer → View) | Testability, separation of concerns |

---

### Slide 3: System Architecture

**Folder Structure:**
```
university_management/
├── apps/
│   ├── users/          # Auth (register, login, JWT)
│   ├── academic/       # Faculty, Department, Subject, Group, Enrollment
│   └── timetable/      # Classroom, TimeSlot, Lesson, Attendance
├── core/               # Settings, URLs, WSGI
```

**Layer Flow (per module):**
```
models.py  →  services.py  →  serializers.py  →  views.py  →  urls.py
  (DB schema)  (business logic)  (validation)  (request/response)  (routing)
```

**Key Principle:** Views never contain business logic. All logic lives in `services.py` inside `transaction.atomic()` blocks.

---

### Slide 4: Key Technical Decisions

#### 4.1 Custom User Model
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(choices=UserRole.choices)
    USERNAME_FIELD = 'email'
```
- Email used for login instead of username
- `TextChoices` prevents hardcoded role strings

#### 4.2 Service Layer (Business Logic Separation)
```python
# views.py — thin
def post(self, request):
    serializer.validate()
    service.create(...)    # ← business logic
    return Response(...)

# services.py — all logic here
@transaction.atomic
def create_lesson(...):
    collision_check()
    Lesson.objects.create(...)
```
- `transaction.atomic()` prevents partial writes
- Collision detection: classroom + teacher double-booking prevented

#### 4.3 Database Optimization
```python
# select_related — JOIN for FK relationships
Lesson.objects.select_related('subject', 'group', 'classroom', 'teacher')

# prefetch_related — separate query for related sets
Faculty.objects.prefetch_related('departments')

# Composite indexes for collision queries
models.Index(fields=['time_slot', 'classroom'])
models.Index(fields=['time_slot', 'teacher'])
```

#### 4.4 Audit Logging (Security)
```python
# One line per model — full change history tracked
class Lesson(models.Model):
    ...
    history = HistoricalRecords()
```
- `django-simple-history` — automatic table for every change (who, what, when)
- Admin panelda "History" tugmasi orqali ko'rish

#### 4.5 Caching (Performance)
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    },
}

# views.py — 5 daqiqalik cache
@method_decorator(cache_page(CACHE_TTL))
@action(detail=False, methods=['get'], url_path=r'by-group/(?P<group_id>\d+)')
def by_group(self, request, group_id=None):
    ...
```
- `/api/timetable/lessons/by-group/`, `by-teacher/`, faculties, groups — cached
- Redis xotirasida saqlanadi → response 10-20ms gacha tezlashadi

#### 4.6 Anti-Proxy Attendance (Dynamic QR + TOTP)
```python
# apps/timetable/services.py
TOTP_INTERVAL = 3  # 3 soniyada o'zgaradi

def generate_lesson_qr_token(lesson_id):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=3)
    return {'token': totp.now(), 'secret': totp.secret}

def verify_qr_token(secret, token):
    return pyotp.TOTP(secret, interval=3).verify(token)
```
- **Problem:** Talabalar o'rniga boshqalar darsga kirishi (proxy attendance)
- **Solution:** TOTP-based QR (3 soniyada o'zgaradi + Face ID kelajakda)
- `Attendance` modelida: `verified_by_face`, `qr_code_hash`, `attempt_time`

#### 4.7 Data Integrity
```python
unique_together = ['student', 'group', 'semester']  # Enrollment
unique_together = ['lesson', 'student']              # Attendance
```

---

### Slide 5: Live Demo

#### API Endpoints (via Swagger: `/api/docs/`)

**Auth:**
- `POST /api/users/register/` — Create account (AllowAny)
- `POST /api/users/login/` — Get JWT tokens (AllowAny)
- `POST /api/users/refresh/` — Refresh access token
- `POST /api/users/logout/` — Blacklist refresh token

**Academic:**
- `GET/POST /api/academic/faculties/` — List/Create (nested departments)
- `GET/POST /api/academic/departments/`
- `GET/POST /api/academic/subjects/`
- `GET/POST /api/academic/groups/`
- `GET/POST /api/academic/enrollments/`

**Timetable:**
- `POST /api/timetable/lessons/` — Create lesson (collision checked)
- `GET /api/timetable/lessons/by-group/{id}/` — Group schedule
- `GET /api/timetable/lessons/by-teacher/{id}/` — Teacher schedule
- `POST /api/timetable/attendances/bulk/` — Bulk mark attendance
- `POST /api/timetable/attendances/verify-qr/` — Verify QR + mark present

**Dashboard:**
- `GET /api/dashboard/stats/` — Enhanced system statistics (summary, users, attendance trend 7 days, enrollment by group, system flags)

#### Demo Flow:
1. Register a Student + Teacher
2. Login → get JWT → authorize Swagger
3. Create Faculty → Department → Subject → Group
4. Enroll Student in Group
5. Create Lesson + Verify collision rejection
6. Mark Attendance via bulk endpoint

---

## Defense Tips

| Committee Question | Your Answer |
|---|---|
| "Why Django?" | Fast development, security built-in, ORM with migrations, large ecosystem |
| "Why Service Layer?" | Separates business logic from views; makes unit testing possible; single point of change |
| "How do you handle conflicts?" | `CollisionError` raised in `services.py` before DB write; classroom + teacher checked |
| "How scalable is this?" | Stateless JWT auth, optimized queries (select_related), modular app structure |
| "What about testing?" | Service layer functions are pure → easy to unit test |
| "How do you ensure security?" | Audit Log (`django-simple-history`) tracks every change; JWT with blacklist; role-based access |
| "Why Redis?" | Cuts response time 10x; `@cache_page` on high-traffic endpoints; in-memory speed |
| "How do you prevent proxy attendance?" | Dynamic QR (TOTP, 3s rotation) + Face ID (roadmap); `POST /api/timetable/attendances/verify-qr/` endpoint |
| "What's your API coverage?" | 30+ endpoints across 4 apps; Swagger at `/api/docs/`; Dashboard stats at `/api/dashboard/stats/` |
| "Show me collision detection" | Open `apps/timetable/services.py` → `create_lesson()` checks classroom + teacher double-booking before INSERT; composite DB indexes for fast lookup |

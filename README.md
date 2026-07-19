Gym Management System — Backend
Django REST Framework backend for a gym management system: web dashboard for
admin/business owner, mobile app access for members, trainers, and receptionists.
Final-year project. Built incrementally, app by app, with real PostgreSQL
data and manual + automated testing at each step.
Tech Stack
Backend: Django 6.0, Django REST Framework
Auth: JWT (djangorestframework-simplejwt)
Database: PostgreSQL (production/dev), SQLite never used — Postgres from day one
Other: python-decouple (env config), Pillow (image uploads), python-dateutil (date math)
Project Structure
```
gym_project/
├── config/              # Django settings, root urls
├── apps/
│   ├── identity/        # Custom User, MemberProfile, StaffProfile, JWT auth
│   ├── membership/      # Plans, subscriptions, freeze/unfreeze
│   ├── attendance/       # QR check-in, manual check-in, staff attendance
│   ├── billing/          # Invoices, invoice items, payments, expenses
│   ├── fitness/           # Goals, measurements, workout/diet plans, trainer assignment
│   ├── notifications/     # Per-user notifications, announcements
│   ├── messaging/         # Conversations & messages (member <-> trainer)
│   ├── facility/          # Equipment, maintenance, lockers
│   ├── events/            # Events and registrations
│   ├── system/            # Audit log, app settings
│   └── dashboard/         # Admin aggregate stats endpoint
├── requirements.txt
└── manage.py
```
Setup
```bash
git clone https://github.com/RupeshPradhan369/gym-management-system.git
cd gym-management-system
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```
Create a `.env` file in the project root (never committed — see `.gitignore`):
```
SECRET_KEY=<your-secret-key>
DEBUG=True
DB_NAME=gym_db
DB_USER=gym_admin
DB_PASSWORD=<your-db-password>
DB_HOST=localhost
DB_PORT=5432
```
Create the database and a dedicated (non-superuser) app user in PostgreSQL:
```sql
CREATE DATABASE gym_db;
CREATE USER gym_admin WITH PASSWORD '<password>' CREATEDB;
ALTER SCHEMA public OWNER TO gym_admin;
```
(`CREATEDB` is needed so Django's automated test runner can create its
temporary test database — not required for the app to run normally.)
Run migrations and start the server:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
API is served under `http://127.0.0.1:8000/api/`, Django admin at `/admin/`.
Running Tests
```bash
python manage.py test apps.identity
python manage.py test apps.membership
python manage.py test apps.fitness
```
Django spins up a separate, temporary test database automatically — your
real data is never touched.
What's Built and Tested
Every item below was verified with real HTTP requests against a running
PostgreSQL-backed server (not just written and assumed to work). Several
real bugs were caught this way and fixed — see the commit history for
specifics (e.g. missing `read_only_fields` on generated codes, a duplicate
kwarg bug in nested serializer `create()`, and an inconsistent trainer
visibility gap that's now covered by an automated test).
App	Status	Key features
identity	✅ Tested	Custom User with roles (admin/receptionist/trainer/member), JWT login with role in response, member/staff registration, role-based permissions
membership	✅ Tested	Plans catalog, subscriptions with server-computed `end_date`, freeze/unfreeze lifecycle
attendance	✅ Tested	QR check-in with single-use token + replay protection, manual check-in with staff attribution, validity duration is runtime-configurable
billing	✅ Tested	Invoices with nested line items, partial/full cash payment recording, auto-notification on payment success. eSewa integration deliberately deferred.
fitness	✅ Tested	Goals, body measurements, progress reports, workout/diet plans, `TrainerAssignment` — trainers can only see/manage members they're actually assigned to (verified both by manual test and automated test)
notifications	✅ Tested	Per-user isolated inbox, `notify()` helper reused across apps, announcements with audience-based fan-out
messaging	✅ Tested	Conversations (M2M participants, extensible to group chat later), strict participant-only access
facility	✅ Tested	Equipment + maintenance history, locker assignment with double-booking guard and automatic status sync
events	✅ Tested	Registration with capacity checks, duplicate-registration handling, cancel/re-register flow
system	✅ Tested	`AuditLog` (who changed what, e.g. membership freeze history), `AppSetting` (runtime-configurable values, e.g. QR validity)
dashboard	✅ Tested	Member counts, attendance, membership health, real revenue (no fabricated numbers)
Automated test coverage so far: identity (login/role, registration
permissions), membership (end_date computation, freeze/unfreeze), fitness
(trainer isolation on Goal and WorkoutPlan). Other apps have been verified
manually via curl but don't yet have automated tests — a good next step.
Deliberately Not Built Yet
eSewa payment gateway — cash/card payment recording works; real eSewa
initiate/callback flow is more involved (signature verification) and was
intentionally deferred until the rest of the system was stable.
Scheduled jobs — nothing currently auto-expires memberships when
`end_date` passes; the dashboard's `expired_but_marked_active` field
exists specifically to surface this gap honestly rather than hide it.
A cron job or Celery beat task would close this.
Automated tests for billing, attendance, notifications, messaging,
facility, events, system — logic is manually verified but not yet locked
in with `TestCase`s.
Notes on Design Decisions
A few choices that might not be obvious from the code alone:
Server-computed dates everywhere (`Membership.end_date`,
`Invoice.invoice_number`, generated member/employee codes) — never
trusted from client input, always computed in `perform_create`/serializer
`create()`. This was a real bug caught and fixed early on.
`TrainerAssignment` as an explicit model, not inferred from "did this
trainer create a plan for this member" — assignment happens first (e.g.
when a member buys a PT package), and is what actually gates a trainer's
visibility into a member's fitness data, messaging, etc.
Read-only-until-action state fields (`Locker.status`,
`Membership.status`, `EventRegistration.status`) — these only change
through a controlled action/endpoint (freeze, release, register), never
direct client edits, to keep related records in sync.

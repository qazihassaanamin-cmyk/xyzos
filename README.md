# Tavryc — Internal Management Software

Tavryc's private, custom-built platform for day-to-day operations: projects
and tasks, deadlines, team communication (lounge), daily reports, focus
sessions, XP and achievements, shared knowledge base, announcements,
suggestions, inquiries, and company decision records. Built for the four
founders to coordinate work and stay accountable through one central system.

## Stack

- Python 3.13 / Flask 3 (application factory in `app/__init__.py`)
- Flask-SQLAlchemy + Flask-Migrate (Alembic), SQLite by default
- Flask-Login (sessions), Flask-WTF (CSRF), Flask-Argon2 (password hashing)
- Flask-Limiter (rate limiting), Pillow (upload validation)
- Vanilla JS + custom CSS design system (no build step)

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
Copy-Item .env.example .env   # then edit placeholders
.\.venv\Scripts\python -m flask --app wsgi db upgrade   # create/migrate the DB
.\.venv\Scripts\python set_founder_passwords.py          # seed founder accounts
.\.venv\Scripts\python -m flask --app wsgi run           # http://127.0.0.1:5000
```

The database lives at `instance/tavryc.sqlite` and is **never** created or
deleted automatically at boot — run the Alembic migrations explicitly.

## Testing

```powershell
.\.venv\Scripts\python tests\qa_smoke_routes.py
```

Hits every GET route against the real database with the predefined founder
credentials (read-only). Run `set_founder_passwords.py` first if the database
is fresh.

## Configuration

All configuration is environment-driven (see `.env.example` and
`app/config.py`):

- `SECRET_KEY` — required in production (a strong value is generated into
  `instance/secret.key` automatically on first production boot if absent).
- `COOKIE_SECURE=true` — required in production; `ProductionConfig.validate()`
  refuses to boot otherwise.
- `DATABASE_URL` — optional; defaults to the SQLite file above.
- `UPLOAD_ROOT` — where user uploads are stored (defaults to `uploads/`).
- SMTP settings — optional; password reset emails are printed to the log when
  SMTP is not configured.

Debug mode is enabled only under the `development` config; the WSGI entry
point (`wsgi.py`) uses production mode when `FLASK_ENV` is unset.

## Deployment to PythonAnywhere (free tier)

1. Push this repo to GitHub.
2. On PythonAnywhere, open a Bash console:
   ```bash
   git clone https://github.com/<you>/<repo>.git ~/xyz-os
   cd ~/xyz-os
   mkvirtualenv --python=python3.13 tavryc
   pip install -r requirements.txt
   flask --app wsgi db upgrade
   python set_founder_passwords.py
   ```
3. Web tab → *Add a new web app* → *Manual configuration* → Python 3.13.
4. Set the WSGI file to point at this checkout (copy `wsgi.py` to
   `/var/www/<username>_pythonanywhere_com_wsgi.py`, or set the source
   directory and import `wsgi.application`).
5. Set `FLASK_ENV=production`, `COOKIE_SECURE=true` and `PYTHONANYWHERE_FREE_TIER=1`
   in the web app's environment variables; reload the web app.
6. Uploads are written to `~/xyz-os/uploads/` — include that directory in any
   backup routine; it is excluded from Git.

Free-tier notes: no WebSockets, no scheduled tasks, no background workers —
the app is built around polling and works within these limits. SQLite is fine
for a four-person team; switch to PostgreSQL by setting `DATABASE_URL` if
needed (psycopg2 is already in `requirements.txt`).

## Voice and screen sharing

Not implemented. PythonAnywhere's free tier does not support WebSockets, so
WebRTC signalling cannot run there. See the final report for a recommended
architecture.

## Repository hygiene

- `.gitignore` excludes virtualenvs, caches, `instance/` (database +
  generated secret key), user uploads, and test output files.
- `.env` with real secrets must never be committed; use `.env.example`.

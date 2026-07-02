# FSD Phase 2

Monorepo for the full-stack game key marketplace project.

## Structure

- `backend/` - Django REST API, Celery, Docker, and deployment config
- `frontend/` - Angular client application

## Upload Notes

This folder is ready to upload as a single repository. The local build and environment artifacts are ignored so only source files and deployment config are tracked.

## Run Locally

Backend:

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm start
```



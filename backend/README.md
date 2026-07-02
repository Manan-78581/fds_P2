# GameKey Platform

A deployable Django REST API for a digital game key marketplace. The product supports:

- user registration and token authentication
- publisher and game management
- game key purchasing through orders
- expiry detection and webhook delivery
- Celery workers for asynchronous tasks
- Docker-based local and production deployment

## Local setup

1. Copy `.env.example` to `.env` and adjust values if needed.
2. Install dependencies with `uv sync`.
3. Run database migrations with `uv run python manage.py migrate`.
4. Start the API with `uv run python manage.py runserver`.

## Docker

Build and run the stack with:

```bash
docker compose up --build
```

The API will be available on `http://localhost:8000/`.

## Main endpoints

- `GET /api/health/`
- `POST /api/register/`
- `POST /api/token/`
- `GET|POST /api/publishers/`
- `GET|POST /api/games/`
- `GET|POST /api/orders/`
- `GET /admin/`
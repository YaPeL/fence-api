# school-billing API

[![CI](https://github.com/YaPeL/school-billing-api/actions/workflows/ci.yml/badge.svg)](https://github.com/YaPeL/school-billing-api/actions/workflows/ci.yml)
![Type Check](https://img.shields.io/badge/type%20check-mypy-blue)
![Tests](https://img.shields.io/badge/tests-smoke%20in%20CI-brightgreen)

TODO: add coverage badge once integration coverage reporting is added.

## Requirements
- Python 3.12
- Poetry
- Docker + Docker Compose

## Quickstart
1. Install dependencies:
   - `poetry install`
   - `pre-commit install`
2. Start PostgreSQL:
   - `docker compose up -d db`
3. Apply migrations:
   - `poetry run db-upgrade`
4. Run the API:
   - `poetry run uvicorn app.main:app --reload`
   
Extra generate migrations:
   - `poetry run db-revision -m "message"`

Open:
- http://localhost:8000/docs
- http://localhost:8000/health
- http://localhost:8000/health/db
- http://localhost:8000/metrics


## Run (docker)
- `docker compose up --build`

## Tests
- Fast tests (no DB):
  - `poetry run pytest -m smoke`
- Integration tests (opt-in, real DB, safe-only):
  - Start Postgres: `docker compose up -d db`
  - Create isolated test DB:
    - `docker compose exec -T db psql -U school_billing -d postgres -c "CREATE DATABASE school_billing_test;"`
  - Export test DB URL:
    - `export TEST_DATABASE_URL=postgresql+asyncpg://school_billing:school_billing@localhost:5432/school_billing_test`
  - Run:
    - `poetry run pytest -m integration`

Integration tests are skipped unless `TEST_DATABASE_URL` is set, points to a local host, and uses a test-named database.

## Notes
- Migrations are manual by design (they are not auto-run on app import/startup)
- CI runs `ruff`, `mypy`, and smoke tests on push/PR to `main`


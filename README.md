# Fence API

[![CI](https://github.com/YaPeL/school-billing-api/actions/workflows/ci.yml/badge.svg)](https://github.com/YaPeL/school-billing-api/actions/workflows/ci.yml)
![Type Check](https://img.shields.io/badge/type%20check-mypy-blue)
![Tests](https://img.shields.io/badge/tests-smoke%20in%20CI-brightgreen)

Small FastAPI service that ingests facility-specific portfolio snapshots, computes facility-specific covenant rates, and publishes the resulting covenant report as a persisted trusted record.

Implemented facilities:
- Educa Capital I
- PayEarly US
- Nomina Express I

## Requirements
- Python 3.12
- Poetry
- Docker + Docker Compose
- PostgreSQL

## What this service does

For each facility-specific portfolio submission, the service:

1. normalizes the incoming facility-specific asset payload
2. evaluates eligibility rules per facility
3. computes the facility-specific effective rate
4. determines covenant status (`COMPLIANT` or `BREACH`)
5. publishes the resulting covenant report to PostgreSQL
6. returns the report along with publication metadata

## API

Example payloads for manual testing are available in:
- [`docs/examples/portfolio_examples.md`](docs/examples/portfolio_examples.md)

### POST `/facilities/educa/covenant-report`
Computes and publishes the Educa covenant report.

### POST `/facilities/payearly/covenant-report`
Computes and publishes the PayEarly covenant report.

### POST `/facilities/nomina/covenant-report`
Computes and publishes the Nomina covenant report.

Request body:
- raw JSON array of facility assets

Response body:
- covenant report
- included and excluded assets
- publication metadata

Swagger/OpenAPI:
- http://localhost:8000/docs

Health:
- http://localhost:8000/health

## Architecture

The project follows a simple hexagonal-inspired structure:

- `app/api`
  - FastAPI routes and HTTP schemas
- `app/application`
  - use cases and output ports
- `app/domain`
  - business models and covenant calculation logic
- `app/core`
  - facility normalizers
  - deterministic hashing
  - SQLAlchemy models
  - database-backed publication adapter

Main design choices:
- explicit endpoint per facility instead of one generic endpoint
- facility-specific normalization before calculation
- facility-specific domain services
- database-first publication instead of smart-contract implementation

## AI-assisted development process

This challenge was developed using an iterative AI-assisted workflow.

Instead of using a single large prompt, I worked in small scoped iterations:
- define the next task
- generate code with Codex
- review the resulting diff
- run automated checks
- manually validate behavior with Swagger and targeted JSON payloads
- write focused fix prompts for edge cases or review findings

This approach made the changes easier to inspect, test, and reason about.

Artifacts:
- prompts: [`docs/codex/`](docs/codex/)
- fix prompts: [`docs/codex/FIXES/`](docs/codex/FIXES/)
- manual request examples: [`docs/examples/portfolio_examples.md`](docs/examples/portfolio_examples.md)

## Why explicit facility endpoints

I chose explicit facility endpoints because the challenge domain is naturally facility-specific.

Each facility differs in:
- asset schema
- field names
- date formats
- status vocabulary
- eligibility rules
- rate formula

Using explicit endpoints made the code easier to read, easier to test, and easier to discuss in an interview, while avoiding premature abstraction.

## Publication and idempotency

After computing a covenant report, the service persists it as a trusted published record in PostgreSQL.

Publication is part of request success:
- if calculation succeeds and persistence succeeds, the request succeeds
- if persistence fails, the request fails

Each published report stores:
- facility
- calculation version
- normalized payload JSON
- normalized payload hash
- computed rate
- threshold
- covenant status
- included and excluded assets
- publication timestamp

Idempotency is enforced with a unique key based on:
- `facility`
- `calculation_version`
- `normalized_payload_hash`

The hash is computed from a canonical normalized payload representation, so equivalent payloads with:
- different asset ordering
- equivalent decimal scales like `21.5` vs `21.50`

produce the same idempotency key.

## Assumptions and trade-offs

### Database-first publication
The challenge mentions publishing to a smart contract, but also explicitly allows using a database if smart-contract implementation becomes too time-consuming.

Given the timebox, I implemented a database-backed publication adapter behind a publication port. This keeps the core flow simple while leaving room for a future blockchain-backed adapter.

### Snapshot-based calculation
Each request is evaluated as a self-contained portfolio snapshot.
The current covenant calculation does not depend on previously published reports.

Historical publications are stored for:
- auditability
- reproducibility
- idempotency
- future extension of the publication mechanism

### All-excluded portfolios
The current implementation can still publish a covenant report even when all assets are excluded, as long as the submission can still be normalized and evaluated into a report.

This was kept intentionally simple for the challenge. In a production system, I would revisit whether fully invalid or fully excluded submissions should be rejected, published, or stored separately as ingestion/audit events.

## Edge cases handled

The implementation explicitly handles:
- case-insensitive status matching
- missing rates and fees
- zero-outstanding Educa assets
- negative outstanding rejection
- threshold equality as `BREACH`
- non-finite numeric values such as `NaN` and `Infinity`
- PayEarly timestamp precision
- Nomina end-of-month and leap-year month spans
- deterministic hashing for equivalent normalized payloads

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

Extra: generate migrations:
- `poetry run db-revision -m "message"`

Open:
- http://localhost:8000/docs
- http://localhost:8000/health

## Run with Docker
- `docker compose up --build`

## Tests

Smoke tests:
```bash
poetry run pytest -m smoke -q
```

Integration tests:
```bash
poetry run pytest -m integration -q
```

Lint:
```bash
poetry run ruff check app tests
```

Typing:
```bash
poetry run mypy app tests
```

## Future improvements

If I continued this beyond the challenge, I would likely:
- add clearer ingestion-versus-publication separation
- introduce a blockchain-backed publication adapter
- improve validation and error taxonomy for structurally wrong cross-facility payloads
- add richer audit metadata and report retrieval endpoints
- revisit the handling of fully excluded submissions depending on product requirements

# TASK_02_PUBLICATION.md

## Objective
Implement database-backed covenant report publication for the current FastAPI challenge solution.

This task should add:
- a publication port
- a database-backed publisher implementation
- SQLAlchemy persistence
- an Alembic migration
- deterministic normalized-payload hashing
- idempotent publication
- publication metadata in the API response

Keep the solution simple, demo-friendly, and easy to explain in an interview.

Do NOT implement any smart contract or EVM integration in this task.
Do NOT add speculative blockchain abstractions.
Do NOT store the raw request payload in this task.
Do NOT perform broad refactors.

## Context
The current implementation already:
- exposes facility-specific covenant-report endpoints
- normalizes facility-specific payloads
- computes covenant reports

Now the endpoint should also publish the computed covenant report as a trusted persisted record using a database-first approach.

Publication is part of the request success criteria:
- if calculation succeeds and publication succeeds, return success
- if calculation succeeds but publication fails, the request must fail
- do not return a successful covenant report response if it was not persisted

Idempotency must be based on:
- `facility`
- `calculation_version`
- `normalized_payload_hash`

The normalized payload itself should be stored for auditability and reproducibility.

## Scope

### 1. Publication port
Add a small output port focused on this use case, for example:
- `CovenantReportPublisher`

Keep the interface narrow and explicit.
Do not create a generic repository abstraction if it does not add value.

### 2. Publication command/result models
Add small application/domain models for:
- the data required to publish a covenant report
- the result returned by publication

Keep them explicit and easy to read.

### 3. SQLAlchemy model
Add a SQLAlchemy model for a single table:

- `published_covenant_reports`

Fields should include at least:
- `id`
- `facility`
- `calculation_version`
- `normalized_payload_json`
- `normalized_payload_hash`
- `effective_rate_percentage`
- `threshold_percentage`
- `covenant_status`
- `total_assets_evaluated`
- `assets_included_count`
- `assets_excluded_count`
- `included_assets`
- `excluded_assets`
- `published_at`
- `created_at`

Use PostgreSQL-friendly types.
Use JSONB where appropriate for:
- `normalized_payload_json`
- `included_assets`
- `excluded_assets`

Use sensible numeric precision for percentage fields.

Add a uniqueness constraint on:
- `facility`
- `calculation_version`
- `normalized_payload_hash`

### 4. Alembic migration
Add the corresponding Alembic migration for the new table.

The migration must:
- create `published_covenant_reports`
- create the unique constraint on `(facility, calculation_version, normalized_payload_hash)`
- use JSONB for the JSON fields if that matches the repo stack
- include downgrade support

### 5. Deterministic normalized payload hash
Add a deterministic hash generation step for the normalized payload.

Requirements:
- hash the normalized payload, not the raw request body
- use a stable canonical representation
- ensure equivalent normalized portfolios produce the same hash even if ordering differs
- sort by `external_id` when appropriate
- serialize with sorted keys
- use SHA-256

Persist both:
- the normalized payload JSON
- the normalized payload hash

### 6. Idempotent database-backed publisher
Implement a DB-backed publication adapter using the repo’s current SQLAlchemy patterns.

Publication behavior:
- if a record already exists for the same `facility + calculation_version + normalized_payload_hash`, return the existing record
- otherwise insert a new record and return it

Do not rely on prior published records for the current calculation.
Current calculation remains snapshot-based on the current request only.

Keep this behavior explicit and easy to follow.
Do not overengineer around upsert unless the repo already has a preferred pattern.

### 7. Integrate publication into the current flow
Update the facility covenant-report flow so that after a report is calculated, it is also published through the publication port.

Do not move business rules into the persistence layer.
Calculation should remain where it already belongs.
Publishing happens after calculation.

### 8. Failure behavior
Publication is required for request success.

If persistence/publication fails:
- do not silently continue
- do not return a successful covenant report response
- surface a clear failure through the API in a repo-consistent way

Use the smallest reasonable error-handling approach consistent with the current project.

### 9. API response
Extend the existing API response to include publication metadata, for example:

- `publication.id`
- `publication.calculation_version`
- `publication.normalized_payload_hash`
- `publication.published_at`
- `publication.was_already_published`

Keep the existing covenant report fields unchanged.

### 10. Calculation version
Introduce a simple calculation version value, for example:
- `"v1"`

Keep it simple and explicit for now.
Do not build a complex versioning framework.

### 11. Tests
Add tests appropriate to the repo style.

At minimum include:

#### Smoke tests
- deterministic normalized-payload hashing for logically equivalent normalized payloads with different ordering
- application/use-case level behavior where publication metadata is attached correctly, if this can be tested without DB by mocking the publisher

#### Integration tests
If the repo already supports DB-backed integration tests, add focused tests for:
- publication creates a record when none exists
- publication is idempotent for the same `facility + calculation_version + normalized_payload_hash`
- changing `calculation_version` creates a new record
- API response includes publication metadata after successful persistence

Keep fixtures small and readable.

### 12. Constraints
- Keep the diff reasonably small
- Do not introduce smart contract code
- Do not introduce async/event-driven publication
- Do not add large abstractions
- Do not rewrite the current architecture
- Do not store raw request payload in this task
- Prefer clarity over cleverness

## Delivery
Before coding:
1. inspect the current repo structure and existing implementation
2. identify the minimal files to add or modify
3. explain the minimal implementation plan

Then implement the task.

At the end:
- summarize the main files changed
- summarize the publication flow
- summarize idempotency behavior
- summarize the migration added
- mention any follow-up items for final documentation

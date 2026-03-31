# AGENTS.md

## Global (applies to all runs)
- Treat the user-provided prompt files (`PROMPT.md`, `TASK_*.md`) as the source of truth for what to do in this run.
- Follow repo conventions: FastAPI + SQLAlchemy 2.0 + PostgreSQL, Poetry, ruff/mypy, pytest markers (`smoke` / `integration`).
- Prefer small, safe diffs. Keep changes scoped to the requested task.
- Do not rewrite the project structure unless the task explicitly asks for it.
- Adapt to the existing codebase and naming conventions.

## Architecture guidelines for this repository
This repository follows a simple, pragmatic hexagonal-inspired structure.

High-level responsibilities:
- `app/api`: FastAPI routes and HTTP schemas only
- `app/application`: use cases and ports
- `app/domain`: business models and business logic
- `app/core`: technical adapters and implementations, including:
  - facility normalizers
  - hashing utilities
  - database models
  - database-backed publisher/repository implementations

Rules:
- Keep HTTP concerns inside `app/api`.
- Keep business rules and calculation logic inside `app/domain`.
- Keep orchestration inside `app/application`.
- Keep technical concerns and adapters inside `app/core`.
- Do not couple domain logic to FastAPI or ORM models.
- SQLAlchemy models belong in `app/core/db/models`.
- Database-backed implementations of output ports belong in `app/core/db/repositories` or an equivalent repo-consistent location.
- Avoid introducing formal patterns such as factories or strategies unless they clearly improve readability for the current task.
- Prefer explicit facility-specific code when that is clearer than abstraction.

## Challenge-specific guidelines
This challenge is about facility-specific covenant calculation.

Important assumptions:
- Each facility has its own raw asset schema.
- Each facility has its own normalization rules.
- Each facility has its own eligibility rules.
- Each facility has its own effective rate formula.
- Endpoints are explicit per facility, not generic.
- The request body for facility endpoints should follow the challenge samples as closely as practical.
- Publication is database-first unless a task explicitly says otherwise.
- Idempotency for publication is based on:
  - facility
  - calculation_version
  - normalized_payload_hash

Expected style:
- Clear and interview-friendly code
- Minimal ceremony
- Small focused abstractions
- Good naming over cleverness

## Testing guidelines
- `smoke` tests must be fast and must NOT hit the database.
- `integration` tests may hit the database and are optional depending on the task.
- Prefer smoke tests for domain services, use cases, normalization, hashing, and route behavior that can be tested without Postgres.
- Use integration tests only when validating real persistence behavior, migrations, or SQLAlchemy-backed publication flows.
- Keep fixtures small and readable.
- Test edge cases that matter for correctness and discussion quality.

## Review mode guidelines (for codex review)
Act as a senior reviewer. Review uncommitted changes.

Priorities:
1. Correctness and edge cases
2. API design consistency
3. Typing, mypy, and test quality
4. Maintainability, naming, and module boundaries
5. Alignment with the intended architecture

Output format:
- Top 5 issues (most important first)
- Quick wins (small changes with high impact)
- Optional refactors (only if worth it)

Constraints:
- Do not propose large scope expansions.
- Do not suggest skipping tests.
- Prefer to actionable findings over abstract commentary.

Review strictness:
- Even if everything looks OK, still provide:
  - 2 potential risks or edge cases to double-check
  - 2 consistency checks
  - 1 small improvement suggestion, otherwise say "No changes recommended"
- If changes include tests, comment on test intent and what they do NOT cover.

## Run modes
- If running `codex exec`: produce code changes that satisfy the provided `TASK_*.md`.
- If running `codex review`: do not propose large refactors; focus on actionable findings.
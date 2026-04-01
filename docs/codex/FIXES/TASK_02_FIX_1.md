# TASK_02_FIX_1.md

## Objective
Apply a small corrective patch to the publication/idempotency implementation.

Keep this task tightly scoped.
Do not refactor the whole project.
Do not change the API shape unless strictly required.
Only fix:
1. canonical Decimal handling for normalized payload hashing
2. post-commit refresh failure handling in the SQLAlchemy publisher

## Issues to fix

### 1. Canonicalize Decimal values before hashing
The current normalized payload hashing preserves textual Decimal scale differences such as:
- `21.5`
- `21.50`

Those values are numerically equal after normalization, but they currently produce different hash inputs and therefore different `normalized_payload_hash` values.

That breaks semantic idempotency.

Expected behavior:
- semantically identical normalized payloads must produce the same hash
- Decimal values must be converted to a canonical stable representation before hashing
- insignificant trailing zeros must not affect the hash

Examples:
- `21.5` and `21.50` must hash the same
- `0.00` and `0` must hash the same
- `100.000` and `100` must hash the same

Keep the hashing logic deterministic and easy to explain.

### 2. Do not treat post-commit refresh failures as publish failures
In the SQLAlchemy publisher, if `commit()` succeeds but `refresh()` fails afterward, the current code treats the publish as failed.

That is incorrect if the row was already persisted.

Expected behavior:
- if `commit()` succeeds, publication should be considered persisted
- if `refresh()` fails after a successful commit, try to recover by reading the existing row using the idempotency key
- if the row can be found, return it successfully
- only fail if the row cannot be refreshed and also cannot be recovered from the database

Do not incorrectly return a 500 for a publication that was already committed.

## Scope
Only touch the minimum code needed to:
1. canonicalize Decimal values for hashing
2. make post-commit refresh handling robust
3. preserve the current public behavior otherwise

Do not perform unrelated cleanup in this task.

## Tests
Add or update tests to cover at least:

1. Hash stability for semantically equal Decimal values with different textual scales
Examples:
- `21.5` vs `21.50`
- `0.00` vs `0`

2. Publisher behavior when commit succeeds and refresh fails afterward
Expected:
- publisher still returns success if the committed row can be recovered by lookup

3. Existing idempotency tests should continue to pass

Keep tests small and focused.

## Constraints
- Keep the diff small
- No broad refactors
- No API redesign
- No schema changes unless absolutely necessary

## Delivery
Before coding:
1. identify the minimal files to modify
2. explain the minimal fix plan

Then implement the fix.

At the end:
- summarize the Decimal canonicalization change
- summarize the refresh-recovery change
- summarize the tests added or updated

# TASK_01_FIX_5.md

## Objective
Apply a small corrective patch for PayEarly timestamp handling.

Keep this task tightly scoped.
Do not refactor the whole project.
Do not add persistence.
Do not change the API shape.
Only fix the incorrect truncation of PayEarly timestamp inputs and add/update the relevant tests.

## Issue to fix

### PayEarly must preserve time-of-day when timestamp inputs are accepted
The current PayEarly normalizer accepts timestamp-like inputs such as:
- `%Y-%m-%dT%H:%M:%S`
- `%Y-%m-%dT%H:%M:%SZ`

However, those parsed values are currently coerced to `.date()`, which discards the time-of-day.

That is incorrect when the service later computes tenor from `created_at` to `due_date`, because truncating timestamps to calendar dates can materially understate the annualized fee yield.

Example:
- a very short tenor such as 2 hours can be silently turned into 1 calendar day
- this lowers the reported annualized rate
- a portfolio may appear `COMPLIANT` when it should be `BREACH`

## Expected behavior

For PayEarly:
- if timestamp inputs are accepted, preserve them as datetimes
- do not silently coerce accepted timestamps to dates
- tenor calculation must use the actual temporal distance, not truncated calendar dates

This means:
- `created_at` and `due_date` should remain precise enough for the PayEarly tenor calculation
- if the current model uses `date`, update it to a more appropriate type for PayEarly
- if mixed date-only and datetime inputs are supported, handle them consistently and explicitly

A simple acceptable behavior is:
- parse date-only values as midnight datetimes
- parse timestamp values as real datetimes
- compute tenor from those normalized datetime values

## Scope
Only touch the minimum code needed to:
1. preserve PayEarly time-of-day precision
2. ensure tenor calculation uses that precision
3. keep the rest of the facilities unchanged
4. preserve the outward API shape

Do not perform unrelated cleanup in this task.

## Implementation guidance
- Keep the fix localized to PayEarly normalization/modeling/service code
- Do not introduce a broad date/time abstraction layer
- Do not change Educa or Nomina date handling unless strictly required
- Keep the code easy to explain in an interview

## Tests
Add or update smoke tests to cover at least:

1. A PayEarly case with timestamp input including non-midnight time-of-day
Expected:
- the normalized value preserves time-of-day
- tenor calculation uses actual timestamp distance, not truncated dates

2. A test demonstrating that a short timestamp-based tenor produces a materially different annualized result than a date-truncated approach
Expected:
- the corrected implementation reflects the shorter tenor and higher annualized rate

3. Existing PayEarly date-only behavior should continue to work if still supported

Keep tests small and fast.
Do not require Postgres.

## Constraints
- Keep the diff very small
- No persistence
- No DB changes
- No broad refactors
- No API contract changes

## Delivery
Before coding:
1. identify the minimal files to modify
2. explain the minimal fix plan

Then implement the fix.

At the end:
- summarize the timestamp-preservation correction
- summarize the tests added or updated
- mention whether any PayEarly internal model types had to change

# TASK_01_FIX_7.md

## Objective
Apply a small corrective patch for Nomina repayment-month calculation.

Keep this task tightly scoped.
Do not refactor the whole project.
Do not add persistence.
Do not change the API shape.
Only fix the repayment-month calculation so valid end-of-month schedules are treated correctly, and add/update the relevant tests.

## Issue to fix

### Nomina must treat end-of-month rollovers as valid month spans
The current Nomina repayment-month calculation uses a day-of-month adjustment that incorrectly turns valid one-month schedules into `0` months for end-of-month rollovers.

Examples of valid schedules that should count as one repayment month:
- `2026-01-31` -> `2026-02-28`
- `2024-01-31` -> `2024-02-29`

Right now, those cases are being treated as invalid date ranges and excluded from the covenant calculation.

That is incorrect for this challenge.

## Expected behavior

For Nomina:
- repayment months should represent the month span between `origination_date` and `maturity_date`
- valid shorter-month end-of-month rollovers should still count as one repayment month
- the examples above must evaluate as `1` repayment month, not `0`

Important:
- preserve the existing rule that clearly invalid or non-positive ranges should still be excluded
- do not silently change the outward API shape
- keep the fix easy to explain in an interview

## Implementation guidance
Use the smallest clear fix that correctly handles end-of-month schedules.

Acceptable approaches:
- adjust the current month-difference logic so that end-of-month rollovers count as a full month span, or
- use a small date-aware helper that handles this case explicitly

Do NOT introduce a large date abstraction layer.
Do NOT refactor other facilities.

## Scope
Only touch the minimum code needed to:
1. fix Nomina repayment month calculation for valid end-of-month rollovers
2. preserve existing behavior for clearly invalid date ranges
3. keep the rest of the facilities unchanged
4. preserve the outward API shape

Do not perform unrelated cleanup in this task.

## Tests
Add or update smoke tests to cover at least:

1. Nomina case:
- `origination_date = 2026-01-31`
- `maturity_date = 2026-02-28`
Expected:
- repayment months treated as `1`
- asset is not excluded for invalid date range solely because of this rollover

2. Leap-year Nomina case:
- `origination_date = 2024-01-31`
- `maturity_date = 2024-02-29`
Expected:
- repayment months treated as `1`

3. A clearly invalid non-positive range should still be excluded
Expected:
- same outward exclusion behavior as before

4. If existing Nomina happy-path tests need adjustment, keep them aligned with the corrected month-span semantics

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
- summarize the repayment-month correction
- summarize the tests added or updated
- confirm that valid end-of-month one-month schedules are now included correctly

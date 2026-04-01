# TASK_01_FIX_4.md

## Objective
Apply a small corrective patch for Educa outstanding amount handling.

Keep this task tightly scoped.
Do not refactor the whole project.
Do not add persistence.
Do not change the API shape.
Only fix the incorrect handling of negative Educa outstanding amounts and add/update the relevant tests.

## Issue to fix

### Educa should allow zero outstanding but reject negative outstanding
After the previous fix, Educa no longer excludes assets with `outstanding_amount == 0`, which is correct.

However, the current implementation now also allows assets with `outstanding_amount < 0` to pass through as eligible, which is incorrect for malformed inputs.

This creates bad behavior such as:
- an Educa asset with negative outstanding being included
- a portfolio with only negative outstanding weights falling into a `0.00` / `COMPLIANT` result

That is not acceptable.

## Expected behavior

For Educa:
- `outstanding_amount is None` -> exclude
- `outstanding_amount < 0` -> exclude
- `outstanding_amount == 0` -> include
- `outstanding_amount > 0` -> include

Important:
- zero outstanding assets that otherwise meet Educa eligibility must still be included
- negative outstanding assets must be excluded with a clear reason
- the existing zero-outstanding compliant behavior must remain intact

## Exclusion reason
Use a clear explicit reason for negative values, for example:
- `outstanding_amount must be >= 0`

Keep the wording consistent with the rest of the service.

## Scope
Only touch the minimum code needed to:
1. reject negative Educa outstanding amounts
2. preserve zero-outstanding inclusion
3. preserve the current outward response shape
4. keep the previous zero-weight portfolio fix working

Do not perform unrelated cleanup in this task.

## Tests
Add or update smoke tests to cover at least:

1. Educa asset with valid open/current/eligible fields and `outstanding_amount = 0`
Expected:
- included, not excluded

2. Educa asset with valid open/current/eligible fields and `outstanding_amount < 0`
Expected:
- excluded
- explicit exclusion reason
- not included in the weighted calculation

3. A portfolio with eligible Educa assets whose total outstanding weight is exactly zero because all included assets have `outstanding_amount == 0`
Expected:
- effective rate `0.00`
- covenant status `COMPLIANT`

4. Ensure the malformed negative-outstanding case does not incorrectly produce a compliant included portfolio

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
- summarize the negative-outstanding correction
- summarize the tests added or updated
- confirm that zero-outstanding inclusion still works

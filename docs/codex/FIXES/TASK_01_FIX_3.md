# TASK_01_FIX_3.md

## Objective
Apply a small corrective patch for the PayEarly covenant calculation.

Keep this task tightly scoped.
Do not refactor the whole project.
Do not add persistence.
Do not change the API shape.
Only fix the unit mismatch in the PayEarly effective-rate calculation and add/update the relevant tests.

## Issue to fix

### PayEarly fee yield is currently being treated as a percentage when it is still a fraction
In the current implementation, the PayEarly formula:

`(total_fee_amount / total_principal_amount) * (365 / tenor_days)`

produces a decimal fraction, not a percentage.

However, the service currently:
- compares that value directly against the covenant threshold `3.0`
- exposes it as `effective_rate_percentage`
- formats it as if it were already in percentage units

This underreports PayEarly rates by a factor of 100.

Example:
- a computed value of `0.1216` means `12.16%`, not `0.12%`

## Expected behavior

For PayEarly:
- the outward `effective_rate_percentage` must be expressed in percentage units
- the covenant comparison must also use percentage units
- therefore the computed annualized fee yield must be converted from fraction to percentage before threshold evaluation and response formatting

The threshold remains:
- `COMPLIANT` only if effective rate `< 3.0`
- `BREACH` if effective rate `>= 3.0`

After the fix:
- a portfolio yielding about `12.16%` must be reported around `12.16`
- and must be `BREACH`, not `COMPLIANT`

## Scope
Only touch the minimum code needed to:
1. correct the PayEarly unit handling
2. keep the rest of the facilities unchanged
3. preserve the existing response shape

Do not perform unrelated cleanup in this task.

## Tests
Add or update smoke tests to cover at least:

1. A PayEarly example where the current implementation would incorrectly return a much smaller percentage
Expected:
- output is in percentage units
- covenant status is correct

2. A boundary-oriented PayEarly test if useful, ensuring the threshold comparison is being performed against percentage values, not fractional values

3. Existing PayEarly happy-path tests should continue to pass with corrected expectations if necessary

Keep tests small and fast.
Do not require Postgres.

## Constraints
- Keep the diff very small
- No persistence
- No DB changes
- No broad refactors
- No API contract changes
- Preserve naming unless a very small rename is necessary for clarity inside the service

## Delivery
Before coding:
1. identify the minimal files to modify
2. explain the minimal fix plan

Then implement the fix.

At the end:
- summarize the unit correction
- summarize the tests added or updated
- mention whether any existing test expectations had to change because they were based on the incorrect x100 behavior

# TASK_01_FIX.md

## Objective
Fix the issues found during review for the first covenant-report implementation, while keeping the current architecture and scope intact.

This is a small corrective task.
Do not refactor the whole solution.
Do not add persistence.
Do not add publication logic.
Do not introduce new abstractions unless strictly necessary.

## Issues to fix

### 1. Educa eligibility must not exclude zero outstanding assets
In the current implementation, Educa assets are being excluded when `outstanding_amount <= 0`.

That is incorrect for this challenge.

For Educa, the eligibility criteria are only:
- `status = "open"`
- `is_eligible = true`
- `loan_status = "current"`
- `interest_rate_percentage` is not null

Do NOT require `outstanding_amount > 0` for Educa eligibility.

Important:
- A zero-outstanding Educa asset that otherwise qualifies should be included
- It should contribute zero weight to the weighted average
- It must not appear in `excluded_assets` with reason `outstanding_amount must be > 0`

### 2. Reject non-finite decimal inputs during normalization
The decimal parsing helper currently accepts values such as:
- `"NaN"`
- `"Infinity"`
- `"-Infinity"`

These must not be treated as valid numeric values.

Fix the decimal normalization helper so that:
- invalid decimal inputs return `None`
- non-finite decimal values also return `None`

This should prevent facility endpoints from crashing later during comparisons or quantization.

The goal is to handle malformed numeric inputs reasonably, not with uncaught server errors.

## Expected behavior
- Facility endpoints should not crash with 500 errors because of non-finite decimal strings
- Educa should not incorrectly exclude zero-outstanding assets
- Existing task behavior should remain otherwise unchanged

## Tests
Add or adjust smoke tests to cover at least:

1. Educa asset with:
- valid open/current/eligible fields
- non-null `interest_rate_percentage`
- `outstanding_amount = 0`
Expected:
- asset is included, not excluded

2. Decimal normalization rejects `"NaN"`

3. Decimal normalization rejects `"Infinity"`

4. If needed, one route/service test proving malformed non-finite numeric input does not cause an uncaught exception

Keep tests small and fast.
Smoke tests must not require Postgres.

## Constraints
- Keep the diff small
- Do not change the overall architecture
- Do not introduce persistence or DB changes
- Do not add unrelated cleanup
- Prefer a focused bug-fix patch

## Delivery
Before coding:
1. briefly identify the files to modify
2. explain the minimal fix plan

Then implement the fixes.

At the end:
- summarize the bug fixes
- summarize the tests added or changed

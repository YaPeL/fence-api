# TASK_01_FIX_2.md

## Objective
Apply a second small corrective patch to the covenant-report implementation.

Keep this task tightly scoped.
Do not refactor the whole project.
Do not add persistence.
Do not introduce new architecture.
Only fix the reviewed correctness issue and perform a very small readability cleanup where it directly improves the touched code.

## Issues to fix

### 1. Zero-outstanding Educa portfolios must evaluate as a 0% compliant result
After the previous fix, zero-outstanding Educa assets can now be included.
However, if all included Educa assets have `outstanding_amount == 0`, the current implementation still falls into the conservative fallback branch and returns:

- `effective_rate_percentage = 0.00`
- `covenant_status = BREACH`

That is incorrect.

Expected behavior:
- if Educa assets are eligible and included
- and their weighted contribution results in a total outstanding weight of 0
- then the effective rate should be treated as `0.00`
- and the covenant status should be evaluated normally against the threshold

Since Educa is compliant only when `effective_rate < 22.0`, a 0% effective rate must result in:
- `effective_rate_percentage = 0.00`
- `covenant_status = COMPLIANT`

Important distinction:
- "no eligible assets at all" may still use the explicitly chosen fallback behavior from the previous task
- "eligible assets exist, but total weight is zero" must NOT be treated the same as "no eligible assets"

### 2. Small readability cleanup for repeated hardcoded exclusion reason strings
In the domain services there are some repeated hardcoded exclusion reason strings inside loops.

Do a small cleanup only where it improves readability in the touched code.
Examples:
- define local named constants for repeated reasons within a service module, or
- extract a tiny obvious helper if it clearly reduces repetition without adding abstraction noise

Do NOT perform a broad refactor.
Do NOT introduce a shared constants framework unless it is genuinely minimal and justified.
Keep the current style simple and interview-friendly.

## Expected behavior
After this patch:

- Educa portfolios with included assets and zero total outstanding weight should return `0.00` and `COMPLIANT`
- The existing "no eligible assets" behavior should remain unchanged unless required for correctness
- The touched domain service code should be slightly clearer where repeated exclusion reasons were previously hardcoded

## Tests
Add or update smoke tests to cover at least:

1. Educa portfolio with one or more eligible included assets and all `outstanding_amount == 0`
Expected:
- included assets count > 0
- effective rate is `0.00`
- covenant status is `COMPLIANT`

2. Distinguish this from the "no eligible assets" case if not already covered

3. If you perform the small string-readability cleanup, ensure existing tests still validate the same exclusion reasons and outward behavior

Keep tests small and fast.
Do not require Postgres.

## Constraints
- Keep the diff very small
- No persistence
- No DB changes
- No large refactors
- No new cross-cutting abstractions
- Preserve existing outward response shape

## Delivery
Before coding:
1. identify the minimal files to touch
2. explain the minimal fix plan

Then implement the fix.

At the end:
- summarize the correctness fix
- summarize the small readability cleanup
- summarize the tests added or changed

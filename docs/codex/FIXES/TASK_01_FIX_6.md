# TASK_01_FIX_6.md

## Objective
Apply a very small test/tooling fix for async smoke tests and mypy invocation.

Keep this task tightly scoped.
Do not touch application logic.
Do not refactor tests broadly.
Only restore the explicit AnyIO backend configuration required for this repository and address the current mypy execution issue related to the `tests` path.

## Issues to fix

### 1. Async smoke tests must explicitly use the asyncio backend
The newly added `@pytest.mark.anyio` smoke tests currently do not force the AnyIO backend.

In this repository, Trio is not installed as a development dependency.
Without an explicit backend fixture, `pytest-anyio` may also try to run tests with the Trio backend and fail before the test assertions run, with an error like:

`ModuleNotFoundError: No module named 'trio'`

### 2. Make mypy checks work cleanly for the current test layout
`poetry run mypy app tests` currently fails because of the `tests` directory structure / discovery, not because of real typing errors in `app`.

Fix this in the smallest reasonable way so that the repository can run a clean mypy command without failing on test discovery/layout issues.

Acceptable solutions include:
- adding the minimal package markers needed for `tests` to be recognized properly, if that matches the repo style
- or adjusting mypy configuration / invocation in the smallest repo-consistent way so mypy checks the intended code without tripping on the current `tests` layout

Prefer the smallest, clearest fix.
Do not introduce broad tooling changes.

## Expected behavior
- Async smoke tests should run using `asyncio`
- The test suite should not attempt to run them with Trio
- Mypy should run cleanly for the intended checked paths without failing because of the `tests` directory structure

## Scope
Only touch the minimum test and tooling/config files needed.

Acceptable solutions:
- add a module-level `anyio_backend` fixture returning `"asyncio"` in the affected test module, or an equivalent shared test fixture if that is already the repo convention
- add the minimal mypy/test-layout fix needed for clean local execution

## Constraints
- No application code changes
- No architecture changes
- No new dependencies
- No broad test refactor
- No broad mypy config rewrite unless strictly necessary

## Delivery
Before coding:
1. identify the minimal files to modify
2. explain the minimal fix plan

Then implement the fix.

At the end:
- summarize the change
- confirm that the async smoke tests are pinned to asyncio
- confirm how the mypy/test-layout issue was resolved

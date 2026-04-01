# TASK_01.md

## Objective
Implement the first working slice of the covenant calculation service.

This task should deliver:
- explicit facility-specific FastAPI endpoints
- facility-specific normalization
- facility-specific covenant calculation services
- a common covenant report response schema
- smoke tests for the first slice

Do NOT implement database publication in this task.
Do NOT implement SQLAlchemy persistence in this task.
Do NOT implement smart contract publishing in this task.

## Scope

### Endpoints
Add the following POST endpoints:

- `/facilities/educa/covenant-report`
- `/facilities/payearly/covenant-report`
- `/facilities/nomina/covenant-report`

Each endpoint must accept the request body as a raw JSON array of assets, following the facility-specific sample shape.

Do not wrap the request body in an object like `{ "assets": [...] }`.

### Facility-specific normalization
Implement one normalizer per facility.

Each normalizer must:
- accept raw facility asset dictionaries
- normalize status case-insensitively
- parse facility-specific date fields where needed
- map raw asset data into a clear facility-specific internal model

Important normalization expectations:
- Educa statuses may appear as `open`, `Open`, `OPEN`
- PayEarly statuses may appear as `performing`, `PERFORMING`, `Performing`
- Nomina statuses may appear as `active`, `ACTIVE`
- Date formats differ across facilities
- Do not force a fake shared input model across all facilities

### Facility-specific calculation
Implement one domain service per facility.

Each service must:
1. evaluate asset eligibility
2. calculate the effective rate using only eligible assets
3. collect included assets
4. collect excluded assets with explicit reasons
5. determine covenant status based on the facility threshold
6. return a common covenant report structure

Use explicit facility-specific services rather than introducing a formal factory or strategy abstraction.

### Facility rules

#### Educa
Effective Rate:

`sum(outstanding_amount_i * interest_rate_percentage_i) / sum(outstanding_amount_i)`

Eligibility, all must hold:
- `status = "open"`
- `is_eligible = true`
- `loan_status = "current"`
- `interest_rate_percentage` is not null

Threshold:
- `COMPLIANT` only if effective rate `< 22.0`
- `BREACH` if effective rate `>= 22.0`

#### PayEarly
For each eligible asset:

`fee_yield_i = (total_fee_amount_i / total_principal_amount_i) * (365 / tenor_days_i)`

Effective Rate:

`sum(outstanding_principal_amount_i * fee_yield_i) / sum(outstanding_principal_amount_i)`

Where:
- `tenor_days_i` is the number of days between `created_at` and `due_date`

Eligibility, all must hold:
- `status = "performing"`
- `is_eligible = true`
- `outstanding_principal_amount > 0`

Threshold:
- `COMPLIANT` only if effective rate `< 3.0`
- `BREACH` if effective rate `>= 3.0`

#### Nomina
For each eligible asset:

`annualized_fee_i = fee_percentage_i * (12 / repayment_months_i)`

Effective Rate:

`sum(outstanding_amount_i * annualized_fee_i) / sum(outstanding_amount_i)`

Where:
- `repayment_months_i` is the number of months between `origination_date` and `maturity_date`

Eligibility, all must hold:
- `status = "active"`
- `is_eligible = true`
- `outstanding_amount > 0`

Threshold:
- `COMPLIANT` only if effective rate `< 5.0`
- `BREACH` if effective rate `>= 5.0`

## Response shape
Define a common response schema for all three endpoints with fields equivalent to:

- `facility`
- `effective_rate_percentage`
- `covenant_status`
- `summary`
  - `total_assets_evaluated`
  - `assets_included`
  - `assets_excluded`
- `included_assets`
- `excluded_assets`

Where:
- `included_assets` is a list of external IDs
- `excluded_assets` is a list of objects with:
  - `external_id`
  - `reasons`

Format the effective rate to 2 decimals in the outward response.

## Exclusion reasons
When an asset is excluded, include explicit reasons. Examples:
- `status mismatch`
- `ineligible flag`
- `loan_status mismatch`
- `missing interest_rate_percentage`
- `outstanding_principal_amount must be > 0`
- `outstanding_amount must be > 0`
- `invalid created_at or due_date`
- `invalid origination_date or maturity_date`

Do not overengineer the exclusion-reason collection.

## Edge cases
Handle these cases reasonably and consistently:
- no eligible assets
- division by zero
- invalid dates
- missing critical fields

For this task, choose a simple and explicit behavior for the no-eligible-assets case.
Document that behavior briefly in code comments or docstrings if needed.

Threshold boundary behavior must be correct:
- equality with the threshold means `BREACH`

## Numeric handling
Use `Decimal` for money/rates in business logic where practical.
Avoid `float` in core calculation logic.

## Architecture expectations
Follow the repository structure and conventions from `PROMPT.md` and `AGENTS.md`.

Keep responsibilities separated:
- `app/api`: routes and HTTP schemas
- `app/application`: orchestration if needed
- `app/domain`: business models and calculation logic
- `app/core`: normalizers and technical helpers

Do not introduce persistence in this task.

## Tests
Add smoke tests only in this task.

At minimum include:
- one happy-path test per facility service or route
- one test proving status matching is case-insensitive
- one Educa test where `interest_rate_percentage` is null and the asset is excluded for that reason
- one threshold-boundary test proving that `rate == threshold` results in `BREACH`
- one no-eligible-assets test

Smoke tests must not require Postgres.

## Constraints
- Keep the diff small and coherent
- Do not add persistence
- Do not add Alembic migrations
- Do not add SQLAlchemy models for publication yet
- Do not introduce formal factory or strategy abstractions unless clearly necessary
- Prefer explicit, readable code over clever abstractions

## Delivery
Before writing code:
1. inspect the current repo structure
2. briefly state the plan of files to create or modify

Then implement the task.

At the end:
- summarize the main files changed
- summarize assumptions made
- mention any small follow-up items that should be handled in the publication task

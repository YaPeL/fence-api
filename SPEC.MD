# SPEC

## Goal
Build a small backend service that ingests facility-specific portfolio data, computes a covenant effective rate according to each facility’s rules, and returns a covenant report that can later be published as a trusted record.

The system must support multiple facilities with:
- different raw asset payload schemas
- different normalization rules
- different eligibility criteria
- different effective rate formulas

The backend should make these facility-specific differences explicit while keeping the overall design simple and easy to extend.

## Facilities in scope

### Facility A: Educa Capital I
Education / ISA-style assets.

### Facility B: PayEarly US
Earned Wage Access assets.

### Facility C: Nomina Express I
Salary advance assets.

## Core requirements

### Ingestion and normalization
The system must accept raw portfolio data for each facility in its native format.

Each facility may differ in:
- field names
- date formats
- status vocabulary and casing
- numeric fields used for eligibility and calculation

Before calculation, raw assets must be normalized into clear internal models per facility.

### Covenant calculation
For each facility, the system must:
1. evaluate asset eligibility
2. include only eligible assets in the facility calculation
3. compute the effective rate according to the facility formula
4. evaluate the covenant threshold
5. produce a covenant report

### Covenant report
For each facility request, the system should produce:
1. computed effective rate as a percentage, rounded/formatted to 2 decimals
2. covenant status: `COMPLIANT` or `BREACH`
3. summary:
   - total assets evaluated
   - assets included
   - assets excluded
4. included assets:
   - list of `external_id`
5. excluded assets:
   - list of `external_id` plus exclusion reasons

## Facility rules

### Facility A: Educa Capital I
Effective Rate:

`sum(outstanding_amount_i * interest_rate_percentage_i) / sum(outstanding_amount_i)`

Eligibility criteria, all must hold:
- `status = "open"` (case-insensitive after normalization)
- `is_eligible = true`
- `loan_status = "current"`
- `interest_rate_percentage` is not null

Threshold:
- `COMPLIANT` only if effective rate `< 22.0`
- `BREACH` if effective rate `>= 22.0`

### Facility B: PayEarly US
For each eligible asset:

`fee_yield_i = (total_fee_amount_i / total_principal_amount_i) * (365 / tenor_days_i)`

Effective Rate:

`sum(outstanding_principal_amount_i * fee_yield_i) / sum(outstanding_principal_amount_i)`

Where:
- `tenor_days_i` is the number of days between `created_at` and `due_date`

Eligibility criteria, all must hold:
- `status = "performing"` (case-insensitive after normalization)
- `is_eligible = true`
- `outstanding_principal_amount > 0`

Threshold:
- `COMPLIANT` only if effective rate `< 3.0`
- `BREACH` if effective rate `>= 3.0`

### Facility C: Nomina Express I
For each eligible asset:

`annualized_fee_i = fee_percentage_i * (12 / repayment_months_i)`

Effective Rate:

`sum(outstanding_amount_i * annualized_fee_i) / sum(outstanding_amount_i)`

Where:
- `repayment_months_i` is the number of months between `origination_date` and `maturity_date`

Eligibility criteria, all must hold:
- `status = "active"` (case-insensitive after normalization)
- `is_eligible = true`
- `outstanding_amount > 0`

Threshold:
- `COMPLIANT` only if effective rate `< 5.0`
- `BREACH` if effective rate `>= 5.0`

## API
Minimum endpoints:

- `POST /facilities/educa/covenant-report`
- `POST /facilities/payearly/covenant-report`
- `POST /facilities/nomina/covenant-report`

Request body:
- raw JSON array of assets for the target facility, following that facility’s native sample shape

Response body:
- covenant report with:
  - facility
  - effective_rate_percentage
  - covenant_status
  - summary
  - included_assets
  - excluded_assets

Swagger / OpenAPI docs should be available.

## Publication and persistence
The system should be designed so that covenant reports can be published as trusted records.

For the initial implementation, database-backed publication is acceptable and preferred over smart-contract implementation unless explicitly requested.

When publication is implemented, it should support:
- storing the normalized payload
- storing a calculation version
- idempotent publication based on:
  - facility
  - calculation_version
  - normalized_payload_hash

## Technical requirements
- Python
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Poetry
- pytest
- Alembic migrations
- ruff
- mypy

## Testing requirements
- `smoke` tests must be fast and must NOT hit the database
- `integration` tests may hit the database
- business logic should be testable in isolation
- normalization and edge cases should be covered by tests
- persistence behavior should be covered by integration tests when publication is added

## Architecture expectations
Use a simple, pragmatic, hexagonal-inspired structure.

The code should separate:
- HTTP/API concerns
- use-case orchestration
- domain calculation logic
- technical adapters such as:
  - normalizers
  - hashing
  - database-backed publication

Avoid unnecessary abstraction or overengineering.

## Edge cases to handle
At minimum, handle these cases reasonably:
- no eligible assets
- division by zero
- invalid dates
- missing critical fields
- case-insensitive status matching
- threshold boundary behavior where equality means `BREACH`

## Nice-to-haves
Optional, only if time allows:
- health endpoints
- basic metrics
- clearer audit metadata on published covenant reports
- sample payload fixtures for local manual testing
- concise README explaining architecture decisions and trade-offs

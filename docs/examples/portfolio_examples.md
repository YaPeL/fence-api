# Manual Test Payloads for Covenant Report Publishing

This document contains test payloads and expected outcomes for validating covenant report publication, idempotency behavior, payload normalization, and invalid-input handling.

## 1. Educa, valid and republishable case

**Endpoint**

`POST /facilities/educa/covenant-report`

```json
[
  {
    "external_id": "EDU-PUB-001",
    "effective_date": "2024-06-25",
    "reporting_date": "2026-01-15",
    "status": "open",
    "is_eligible": true,
    "student_id": "STU-001",
    "school_id": "SCH-001",
    "loan_status": "current",
    "disbursement_amount": 6500.00,
    "outstanding_amount": 5000.00,
    "repaid_amount": 1500.00,
    "interest_rate_percentage": 20.50,
    "days_past_due": 0,
    "country": "ES",
    "amount": 6500.00
  },
  {
    "external_id": "EDU-PUB-002",
    "effective_date": "2024-07-01",
    "reporting_date": "2026-01-15",
    "status": "OPEN",
    "is_eligible": true,
    "student_id": "STU-002",
    "school_id": "SCH-002",
    "loan_status": "current",
    "disbursement_amount": 3000.00,
    "outstanding_amount": 1000.00,
    "repaid_amount": 2000.00,
    "interest_rate_percentage": 19.50,
    "days_past_due": 0,
    "country": "ES",
    "amount": 3000.00
  }
]
```

**Expected**

- Rate close to `20.33`
- `COMPLIANT`
- A publication record is created
- First request: `was_already_published = false`
- Second request with the exact same body: `was_already_published = true`

---

## 2. Educa, same logical content but different asset order

Use exactly the same content as above, but reverse the asset order.

```json
[
  {
    "external_id": "EDU-PUB-002",
    "effective_date": "2024-07-01",
    "reporting_date": "2026-01-15",
    "status": "OPEN",
    "is_eligible": true,
    "student_id": "STU-002",
    "school_id": "SCH-002",
    "loan_status": "current",
    "disbursement_amount": 3000.00,
    "outstanding_amount": 1000.00,
    "repaid_amount": 2000.00,
    "interest_rate_percentage": 19.50,
    "days_past_due": 0,
    "country": "ES",
    "amount": 3000.00
  },
  {
    "external_id": "EDU-PUB-001",
    "effective_date": "2024-06-25",
    "reporting_date": "2026-01-15",
    "status": "open",
    "is_eligible": true,
    "student_id": "STU-001",
    "school_id": "SCH-001",
    "loan_status": "current",
    "disbursement_amount": 6500.00,
    "outstanding_amount": 5000.00,
    "repaid_amount": 1500.00,
    "interest_rate_percentage": 20.50,
    "days_past_due": 0,
    "country": "ES",
    "amount": 6500.00
  }
]
```

**Expected**

- Same `normalized_payload_hash`
- `was_already_published = true`
- Ideally, the same `publication.id` as in the previous case

---

## 3. Educa, same numeric values but different decimal scales

This case validates the `Decimal` canonicalization fix.

```json
[
  {
    "external_id": "EDU-PUB-001",
    "effective_date": "2024-06-25",
    "reporting_date": "2026-01-15",
    "status": "open",
    "is_eligible": true,
    "student_id": "STU-001",
    "school_id": "SCH-001",
    "loan_status": "current",
    "disbursement_amount": 6500.0,
    "outstanding_amount": 5000.000,
    "repaid_amount": 1500.00,
    "interest_rate_percentage": 20.500,
    "days_past_due": 0,
    "country": "ES",
    "amount": 6500.00
  },
  {
    "external_id": "EDU-PUB-002",
    "effective_date": "2024-07-01",
    "reporting_date": "2026-01-15",
    "status": "OPEN",
    "is_eligible": true,
    "student_id": "STU-002",
    "school_id": "SCH-002",
    "loan_status": "current",
    "disbursement_amount": 3000.00,
    "outstanding_amount": 1000.0,
    "repaid_amount": 2000.000,
    "interest_rate_percentage": 19.5000,
    "days_past_due": 0,
    "country": "ES",
    "amount": 3000.00
  }
]
```

**Expected**

- Same hash as in case 1
- `was_already_published = true`

---

## 4. PayEarly, normal case that should persist

**Endpoint**

`POST /facilities/payearly/covenant-report`

```json
[
  {
    "external_id": "PAY-PUB-001",
    "created_at": "2026-01-01",
    "due_date": "2026-01-31",
    "last_updated": "2026-01-05T10:00:00Z",
    "status": "performing",
    "is_eligible": true,
    "employer_id": "EMP-001",
    "employer_name": "Acme Corp",
    "employee_id": "USR-001",
    "user_state": "CA",
    "total_principal_amount": 1000.00,
    "outstanding_principal_amount": 1000.00,
    "repaid_principal_amount": 0.00,
    "total_fee_amount": 10.00,
    "outstanding_fee_amount": 10.00,
    "receivable_currency": "USD",
    "days_past_due": 0,
    "amount": 1000.00
  }
]
```

**Expected**

- `12.17`
- `BREACH`
- Publication is persisted successfully
- Repeating the same request returns `was_already_published = true`

---

## 5. PayEarly, extremely short timestamp window

```json
[
  {
    "external_id": "PAY-PUB-TS-001",
    "created_at": "2026-01-01T10:00:00Z",
    "due_date": "2026-01-01T12:00:00Z",
    "last_updated": "2026-01-01T10:05:00Z",
    "status": "performing",
    "is_eligible": true,
    "employer_id": "EMP-002",
    "employer_name": "Acme Corp",
    "employee_id": "USR-002",
    "user_state": "CA",
    "total_principal_amount": 1000.00,
    "outstanding_principal_amount": 1000.00,
    "repaid_principal_amount": 0.00,
    "total_fee_amount": 10.00,
    "outstanding_fee_amount": 10.00,
    "receivable_currency": "USD",
    "days_past_due": 0,
    "amount": 1000.00
  }
]
```

**Expected**

- Extremely large rate
- `BREACH`
- Publication is persisted successfully

---

## 6. Nomina, end-of-month case

**Endpoint**

`POST /facilities/nomina/covenant-report`

```json
[
  {
    "external_id": "NOM-PUB-001",
    "origination_date": "2026-01-31",
    "cutoff_date": "2026-02-01",
    "status": "active",
    "is_eligible": true,
    "employer_name": "Merlin Properties SOCIMI",
    "employer_tax_id": "ESA86648867",
    "net_monthly_salary": 3200.00,
    "advance_amount": 1800.00,
    "outstanding_amount": 900.00,
    "repaid_amount": 900.00,
    "fee_percentage": 2.5,
    "fee_amount": 45.00,
    "days_past_due": 0,
    "maturity_date": "28/02/2026",
    "amount": 1800.00
  }
]
```

**Expected**

- `30.00`
- `BREACH`
- Publication is persisted successfully

---

## 7. Invalid payload, useful for verifying that no garbage is persisted

```json
[
  {
    "external_id": "PAY-BAD-PERSIST-001",
    "created_at": "2026-01-01",
    "due_date": "2026-01-31",
    "last_updated": "2026-01-05T10:00:00Z",
    "status": "performing",
    "is_eligible": true,
    "employer_id": "EMP-003",
    "employer_name": "Gamma LLC",
    "employee_id": "USR-003",
    "user_state": "FL",
    "total_principal_amount": "NaN",
    "outstanding_principal_amount": 1000.00,
    "repaid_principal_amount": 0.00,
    "total_fee_amount": 10.00,
    "outstanding_fee_amount": 10.00,
    "receivable_currency": "USD",
    "days_past_due": 0,
    "amount": 1000.00
  }
]
```

**Expected**

- The calculation response should either exclude the record or use a fallback, depending on the current behavior
- If the system still publishes the calculated snapshot, verify that the result is consistent
- If fully invalid cases are not meant to be published, that is also acceptable, but the API should fail clearly and explicitly
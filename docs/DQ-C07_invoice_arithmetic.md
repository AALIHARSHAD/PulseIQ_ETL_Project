# DQ-C07 — Invoice Arithmetic

## Status
FAIL — Reference-data issue identified; production validation unavailable.

## Rule
Invoice arithmetic must satisfy:
- `amount_paid <= total_amount`
- `balance_due >= 0`

The configured tolerance is ₹0.01.

## Validation Results
- Reference invoice rows inspected: 743
- Identified invalid row: INV-00385
- Issue: amount paid exceeds total amount by ₹100

## Production Limitation
The production warehouse does not contain a `fact_invoice` table.
Therefore, this finding is based on workbook reference data and is
not a completed validation of a production invoice table.

## Recommended Action
1. Ask the invoice/Finance data owner to investigate INV-00385.
2. Confirm the correct total, paid amount, and balance due.
3. Do not change the source record without approval.
4. Run DQ-C07 against the production invoice table when available.

## Conclusion
The reference data contains an invoice arithmetic issue. Production
DQ-C07 remains unverified until the invoice data is available in the
warehouse.

# DQ-C08 — Expense Arithmetic

## Status
FAIL — Reference-data issue identified; production validation unavailable.

## Rule
Expense total must equal the amount excluding GST plus GST,
within the configured tolerance of ₹0.01.

## Validation Results
- Reference expense rows inspected: 501
- Identified invalid row: EXP-00371
- Issue: recorded total is ₹500 higher than the expected total.

## Production Limitation
The production warehouse does not contain a `fact_expense` table.
This finding comes from workbook reference data and does not establish
the status of production expense records.

## Recommended Action
1. Ask the Finance/expense data owner to investigate EXP-00371.
2. Recalculate the expected total from the source amount and GST.
3. Confirm the correct values with the data owner before making changes.
4. Run DQ-C08 against production expense records when available.

## Conclusion
A reference-data arithmetic discrepancy was identified. Production
validation remains pending until the expense table is available.

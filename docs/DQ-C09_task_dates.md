# DQ-C09 — Task Dates Sensible

## Status
FAIL — Reference-data issues identified; production validation unavailable.

## Rules
- A task completion date must not be earlier than its start date.
- A task with status `Done` must have a completion date.

## Validation Results
- Reference task rows inspected: 28,868
- Rows with completion date before start date: 12
- `Done` tasks missing completion date: 8
- Total unique invalid rows: 20

The total counts unique invalid rows, avoiding double-counting if a row
violates both rules.

## Production Limitation
The production warehouse does not contain a `fact_task` table.
These findings are based on workbook reference data, not production
task records.

## Recommended Action
1. Ask the task-data owner to review the 20 invalid rows.
2. Confirm task status and start/completion dates against source records.
3. Do not alter source values without owner approval.
4. Run DQ-C09 against production data when the task table is available.

## Conclusion
Reference data contains task-date inconsistencies. Production validation
remains pending until task records are available in the warehouse.

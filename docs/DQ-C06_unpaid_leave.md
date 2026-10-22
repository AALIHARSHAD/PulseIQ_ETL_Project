# DQ-C06 — Unpaid Leave Deduction

## Status
FAIL — Business investigation required.

## Rule
Compare attendance `unpaid_absence_days` with payroll `lop_days`
for each employee and month. The configured tolerance is 0.5 days.

## Validation Results
- Matched employee-months checked: 7,339
- Mismatches exceeding tolerance: 39
- Difference of -1.0 day: 38 rows
- Difference of -1.5 days: 1 row

Difference is calculated as:

`attendance unpaid_absence_days - payroll lop_days`

The negative differences indicate that payroll LOP days exceed the
attendance unpaid-absence days for the affected employee-months.

## Example Mismatches
- EMP-0011, 2026-02: attendance 3 days, payroll LOP 4 days
- EMP-0019, 2026-01: attendance 0 days, payroll LOP 1 day
- EMP-0578, 2026-01: attendance 1 day, payroll LOP 2.5 days

## Recommended Action
1. Ask the HR/Payroll data owner to investigate the 39 mismatches.
2. Confirm whether payroll adjustments, different calculation rules,
   or source-data issues explain the differences.
3. Do not modify source records without business-owner approval.
4. Rerun DQ-C06 after any approved correction.

## Limitation
This check establishes a discrepancy between attendance and payroll.
It does not by itself prove which source is correct.

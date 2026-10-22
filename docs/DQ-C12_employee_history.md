# DQ-C12 — Employee History Overlap

## Status
FAIL — source-data issue confirmed.

## Check
Employee history intervals for the same employee must not overlap.

## Evidence
The original `PulseIQ_master_dataset.xlsx` workbook, sheet `dim_employee`,
contains three records for `EMP-0001`.

| Employee key | Valid from | Valid to | Change reason |
|---|---|---|---|
| 100000 | 2012-01-19 | 2012-05-12 | Joining |
| 100001 | 2012-05-03 | 2015-05-13 | Manager Change |
| 100002 | 2015-05-14 | 2020-01-24 | Manager Change |

Records 100000 and 100001 overlap from 2012-05-03 through 2012-05-12,
inclusive. The overlap is present in the original workbook and in the
warehouse, so it is not caused solely by the warehouse build.

## Impact
A date falling inside the overlap matches two employee-history versions.
This can create ambiguity in historical reporting and slowly changing
dimension joins.

## Recommended remediation
1. Ask the data owner to confirm the correct effective date of the
   manager change.
2. Correct the source workbook only after the owner confirms the date.
3. Rebuild the warehouse and reapply primary/foreign-key constraints.
4. Rerun DQ-C12 and verify that no employee history intervals overlap.

## Safety note
No source or warehouse dates were changed during this investigation.
The check remains FAIL until an approved correction is made and verified.

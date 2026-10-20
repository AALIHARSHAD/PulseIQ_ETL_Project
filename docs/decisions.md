# Data-quality decisions (Task 1)

| Situation | Rule | Why |
|---|---|---|
| **hire_date after exit_date** (the "think for yourself" case) | **Quarantine** every version of that employee: removed from clean data, saved in `rejected_rows.csv` as `HIRE_AFTER_EXIT`, counted in the run log. Fix at source. | Dropping silently hides a person from headcount. "Fixing" means guessing which date is wrong, and either guess corrupts tenure, headcount and attrition. Quarantine keeps the evidence and keeps the numbers honest. Rows that depend on that person (payroll, attendance) are rejected as orphans. |
| Duplicate payroll row (same employee + run) | Keep lowest `payroll_item_id`, reject the copy | Overstates pay if kept |
| Payroll for unknown employee | Reject (`ORPHAN_FOREIGN_KEY`) | Money cannot be assigned to anyone |
| Attendance after exit / before hire | Reject (`ATTENDANCE_OUTSIDE_EMPLOYMENT`) | Impossible; cannot tell which side is wrong |
| Leave end date before start date | **Fix** by swapping, flag `dates_swapped_fixed`, list in `corrected_rows.csv` | Pattern is clearly swapped dates; nothing is lost |
| SCD versions overlap (valid_to runs into next valid_from) | **Fix**: `valid_to = next valid_from - 1 day`, flag `valid_to_adjusted` | The next version's start is the authoritative change date; otherwise facts join to two versions |
| Missing `variable_pay_type` with zero variable pay | Fill with `"None"` | Normal case, make it explicit |
| Negative pay | Reject, never `abs()` | A sign error may hide a bigger problem |
| Reject rate above `MAX_REJECT_PCT` (2%) | Run **fails**, nothing written to `clean/` | A few bad rows are normal; many means the source is broken |

Repeatability: output sorted deterministically, no `today()` (a fixed `DATA_CUTOFF_DATE` is used for tenure), atomic file replace. The run log stores a SHA-256 of every output file so two runs can be compared.

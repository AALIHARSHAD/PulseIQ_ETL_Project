# DQ-C14 — Minimum Group Size

## Rule
Manager-facing aggregate metrics must not expose groups below
the minimum group size specified in the metric dictionary.
Small groups must be suppressed or combined.

## Diagnostic findings
The payroll diagnostic grouped records by month and department,
then counted distinct employees.

- Executive Office (D00): 1 employee in each reported month.
- Legal & Compliance (D10): 8–9 employees in the reported months.
- These groups are below the applicable thresholds of 5 and 10,
  respectively.

## Interpretation
The diagnostic identifies groups requiring privacy suppression.
It does not indicate that the underlying source records are invalid.

## Limitations
This diagnostic uses payroll employee counts as a proxy for group
size. It does not independently validate all 28 metrics.
Metric-specific population logic must be applied where necessary.
Metrics without a defined threshold, or without their required
production source tables, remain unverified.

## Required remediation
1. Apply the metric dictionary's threshold to each manager-facing view.
2. Suppress or combine groups below the threshold.
3. Test each metric view and confirm that suppressed values cannot
   be recovered through dashboard filters or drill-downs.
4. Record unavailable metrics and thresholds as limitations.

## Privacy suppression test — M09

Tested view: `metric_m09_payroll_cost`

- Minimum group size: 5 employees
- Source department-month groups below threshold: 18
- Small groups exposed through the metric view: 0
- Result: PASS

The test compared source payroll groups with the protected view.
No department-month group with fewer than five distinct employees
was exposed by this view.

Scope limitation: this result applies only to M09. The other metric
views and dashboard filters/drill-down paths require separate tests.

## Privacy suppression tests — M09 to M14

| Metric view | Source groups below threshold | Exposed small groups | Result |
|---|---:|---:|---|
| metric_m09_payroll_cost | 18 | 0 | PASS |
| metric_m10_cost_per_head | 18 | 0 | PASS |
| metric_m11_overtime_share | 18 | 0 | PASS |
| metric_m12_variable_pay_share | 18 | 0 | PASS |
| metric_m13_attendance_rate | 18 | 0 | PASS |
| metric_m14_late_arrival_rate | 18 | 0 | PASS |

All six tested views enforce a minimum group size of five distinct
employees. The source-to-view comparison found no small groups
exposed through these views.

Remaining scope: M01-M08, M15-M28, metric-specific population
validation, and dashboard filters/drill-down paths are not covered
by these six tests. M04-M06 require a threshold of 10.

## M04-M06 — Attrition metric privacy validation

The headcount fact contains 891 department-month groups.
A comparison against active employees derived from dim_employee
found 513 groups where ending headcount did not match the
dimension-derived count.

Groups with headcount_start below 10: 245.
Groups with headcount_end below 10: 240.

Status: NOT VALIDATED.

Reason: the aggregate fact and employee dimension do not reconcile
consistently. The dimension also contains a previously identified
overlapping history interval for EMP-0001. These discrepancies
prevent reliable confirmation of the distinct employee population
behind each monthly attrition metric.

Do not mark M04-M06 privacy checks as PASS until the headcount
reconciliation and employee-history issues are investigated.
No source data was modified during these checks.

### Additional headcount reconciliation

The initial formula, headcount_start + hires - exits, showed
26 mismatches across 891 department-month groups.

After including transfers, the formula
headcount_start + hires - exits + transfers_in - transfers_out
matched headcount_end in all 891 groups.

Result: PASS for aggregate headcount arithmetic.
This does not resolve the separate mismatch against
dimension-derived active employee counts, so M04-M06 privacy
validation remains NOT VALIDATED.

### Historical headcount reconciliation — corrected

The initial comparison counted employee records without applying
their historical validity intervals, causing false mismatches.

After applying valid_from <= month_end_date and
valid_to >= month_end_date, all 891 department-month groups
matched headcount_end across all 11 departments and 81 months.

Result: PASS for historical headcount reconciliation.

Note: EMP-0001 has an overlapping validity interval in the
dimension. Although the department-month headcount reconciles,
that overlap remains a separate DQ-C12 issue and must be
investigated. M04-M06 privacy validation is not yet marked PASS.

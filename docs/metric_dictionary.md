# PulseIQ Metric Dictionary (v0.1, first 5 metrics)

Official names, definitions and formulas come from the master dataset's `metric_dictionary` sheet. Chart titles in later tasks must use these exact names. The *Clean-data lineage* line shows which columns from Task 1 feed each metric.

Privacy rule: never show a group smaller than **minimum group size** (a group of one reveals one person).

## M01 - Headcount

| Field | Value |
|---|---|
| Business definition | Active employees on the last day of the month (permanent and contract). |
| Formula | `COUNT(DISTINCT employee_id) with hire_date <= month_end AND (exit_date IS NULL OR exit_date > month_end)` |
| Grain | Department x month |
| Time period | Month end |
| Unit | count |
| Good direction | Context dependent |
| Owner | HR Analytics |
| Source table | fact_headcount_monthly / dim_employee |
| Clean-data lineage | employee.hire_date, employee.exit_date, employee.employee_id (latest version per employee; Task 2 builds fact_headcount_monthly) |
| Caveat | Excludes CEO if you compare departments only |
| Minimum group size | 5 |

## M02 - Hires

| Field | Value |
|---|---|
| Business definition | Employees whose hire_date falls in the month. |
| Formula | `COUNT(employee_id) where hire_date in month` |
| Grain | Department x month |
| Time period | Month |
| Unit | count |
| Good direction | Context dependent |
| Owner | HR Analytics |
| Source table | fact_headcount_monthly |
| Clean-data lineage | employee.hire_date / hire_year_month |
| Caveat | Transfers are not hires |
| Minimum group size | 5 |

## M03 - Exits

| Field | Value |
|---|---|
| Business definition | Employees whose exit_date falls in the month (resigned, terminated or contract ended). |
| Formula | `COUNT(employee_id) where exit_date in month` |
| Grain | Department x month |
| Time period | Month |
| Unit | count |
| Good direction | Lower is better |
| Owner | HR Analytics |
| Source table | fact_headcount_monthly |
| Clean-data lineage | employee.exit_date / exit_year |
| Caveat | - |
| Minimum group size | 5 |

## M04 - Attrition rate (monthly)

| Field | Value |
|---|---|
| Business definition | Share of people who left in the month. |
| Formula | `Exits / headcount_start x 100` |
| Grain | Department x month |
| Time period | Month |
| Unit | percent |
| Good direction | Lower is better |
| Owner | HR Analytics |
| Source table | fact_headcount_monthly |
| Clean-data lineage | M03 and M01 at month start |
| Caveat | Very noisy for small departments |
| Minimum group size | 10 |

## M05 - Attrition rate (rolling 12 months)

| Field | Value |
|---|---|
| Business definition | Leavers in the last 12 months divided by average headcount over the same months. |
| Formula | `SUM(exits, 12m) / AVG(headcount_end, 12m) x 100` |
| Grain | Department x month |
| Time period | 12 months |
| Unit | percent |
| Good direction | Lower is better |
| Owner | HR Analytics |
| Source table | fact_headcount_monthly |
| Clean-data lineage | M03 summed over 12 months and M01 averaged over the same months |
| Caveat | Use for headline reporting; monthly is too noisy |
| Minimum group size | 10 |

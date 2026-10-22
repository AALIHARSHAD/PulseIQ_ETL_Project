-- PulseIQ privacy-safe metric views
-- Read-only source tables; small department-month groups are suppressed.

CREATE OR REPLACE VIEW metric_m09_payroll_cost AS
SELECT
    p.period_year_month,
    p.department_id,
    d.department_name,
    SUM(p.employer_cost) AS payroll_cost,
    COUNT(DISTINCT p.employee_id) AS contributing_employee_count
FROM fact_payroll p
LEFT JOIN dim_department d
    ON p.department_id = d.department_id
WHERE p.period_year_month IS NOT NULL
  AND p.department_id IS NOT NULL
GROUP BY
    p.period_year_month,
    p.department_id,
    d.department_name
HAVING COUNT(DISTINCT p.employee_id) >= 5;

CREATE OR REPLACE VIEW metric_m10_cost_per_head AS
SELECT
    p.period_year_month,
    p.department_id,
    d.department_name,
    SUM(p.employer_cost) / NULLIF(COUNT(DISTINCT p.employee_id), 0)
        AS cost_per_head
FROM fact_payroll p
LEFT JOIN dim_department d
    ON p.department_id = d.department_id
WHERE p.period_year_month IS NOT NULL
  AND p.department_id IS NOT NULL
GROUP BY
    p.period_year_month,
    p.department_id,
    d.department_name
HAVING COUNT(DISTINCT p.employee_id) >= 5;

CREATE OR REPLACE VIEW metric_m11_overtime_share AS
SELECT
    p.period_year_month,
    p.department_id,
    d.department_name,
    100.0 * SUM(p.overtime_pay) /
        NULLIF(SUM(p.employer_cost), 0) AS overtime_share_pct
FROM fact_payroll p
LEFT JOIN dim_department d
    ON p.department_id = d.department_id
WHERE p.period_year_month IS NOT NULL
  AND p.department_id IS NOT NULL
GROUP BY
    p.period_year_month,
    p.department_id,
    d.department_name
HAVING COUNT(DISTINCT p.employee_id) >= 5;

CREATE OR REPLACE VIEW metric_m12_variable_pay_share AS
SELECT
    p.period_year_month,
    p.department_id,
    d.department_name,
    100.0 * SUM(p.variable_pay) /
        NULLIF(SUM(p.gross_pay), 0) AS variable_pay_share_pct
FROM fact_payroll p
LEFT JOIN dim_department d
    ON p.department_id = d.department_id
WHERE p.period_year_month IS NOT NULL
  AND p.department_id IS NOT NULL
GROUP BY
    p.period_year_month,
    p.department_id,
    d.department_name
HAVING COUNT(DISTINCT p.employee_id) >= 5;

CREATE OR REPLACE VIEW metric_m13_attendance_rate AS
SELECT
    a.period_year_month,
    a.department_id,
    d.department_name,
    1.0 * (
        SUM(a.present_days) + 0.5 * SUM(a.half_days_unpaid)
    ) / NULLIF(SUM(a.scheduled_days), 0) AS attendance_rate
FROM fact_attendance_monthly a
LEFT JOIN dim_department d
    ON a.department_id = d.department_id
WHERE a.period_year_month IS NOT NULL
  AND a.department_id IS NOT NULL
GROUP BY
    a.period_year_month,
    a.department_id,
    d.department_name
HAVING COUNT(DISTINCT a.employee_id) >= 5;

CREATE OR REPLACE VIEW metric_m14_late_arrival_rate AS
SELECT
    a.period_year_month,
    a.department_id,
    d.department_name,
    1.0 * SUM(a.late_arrivals) /
        NULLIF(SUM(a.present_days), 0) AS late_arrival_rate
FROM fact_attendance_monthly a
LEFT JOIN dim_department d
    ON a.department_id = d.department_id
WHERE a.period_year_month IS NOT NULL
  AND a.department_id IS NOT NULL
GROUP BY
    a.period_year_month,
    a.department_id,
    d.department_name
HAVING COUNT(DISTINCT a.employee_id) >= 5;

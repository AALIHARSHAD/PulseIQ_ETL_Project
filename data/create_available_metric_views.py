import duckdb

con = duckdb.connect("/app/data/pulseiq_warehouse.duckdb")

sql_statements = [
"""
CREATE OR REPLACE VIEW metric_m01_headcount AS
SELECT h.month_start_date AS month_start_date,
       strftime(h.month_start_date, '%Y-%m') AS period_year_month,
       h.department_id, d.department_name,
       h.headcount_end AS headcount,
       h.headcount_end AS contributing_employee_count
FROM fact_headcount_monthly h
LEFT JOIN dim_department d USING (department_id)
WHERE h.headcount_end >= 5
""",
"""
CREATE OR REPLACE VIEW metric_m02_hires AS
SELECT h.month_start_date AS month_start_date,
       strftime(h.month_start_date, '%Y-%m') AS period_year_month,
       h.department_id, d.department_name,
       h.hires,
       h.hires AS contributing_employee_count
FROM fact_headcount_monthly h
LEFT JOIN dim_department d USING (department_id)
WHERE h.hires >= 5
""",
"""
CREATE OR REPLACE VIEW metric_m03_exits AS
SELECT h.month_start_date AS month_start_date,
       strftime(h.month_start_date, '%Y-%m') AS period_year_month,
       h.department_id, d.department_name,
       h.exits,
       h.exits AS contributing_employee_count
FROM fact_headcount_monthly h
LEFT JOIN dim_department d USING (department_id)
WHERE h.exits >= 5
""",
"""
CREATE OR REPLACE VIEW metric_m04_attrition_monthly AS
SELECT h.month_start_date AS month_start_date,
       strftime(h.month_start_date, '%Y-%m') AS period_year_month,
       h.department_id, d.department_name,
       100.0 * h.exits / NULLIF(h.headcount_start, 0)
           AS attrition_rate_monthly_pct,
       h.headcount_start AS contributing_employee_count
FROM fact_headcount_monthly h
LEFT JOIN dim_department d USING (department_id)
WHERE h.headcount_start >= 10
""",
"""
CREATE OR REPLACE VIEW metric_m05_attrition_rolling_12m AS
WITH rolling AS (
    SELECT h.*,
           SUM(exits) OVER w AS exits_12m,
           AVG(headcount_end) OVER w AS avg_headcount_12m,
           MIN(headcount_end) OVER w AS min_headcount_12m,
           COUNT(*) OVER w AS months_in_window
    FROM fact_headcount_monthly h
    WINDOW w AS (
        PARTITION BY department_id
        ORDER BY month_start_date
        ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
    )
)
SELECT r.month_start_date,
       strftime(r.month_start_date, '%Y-%m') AS period_year_month,
       r.department_id, d.department_name,
       100.0 * r.exits_12m / NULLIF(r.avg_headcount_12m, 0)
           AS attrition_rate_rolling_12m_pct,
       r.min_headcount_12m AS contributing_employee_count
FROM rolling r
LEFT JOIN dim_department d USING (department_id)
WHERE r.months_in_window = 12
  AND r.min_headcount_12m >= 10
""",
"""
CREATE OR REPLACE VIEW metric_m06_voluntary_attrition AS
WITH rolling AS (
    SELECT h.*,
           SUM(voluntary_exits) OVER w AS voluntary_exits_12m,
           AVG(headcount_end) OVER w AS avg_headcount_12m,
           MIN(headcount_end) OVER w AS min_headcount_12m,
           COUNT(*) OVER w AS months_in_window
    FROM fact_headcount_monthly h
    WINDOW w AS (
        PARTITION BY department_id
        ORDER BY month_start_date
        ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
    )
)
SELECT r.month_start_date,
       strftime(r.month_start_date, '%Y-%m') AS period_year_month,
       r.department_id, d.department_name,
       100.0 * r.voluntary_exits_12m
           / NULLIF(r.avg_headcount_12m, 0)
           AS voluntary_attrition_rate_pct,
       r.min_headcount_12m AS contributing_employee_count
FROM rolling r
LEFT JOIN dim_department d USING (department_id)
WHERE r.months_in_window = 12
  AND r.min_headcount_12m >= 10
""",
"""
CREATE OR REPLACE VIEW metric_m07_gross_pay AS
SELECT p.period_year_month, p.department_id, d.department_name,
       SUM(p.gross_pay) AS gross_pay,
       COUNT(DISTINCT p.employee_id) AS contributing_employee_count
FROM fact_payroll p
LEFT JOIN dim_department d USING (department_id)
WHERE p.period_year_month IS NOT NULL
  AND p.department_id IS NOT NULL
GROUP BY p.period_year_month, p.department_id, d.department_name
HAVING COUNT(DISTINCT p.employee_id) >= 5
""",
"""
CREATE OR REPLACE VIEW metric_m08_net_pay AS
SELECT p.period_year_month, p.department_id, d.department_name,
       SUM(p.net_pay) AS net_pay,
       COUNT(DISTINCT p.employee_id) AS contributing_employee_count
FROM fact_payroll p
LEFT JOIN dim_department d USING (department_id)
WHERE p.period_year_month IS NOT NULL
  AND p.department_id IS NOT NULL
GROUP BY p.period_year_month, p.department_id, d.department_name
HAVING COUNT(DISTINCT p.employee_id) >= 5
""",
"""
CREATE OR REPLACE VIEW metric_m15_lop_days AS
SELECT p.period_year_month, p.department_id, d.department_name,
       SUM(p.lop_days) AS lop_days,
       COUNT(DISTINCT p.employee_id) AS contributing_employee_count
FROM fact_payroll p
LEFT JOIN dim_department d USING (department_id)
WHERE p.period_year_month IS NOT NULL
  AND p.department_id IS NOT NULL
GROUP BY p.period_year_month, p.department_id, d.department_name
HAVING COUNT(DISTINCT p.employee_id) >= 5
"""
]

try:
    for sql in sql_statements:
        con.execute(sql)

    print("Created or replaced 9 metric views.")
    print("\nView row counts:")
    names = [
        "metric_m01_headcount",
        "metric_m02_hires",
        "metric_m03_exits",
        "metric_m04_attrition_monthly",
        "metric_m05_attrition_rolling_12m",
        "metric_m06_voluntary_attrition",
        "metric_m07_gross_pay",
        "metric_m08_net_pay",
        "metric_m15_lop_days"
    ]
    for name in names:
        count = con.execute(
            f"SELECT COUNT(*) FROM {name}"
        ).fetchone()[0]
        print(f"{name}: {count} rows")

finally:
    con.close()

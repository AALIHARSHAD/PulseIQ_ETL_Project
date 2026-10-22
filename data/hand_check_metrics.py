import duckdb

con = duckdb.connect(
    "/app/data/pulseiq_warehouse.duckdb",
    read_only=True
)

checks = [
    (
        "M01 Headcount",
        """
        WITH direct AS (
            SELECT month_start_date, department_id,
                   headcount_end AS expected
            FROM fact_headcount_monthly
            WHERE headcount_end >= 5
        )
        SELECT COUNT(*) AS compared,
               SUM(CASE WHEN ABS(d.expected - v.headcount) > 0.001
                        THEN 1 ELSE 0 END) AS mismatches
        FROM direct d
        JOIN metric_m01_headcount v
          ON d.month_start_date = v.month_start_date
         AND d.department_id = v.department_id
        """
    ),
    (
        "M04 Monthly Attrition",
        """
        WITH direct AS (
            SELECT month_start_date, department_id,
                   100.0 * exits / NULLIF(headcount_start, 0) AS expected
            FROM fact_headcount_monthly
            WHERE headcount_start >= 10
        )
        SELECT COUNT(*) AS compared,
               SUM(CASE WHEN ABS(d.expected - v.attrition_rate_monthly_pct) > 0.01
                        THEN 1 ELSE 0 END) AS mismatches
        FROM direct d
        JOIN metric_m04_attrition_monthly v
          ON d.month_start_date = v.month_start_date
         AND d.department_id = v.department_id
        """
    ),
    (
        "M07 Gross Pay",
        """
        WITH direct AS (
            SELECT p.period_year_month, p.department_id,
                   SUM(p.gross_pay) AS expected
            FROM fact_payroll p
            GROUP BY p.period_year_month, p.department_id
            HAVING COUNT(DISTINCT p.employee_id) >= 5
        )
        SELECT COUNT(*) AS compared,
               SUM(CASE WHEN ABS(d.expected - v.gross_pay) > 0.01
                        THEN 1 ELSE 0 END) AS mismatches
        FROM direct d
        JOIN metric_m07_gross_pay v
          ON d.period_year_month = v.period_year_month
         AND d.department_id = v.department_id
        """
    ),
    (
        "M09 Payroll Cost",
        """
        WITH direct AS (
            SELECT p.period_year_month, p.department_id,
                   SUM(p.employer_cost) AS expected
            FROM fact_payroll p
            GROUP BY p.period_year_month, p.department_id
            HAVING COUNT(DISTINCT p.employee_id) >= 5
        )
        SELECT COUNT(*) AS compared,
               SUM(CASE WHEN ABS(d.expected - v.payroll_cost) > 0.01
                        THEN 1 ELSE 0 END) AS mismatches
        FROM direct d
        JOIN metric_m09_payroll_cost v
          ON d.period_year_month = v.period_year_month
         AND d.department_id = v.department_id
        """
    ),
    (
        "M13 Attendance Rate",
        """
        WITH direct AS (
            SELECT a.period_year_month, a.department_id,
                   (SUM(a.present_days) + 0.5 * SUM(a.half_days_unpaid))
                     / NULLIF(SUM(a.scheduled_days), 0) AS expected
            FROM fact_attendance_monthly a
            GROUP BY a.period_year_month, a.department_id
            HAVING COUNT(DISTINCT a.employee_id) >= 5
        )
        SELECT COUNT(*) AS compared,
               SUM(CASE WHEN ABS(d.expected - v.attendance_rate) > 0.0001
                        THEN 1 ELSE 0 END) AS mismatches
        FROM direct d
        JOIN metric_m13_attendance_rate v
          ON d.period_year_month = v.period_year_month
         AND d.department_id = v.department_id
        """
    ),
]

try:
    print("INDEPENDENT METRIC HAND-CHECKS")
    print("=" * 65)

    for name, sql in checks:
        result = con.execute(sql).fetchone()
        compared, mismatches = result
        mismatches = mismatches or 0
        status = "PASS" if compared > 0 and mismatches == 0 else "CHECK"
        print(
            f"{name}: compared={compared}, "
            f"mismatches={mismatches}, status={status}"
        )
finally:
    con.close()

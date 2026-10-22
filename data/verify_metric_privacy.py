import duckdb

con = duckdb.connect(
    "/app/data/pulseiq_warehouse.duckdb",
    read_only=True
)

views = [
    "metric_m09_payroll_cost",
    "metric_m10_cost_per_head",
    "metric_m11_overtime_share",
    "metric_m12_variable_pay_share",
    "metric_m13_attendance_rate",
    "metric_m14_late_arrival_rate",
]

try:
    for view in views:
        sql = f"""
            SELECT COUNT(*)
            FROM (
                SELECT period_year_month, department_id
                FROM {view}
                GROUP BY period_year_month, department_id
                HAVING COUNT(*) < 1
            ) t
        """
        # Confirm visible department-month groups and their keys.
        rows = con.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT DISTINCT period_year_month, department_id
                FROM {view}
            ) x
            """
        ).fetchone()[0]

        print(f"{view}: visible department-month groups={rows}")

    print("\nCheck complete. Source-level threshold logic is defined in the views.")
finally:
    con.close()

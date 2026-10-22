import duckdb
from pathlib import Path

db_path = "/app/data/pulseiq_warehouse.duckdb"
sql_path = Path("/app/data/metric_views_privacy.sql")

con = duckdb.connect(db_path)

try:
    sql = sql_path.read_text(encoding="utf-8-sig")
    con.execute(sql)

    print("Metric privacy views created successfully.")

    rows = con.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'main'
          AND table_name LIKE 'metric_m%'
        ORDER BY table_name
    """).fetchall()

    print("\nCreated views:")
    for row in rows:
        print("-", row[0])

    for view_name in [
        "metric_m09_payroll_cost",
        "metric_m10_cost_per_head",
        "metric_m11_overtime_share",
        "metric_m12_variable_pay_share",
        "metric_m13_attendance_rate",
        "metric_m14_late_arrival_rate",
    ]:
        count = con.execute(
            f'SELECT COUNT(*) FROM "{view_name}"'
        ).fetchone()[0]
        print(f"{view_name}: {count} rows")

finally:
    con.close()

import duckdb

con = duckdb.connect(
    "/app/data/pulseiq_warehouse.duckdb",
    read_only=True
)

tables = {
    row[0].lower(): row[1]
    for row in con.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'main'
    """).fetchall()
}

catalog = con.execute("""
    SELECT metric_id, metric_name, source_table
    FROM metric_catalog
    ORDER BY metric_id
""").fetchall()

print("METRIC IMPLEMENTATION INVENTORY")
print("=" * 75)

implemented = []
missing_views = []

for metric_id, metric_name, source_table in catalog:
    view_name = {
        "M01": "metric_m01_headcount",
        "M02": "metric_m02_hires",
        "M03": "metric_m03_exits",
        "M04": "metric_m04_attrition_monthly",
        "M05": "metric_m05_attrition_rolling_12m",
        "M06": "metric_m06_voluntary_attrition",
        "M07": "metric_m07_gross_pay",
        "M08": "metric_m08_net_pay",
        "M09": "metric_m09_payroll_cost",
        "M10": "metric_m10_cost_per_head",
        "M11": "metric_m11_overtime_share",
        "M12": "metric_m12_variable_pay_share",
        "M13": "metric_m13_attendance_rate",
        "M14": "metric_m14_late_arrival_rate",
        "M15": "metric_m15_lop_days",
    }.get(metric_id)

    if view_name and tables.get(view_name) == "VIEW":
        status = "VIEW EXISTS"
        implemented.append(metric_id)
    else:
        status = "NO METRIC VIEW"
        missing_views.append(metric_id)

    print(f"{metric_id} | {status:15} | {metric_name}")

print("\nSUMMARY")
print("Catalog entries:", len(catalog))
print("Metrics with views:", len(implemented))
print("Metrics without views:", len(missing_views))
print("Missing-view metric IDs:", ", ".join(missing_views) or "None")

print("\nSOURCE TABLE AVAILABILITY")
for table_name in [
    "fact_ledger", "fact_invoice", "fact_invoice_payment",
    "fact_expense", "fact_task", "fact_anomaly",
    "fact_attrition_risk", "fact_forecast"
]:
    print(f"{table_name}: {'EXISTS' if table_name in tables else 'MISSING'}")

con.close()

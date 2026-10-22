import duckdb
from datetime import datetime, timezone

DB = "/app/data/pulseiq_warehouse.duckdb"
con = duckdb.connect(DB)

results = []

def run_check(check_id, table_name, sql, details):
    count = con.execute(sql).fetchone()[0]
    status = "PASS" if count == 0 else "FAIL"
    results.append((check_id, table_name, count, status, details))
    print(f"{check_id}: {status} | bad_rows={count} | {details}")

# C03: One payroll row per employee/run
run_check(
    "DQ-C03", "fact_payroll",
    """
    SELECT COUNT(*) FROM (
        SELECT employee_id, run_id
        FROM fact_payroll
        GROUP BY employee_id, run_id
        HAVING COUNT(*) > 1
    ) q
    """,
    "Duplicate employee/run combinations"
)

# C04: Payroll employees must exist in employee dimension
run_check(
    "DQ-C04", "fact_payroll",
    """
    SELECT COUNT(*)
    FROM fact_payroll f
    WHERE NOT EXISTS (
        SELECT 1 FROM dim_employee d
        WHERE d.employee_id = f.employee_id
    )
    """,
    "Payroll rows with no matching employee dimension record"
)

# C05: Attendance must not occur after employee exit
run_check(
    "DQ-C05", "fact_attendance_monthly",
    """
    SELECT COUNT(*)
    FROM fact_attendance_monthly a
    WHERE EXISTS (
        SELECT 1
        FROM dim_employee e
        WHERE e.employee_id = a.employee_id
          AND CAST(a.period_end_date AS DATE)
              BETWEEN CAST(e.valid_from AS DATE)
                  AND CAST(e.valid_to AS DATE)
          AND e.exit_date IS NOT NULL
          AND CAST(a.period_end_date AS DATE) >
              CAST(e.exit_date AS DATE)
    )
    """,
    "Attendance rows after recorded employee exit date"
)

# C06: Unpaid absence and payroll LOP days should reconcile
run_check(
    "DQ-C06", "fact_attendance_monthly + fact_payroll",
    """
    SELECT COUNT(*)
    FROM fact_attendance_monthly a
    JOIN (
        SELECT employee_id, period_year_month,
               SUM(lop_days) AS lop_days
        FROM fact_payroll
        GROUP BY employee_id, period_year_month
    ) p
      ON p.employee_id = a.employee_id
     AND p.period_year_month = a.period_year_month
    WHERE ABS(
        CAST(a.unpaid_absence_days AS DOUBLE) -
        CAST(p.lop_days AS DOUBLE)
    ) > 0.5
    """,
    "Employee-month unpaid absence versus LOP differences above 0.5 days"
)

# C10: Leave end date cannot be before start date
run_check(
    "DQ-C10", "fact_leave",
    """
    SELECT COUNT(*)
    FROM fact_leave
    WHERE CAST(end_date AS DATE) < CAST(start_date AS DATE)
    """,
    "Leave requests with end date before start date"
)

# C12: Employee history intervals must not overlap
run_check(
    "DQ-C12", "dim_employee",
    """
    SELECT COUNT(*)
    FROM dim_employee a
    JOIN dim_employee b
      ON a.employee_id = b.employee_id
     AND a.employee_key < b.employee_key
     AND CAST(a.valid_from AS DATE) <= CAST(b.valid_to AS DATE)
     AND CAST(b.valid_from AS DATE) <= CAST(a.valid_to AS DATE)
    """,
    "Overlapping employee history intervals; investigate before changing data"
)

# Record checks whose source tables are absent as NOT_TESTABLE
missing_checks = [
    ("DQ-C01", "fact_ledger", "Ledger source is absent; payroll-to-ledger reconciliation unavailable"),
    ("DQ-C02", "fact_ledger", "Ledger source is absent; journal balance check unavailable"),
    ("DQ-C07", "fact_invoice", "Invoice source is absent from production warehouse"),
    ("DQ-C08", "fact_expense", "Expense source is absent from production warehouse"),
    ("DQ-C09", "fact_task", "Task source is absent from production warehouse"),
    ("DQ-C11", "fact_attrition_risk", "AI risk source is absent from production warehouse"),
    ("DQ-C13", "etl_run_log", "ETL run log table availability must be verified separately"),
    ("DQ-C14", "metric views", "Only M09-M14 privacy views have been tested; full metric coverage is incomplete"),
]

for check_id, table_name, details in missing_checks:
    results.append((check_id, table_name, 0, "NOT_TESTABLE", details))
    print(f"{check_id}: NOT_TESTABLE | {details}")

# Append results without deleting prior history
next_id = con.execute(
    "SELECT COALESCE(MAX(result_id), 0) + 1 FROM dq_results"
).fetchone()[0]

now = datetime.now(timezone.utc).replace(tzinfo=None)

for i, (check_id, table_name, bad_count, status, details) in enumerate(results):
    con.execute("""
        INSERT INTO dq_results
        (result_id, check_id, table_name, bad_row_count, status, run_at, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [next_id + i, check_id, table_name, bad_count, status, now, details])

print("\n--- SAVED DQ RESULTS ---")
print(con.execute("""
    SELECT check_id, table_name, bad_row_count, status
    FROM dq_results
    WHERE run_at = ?
    ORDER BY check_id
""", [now]).fetchdf().to_string(index=False))

con.close()

import duckdb

DB_PATH = "/app/data/pulseiq_warehouse.duckdb"

PRIMARY_KEYS = {
    "dim_date": ["date_key"],
    "dim_employee": ["employee_key"],
    "dim_department": ["department_id"],
    "dim_role": ["role_id"],
    "dim_location": ["work_location"],
    "dim_leave_type": ["leave_type_code"],
    "fact_payroll": ["payroll_item_id"],
    "fact_attendance_monthly": ["attendance_fact_id"],
    "fact_leave": ["leave_request_id"],
    "fact_headcount_monthly": ["date_key", "department_id"],
}

con = duckdb.connect(DB_PATH)

try:
    for table, keys in PRIMARY_KEYS.items():
        columns = ", ".join(f'"{key}"' for key in keys)
        con.execute(
            f'ALTER TABLE "{table}" ADD PRIMARY KEY ({columns})'
        )
        print(f"{table}: PRIMARY KEY added")

    print("\nAll 10 PRIMARY KEY constraints added successfully.")

finally:
    con.close()

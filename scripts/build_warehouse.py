from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CLEAN = DATA / "clean"
DB_PATH = DATA / "pulseiq_warehouse.duckdb"
WORKBOOK = DATA / "PulseIQ_master_dataset.xlsx"

DIMENSIONS = [
    "dim_date",
    "dim_employee",
    "dim_department",
    "dim_role",
    "dim_location",
    "dim_leave_type",
]

FACTS = {
    "fact_payroll": ("payroll.parquet", "payroll_item_id"),
    "fact_attendance_monthly": (
        "attendance.parquet",
        "attendance_fact_id",
    ),
    "fact_leave": ("leave.parquet", "leave_request_id"),
}

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


def load_dataframe(con, table_name, df):
    con.register("source_df", df)
    con.execute(
        f'CREATE OR REPLACE TABLE "{table_name}" AS '
        "SELECT * FROM source_df"
    )
    con.unregister("source_df")


def main():
    if not WORKBOOK.exists():
        raise FileNotFoundError(f"Workbook not found: {WORKBOOK}")

    con = duckdb.connect(str(DB_PATH))

    try:
        # Load dimension tables from the supplied master workbook.
        for table in DIMENSIONS:
            df = pd.read_excel(WORKBOOK, sheet_name=table)
            load_dataframe(con, table, df)
            print(f"{table}: {len(df)} rows loaded")

        # Load ETL-cleaned fact tables.
        for table, (filename, _) in FACTS.items():
            path = CLEAN / filename
            if not path.exists():
                raise FileNotFoundError(f"Clean file not found: {path}")

            df = pd.read_parquet(path)
            load_dataframe(con, table, df)
            print(f"{table}: {len(df)} rows loaded")

        # Headcount is supplied by the workbook; ETL does not
        # currently produce a clean headcount Parquet file.
        headcount = pd.read_excel(
            WORKBOOK, sheet_name="fact_headcount_monthly"
        )
        load_dataframe(con, "fact_headcount_monthly", headcount)
        print(f"fact_headcount_monthly: {len(headcount)} rows loaded")

        # Validate key uniqueness and nulls.
        print("\n--- PRIMARY KEY CHECKS ---")
        for table, keys in PRIMARY_KEYS.items():
            quoted_keys = ", ".join(f'"{key}"' for key in keys)
            null_condition = " OR ".join(
                f'"{key}" IS NULL' for key in keys
            )

            total = con.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            duplicates = con.execute(
                f"""
                SELECT COUNT(*) FROM (
                    SELECT {quoted_keys}
                    FROM "{table}"
                    GROUP BY {quoted_keys}
                    HAVING COUNT(*) > 1
                ) AS duplicate_keys
                """
            ).fetchone()[0]

            nulls = con.execute(
                f'SELECT COUNT(*) FROM "{table}" '
                f"WHERE {null_condition}"
            ).fetchone()[0]

            status = "PASS" if duplicates == 0 and nulls == 0 else "FAIL"
            print(
                f"{table}: {status}; rows={total}, "
                f"duplicate_keys={duplicates}, null_keys={nulls}"
            )

        # Validate employee foreign-key references.
        print("\n--- EMPLOYEE ORPHAN CHECKS ---")
        for table in [
            "fact_payroll",
            "fact_attendance_monthly",
            "fact_leave",
        ]:
            orphan_count = con.execute(
                f"""
                SELECT COUNT(*)
                FROM "{table}" f
                LEFT JOIN dim_employee d
                  ON f.employee_key = d.employee_key
                WHERE d.employee_key IS NULL
                """
            ).fetchone()[0]

            print(f"{table}: employee_key orphans={orphan_count}")

        # Reconcile ETL-produced facts against clean Parquet files.
        print("\n--- ROW COUNT RECONCILIATION ---")
        for table, (filename, _) in FACTS.items():
            expected = len(pd.read_parquet(CLEAN / filename))
            actual = con.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]
            status = "PASS" if actual == expected else "FAIL"
            print(
                f"{table}: {status}; clean_rows={expected}, "
                f"warehouse_rows={actual}"
            )

        print(f"\nWarehouse database: {DB_PATH}")

    finally:
        con.close()


if __name__ == "__main__":
    main()

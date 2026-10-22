import duckdb
import pandas as pd

db_path = "/app/data/pulseiq_warehouse.duckdb"
xlsx_path = "/app/data/PulseIQ_master_dataset.xlsx"

df = pd.read_excel(xlsx_path, sheet_name="dq_checks_catalog")
df.columns = [c.strip().lower() for c in df.columns]

con = duckdb.connect(db_path)

con.execute("""
    CREATE TABLE IF NOT EXISTS dq_check_catalog (
        check_id VARCHAR PRIMARY KEY,
        check_name VARCHAR NOT NULL,
        description VARCHAR,
        logic_sql_or_rule VARCHAR,
        severity VARCHAR,
        tolerance VARCHAR,
        frequency VARCHAR,
        owner VARCHAR,
        fix_guidance VARCHAR
    )
""")

con.register("catalog_df", df)
con.execute("""
    INSERT OR REPLACE INTO dq_check_catalog
    SELECT
        check_id, check_name, description, logic_sql_or_rule,
        severity, CAST(tolerance AS VARCHAR), frequency, owner,
        fix_guidance
    FROM catalog_df
""")

print("Catalog checks loaded:", con.execute(
    "SELECT COUNT(*) FROM dq_check_catalog"
).fetchone()[0])

print(con.execute("""
    SELECT check_id, check_name, severity, frequency
    FROM dq_check_catalog
    ORDER BY check_id
""").fetchdf().to_string(index=False))

con.close()

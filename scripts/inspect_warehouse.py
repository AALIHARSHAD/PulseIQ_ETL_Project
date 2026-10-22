import duckdb
from pathlib import Path

db = Path("data/pulseiq_warehouse.duckdb")

print("Database exists:", db.exists())

if db.exists():
    con = duckdb.connect(str(db), read_only=True)

    tables = con.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_name
    """).fetchall()

    print("\n=== WAREHOUSE TABLES ===")
    for (table,) in tables:
        print(f"\n--- {table} ---")

        columns = con.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'main'
              AND table_name = ?
            ORDER BY ordinal_position
        """, [table]).fetchall()

        for column, dtype in columns:
            print(f"  {column}: {dtype}")

    con.close()

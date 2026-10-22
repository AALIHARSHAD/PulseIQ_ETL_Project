import duckdb

con = duckdb.connect("/app/data/pulseiq_warehouse.duckdb", read_only=True)

print("Latest result for each DQ check:")
print(con.execute("""
    SELECT check_id, table_name, bad_row_count, status, run_at, details
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY check_id
                   ORDER BY run_at DESC, result_id DESC
               ) AS rn
        FROM dq_results
    )
    WHERE rn = 1
    ORDER BY check_id
""").fetchdf().to_string(index=False))

print("\nLatest status counts:")
print(con.execute("""
    SELECT status, COUNT(*) AS check_count
    FROM (
        SELECT check_id, status,
               ROW_NUMBER() OVER (
                   PARTITION BY check_id
                   ORDER BY run_at DESC, result_id DESC
               ) AS rn
        FROM dq_results
    )
    WHERE rn = 1
    GROUP BY status
    ORDER BY status
""").fetchdf().to_string(index=False))

con.close()

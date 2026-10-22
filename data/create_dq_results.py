import duckdb

db_path = "/app/data/pulseiq_warehouse.duckdb"
con = duckdb.connect(db_path)

con.execute("""
    CREATE TABLE IF NOT EXISTS dq_results (
        result_id BIGINT PRIMARY KEY,
        check_id VARCHAR NOT NULL,
        table_name VARCHAR NOT NULL,
        bad_row_count BIGINT NOT NULL,
        status VARCHAR NOT NULL,
        run_at TIMESTAMP NOT NULL,
        details VARCHAR
    )
""")

print("dq_results table created.")
print(con.execute("DESCRIBE dq_results").fetchdf().to_string(index=False))

con.close()

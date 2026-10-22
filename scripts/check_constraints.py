import duckdb

con = duckdb.connect("/app/data/pulseiq_warehouse.duckdb")
query = """
SELECT table_name, constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'main'
ORDER BY table_name
"""
print(con.execute(query).fetchall())
con.close()

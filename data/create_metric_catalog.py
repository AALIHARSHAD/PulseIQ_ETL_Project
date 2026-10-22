from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path("/app")
WORKBOOK = ROOT / "data" / "PulseIQ_master_dataset.xlsx"
DB_PATH = ROOT / "data" / "pulseiq_warehouse.duckdb"

metrics = pd.read_excel(
    WORKBOOK,
    sheet_name="metric_dictionary"
)

expected_columns = [
    "metric_id",
    "metric_name",
    "business_definition",
    "formula",
    "source_table",
    "grain",
    "time_period",
    "owner_team",
    "unit",
    "good_direction",
    "caveat",
    "minimum_group_size",
]

missing = [c for c in expected_columns if c not in metrics.columns]
if missing:
    raise ValueError(f"Missing expected workbook columns: {missing}")

metrics = metrics[expected_columns].copy()
metrics = metrics.astype(object).where(pd.notna(metrics), None)

if metrics["metric_id"].duplicated().any():
    duplicates = metrics.loc[
        metrics["metric_id"].duplicated(keep=False), "metric_id"
    ].tolist()
    raise ValueError(f"Duplicate metric IDs in workbook: {duplicates}")

if len(metrics) != 28:
    raise ValueError(
        f"Expected 28 official metrics, found {len(metrics)}. "
        "Catalog was not created."
    )

con = duckdb.connect(str(DB_PATH))
try:
    existing = con.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'main'
          AND lower(table_name) = 'metric_catalog'
    """).fetchone()[0]

    if existing:
        raise RuntimeError(
            "metric_catalog already exists. Refusing to overwrite it."
        )

    con.register("metric_dictionary_df", metrics)
    con.execute("""
        CREATE TABLE metric_catalog AS
        SELECT * FROM metric_dictionary_df
    """)

    print("Created metric_catalog from official workbook.")
    print("Catalog rows:", con.execute(
        "SELECT COUNT(*) FROM metric_catalog"
    ).fetchone()[0])

    print("\nMetric IDs and names:")
    print(con.execute("""
        SELECT metric_id, metric_name, source_table, minimum_group_size
        FROM metric_catalog
        ORDER BY metric_id
    """).fetchdf().to_string(index=False))

finally:
    con.close()

# PulseIQ - Task 1: ETL pipeline

Extract raw HR exports -> clean with pandas -> validate with pandera -> write clean files + run log.

## Run (one command)
```bash
cp .env.example .env          # optional, defaults work
docker compose run --rm etl   # reads data/raw/*.csv, writes data/clean/, data/rejected/, logs/
docker compose run --rm test  # unit tests
```
Exit code is 0 on success and 1 on any failure (validation, too many rejects, missing file).

## Folders
- `data/raw/` input CSVs (employee, salary, payroll, attendance, leave + department, role, leave_type)
- `data/clean/` cleaned tables (parquet by default)
- `data/rejected/` `rejected_rows.csv`, `corrected_rows.csv`, `validation_failures.csv`
- `logs/` `etl.log`, `run_log.jsonl` (one line per run), `last_run.json`
- `docs/` `metric_dictionary.md`, `decisions.md`
- `scripts/make_raw_exports.py` splits the master workbook into the raw CSVs

## Regenerating raw files
`python scripts/make_raw_exports.py data/PulseIQ_master_dataset.xlsx data/raw`

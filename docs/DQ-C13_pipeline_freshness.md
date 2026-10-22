# DQ-C13 — Pipeline Freshness

## Status
NOT TESTABLE — The required production run-log table is unavailable.

## Rule
The latest successful ETL run must have finished within the last
24 hours. The check is expected to run hourly.

## Previous Run Evidence
A previous investigation recorded the latest successful run as:
- Run identifier: `20261020T073747Z`
- Finish timestamp: `2026-10-20T07:37:49.988429+00:00`
- Result at that check time: PASS, based on the recorded run timestamp.

## Current Limitation
The current production warehouse table inventory does not contain
`etl_run_log`. Therefore, the latest successful run cannot be
independently verified from the warehouse during this check.

The historical PASS does not establish the current pipeline freshness.

## Recommended Action
1. Persist ETL run status and finish timestamps in an accessible run log.
2. Record each run's identifier, status, start time, and finish time.
3. Check the latest successful finish time against the 24-hour limit.
4. Store the current result in `dq_results` after run-log access is restored.

## Conclusion
DQ-C13 remains NOT TESTABLE against the current warehouse because
the required run-log table is unavailable.

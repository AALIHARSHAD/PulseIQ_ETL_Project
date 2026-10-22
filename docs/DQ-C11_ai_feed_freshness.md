# DQ-C11 — AI Feed Freshness

## Status
NOT TESTABLE — Required production data and timestamp fields are unavailable.

## Rule
AI prediction feeds should be fresh:
- Prediction as-of dates should be within 7 days of the batch maximum.
- Scoring and load timestamps should support feed-freshness validation.

## Findings
- The production warehouse does not contain `fact_attrition_risk`.
- The reference data does not provide the batch/scored/loaded timestamp
  columns required to fully verify freshness.

## Limitation
Without the required table and timestamp fields, the age of the latest
AI prediction batch cannot be reliably calculated. This is not evidence
that the feed is fresh or stale.

## Recommended Action
1. Make the production AI prediction table available in the warehouse.
2. Include prediction as-of date, batch identifier, scoring timestamp,
   and load timestamp.
3. Compare the latest batch and prediction dates against the 7-day rule.
4. Record the check result in `dq_results` after the required data exists.

## Conclusion
DQ-C11 remains NOT TESTABLE until the required production data and
timestamp fields are available.

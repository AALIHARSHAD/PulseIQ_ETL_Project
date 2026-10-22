import pandas as pd

metrics = pd.read_excel(
    "data/PulseIQ_master_dataset.xlsx",
    sheet_name="metric_dictionary"
)

print("Official metric thresholds:")
print(
    metrics[
        ["metric_id", "metric_name", "minimum_group_size"]
    ].to_string(index=False)
)

print("\nThresholds missing from the dictionary:")
print(
    metrics.loc[
        metrics["minimum_group_size"].isna(),
        ["metric_id", "metric_name"]
    ].to_string(index=False)
)

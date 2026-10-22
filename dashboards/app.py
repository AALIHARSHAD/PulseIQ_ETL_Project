from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st

DB_PATH = Path("/app/data/pulseiq_warehouse.duckdb")

METRICS = {
    "M01 — Headcount": ("metric_m01_headcount", "headcount", "Employees"),
    "M02 — Hires": ("metric_m02_hires", "hires", "Employees"),
    "M03 — Exits": ("metric_m03_exits", "exits", "Employees"),
    "M04 — Attrition rate (monthly)": (
        "metric_m04_attrition_monthly", "attrition_rate_monthly_pct", "%"
    ),
    "M05 — Attrition rate (rolling 12 months)": (
        "metric_m05_attrition_rolling_12m",
        "attrition_rate_rolling_12m_pct", "%"
    ),
    "M06 — Voluntary attrition rate": (
        "metric_m06_voluntary_attrition", "voluntary_attrition_rate_pct", "%"
    ),
    "M07 — Gross pay": ("metric_m07_gross_pay", "gross_pay", "Currency"),
    "M08 — Net pay": ("metric_m08_net_pay", "net_pay", "Currency"),
    "M09 — Payroll cost": ("metric_m09_payroll_cost", "payroll_cost", "Currency"),
    "M10 — Cost per head": ("metric_m10_cost_per_head", "cost_per_head", "Currency"),
    "M11 — Overtime share": ("metric_m11_overtime_share", "overtime_share_pct", "%"),
    "M12 — Variable pay share": (
        "metric_m12_variable_pay_share", "variable_pay_share_pct", "%"
    ),
    "M13 — Attendance rate": (
        "metric_m13_attendance_rate", "attendance_rate", "Rate"
    ),
    "M14 — Late arrival rate": (
        "metric_m14_late_arrival_rate", "late_arrival_rate", "Rate"
    ),
    "M15 — Leave without pay days": (
        "metric_m15_lop_days", "lop_days", "Days"
    ),
}

st.set_page_config(
    page_title="PulseIQ Workforce Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("PulseIQ Workforce Dashboard")
st.caption(
    "Workforce and payroll insights | Data is read from privacy-filtered metric views."
)

if not DB_PATH.exists():
    st.error("Warehouse database not found. Check the data volume.")
    st.stop()

@st.cache_data(ttl=60)
def load_metric(view_name):
    # View names are selected only from the fixed METRICS mapping above.
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(f'SELECT * FROM "{view_name}"').fetchdf()

metric_label = st.sidebar.selectbox("Choose a metric", list(METRICS))
view_name, value_column, unit = METRICS[metric_label]

try:
    df = load_metric(view_name)
except Exception as exc:
    st.error(f"Could not read metric view: {exc}")
    st.stop()

if df.empty:
    st.warning("This metric has no rows available after privacy filtering.")
    st.stop()

if "period_year_month" not in df.columns:
    st.error("Expected period_year_month column is missing.")
    st.stop()

df["period_year_month"] = df["period_year_month"].astype(str)

departments = sorted(df["department_name"].dropna().unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Department",
    departments,
    default=departments,
    help="Choose one or more departments. Only rows present in the metric view are available.",
)

periods = sorted(df["period_year_month"].dropna().unique().tolist())
if not periods:
    st.warning("No valid reporting periods are available.")
    st.stop()

start_period, end_period = st.sidebar.select_slider(
    "Reporting period",
    options=periods,
    value=(periods[0], periods[-1]),
)

filtered = df[
    df["period_year_month"].between(start_period, end_period)
    & df["department_name"].isin(selected_departments)
].copy()

st.subheader(metric_label)

if filtered.empty:
    st.info("No data matches the selected filters.")
    st.stop()

latest_period = filtered["period_year_month"].max()
latest = filtered[filtered["period_year_month"] == latest_period].copy()

c1, c2, c3 = st.columns(3)
c1.metric("Latest reporting period", latest_period)
c2.metric("Departments shown", latest["department_name"].nunique())
c3.metric("Rows in selection", f"{len(filtered):,}")

st.caption(
    "Values are shown at department and period grain. "
    "Rates are not summed across departments."
)

st.markdown("### Metric trend")

# Plot each department separately so rates are not incorrectly added together.
trend = filtered.pivot_table(
    index="period_year_month",
    columns="department_name",
    values=value_column,
    aggfunc="first",
).sort_index()

st.line_chart(trend, height=360)

st.markdown("### Latest period by department")
display_columns = [
    col for col in [
        "department_name",
        "period_year_month",
        value_column,
        "contributing_employee_count",
    ]
    if col in latest.columns
]

latest_table = latest[display_columns].sort_values("department_name")
st.dataframe(latest_table, use_container_width=True, hide_index=True)

with st.expander("Metric definition and privacy notes"):
    catalog = None
    try:
        with duckdb.connect(str(DB_PATH), read_only=True) as con:
            catalog = con.execute(
                """
                SELECT metric_id, metric_name, business_definition,
                       formula, source_table, grain, caveat,
                       minimum_group_size
                FROM metric_catalog
                WHERE metric_id = ?
                """,
                [metric_label.split(" — ")[0]],
            ).fetchdf()
    except Exception:
        pass

    if catalog is not None and not catalog.empty:
        for _, row in catalog.iterrows():
            st.write("**Business definition:**", row["business_definition"])
            st.write("**Formula:**", row["formula"])
            st.write("**Source:**", row["source_table"])
            st.write("**Grain:**", row["grain"])
            st.write("**Minimum group size (dictionary):**",
                     row["minimum_group_size"])
            st.write("**Caveat:**", row["caveat"])

    st.info(
        "This dashboard queries metric views only. "
        "Metrics M16–M28 are catalogued but do not yet have implemented views "
        "because their required source tables are unavailable in this warehouse. "
        "M08's dictionary threshold is blank; its current view uses a conservative "
        "five-employee filter."
    )

st.caption("PulseIQ | Dashboard refreshes cached metric data every 60 seconds.")

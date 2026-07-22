import streamlit as st
import plotly.express as px
import numpy as np
from utils import load_data, apply_filters, ALERT_COLOR, PRIMARY_COLOR, READMISSION_BENCHMARK

st.set_page_config(page_title="Readmission Deep-Dive", page_icon="🔁", layout="wide")

# ============================================================
# LOAD DATA + APPLY FILTERS
# ============================================================

df_raw = load_data()

if "date_range" not in st.session_state:
    st.session_state["date_range"] = (df_raw["admission_date"].min().date(),
                                       df_raw["admission_date"].max().date())
    st.session_state["departments"] = sorted(df_raw["department"].unique())
    st.session_state["insurance_types"] = sorted(df_raw["insurance_type"].unique())
    st.session_state["age_groups"] = list(df_raw["age_group"].cat.categories)

df = apply_filters(df_raw)

if df.empty:
    st.warning("No data matches the current filter selection.")
    st.stop()

st.title("🔁 Readmission Deep-Dive")
st.markdown("Identifying where and why patients return within 30 days")
st.divider()

# ============================================================
# KPI CARDS
# ============================================================

total_admissions = len(df)
readmission_rate = (df["readmitted_30d"] == "Yes").mean()
readmit_delta = readmission_rate - READMISSION_BENCHMARK

readmitted_revenue = df.loc[df["readmitted_30d"] == "Yes", "total_charges"].sum()
readmitted_count = (df["readmitted_30d"] == "Yes").sum()
avg_readmit_charge = df.loc[df["readmitted_30d"] == "Yes", "total_charges"].mean()
excess_readmissions = max(0, readmitted_count - int(total_admissions * READMISSION_BENCHMARK))
estimated_excess_cost = excess_readmissions * avg_readmit_charge

col1, col2, col3 = st.columns(3)
col1.metric(
    "30-Day Readmission Rate", f"{readmission_rate:.1%}",
    delta=f"{readmit_delta:+.1%} vs. 15% benchmark", delta_color="inverse"
)
col2.metric("Readmitted Patients", f"{readmitted_count:,}")
col3.metric("Estimated Excess Cost", f"IDR {estimated_excess_cost/1e6:,.0f}M",
            help="Estimated cost of readmissions above the 15% benchmark rate")

st.divider()

# ============================================================
# CHART: Readmission Rate by Department (with benchmark line)
# ============================================================

readmit_by_dept = (
    df.groupby("department")["readmitted_30d"]
      .apply(lambda x: (x == "Yes").mean())
      .reset_index(name="readmission_rate")
      .sort_values("readmission_rate", ascending=True)
)

fig_readmit_dept = px.bar(
    readmit_by_dept, x="readmission_rate", y="department", orientation="h",
    title="30-Day Readmission Rate by Department",
    color_discrete_sequence=[ALERT_COLOR], text="readmission_rate"
)
fig_readmit_dept.update_traces(texttemplate="%{text:.1%}", textposition="outside")
fig_readmit_dept.add_vline(
    x=READMISSION_BENCHMARK, line_dash="dash", line_color="gray",
    annotation_text="Benchmark (15%)", annotation_position="top"
)
fig_readmit_dept.update_layout(xaxis_title="Readmission Rate", yaxis_title=None, xaxis_tickformat=".0%")

st.plotly_chart(fig_readmit_dept, use_container_width=True)

# Identify the worst-performing department dynamically for use in the Key Finding below
worst_dept_row = readmit_by_dept.sort_values("readmission_rate", ascending=False).iloc[0]
worst_dept_name = worst_dept_row["department"]
worst_dept_rate = worst_dept_row["readmission_rate"]

# ============================================================
# CHART: Readmission Heatmap — Diagnosis × Department
# ============================================================

readmit_heatmap_data = (
    df.groupby(["department", "diagnosis"])["readmitted_30d"]
      .apply(lambda x: (x == "Yes").mean())
      .reset_index(name="readmission_rate")
      .pivot(index="diagnosis", columns="department", values="readmission_rate")
)

fig_readmit_heatmap = px.imshow(
    readmit_heatmap_data,
    title="Readmission Rate — Diagnosis × Department",
    labels=dict(x="Department", y="Diagnosis", color="Readmission Rate"),
    color_continuous_scale="Reds", aspect="auto", text_auto=".0%"
)
fig_readmit_heatmap.update_layout(xaxis_tickangle=-45, height=600)

st.plotly_chart(fig_readmit_heatmap, use_container_width=True)

# ============================================================
# TWO CHARTS SIDE BY SIDE: Risk Factors (Age Group | Smoker Status)
# ============================================================

col4, col5 = st.columns(2)

with col4:
    readmit_by_age = (
        df.groupby("age_group", observed=True)["readmitted_30d"]
          .apply(lambda x: (x == "Yes").mean())
          .reset_index(name="readmission_rate")
    )
    fig_readmit_age = px.bar(
        readmit_by_age, x="age_group", y="readmission_rate",
        title="Readmission Rate by Age Group",
        color_discrete_sequence=[ALERT_COLOR], text="readmission_rate"
    )
    fig_readmit_age.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig_readmit_age.add_hline(y=READMISSION_BENCHMARK, line_dash="dash", line_color="gray")
    fig_readmit_age.update_layout(xaxis_title=None, yaxis_title="Readmission Rate", yaxis_tickformat=".0%")
    st.plotly_chart(fig_readmit_age, use_container_width=True)

with col5:
    readmit_by_smoker = (
        df.groupby("smoker")["readmitted_30d"]
          .apply(lambda x: (x == "Yes").mean())
          .reset_index(name="readmission_rate")
    )
    fig_readmit_smoker = px.bar(
        readmit_by_smoker, x="smoker", y="readmission_rate",
        title="Readmission Rate by Smoking Status",
        color_discrete_sequence=[ALERT_COLOR], text="readmission_rate"
    )
    fig_readmit_smoker.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig_readmit_smoker.add_hline(y=READMISSION_BENCHMARK, line_dash="dash", line_color="gray")
    fig_readmit_smoker.update_layout(xaxis_title=None, yaxis_title="Readmission Rate", yaxis_tickformat=".0%")
    st.plotly_chart(fig_readmit_smoker, use_container_width=True)

# ============================================================
# TWO CHARTS SIDE BY SIDE: LOS vs Readmission | Emergency Comparison
# ============================================================

col6, col7 = st.columns(2)

with col6:
    fig_los_readmit = px.box(
        df, x="readmitted_30d", y="length_of_stay",
        title="Length of Stay by Readmission Status",
        color="readmitted_30d",
        color_discrete_map={"No": PRIMARY_COLOR, "Yes": ALERT_COLOR},
        points=False
    )
    fig_los_readmit.update_layout(showlegend=False, xaxis_title=None, yaxis_title="LOS (days)")
    st.plotly_chart(fig_los_readmit, use_container_width=True)

with col7:
    emergency_comparison = (
        df.groupby("is_emergency")["readmitted_30d"]
          .apply(lambda x: (x == "Yes").mean())
          .reset_index(name="readmission_rate")
    )
    fig_emergency = px.bar(
        emergency_comparison, x="is_emergency", y="readmission_rate",
        title="Readmission Rate: Emergency vs. Rest",
        color="is_emergency",
        color_discrete_map={"Emergency": ALERT_COLOR, "All Other Departments": PRIMARY_COLOR},
        text="readmission_rate"
    )
    fig_emergency.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig_emergency.add_hline(y=READMISSION_BENCHMARK, line_dash="dash", line_color="gray")
    fig_emergency.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Readmission Rate", yaxis_tickformat=".0%")
    st.plotly_chart(fig_emergency, use_container_width=True)

# ============================================================
# DYNAMIC KEY FINDING — auto-generated from live filtered numbers
# ============================================================

st.divider()
st.subheader("📌 Key Finding")

los_no = df.loc[df["readmitted_30d"] == "No", "length_of_stay"].median()
los_yes = df.loc[df["readmitted_30d"] == "Yes", "length_of_stay"].median()
los_comparison = "shorter" if los_yes < los_no else ("longer" if los_yes > los_no else "similar")

st.info(
    f"The hospital's overall 30-day readmission rate is **{readmission_rate:.1%}**, "
    f"compared to a **15% benchmark**. **{worst_dept_name}** shows the highest departmental "
    f"rate at **{worst_dept_rate:.1%}**. Readmitted patients show a **{los_comparison}** "
    f"median length of stay ({los_yes:.0f} days) than non-readmitted patients ({los_no:.0f} days). "
    f"This is estimated to represent **IDR {estimated_excess_cost/1e6:,.0f}M** in excess costs "
    f"relative to benchmark performance."
)


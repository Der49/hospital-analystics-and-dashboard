import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters, DEPARTMENT_COLORS, PRIMARY_COLOR

st.set_page_config(page_title="Operations & Capacity", page_icon="🏢", layout="wide")

# ============================================================
# LOAD DATA + APPLY FILTERS FROM SESSION STATE
# ============================================================

df_raw = load_data()

# If a user lands directly on this page without visiting Home first,
# session_state won't have filter keys yet — fall back to full dataset
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

st.title("🏢 Operations & Capacity")
st.markdown("Where hospital resources and bed-days are being consumed")
st.divider()

# ============================================================
# CHART: LOS by Department (Box Plot)
# ============================================================

fig_los_dept = px.box(
    df, x="department", y="length_of_stay",
    title="Length of Stay Distribution by Department",
    color="department", color_discrete_map=DEPARTMENT_COLORS,
    points=False
)
fig_los_dept.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Length of Stay (days)")

st.plotly_chart(fig_los_dept, use_container_width=True)

# ============================================================
# CHART: Admissions Heatmap — Month × Department
# ============================================================

df["month"] = df["admission_date"].dt.to_period("M").astype(str)

heatmap_data = (
    df.groupby(["month", "department"])
      .size()
      .reset_index(name="admissions")
      .pivot(index="department", columns="month", values="admissions")
      .fillna(0)
)

fig_heatmap = px.imshow(
    heatmap_data,
    title="Admissions Heatmap — Department × Month",
    labels=dict(x="Month", y="Department", color="Admissions"),
    color_continuous_scale="Teal",
    aspect="auto"
)
fig_heatmap.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_heatmap, use_container_width=True)

# ============================================================
# TWO CHARTS SIDE BY SIDE: Bed-Days by Department | Weekday Pattern
# ============================================================

col1, col2 = st.columns(2)

with col1:
    bed_days = (
        df.groupby("department")["length_of_stay"]
          .sum().reset_index(name="total_bed_days")
          .sort_values("total_bed_days", ascending=True)
    )
    fig_beddays = px.bar(
        bed_days, x="total_bed_days", y="department", orientation="h",
        title="Total Bed-Days by Department",
        color="department", color_discrete_map=DEPARTMENT_COLORS, text="total_bed_days"
    )
    fig_beddays.update_layout(showlegend=False, xaxis_title="Bed-Days", yaxis_title=None)
    fig_beddays.update_traces(textposition="outside")
    st.plotly_chart(fig_beddays, use_container_width=True)

with col2:
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_counts = (
        df["admission_date"].dt.day_name()
          .value_counts().reindex(weekday_order).reset_index()
    )
    weekday_counts.columns = ["weekday", "admissions"]

    fig_weekday = px.bar(
        weekday_counts, x="weekday", y="admissions",
        title="Admissions by Day of Week",
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    fig_weekday.update_layout(xaxis_title=None, yaxis_title="Admissions")
    st.plotly_chart(fig_weekday, use_container_width=True)

# ============================================================
# TWO CHARTS SIDE BY SIDE: Diagnosis Volume | LOS by Diagnosis
# ============================================================

col3, col4 = st.columns(2)

with col3:
    diagnosis_counts = (
        df["diagnosis"].value_counts().reset_index()
    )
    diagnosis_counts.columns = ["diagnosis", "admissions"]
    diagnosis_counts = diagnosis_counts.sort_values("admissions", ascending=True)

    fig_diag_volume = px.bar(
        diagnosis_counts, x="admissions", y="diagnosis", orientation="h",
        title="Admission Volume by Diagnosis",
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    fig_diag_volume.update_layout(yaxis_title=None, xaxis_title="Admissions")
    st.plotly_chart(fig_diag_volume, use_container_width=True)

with col4:
    los_by_diagnosis = (
        df.groupby("diagnosis")["length_of_stay"]
          .mean().round(1).reset_index()
          .sort_values("length_of_stay", ascending=True)
    )
    fig_los_diag = px.bar(
        los_by_diagnosis, x="length_of_stay", y="diagnosis", orientation="h",
        title="Average LOS by Diagnosis",
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    fig_los_diag.update_layout(yaxis_title=None, xaxis_title="Avg LOS (days)")
    st.plotly_chart(fig_los_diag, use_container_width=True)

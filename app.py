# app.py

import streamlit as st
from utils import load_data, apply_filters, DEPARTMENT_COLORS, PRIMARY_COLOR, ALERT_COLOR, READMISSION_BENCHMARK

st.set_page_config(
    page_title="Hospital Operations & Quality Dashboard",
    page_icon="🏥",
    layout="wide"
)

df_raw = load_data()

# ============================================================
# SIDEBAR — GLOBAL FILTERS (persist across all pages via session_state)
# ============================================================

st.sidebar.title("🏥 Hospital Dashboard")
st.sidebar.markdown("Filters apply across every page.")

min_date = df_raw["admission_date"].min().date()
max_date = df_raw["admission_date"].max().date()

st.session_state["date_range"] = st.sidebar.date_input(
    "Admission Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

st.session_state["departments"] = st.sidebar.multiselect(
    "Department",
    options=sorted(df_raw["department"].unique()),
    default=sorted(df_raw["department"].unique())
)

st.session_state["insurance_types"] = st.sidebar.multiselect(
    "Insurance Type",
    options=sorted(df_raw["insurance_type"].unique()),
    default=sorted(df_raw["insurance_type"].unique())
)

st.session_state["age_groups"] = st.sidebar.multiselect(
    "Age Group",
    options=list(df_raw["age_group"].cat.categories),
    default=list(df_raw["age_group"].cat.categories)
)

st.sidebar.divider()
st.sidebar.caption("Data: Jan 2023 – Jan 2025 | Synthetic hospital dataset")

# Apply filters — every page will call apply_filters(df_raw) the same way
df = apply_filters(df_raw)

if df.empty:
    st.warning("No data matches the current filter selection. Try widening your filters.")
    st.stop()

import plotly.express as px

# ============================================================
# PAGE HEADER
# ============================================================

st.title("🏥 Hospital Operations & Quality Dashboard")
st.markdown("**Executive Overview** — hospital-wide performance at a glance")
st.divider()

# ============================================================
# KPI CARDS
# ============================================================

total_admissions = len(df)
total_revenue = df["total_charges"].sum()
avg_los = df["length_of_stay"].mean()
avg_charge = df["total_charges"].mean()
readmission_rate = (df["readmitted_30d"] == "Yes").mean()
readmit_delta = readmission_rate - READMISSION_BENCHMARK

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Admissions", f"{total_admissions:,}")
col2.metric("Total Revenue", f"IDR {total_revenue/1e9:.2f}B")
col3.metric("Avg Length of Stay", f"{avg_los:.1f} days")
col4.metric("Avg Charge / Stay", f"IDR {avg_charge/1e6:.1f}M")
col5.metric(
    "30-Day Readmission Rate",
    f"{readmission_rate:.1%}",
    delta=f"{readmit_delta:+.1%} vs. benchmark",
    delta_color="inverse"  # red when ABOVE benchmark, since higher readmission = worse
)

st.divider()

# ============================================================
# CHARTS
# ============================================================

chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    monthly_trend = (
        df.set_index("admission_date")
          .resample("ME")
          .agg(admissions=("patient_id", "count"))
          .reset_index()
    )

    fig_trend = px.line(
        monthly_trend, x="admission_date", y="admissions",
        title="Monthly Admissions Trend",
        markers=True
    )
    fig_trend.update_traces(line_color=PRIMARY_COLOR, line_width=2.5)
    fig_trend.update_layout(hovermode="x unified", xaxis_title=None, yaxis_title="Admissions")

    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col2:
    payer_mix = df["insurance_type"].value_counts().reset_index()
    payer_mix.columns = ["insurance_type", "stays"]

    fig_payer = px.pie(
        payer_mix, values="stays", names="insurance_type",
        title="Payer Mix", hole=0.5
    )
    fig_payer.update_traces(textinfo="label+percent", textposition="outside")
    fig_payer.update_layout(showlegend=False)

    st.plotly_chart(fig_payer, use_container_width=True)

dept_counts = df["department"].value_counts().reset_index()
dept_counts.columns = ["department", "admissions"]
dept_counts = dept_counts.sort_values("admissions", ascending=True)

fig_dept = px.bar(
    dept_counts, x="admissions", y="department", orientation="h",
    title="Admissions by Department",
    color="department", color_discrete_map=DEPARTMENT_COLORS,
    text="admissions"
)
fig_dept.update_layout(showlegend=False, xaxis_title="Admissions", yaxis_title=None)
fig_dept.update_traces(textposition="outside")

st.plotly_chart(fig_dept, use_container_width=True)

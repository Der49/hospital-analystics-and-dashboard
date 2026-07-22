import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters, DEPARTMENT_COLORS, PRIMARY_COLOR

st.set_page_config(page_title="Revenue & Payer Mix", page_icon="💰", layout="wide")

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

st.title("💰 Revenue & Payer Mix")
st.markdown("Financial performance across departments, diagnoses, and payer types")
st.divider()

# ============================================================
# CHART: Monthly Revenue Trend
# ============================================================

monthly_revenue = (
    df.set_index("admission_date")
      .resample("ME")
      .agg(revenue=("total_charges", "sum"))
      .reset_index()
)

fig_revenue_trend = px.line(
    monthly_revenue, x="admission_date", y="revenue",
    title="Monthly Revenue Trend",
    markers=True
)
fig_revenue_trend.update_traces(line_color=PRIMARY_COLOR, line_width=2.5)
fig_revenue_trend.update_layout(hovermode="x unified", xaxis_title=None, yaxis_title="Revenue (IDR)")

st.plotly_chart(fig_revenue_trend, use_container_width=True)

# ============================================================
# REVENUE BY DEPARTMENT — WITH LIVE TOGGLE (Total vs Average)
# ============================================================

view_mode = st.radio(
    "View department revenue as:",
    options=["Total Revenue", "Average Revenue per Stay"],
    horizontal=True
)

dept_revenue = (
    df.groupby("department")["total_charges"]
      .agg(total_revenue="sum", avg_revenue="mean")
      .reset_index()
)

value_col = "total_revenue" if view_mode == "Total Revenue" else "avg_revenue"
dept_revenue_sorted = dept_revenue.sort_values(value_col, ascending=True)

fig_dept_revenue = px.bar(
    dept_revenue_sorted, x=value_col, y="department", orientation="h",
    title=f"{view_mode} by Department",
    color="department", color_discrete_map=DEPARTMENT_COLORS,
    text=value_col
)
fig_dept_revenue.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig_dept_revenue.update_layout(showlegend=False, xaxis_title="Revenue (IDR)", yaxis_title=None)

st.plotly_chart(fig_dept_revenue, use_container_width=True)

# ============================================================
# TWO CHARTS SIDE BY SIDE: Charge/Day by Dept | Insurance Comparison
# ============================================================

col1, col2 = st.columns(2)

with col1:
    charge_per_day_dept = (
        df.groupby("department")["charge_per_day"]
          .mean().round(0).reset_index()
          .sort_values("charge_per_day", ascending=True)
    )
    fig_charge_day = px.bar(
        charge_per_day_dept, x="charge_per_day", y="department", orientation="h",
        title="Avg Charge per Day by Department",
        color_discrete_sequence=[PRIMARY_COLOR], text="charge_per_day"
    )
    fig_charge_day.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_charge_day.update_layout(xaxis_title="IDR / day", yaxis_title=None)
    st.plotly_chart(fig_charge_day, use_container_width=True)

with col2:
    insurance_stats = (
        df.groupby("insurance_type")
          .agg(avg_charges=("total_charges", "mean"))
          .round(0).reset_index()
          .sort_values("avg_charges", ascending=True)
    )
    fig_insurance = px.bar(
        insurance_stats, x="avg_charges", y="insurance_type", orientation="h",
        title="Avg Charges by Insurance Type",
        color_discrete_sequence=[PRIMARY_COLOR], text="avg_charges"
    )
    fig_insurance.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_insurance.update_layout(xaxis_title="IDR", yaxis_title=None)
    st.plotly_chart(fig_insurance, use_container_width=True)

# ============================================================
# CHART: Revenue by Diagnosis (Treemap)
# ============================================================

diagnosis_revenue = (
    df.groupby("diagnosis")["total_charges"]
      .sum().reset_index(name="total_revenue")
      .sort_values("total_revenue", ascending=False)
)

fig_treemap = px.treemap(
    diagnosis_revenue, path=["diagnosis"], values="total_revenue",
    title="Revenue Share by Diagnosis",
    color="total_revenue", color_continuous_scale="Teal"
)
fig_treemap.update_traces(textinfo="label+percent root")

st.plotly_chart(fig_treemap, use_container_width=True)


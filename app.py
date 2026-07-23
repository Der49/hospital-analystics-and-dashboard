import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, DEPARTMENT_COLORS, PRIMARY_COLOR, ALERT_COLOR, READMISSION_BENCHMARK

st.set_page_config(page_title="Hospital Operations & Quality Dashboard", page_icon="🏥", layout="wide")

df_raw = load_data()

st.title("🏥 Hospital Operations & Quality Dashboard")

# ============================================================
# FILTER BAR — aligned labels + widgets, no extra caption text
# ============================================================

f1, f2, f3, f4 = st.columns([2, 1, 1, 1])

with f1:
    st.markdown("**📅 Admission Date Range**")
    min_date = df_raw["admission_date"].min().date()
    max_date = df_raw["admission_date"].max().date()
    date_range = st.date_input(
        "Admission Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

with f2:
    st.markdown("**🏢 Department**")
    with st.popover("Select department(s)", use_container_width=True):
        departments = st.multiselect(
            "Select department(s)",
            options=sorted(df_raw["department"].unique()),
            default=sorted(df_raw["department"].unique()),
            label_visibility="collapsed"
        )

with f3:
    st.markdown("**💳 Insurance**")
    with st.popover("Select insurance type(s)", use_container_width=True):
        insurance_types = st.multiselect(
            "Select insurance type(s)",
            options=sorted(df_raw["insurance_type"].unique()),
            default=sorted(df_raw["insurance_type"].unique()),
            label_visibility="collapsed"
        )

with f4:
    st.markdown("**🧍 Age Group**")
    with st.popover("Select age group(s)", use_container_width=True):
        age_groups = st.multiselect(
            "Select age group(s)",
            options=list(df_raw["age_group"].cat.categories),
            default=list(df_raw["age_group"].cat.categories),
            label_visibility="collapsed"
        )

# Handle edge case: date_input returns a single date if user clears one side of the range
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# ============================================================
# APPLY FILTERS
# ============================================================

df = df_raw[
    (df_raw["admission_date"] >= pd.Timestamp(start_date)) &
    (df_raw["admission_date"] <= pd.Timestamp(end_date)) &
    (df_raw["department"].isin(departments)) &
    (df_raw["insurance_type"].isin(insurance_types)) &
    (df_raw["age_group"].isin(age_groups))
]

if df.empty:
    st.warning("No data matches the current filter selection. Try widening your filters.")
    st.stop()

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "🏢 Operations", "💰 Revenue", "🔁 Patient Safety", "🧍 Patient Profile"]
)

# ============================================================
# TAB 1: EXECUTIVE OVERVIEW
# ============================================================
with tab1:
    total_admissions = len(df)
    total_revenue = df["total_charges"].sum()
    avg_los = df["length_of_stay"].mean()
    avg_charge = df["total_charges"].mean()
    readmission_rate = (df["readmitted_30d"] == "Yes").mean()
    readmit_delta = readmission_rate - READMISSION_BENCHMARK

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Admissions", f"{total_admissions:,}")
    k2.metric("Total Revenue", f"IDR {total_revenue/1e9:.2f}B")
    k3.metric("Average Length of Stay", f"{avg_los:.1f} days")
    k4.metric("Average Charge per Stay", f"IDR {avg_charge/1e6:.1f}M")
    k5.metric(
        "30-Day Readmission Rate", f"{readmission_rate:.1%}",
        delta=f"{readmit_delta:+.1%} vs. benchmark", delta_color="inverse",
        help="Positive delta means the readmission rate is above the 15% benchmark (worse)."
    )

    st.divider()

    c1, c2 = st.columns([2, 1])
    with c1:
        monthly_trend = (
            df.set_index("admission_date").resample("ME")
              .agg(admissions=("patient_id", "count")).reset_index()
        )
        fig_trend = px.line(monthly_trend, x="admission_date", y="admissions",
                             title="Monthly Admissions Trend", markers=True)
        fig_trend.update_traces(line_color=PRIMARY_COLOR, line_width=2.5)
        fig_trend.update_layout(hovermode="x unified", xaxis_title=None, yaxis_title="Admissions")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        payer_mix = df["insurance_type"].value_counts().reset_index()
        payer_mix.columns = ["insurance_type", "stays"]
        fig_payer = px.pie(payer_mix, values="stays", names="insurance_type",
                            title="Payer Mix", hole=0.5)
        fig_payer.update_traces(textinfo="label+percent", textposition="outside")
        fig_payer.update_layout(showlegend=False)
        st.plotly_chart(fig_payer, use_container_width=True)

    dept_counts = df["department"].value_counts().reset_index()
    dept_counts.columns = ["department", "admissions"]
    dept_counts = dept_counts.sort_values("admissions", ascending=True)
    fig_dept = px.bar(dept_counts, x="admissions", y="department", orientation="h",
                       title="Admissions by Department", color="department",
                       color_discrete_map=DEPARTMENT_COLORS, text="admissions")
    fig_dept.update_layout(showlegend=False, xaxis_title="Admissions", yaxis_title=None)
    fig_dept.update_traces(textposition="outside")
    st.plotly_chart(fig_dept, use_container_width=True)


# ============================================================
# TAB 2: OPERATIONS & CAPACITY
# ============================================================
with tab2:
    fig_los_dept = px.box(df, x="department", y="length_of_stay",
                           title="Length of Stay Distribution by Department",
                           color="department", color_discrete_map=DEPARTMENT_COLORS, points=False)
    fig_los_dept.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Length of Stay (days)")
    st.plotly_chart(fig_los_dept, use_container_width=True)

    df_month = df.copy()
    df_month["month"] = df_month["admission_date"].dt.to_period("M").astype(str)
    heatmap_data = (
        df_month.groupby(["month", "department"]).size().reset_index(name="admissions")
                .pivot(index="department", columns="month", values="admissions").fillna(0)
    )
    fig_heatmap = px.imshow(heatmap_data, title="Admissions Heatmap — Department × Month",
                             labels=dict(x="Month", y="Department", color="Admissions"),
                             color_continuous_scale="Teal", aspect="auto")
    fig_heatmap.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        bed_days = (df.groupby("department")["length_of_stay"].sum()
                      .reset_index(name="total_bed_days").sort_values("total_bed_days", ascending=True))
        fig_beddays = px.bar(bed_days, x="total_bed_days", y="department", orientation="h",
                              title="Total Bed-Days by Department", color="department",
                              color_discrete_map=DEPARTMENT_COLORS, text="total_bed_days")
        fig_beddays.update_layout(showlegend=False, xaxis_title="Bed-Days", yaxis_title=None)
        fig_beddays.update_traces(textposition="outside")
        st.plotly_chart(fig_beddays, use_container_width=True)

    with col2:
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_counts = (df["admission_date"].dt.day_name().value_counts()
                           .reindex(weekday_order).reset_index())
        weekday_counts.columns = ["weekday", "admissions"]
        fig_weekday = px.bar(weekday_counts, x="weekday", y="admissions",
                              title="Admissions by Day of Week", color_discrete_sequence=[PRIMARY_COLOR])
        fig_weekday.update_layout(xaxis_title=None, yaxis_title="Admissions")
        st.plotly_chart(fig_weekday, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        diagnosis_counts = df["diagnosis"].value_counts().reset_index()
        diagnosis_counts.columns = ["diagnosis", "admissions"]
        diagnosis_counts = diagnosis_counts.sort_values("admissions", ascending=True)
        fig_diag_volume = px.bar(diagnosis_counts, x="admissions", y="diagnosis", orientation="h",
                                  title="Admission Volume by Diagnosis", color_discrete_sequence=[PRIMARY_COLOR])
        fig_diag_volume.update_layout(yaxis_title=None, xaxis_title="Admissions")
        st.plotly_chart(fig_diag_volume, use_container_width=True)

    with col4:
        los_by_diagnosis = (df.groupby("diagnosis")["length_of_stay"].mean().round(1)
                             .reset_index().sort_values("length_of_stay", ascending=True))
        fig_los_diag = px.bar(los_by_diagnosis, x="length_of_stay", y="diagnosis", orientation="h",
                               title="Average LOS by Diagnosis", color_discrete_sequence=[PRIMARY_COLOR])
        fig_los_diag.update_layout(yaxis_title=None, xaxis_title="Avg LOS (days)")
        st.plotly_chart(fig_los_diag, use_container_width=True)


# ============================================================
# TAB 3: REVENUE & PAYER MIX
# ============================================================
with tab3:
    monthly_revenue = (df.set_index("admission_date").resample("ME")
                         .agg(revenue=("total_charges", "sum")).reset_index())
    fig_revenue_trend = px.line(monthly_revenue, x="admission_date", y="revenue",
                                 title="Monthly Revenue Trend", markers=True)
    fig_revenue_trend.update_traces(line_color=PRIMARY_COLOR, line_width=2.5)
    fig_revenue_trend.update_layout(hovermode="x unified", xaxis_title=None, yaxis_title="Revenue (IDR)")
    st.plotly_chart(fig_revenue_trend, use_container_width=True)

    view_mode = st.radio("View department revenue as:",
                          options=["Total Revenue", "Average Revenue per Stay"], horizontal=True)
    dept_revenue = (df.groupby("department")["total_charges"]
                     .agg(total_revenue="sum", avg_revenue="mean").reset_index())
    value_col = "total_revenue" if view_mode == "Total Revenue" else "avg_revenue"
    dept_revenue_sorted = dept_revenue.sort_values(value_col, ascending=True)
    fig_dept_revenue = px.bar(dept_revenue_sorted, x=value_col, y="department", orientation="h",
                               title=f"{view_mode} by Department", color="department",
                               color_discrete_map=DEPARTMENT_COLORS, text=value_col)
    fig_dept_revenue.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_dept_revenue.update_layout(showlegend=False, xaxis_title="Revenue (IDR)", yaxis_title=None)
    st.plotly_chart(fig_dept_revenue, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        charge_per_day_dept = (df.groupby("department")["charge_per_day"].mean().round(0)
                                .reset_index().sort_values("charge_per_day", ascending=True))
        fig_charge_day = px.bar(charge_per_day_dept, x="charge_per_day", y="department", orientation="h",
                                 title="Average Charge per Day by Department",
                                 color_discrete_sequence=[PRIMARY_COLOR], text="charge_per_day")
        fig_charge_day.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_charge_day.update_layout(xaxis_title="IDR / day", yaxis_title=None)
        st.plotly_chart(fig_charge_day, use_container_width=True)

    with col2:
        insurance_stats = (df.groupby("insurance_type").agg(avg_charges=("total_charges", "mean"))
                            .round(0).reset_index().sort_values("avg_charges", ascending=True))
        fig_insurance = px.bar(insurance_stats, x="avg_charges", y="insurance_type", orientation="h",
                                title="Average Charges by Insurance Type",
                                color_discrete_sequence=[PRIMARY_COLOR], text="avg_charges")
        fig_insurance.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_insurance.update_layout(xaxis_title="IDR", yaxis_title=None)
        st.plotly_chart(fig_insurance, use_container_width=True)

    # --- Revenue Concentration by Diagnosis: Pareto chart (upgraded from treemap) ---
    diagnosis_revenue = (df.groupby("diagnosis")["total_charges"].sum()
                          .reset_index(name="total_revenue")
                          .sort_values("total_revenue", ascending=False))
    diagnosis_revenue["cum_pct"] = (
        diagnosis_revenue["total_revenue"].cumsum() / diagnosis_revenue["total_revenue"].sum() * 100
    )

    fig_pareto = go.Figure()
    fig_pareto.add_bar(
        x=diagnosis_revenue["diagnosis"], y=diagnosis_revenue["total_revenue"],
        name="Revenue", marker_color=PRIMARY_COLOR
    )
    fig_pareto.add_scatter(
        x=diagnosis_revenue["diagnosis"], y=diagnosis_revenue["cum_pct"],
        name="Cumulative %", mode="lines+markers",
        line=dict(color=ALERT_COLOR, width=2.5), yaxis="y2"
    )
    fig_pareto.update_layout(
        title="Revenue Concentration by Diagnosis (Pareto Analysis)",
        xaxis=dict(title=None, tickangle=-45),
        yaxis=dict(title="Total Revenue (IDR)"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105], ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig_pareto, use_container_width=True)


# ============================================================
# TAB 4: PATIENT SAFETY (READMISSION DEEP-DIVE)
# ============================================================
with tab4:
    total_admissions_t4 = len(df)
    readmission_rate = (df["readmitted_30d"] == "Yes").mean()
    readmit_delta = readmission_rate - READMISSION_BENCHMARK
    readmitted_count = (df["readmitted_30d"] == "Yes").sum()
    avg_readmit_charge = df.loc[df["readmitted_30d"] == "Yes", "total_charges"].mean()
    excess_readmissions = max(0, readmitted_count - int(total_admissions_t4 * READMISSION_BENCHMARK))
    estimated_excess_cost = excess_readmissions * avg_readmit_charge

    k1, k2, k3 = st.columns(3)
    k1.metric("30-Day Readmission Rate", f"{readmission_rate:.1%}",
              delta=f"{readmit_delta:+.1%} vs. 15% benchmark", delta_color="inverse")
    k2.metric("Readmitted Patients", f"{readmitted_count:,}")
    k3.metric("Estimated Excess Cost", f"IDR {estimated_excess_cost/1e6:,.0f}M",
              help="Estimated cost of readmissions above the 15% benchmark rate")

    st.divider()

    readmit_by_dept = (df.groupby("department")["readmitted_30d"]
                        .apply(lambda x: (x == "Yes").mean())
                        .reset_index(name="readmission_rate").sort_values("readmission_rate", ascending=True))
    fig_readmit_dept = px.bar(readmit_by_dept, x="readmission_rate", y="department", orientation="h",
                               title="30-Day Readmission Rate by Department",
                               color_discrete_sequence=[ALERT_COLOR], text="readmission_rate")
    fig_readmit_dept.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig_readmit_dept.add_vline(x=READMISSION_BENCHMARK, line_dash="dash", line_color="gray",
                                annotation_text="Benchmark (15%)", annotation_position="top")
    fig_readmit_dept.update_layout(xaxis_title="Readmission Rate", yaxis_title=None, xaxis_tickformat=".0%")
    st.plotly_chart(fig_readmit_dept, use_container_width=True)

    readmit_heatmap_data = (df.groupby(["department", "diagnosis"])["readmitted_30d"]
                             .apply(lambda x: (x == "Yes").mean()).reset_index(name="readmission_rate")
                             .pivot(index="diagnosis", columns="department", values="readmission_rate"))
    fig_readmit_heatmap = px.imshow(readmit_heatmap_data, title="Readmission Rate — Diagnosis × Department",
                                     labels=dict(x="Department", y="Diagnosis", color="Readmission Rate"),
                                     color_continuous_scale="Reds", aspect="auto", text_auto=".0%")
    fig_readmit_heatmap.update_layout(xaxis_tickangle=-45, height=600)
    st.plotly_chart(fig_readmit_heatmap, use_container_width=True)

    col4, col5 = st.columns(2)
    with col4:
        readmit_by_age = (df.groupby("age_group", observed=True)["readmitted_30d"]
                           .apply(lambda x: (x == "Yes").mean()).reset_index(name="readmission_rate"))
        fig_readmit_age = px.bar(readmit_by_age, x="age_group", y="readmission_rate",
                                  title="Readmission Rate by Age Group",
                                  color_discrete_sequence=[ALERT_COLOR], text="readmission_rate")
        fig_readmit_age.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_readmit_age.add_hline(y=READMISSION_BENCHMARK, line_dash="dash", line_color="gray")
        fig_readmit_age.update_layout(xaxis_title=None, yaxis_title="Readmission Rate", yaxis_tickformat=".0%")
        st.plotly_chart(fig_readmit_age, use_container_width=True)

    with col5:
        readmit_by_smoker = (df.groupby("smoker")["readmitted_30d"]
                              .apply(lambda x: (x == "Yes").mean()).reset_index(name="readmission_rate"))
        fig_readmit_smoker = px.bar(readmit_by_smoker, x="smoker", y="readmission_rate",
                                     title="Readmission Rate by Smoking Status",
                                     color_discrete_sequence=[ALERT_COLOR], text="readmission_rate")
        fig_readmit_smoker.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_readmit_smoker.add_hline(y=READMISSION_BENCHMARK, line_dash="dash", line_color="gray")
        fig_readmit_smoker.update_layout(xaxis_title=None, yaxis_title="Readmission Rate", yaxis_tickformat=".0%")
        st.plotly_chart(fig_readmit_smoker, use_container_width=True)

    col6, col7 = st.columns(2)
    with col6:
        fig_los_readmit = px.box(df, x="readmitted_30d", y="length_of_stay",
                                  title="Length of Stay by Readmission Status", color="readmitted_30d",
                                  color_discrete_map={"No": PRIMARY_COLOR, "Yes": ALERT_COLOR}, points=False)
        fig_los_readmit.update_layout(showlegend=False, xaxis_title=None, yaxis_title="LOS (days)")
        st.plotly_chart(fig_los_readmit, use_container_width=True)

    with col7:
        emergency_comparison = (df.groupby("is_emergency")["readmitted_30d"]
                                 .apply(lambda x: (x == "Yes").mean()).reset_index(name="readmission_rate"))
        fig_emergency = px.bar(emergency_comparison, x="is_emergency", y="readmission_rate",
                                title="Readmission Rate: Emergency vs. Rest", color="is_emergency",
                                color_discrete_map={"Emergency": ALERT_COLOR, "All Other Departments": PRIMARY_COLOR},
                                text="readmission_rate")
        fig_emergency.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_emergency.add_hline(y=READMISSION_BENCHMARK, line_dash="dash", line_color="gray")
        fig_emergency.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Readmission Rate", yaxis_tickformat=".0%")
        st.plotly_chart(fig_emergency, use_container_width=True)


# ============================================================
# TAB 5: PATIENT PROFILE (DEMOGRAPHICS & RISK FACTORS)
# ============================================================
with tab5:
    fig_age_dist = px.histogram(df, x="age", color="age_group", title="Patient Age Distribution",
                                 nbins=40, color_discrete_sequence=px.colors.sequential.Teal)
    fig_age_dist.update_layout(xaxis_title="Age", yaxis_title="Number of Patients",
                                legend_title="Age Group", bargap=0.05)
    st.plotly_chart(fig_age_dist, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_bmi_dept = px.box(df, x="department", y="bmi", title="BMI Distribution by Department",
                               color="department", color_discrete_map=DEPARTMENT_COLORS, points=False)
        fig_bmi_dept.update_layout(showlegend=False, xaxis_title=None, yaxis_title="BMI")
        st.plotly_chart(fig_bmi_dept, use_container_width=True)

    with col2:
        smoker_by_dept = (df.groupby("department")["smoker"].apply(lambda x: (x == "Yes").mean())
                           .reset_index(name="smoker_pct").sort_values("smoker_pct", ascending=True))
        fig_smoker_dept = px.bar(smoker_by_dept, x="smoker_pct", y="department", orientation="h",
                                  title="Smoker Percentage by Department",
                                  color_discrete_sequence=[PRIMARY_COLOR], text="smoker_pct")
        fig_smoker_dept.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_smoker_dept.update_layout(xaxis_title="% Smokers", yaxis_title=None, xaxis_tickformat=".0%")
        st.plotly_chart(fig_smoker_dept, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        gender_counts = df["gender"].value_counts().reset_index()
        gender_counts.columns = ["gender", "count"]
        fig_gender = px.pie(gender_counts, values="count", names="gender", title="Patient Gender Split",
                             color="gender", color_discrete_map={"Male": PRIMARY_COLOR, "Female": "#5a9bb0"}, hole=0.5)
        fig_gender.update_traces(textinfo="label+percent")
        fig_gender.update_layout(showlegend=False)
        st.plotly_chart(fig_gender, use_container_width=True)

    with col4:
        blood_counts = df["blood_type"].value_counts().reset_index()
        blood_counts.columns = ["blood_type", "count"]
        blood_counts = blood_counts.sort_values("count", ascending=True)
        fig_blood = px.bar(blood_counts, x="count", y="blood_type", orientation="h",
                            title="Blood Type Distribution", color_discrete_sequence=["#a3c9d1"])
        fig_blood.update_layout(xaxis_title="Patients", yaxis_title=None)
        st.plotly_chart(fig_blood, use_container_width=True)
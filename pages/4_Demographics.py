import streamlit as st
import plotly.express as px
from utils import load_data, apply_filters, DEPARTMENT_COLORS, PRIMARY_COLOR

st.set_page_config(page_title="Demographics & Risk Factors", page_icon="🧍", layout="wide")

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

st.title("🧍 Patient Demographics & Risk Factors")
st.markdown("Who the hospital serves — supporting context for the operational and quality findings")
st.divider()

# ============================================================
# CHART: Age Distribution (colored by age_group)
# ============================================================

fig_age_dist = px.histogram(
    df, x="age", color="age_group",
    title="Patient Age Distribution",
    nbins=40,
    color_discrete_sequence=px.colors.sequential.Teal
)
fig_age_dist.update_layout(
    xaxis_title="Age", yaxis_title="Number of Patients",
    legend_title="Age Group", bargap=0.05
)

st.plotly_chart(fig_age_dist, use_container_width=True)

# ============================================================
# TWO CHARTS SIDE BY SIDE: BMI by Department | Smoker % by Department
# ============================================================

col1, col2 = st.columns(2)

with col1:
    fig_bmi_dept = px.box(
        df, x="department", y="bmi",
        title="BMI Distribution by Department",
        color="department", color_discrete_map=DEPARTMENT_COLORS,
        points=False
    )
    fig_bmi_dept.update_layout(showlegend=False, xaxis_title=None, yaxis_title="BMI")
    st.plotly_chart(fig_bmi_dept, use_container_width=True)

with col2:
    smoker_by_dept = (
        df.groupby("department")["smoker"]
          .apply(lambda x: (x == "Yes").mean())
          .reset_index(name="smoker_pct")
          .sort_values("smoker_pct", ascending=True)
    )
    fig_smoker_dept = px.bar(
        smoker_by_dept, x="smoker_pct", y="department", orientation="h",
        title="Smoker Percentage by Department",
        color_discrete_sequence=[PRIMARY_COLOR], text="smoker_pct"
    )
    fig_smoker_dept.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig_smoker_dept.update_layout(xaxis_title="% Smokers", yaxis_title=None, xaxis_tickformat=".0%")
    st.plotly_chart(fig_smoker_dept, use_container_width=True)

# ============================================================
# TWO CHARTS SIDE BY SIDE: Gender Split | Blood Type (minor)
# ============================================================

col3, col4 = st.columns(2)

with col3:
    gender_counts = df["gender"].value_counts().reset_index()
    gender_counts.columns = ["gender", "count"]

    fig_gender = px.pie(
        gender_counts, values="count", names="gender",
        title="Patient Gender Split",
        color="gender",
        color_discrete_map={"Male": PRIMARY_COLOR, "Female": "#5a9bb0"},
        hole=0.5
    )
    fig_gender.update_traces(textinfo="label+percent")
    fig_gender.update_layout(showlegend=False)
    st.plotly_chart(fig_gender, use_container_width=True)

with col4:
    blood_counts = df["blood_type"].value_counts().reset_index()
    blood_counts.columns = ["blood_type", "count"]
    blood_counts = blood_counts.sort_values("count", ascending=True)

    fig_blood = px.bar(
        blood_counts, x="count", y="blood_type", orientation="h",
        title="Blood Type Distribution",
        color_discrete_sequence=["#a3c9d1"]
    )
    fig_blood.update_layout(xaxis_title="Patients", yaxis_title=None)
    st.plotly_chart(fig_blood, use_container_width=True)

# ============================================================
# DATA QUALITY TRANSPARENCY NOTE
# ============================================================

st.divider()
st.caption(
    "**Data note:** This dataset does not show a clinically realistic correlation between "
    "patient age and diagnosis (e.g., some pediatric patients are recorded with adult-typical "
    "diagnoses such as coronary artery disease). This is a known limitation of the underlying "
    "data and is disclosed here for analytical transparency."
)


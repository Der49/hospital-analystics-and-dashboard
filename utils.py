import pandas as pd
import streamlit as st

# ============================================================
# COLOR CONSTANTS — used across every tab for visual consistency
# ============================================================

DEPARTMENT_COLORS = {
    "Cardiology": "#1f77b4",
    "Pulmonology": "#ff7f0e",
    "Urology": "#2ca02c",
    "Internal Medicine": "#d62728",
    "Neurology": "#9467bd",
    "Orthopedics": "#8c564b",
    "Gastroenterology": "#e377c2",
    "Emergency": "#7f7f7f"
}

PRIMARY_COLOR = "#0d6178"
ALERT_COLOR = "#c0392b"
READMISSION_BENCHMARK = 0.15


@st.cache_data
def load_data(path: str = "hospital_stays.csv") -> pd.DataFrame:
    """Load and clean the hospital stays dataset. Cached so it only runs once per session."""
    df = pd.read_csv(path)

    df["admission_date"] = pd.to_datetime(df["admission_date"], format="%Y-%m-%d")
    df["discharge_date"] = pd.to_datetime(df["discharge_date"], format="%Y-%m-%d")

    age_bins = [0, 1, 5, 12, 18, 40, 65, 120]
    age_labels = ["Infant (0-1)", "Toddler (2-5)", "Child (6-12)",
                  "Teen (13-18)", "Adult (19-40)", "Middle-age (41-65)", "Senior (65+)"]
    df["age_group"] = pd.cut(df["age"], bins=age_bins, labels=age_labels, right=True)

    df["charge_per_day"] = (df["total_charges"] / df["length_of_stay"]).round(0)
    df["is_emergency"] = df["department"].apply(
        lambda d: "Emergency" if d == "Emergency" else "All Other Departments"
    )

    assert df["patient_id"].is_unique, "Duplicate patient_id found!"
    assert (df["discharge_date"] >= df["admission_date"]).all(), "Invalid date order!"

    return df

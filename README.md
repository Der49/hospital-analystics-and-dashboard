# 🏥 Hospital Operations & Quality Dashboard

An interactive analytics dashboard analyzing 10,500 hospital stays (2023–2025) to uncover
operational, financial, and patient-quality insights — built as a full data analyst
portfolio project from raw CSV to a deployed, filterable Streamlit app.

**🔗 Live Dashboard:** [hospital-analytics-and-dashboard-darrel-christofer.streamlit.app](https://hospital-analytics-and-dashboard-darrel-christofer.streamlit.app)
*(Free-tier hosting — the app may take ~30 seconds to wake up if it's been idle.)*

**📓 Full Analysis Notebook:** [`hospital_analysis.ipynb`](./hospital_analysis.ipynb)

---

## 📌 The Business Problem

This hospital's 30-day readmission rate sits at **19.1%**, roughly **4 percentage points above**
the commonly used 15% quality benchmark. This project investigates *where* that problem
concentrates (which departments, which diagnoses, which patient groups) and *what it's
costing the hospital*, then packages the findings into a live, explorable dashboard rather
than a static report.

---

## 🖼️ Preview

*(Add 1–2 screenshots of the Overview and Patient Safety tabs here once available)*

---

## 🧰 Tech Stack

| Layer | Tools |
|---|---|
| Data wrangling & analysis | Python, Pandas, NumPy |
| Visualization | Plotly |
| Dashboard / app | Streamlit |
| Deployment | Streamlit Community Cloud, GitHub |
| Analysis environment | Jupyter Notebook |

---

## 📊 What's in the Dashboard

The app is organized into 5 tabs, all driven by a shared set of filters
(date range, department, insurance type, age group):

1. **Overview** — hospital-wide KPIs: admissions, revenue, average length of stay,
   average charge per stay, and the headline readmission-rate-vs-benchmark metric
2. **Operations** — length of stay by department, admission seasonality, bed-day
   capacity load, weekday patterns, and diagnosis volume/LOS
3. **Revenue** — monthly revenue trend, department revenue (total vs. average toggle),
   cost intensity (charge per day), payer economics, and a Pareto analysis of
   revenue concentration by diagnosis
4. **Patient Safety** — the flagship analysis: readmission rate by department and
   diagnosis (heatmap), risk factors (age, smoking status), the length-of-stay vs.
   readmission relationship, and an Emergency department comparison
5. **Patient Profile** — age, BMI, smoking, gender, and blood type distributions
   for demographic context

---

## 🔍 Key Findings

- Overall 30-day readmission rate (**19.1%**) is notably above the 15% industry benchmark
- Readmission risk is not evenly distributed — certain department/diagnosis combinations
  show meaningfully higher rates than others (see the Patient Safety tab's heatmap)
- A small number of diagnoses account for a disproportionate share of total revenue
  (see the Pareto chart in the Revenue tab)
- **BPJS Kesehatan** (Indonesia's national health insurance) is the dominant payer,
  consistent with this appearing to be a general hospital serving a broad population

---

## ⚠️ Data Limitations

This dataset does not show a clinically realistic correlation between patient age and
diagnosis (e.g., some very young patients are recorded with adult-typical diagnoses such
as coronary artery disease). This is disclosed here for analytical transparency — the
dataset is used as-is for the purposes of this project, with this caveat in mind for any
age-based clinical interpretation.

---

## 🗂️ Project Structure

```
hospital-analytics-and-dashboard/
├── app.py                      # Streamlit dashboard (main entry point)
├── utils.py                    # Data loading, cleaning, and shared constants
├── requirements.txt            # Python dependencies
├── hospital_stays.csv          # Source dataset
├── hospital_analysis.ipynb     # Full exploratory analysis notebook
└── README.md
```

---

## ▶️ Running Locally

```bash
git clone https://github.com/<your-username>/hospital-analytics-and-dashboard.git
cd hospital-analytics-and-dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## 👤 Author

**Darrel Christofer**
*(Add your LinkedIn / portfolio site / email here)*

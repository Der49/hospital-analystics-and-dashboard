# Hospital Operations & Quality Dashboard

A full data analyst portfolio project from raw CSV to a deployed, filterable Streamlit app dashboard analyzing 10,500 hospital stays from 2023-2025 to uncover operational, financial, and patient-quality insights.

**Live Dashboard:** 

**Full Analysis Notebook:** [`hospital_analysis.ipynb`](https://colab.research.google.com/drive/1rG76eUsStV77eWMbE9zc09tYV9IZg55Q?usp=sharing)

---

## 📌 Business Case

This project examines why **the hospital's 30-day readmission rate** (19.1%)—the percentage of patients who return to the hospital within 30 days of being discharged—**is above the 15% benchmark**. It identifies the main factors behind readmissions and presents the findings in an interactive dashboard to support better decision-making.

---

## 🗂️ Dataset

This is a dataset that we can get through praktikdata website by the link below:

https://praktikdata.com/resources/data-playground/hospital-stays

or access through Drive:

https://drive.google.com/file/d/1f7q9IIixLn2vZczn_kBCGI1Mk77wbxQj/view?usp=sharing

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

## 💡 Business Analysis and Insights

### Executive Summary
Across 10,500 inpatient stays between **January 2023 and January 2025**, the hospital generated approximately **IDR 103.68 billion** revenue. Patients stayed an average of **6.9 days**, with an average hospital charge of **IDR 9.9 million** per stay. One of the most important findings is the **30-day readmission rate of 19.1%**, meaning nearly **1 in 5 patients returned to the hospital within 30 days of discharge**. This is **4.1 percentage points higher** than the **15% quality benchmark**, indicating opportunities to improve patient care while reducing unnecessary costs.


### Operational Insights
- Cardiology and Pulmonology are our busiest departments, each making up about 20% of all admissions. These two are also where capacity strain will hit hardest if volume keeps growing.
- Just because a department admits more patients doesn't mean it uses more hospital beds overall. Some departments see fewer patients but keep them longer, so they end up eating a bigger share of bed capacity than their admission numbers suggest. (Check the "Total Bed-Days by Department" chart in the Operations tab)
- Admissions follow a pattern tied to season/day of week, so that we can staff up in advance instead of reacting after beds start filling.

### Financial Insights
- BPJS Kesehatan (Indonesia's national health insurance) pays for roughly 40% of all patient stays. That means a big part of our revenue depends on one nationally-set reimbursement system, not a mix of private payers.
- A small handful of diagnoses bring in most of the hospital's revenue. These cases deserve extra attention when planning capacity or looking for cost savings.
- Not every department that brings in less revenue is low value. Some cost more per day to run, even if their total revenue looks small. (See "Average Charge per Day by Department.")

### Patient Safety Insights
- Our overall readmission rate is 19.1%, but it's not spread evenly.
- Some diagnosis and department combinations show much higher readmission risk than others. These specific combos are the best places to focus a discharge-planning fix, rather than rolling out a hospital-wide policy.
- One thing that could be our main focus: do readmitted patients tend to have shorter hospital stays than patients who aren't readmitted? If so, it could mean people are being discharged too early.
- We estimate readmissions above the target rate are costing the hospital an extra IDR 4,212M. This turns a clinical issue into something leadership can act on financially.

### Demographic Insights
- The patient population spans a wide age range (1–95 years), consistent with
  a general hospital serving a broad community rather than a specialty clinic.
- Age does not show a clinically realistic correlation with diagnosis in this dataset (e.g., some very young patients are recorded with adult-typical
  diagnoses)

### Recommendations
1. Instead of rolling out one big policy for the whole hospital, **focus on the specific department and diagnosis pairs where readmissions spike**. Fix discharge planning first for the specific department and diagnosis combos flagged in the readmission heatmap. Targeting these will go further than a blanket policy change.
2. **Dig into whether shorter stays are linked to more readmissions**. If shorter stays are tied to more readmissions, that could point to patients being discharged too soon that's worth to investigate on the clinical side.
3. **Maximize our planning on some diagnoses that shows up a lot and generate serious revenue**. It's about not letting our most important patients be the ones who get squeezed when things get busy.
4. **Watch how dependent we are on BPJS Kesehatan**. Since BPJS Kesehatan covers such a large share of stays, any change in national reimbursement policy could hit hospital revenue hard.

---

## 🗂️ Project Structure

```
hospital-analytics-and-dashboard/
├── app.py                      # Streamlit dashboard 
├── utils.py                    # Data loading, cleaning, and shared constants
├── hospital_stays.csv          # Source dataset
├── hospital_analysis.ipynb     # Full exploratory analysis notebook
└── README.md
```

---

## 👤 Author

**Darrel Christofer**
*(www.linkedin.com/in/darrel-christofer / christoferdarrel@gmail.com)*

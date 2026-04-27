# 📊 Student Performance Analysis Dashboard

A full-stack data analysis project built with **Python · Pandas · SQLite/SQL · Matplotlib**.  
Analyses 520+ synthetic student academic records to surface grade patterns, at-risk cohorts, and subject-wise trends.

---

## 🗂️ Project Structure

```
student-performance-dashboard/
├── data/
│   ├── generate_data.py      # Generates synthetic CSVs (students.csv, marks.csv)
│   ├── students.csv          # Auto-generated on first run
│   └── marks.csv             # Auto-generated on first run
├── sql/
│   └── queries.py            # 7 SQL queries via SQLite in-memory
├── analysis/
│   └── analysis.py           # Pandas EDA: KPIs, distributions, pivots
├── visualizations/           # (reserved for extra notebooks)
├── outputs/                  # ← 3 dashboard PNGs saved here
│   ├── dashboard1_overview.png
│   ├── dashboard2_heatmaps.png
│   └── dashboard3_correlations.png
├── dashboard.py              # 🏁 MAIN entry point
├── requirements.txt
└── README.md
```

---

## ✨ Features

| Module | What it does |
|--------|-------------|
| **Data Generation** | 520 students × 8 subjects = 4 160 academic records with realistic distributions |
| **SQL Queries** | 7 complex aggregations: GPA averages, attendance correlations, pass/fail rates, at-risk cohorts, year-wise stats |
| **Pandas EDA** | Grade distribution, department analysis, subject performance, gender analysis, correlation matrix |
| **Dashboard 1** | KPI banner · Grade bar chart · Dept GPA · Subject marks · Attendance→GPA · Year-wise pass rate |
| **Dashboard 2** | Dept×Subject heatmap · GPA histogram · Marks histogram · Pass rate per subject · At-risk % |
| **Dashboard 3** | Attendance vs GPA scatter (with regression) · Year-wise box plot · Scholarship split pie |

---

## 🚀 How to Run (Step-by-Step)

### 1. Clone / Download the project

```bash
git clone https://github.com/<YOUR_USERNAME>/student-performance-dashboard.git
cd student-performance-dashboard
```

### 2. Create a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
python dashboard.py
```

The script will:
1. ✅ Generate `data/students.csv` and `data/marks.csv`
2. ✅ Run all 7 SQL queries and print results to the terminal
3. ✅ Print all key KPIs
4. ✅ Save 3 dashboard images to `outputs/`

### 5. View the outputs

Open the PNG files in `outputs/`:

```
outputs/
├── dashboard1_overview.png      # Main 6-panel overview
├── dashboard2_heatmaps.png      # Heatmaps + distributions
└── dashboard3_correlations.png  # Scatter plots + box plots
```

---

## 🗄️ SQL Queries Included

```sql
-- 1. Overall grade distribution with window percentages
-- 2. Department-wise avg GPA, attendance, at-risk count
-- 3. Subject-wise avg/min/max marks and pass rates
-- 4. At-risk student cohort (GPA < 2.0 or failed ≥2 subjects)
-- 5. Attendance bucket → GPA correlation
-- 6. Year-wise pass rates and avg marks
-- 7. Department × Subject pivot for heatmap
```

---

## 📈 Key Findings (Sample)

- Strong positive correlation (**r ≈ 0.55**) between attendance and GPA
- Students with attendance **< 50%** average GPA drops below 2.0 (at-risk threshold)
- **Computer Science** and **Mathematics** show highest average GPA
- **Year 3** students have the highest pass rate
- Scholarship holders average **~8 marks higher** than non-scholarship peers

---

## 🛠️ Tech Stack

| Tool | Usage |
|------|-------|
| Python 3.10+ | Core language |
| Pandas | Data manipulation, EDA, pivot tables |
| SQLite3 (stdlib) | In-memory SQL queries |
| Matplotlib | All visualizations (bar, histogram, heatmap, scatter, pie, box) |
| NumPy | Numerical operations, synthetic data generation |

---

## 📤 Deploying to GitHub

See the [Deployment Guide](#-deploy-to-github) section below or follow the GitHub instructions in this README.

---

## 👤 Author

Built as a data analysis portfolio project.  
Feel free to fork, extend, or adapt for your own academic datasets.
"# student-performance-dashboard" 

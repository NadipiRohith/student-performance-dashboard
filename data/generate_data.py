"""
generate_data.py
Generates synthetic student academic records and saves them as CSV files.
"""

import pandas as pd
import numpy as np
import random
import os

np.random.seed(42)
random.seed(42)

N = 520  # 520+ student records

# ── Students ─────────────────────────────────────────────────────────────────
student_ids = [f"STU{str(i).zfill(4)}" for i in range(1, N + 1)]
first_names = ["Aarav","Priya","Rohan","Sneha","Vikram","Anjali","Kiran","Meera",
               "Arjun","Divya","Rahul","Pooja","Amit","Riya","Suresh","Nisha",
               "Raj","Kavita","Sanjay","Lakshmi","Dev","Ananya","Nikhil","Swati",
               "Aditya","Preeti","Varun","Shreya","Kunal","Neha"]
last_names  = ["Sharma","Patel","Kumar","Singh","Reddy","Gupta","Nair","Iyer",
               "Joshi","Mehta","Verma","Chatterjee","Das","Bose","Roy","Pillai"]

students = pd.DataFrame({
    "student_id":  student_ids,
    "name":        [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(N)],
    "age":         np.random.randint(17, 23, N),
    "gender":      np.random.choice(["Male", "Female"], N, p=[0.52, 0.48]),
    "department":  np.random.choice(
                       ["Computer Science", "Mathematics", "Physics",
                        "Chemistry", "Biology", "Economics"],
                       N, p=[0.25, 0.18, 0.15, 0.14, 0.13, 0.15]),
    "year":        np.random.choice([1, 2, 3, 4], N, p=[0.28, 0.26, 0.25, 0.21]),
    "scholarship": np.random.choice([True, False], N, p=[0.30, 0.70]),
})

# ── Attendance ────────────────────────────────────────────────────────────────
attendance_pct = np.clip(np.random.normal(78, 14, N), 20, 100)
students["attendance_pct"] = attendance_pct.round(1)

# ── Subjects ──────────────────────────────────────────────────────────────────
subjects = ["Mathematics", "Physics", "Chemistry", "English",
            "Computer Science", "Biology", "Economics", "Statistics"]

records = []
for sid, att in zip(student_ids, attendance_pct):
    base_ability = np.random.normal(65, 15)
    att_bonus    = (att - 70) * 0.3
    for subj in subjects:
        marks = np.clip(
            base_ability + att_bonus + np.random.normal(0, 10), 0, 100
        )
        records.append({"student_id": sid, "subject": subj, "marks": round(marks, 1)})

marks_df = pd.DataFrame(records)

# Grade helper
def assign_grade(m):
    if m >= 90: return "A+"
    if m >= 80: return "A"
    if m >= 70: return "B"
    if m >= 60: return "C"
    if m >= 50: return "D"
    return "F"

marks_df["grade"]   = marks_df["marks"].apply(assign_grade)
marks_df["pass"]    = marks_df["marks"] >= 50
marks_df["gpa_pts"] = marks_df["marks"].apply(
    lambda m: 4.0 if m>=90 else 3.7 if m>=85 else 3.3 if m>=80
              else 3.0 if m>=75 else 2.7 if m>=70 else 2.3 if m>=65
              else 2.0 if m>=60 else 1.7 if m>=55 else 1.3 if m>=50 else 0.0
)

# ── Semester GPA summary ──────────────────────────────────────────────────────
gpa_summary = (marks_df.groupby("student_id")
               .agg(avg_marks=("marks","mean"),
                    gpa=("gpa_pts","mean"),
                    subjects_failed=("pass", lambda x: (~x).sum()))
               .reset_index())
gpa_summary["avg_marks"]       = gpa_summary["avg_marks"].round(2)
gpa_summary["gpa"]             = gpa_summary["gpa"].round(2)
gpa_summary["at_risk"]         = (
    (gpa_summary["gpa"] < 2.0) | (gpa_summary["subjects_failed"] >= 2)
)

students = students.merge(gpa_summary, on="student_id")

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__))
students.to_csv(f"{out}/students.csv",   index=False)
marks_df.to_csv(f"{out}/marks.csv",      index=False)
print(f"✅  Generated {len(students)} students  |  {len(marks_df)} subject records")

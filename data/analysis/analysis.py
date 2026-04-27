"""
analysis.py  –  Pandas-powered exploratory data analysis on student records.
"""

import pandas as pd
import numpy as np


def load_data(data_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame]:
    students = pd.read_csv(f"{data_dir}/students.csv")
    marks    = pd.read_csv(f"{data_dir}/marks.csv")
    return students, marks


def summary_stats(students: pd.DataFrame, marks: pd.DataFrame) -> dict:
    """Return key KPI metrics as a flat dict."""
    return {
        "total_students":      len(students),
        "total_records":       len(marks),
        "overall_avg_marks":   round(marks["marks"].mean(), 2),
        "overall_pass_rate":   round(marks["pass"].mean() * 100, 2),
        "overall_avg_gpa":     round(students["gpa"].mean(), 2),
        "at_risk_students":    int(students["at_risk"].sum()),
        "at_risk_pct":         round(students["at_risk"].mean() * 100, 2),
        "avg_attendance":      round(students["attendance_pct"].mean(), 2),
        "scholarship_students": int(students["scholarship"].sum()),
    }


def grade_distribution(marks: pd.DataFrame) -> pd.DataFrame:
    order = ["A+", "A", "B", "C", "D", "F"]
    dist  = (marks["grade"]
             .value_counts()
             .reindex(order, fill_value=0)
             .reset_index())
    dist.columns = ["grade", "count"]
    dist["percentage"] = (dist["count"] / dist["count"].sum() * 100).round(2)
    return dist


def department_analysis(students: pd.DataFrame) -> pd.DataFrame:
    return (students
            .groupby("department")
            .agg(
                students=("student_id", "count"),
                avg_gpa=("gpa", "mean"),
                avg_attendance=("attendance_pct", "mean"),
                at_risk_count=("at_risk", "sum"),
                avg_marks=("avg_marks", "mean"),
            )
            .round(2)
            .reset_index()
            .sort_values("avg_gpa", ascending=False))


def subject_performance(marks: pd.DataFrame) -> pd.DataFrame:
    df = (marks
          .groupby("subject")
          .agg(
              avg_marks=("marks", "mean"),
              min_marks=("marks", "min"),
              max_marks=("marks", "max"),
              std_marks=("marks", "std"),
              pass_rate=("pass",  "mean"),
          )
          .round(2)
          .reset_index()
          .sort_values("avg_marks", ascending=False))
    df["pass_rate"] = (df["pass_rate"] * 100).round(2)
    return df


def attendance_correlation(students: pd.DataFrame) -> float:
    corr = students["attendance_pct"].corr(students["gpa"])
    return round(corr, 4)


def heatmap_pivot(students: pd.DataFrame, marks: pd.DataFrame) -> pd.DataFrame:
    merged = marks.merge(students[["student_id", "department"]], on="student_id")
    pivot  = (merged
              .groupby(["department", "subject"])["marks"]
              .mean()
              .round(2)
              .unstack("subject"))
    return pivot


def year_wise(students: pd.DataFrame, marks: pd.DataFrame) -> pd.DataFrame:
    merged = marks.merge(students[["student_id", "year", "attendance_pct"]],
                         on="student_id")
    return (merged
            .groupby("year")
            .agg(
                avg_marks=("marks",         "mean"),
                pass_rate=("pass",          "mean"),
                avg_attendance=("attendance_pct", "mean"),
            )
            .round(2)
            .reset_index()
            .assign(pass_rate=lambda d: (d["pass_rate"] * 100).round(2)))


def gender_analysis(students: pd.DataFrame) -> pd.DataFrame:
    return (students
            .groupby("gender")
            .agg(count=("student_id","count"),
                 avg_gpa=("gpa","mean"),
                 avg_attendance=("attendance_pct","mean"),
                 at_risk_pct=("at_risk","mean"))
            .round(2)
            .reset_index()
            .assign(at_risk_pct=lambda d: (d["at_risk_pct"]*100).round(2)))


def run_full_analysis(data_dir: str = "data") -> dict:
    students, marks = load_data(data_dir)
    pivot           = heatmap_pivot(students, marks)

    return {
        "students":       students,
        "marks":          marks,
        "kpis":           summary_stats(students, marks),
        "grade_dist":     grade_distribution(marks),
        "dept_analysis":  department_analysis(students),
        "subj_perf":      subject_performance(marks),
        "att_corr":       attendance_correlation(students),
        "heatmap":        pivot,
        "year_wise":      year_wise(students, marks),
        "gender":         gender_analysis(students),
    }

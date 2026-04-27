"""
queries.py  –  SQL queries executed via SQLite (in-memory) using pandas + sqlite3
"""

import sqlite3
import pandas as pd

# ── Load CSVs into SQLite ─────────────────────────────────────────────────────
def get_connection(students_df: pd.DataFrame, marks_df: pd.DataFrame) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    students_df.to_sql("students", conn, index=False, if_exists="replace")
    marks_df.to_sql("marks",    conn, index=False, if_exists="replace")
    return conn

# ─────────────────────────────────────────────────────────────────────────────
# 1. Overall grade distribution
# ─────────────────────────────────────────────────────────────────────────────
Q_GRADE_DIST = """
SELECT
    grade,
    COUNT(*)                                      AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM marks
GROUP BY grade
ORDER BY
    CASE grade
        WHEN 'A+' THEN 1 WHEN 'A' THEN 2 WHEN 'B' THEN 3
        WHEN 'C'  THEN 4 WHEN 'D' THEN 5 ELSE 6
    END;
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Department-wise average GPA
# ─────────────────────────────────────────────────────────────────────────────
Q_DEPT_GPA = """
SELECT
    s.department,
    COUNT(DISTINCT s.student_id)  AS students,
    ROUND(AVG(s.gpa), 2)          AS avg_gpa,
    ROUND(AVG(s.attendance_pct), 2) AS avg_attendance,
    SUM(CASE WHEN s.at_risk THEN 1 ELSE 0 END) AS at_risk_count
FROM students s
GROUP BY s.department
ORDER BY avg_gpa DESC;
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3. Subject-wise performance trends
# ─────────────────────────────────────────────────────────────────────────────
Q_SUBJECT_PERF = """
SELECT
    subject,
    ROUND(AVG(marks), 2)  AS avg_marks,
    ROUND(MIN(marks), 2)  AS min_marks,
    ROUND(MAX(marks), 2)  AS max_marks,
    ROUND(
        100.0 * SUM(CASE WHEN pass THEN 1 ELSE 0 END) / COUNT(*), 2
    )                     AS pass_rate
FROM marks
GROUP BY subject
ORDER BY avg_marks DESC;
"""

# ─────────────────────────────────────────────────────────────────────────────
# 4. At-risk cohort details
# ─────────────────────────────────────────────────────────────────────────────
Q_AT_RISK = """
SELECT
    s.student_id, s.name, s.department, s.year,
    ROUND(s.gpa, 2)             AS gpa,
    s.subjects_failed,
    ROUND(s.attendance_pct, 1)  AS attendance_pct
FROM students s
WHERE s.at_risk = 1
ORDER BY s.gpa ASC
LIMIT 30;
"""

# ─────────────────────────────────────────────────────────────────────────────
# 5. Attendance vs GPA correlation buckets
# ─────────────────────────────────────────────────────────────────────────────
Q_ATT_GPA = """
SELECT
    CASE
        WHEN attendance_pct < 50  THEN '< 50%'
        WHEN attendance_pct < 65  THEN '50-65%'
        WHEN attendance_pct < 75  THEN '65-75%'
        WHEN attendance_pct < 85  THEN '75-85%'
        ELSE '85%+'
    END  AS attendance_bucket,
    COUNT(*)             AS students,
    ROUND(AVG(gpa), 2)   AS avg_gpa,
    ROUND(AVG(avg_marks),2) AS avg_marks
FROM students
GROUP BY attendance_bucket
ORDER BY MIN(attendance_pct);
"""

# ─────────────────────────────────────────────────────────────────────────────
# 6. Year-wise pass/fail rates
# ─────────────────────────────────────────────────────────────────────────────
Q_YEAR_PASS = """
SELECT
    s.year,
    COUNT(DISTINCT s.student_id)     AS total_students,
    ROUND(AVG(m.marks), 2)           AS avg_marks,
    ROUND(
        100.0 * SUM(CASE WHEN m.pass THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                AS pass_rate,
    ROUND(AVG(s.attendance_pct), 2)  AS avg_attendance
FROM students s
JOIN marks m ON s.student_id = m.student_id
GROUP BY s.year
ORDER BY s.year;
"""

# ─────────────────────────────────────────────────────────────────────────────
# 7. Subject × Department heatmap pivot
# ─────────────────────────────────────────────────────────────────────────────
Q_HEATMAP = """
SELECT
    s.department,
    m.subject,
    ROUND(AVG(m.marks), 2) AS avg_marks
FROM students s
JOIN marks m ON s.student_id = m.student_id
GROUP BY s.department, m.subject
ORDER BY s.department, m.subject;
"""

# ─────────────────────────────────────────────────────────────────────────────
# Runner helper
# ─────────────────────────────────────────────────────────────────────────────
def run_all(conn: sqlite3.Connection) -> dict:
    queries = {
        "grade_dist":   Q_GRADE_DIST,
        "dept_gpa":     Q_DEPT_GPA,
        "subject_perf": Q_SUBJECT_PERF,
        "at_risk":      Q_AT_RISK,
        "att_gpa":      Q_ATT_GPA,
        "year_pass":    Q_YEAR_PASS,
        "heatmap":      Q_HEATMAP,
    }
    results = {}
    for key, sql in queries.items():
        results[key] = pd.read_sql_query(sql, conn)
    return results

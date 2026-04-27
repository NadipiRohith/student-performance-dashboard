"""
dashboard.py  –  Matplotlib dashboard with 9 charts saved to outputs/
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# ── path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from data.generate_data   import *          # just to make imports clear
from analysis.analysis    import run_full_analysis
from sql.queries          import get_connection, run_all
import pandas as pd

OUT_DIR = os.path.join(ROOT, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ── palette ───────────────────────────────────────────────────────────────────
DARK_BG   = "#0D1117"
PANEL_BG  = "#161B22"
ACCENT    = "#58A6FF"
GREEN     = "#3FB950"
ORANGE    = "#D29922"
RED       = "#F85149"
PURPLE    = "#BC8CFF"
CYAN      = "#39D353"
TEXT_PRI  = "#E6EDF3"
TEXT_SEC  = "#8B949E"
GRID_COL  = "#21262D"

GRADE_COLORS = {
    "A+": GREEN, "A": CYAN, "B": ACCENT,
    "C": ORANGE, "D": PURPLE, "F": RED,
}

def style():
    plt.rcParams.update({
        "figure.facecolor":  DARK_BG,
        "axes.facecolor":    PANEL_BG,
        "axes.edgecolor":    GRID_COL,
        "axes.labelcolor":   TEXT_SEC,
        "text.color":        TEXT_PRI,
        "xtick.color":       TEXT_SEC,
        "ytick.color":       TEXT_SEC,
        "grid.color":        GRID_COL,
        "grid.linewidth":    0.6,
        "font.family":       "DejaVu Sans",
        "axes.titlepad":     12,
        "axes.titlesize":    11,
        "axes.labelsize":    9,
    })

def panel_title(ax, title):
    ax.set_title(title, color=TEXT_PRI, fontsize=11, fontweight="bold", pad=10)

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD 1: Overview (2×3 grid)
# ─────────────────────────────────────────────────────────────────────────────
def plot_dashboard1(data: dict):
    style()
    fig = plt.figure(figsize=(18, 11), facecolor=DARK_BG)
    fig.suptitle(
        "STUDENT PERFORMANCE ANALYSIS DASHBOARD",
        fontsize=18, fontweight="bold", color=TEXT_PRI, y=0.98,
        fontfamily="DejaVu Sans",
    )

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35,
                           left=0.06, right=0.97, top=0.92, bottom=0.07)

    # ── [0,0] KPI banner ─────────────────────────────────────────────────────
    ax0 = fig.add_subplot(gs[0, 0])
    ax0.axis("off")
    kpis = data["kpis"]
    metrics = [
        ("Total Students",  str(kpis["total_students"]),   ACCENT),
        ("Avg GPA",         str(kpis["overall_avg_gpa"]),  GREEN),
        ("Pass Rate",       f"{kpis['overall_pass_rate']}%", CYAN),
        ("At-Risk",         f"{kpis['at_risk_students']}  ({kpis['at_risk_pct']}%)", RED),
        ("Avg Attendance",  f"{kpis['avg_attendance']}%",  ORANGE),
        ("Scholarship",     str(kpis["scholarship_students"]), PURPLE),
    ]
    for i, (label, val, col) in enumerate(metrics):
        y = 0.88 - i * 0.155
        ax0.add_patch(mpatches.FancyBboxPatch(
            (0.03, y - 0.06), 0.94, 0.13,
            boxstyle="round,pad=0.01", facecolor=DARK_BG,
            edgecolor=col, linewidth=1.2, transform=ax0.transAxes,
        ))
        ax0.text(0.08, y + 0.01, label, transform=ax0.transAxes,
                 fontsize=8, color=TEXT_SEC)
        ax0.text(0.92, y + 0.01, val, transform=ax0.transAxes,
                 fontsize=10, color=col, ha="right", fontweight="bold")
    panel_title(ax0, "📊 Key Metrics")

    # ── [0,1] Grade distribution bar ─────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 1])
    gd = data["grade_dist"]
    bars = ax1.bar(gd["grade"], gd["count"],
                   color=[GRADE_COLORS.get(g, ACCENT) for g in gd["grade"]],
                   edgecolor=DARK_BG, linewidth=0.8, width=0.6)
    for bar, pct in zip(bars, gd["percentage"]):
        ax1.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 6, f"{pct}%",
                 ha="center", va="bottom", fontsize=8, color=TEXT_SEC)
    ax1.set_xlabel("Grade"); ax1.set_ylabel("Number of Students")
    ax1.yaxis.grid(True); ax1.set_axisbelow(True)
    panel_title(ax1, "🎓 Grade Distribution")

    # ── [0,2] Department GPA horizontal bar ──────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 2])
    dept = data["dept_analysis"].sort_values("avg_gpa")
    colors_dept = [GREEN if g >= 3.0 else ORANGE if g >= 2.5 else RED
                   for g in dept["avg_gpa"]]
    bars2 = ax2.barh(dept["department"], dept["avg_gpa"],
                     color=colors_dept, edgecolor=DARK_BG, height=0.55)
    for bar, val in zip(bars2, dept["avg_gpa"]):
        ax2.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                 f"{val:.2f}", va="center", fontsize=8.5, color=TEXT_PRI)
    ax2.set_xlabel("Average GPA"); ax2.axvline(2.0, color=RED, ls="--", lw=1, alpha=0.5)
    ax2.xaxis.grid(True); ax2.set_axisbelow(True); ax2.set_xlim(0, 4.3)
    panel_title(ax2, "🏢 Dept-wise Average GPA")

    # ── [1,0] Subject performance bars ───────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    sp = data["subj_perf"]
    short = [s.replace(" ", "\n") for s in sp["subject"]]
    bar_colors = [GREEN if m >= 70 else ORANGE if m >= 60 else RED
                  for m in sp["avg_marks"]]
    ax3.bar(range(len(sp)), sp["avg_marks"], color=bar_colors,
            edgecolor=DARK_BG, width=0.6)
    ax3.set_xticks(range(len(sp))); ax3.set_xticklabels(short, fontsize=7.5)
    ax3.axhline(50, color=RED, ls="--", lw=1, alpha=0.7, label="Pass line (50)")
    ax3.set_ylabel("Avg Marks"); ax3.yaxis.grid(True); ax3.set_axisbelow(True)
    ax3.legend(fontsize=7, framealpha=0.2)
    panel_title(ax3, "📚 Subject-wise Avg Marks")

    # ── [1,1] Attendance bucket vs GPA ───────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    att = data["students"].copy()
    bins   = [0, 50, 65, 75, 85, 101]
    labels = ["<50%", "50-65%", "65-75%", "75-85%", "85%+"]
    att["bucket"] = pd.cut(att["attendance_pct"], bins=bins, labels=labels, right=False)
    bucket_gpa    = att.groupby("bucket", observed=True)["gpa"].mean()
    bucket_cnt    = att.groupby("bucket", observed=True)["gpa"].count()
    bar_col = [GREEN if g >= 3.0 else ORANGE if g >= 2.5 else RED for g in bucket_gpa]
    bars4   = ax4.bar(labels, bucket_gpa, color=bar_col, edgecolor=DARK_BG, width=0.55)
    for bar, cnt, val in zip(bars4, bucket_cnt, bucket_gpa):
        ax4.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.03,
                 f"n={cnt}\n{val:.2f}", ha="center", va="bottom", fontsize=7.5, color=TEXT_SEC)
    ax4.set_xlabel("Attendance Bucket"); ax4.set_ylabel("Avg GPA")
    ax4.yaxis.grid(True); ax4.set_axisbelow(True); ax4.set_ylim(0, 4.5)
    ax4.axhline(2.0, color=RED, ls="--", lw=1, alpha=0.6)
    panel_title(ax4, "📅 Attendance → GPA Impact")

    # ── [1,2] Year-wise pass rate ─────────────────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 2])
    yw  = data["year_wise"]
    x   = np.arange(len(yw))
    w   = 0.35
    b1  = ax5.bar(x - w/2, yw["avg_marks"],  w, label="Avg Marks", color=ACCENT,  edgecolor=DARK_BG)
    b2  = ax5.bar(x + w/2, yw["pass_rate"],  w, label="Pass Rate %", color=GREEN, edgecolor=DARK_BG)
    ax5.set_xticks(x)
    ax5.set_xticklabels([f"Year {y}" for y in yw["year"]])
    ax5.set_ylabel("Value"); ax5.yaxis.grid(True); ax5.set_axisbelow(True)
    ax5.legend(fontsize=8, framealpha=0.2)
    panel_title(ax5, "📈 Year-wise Marks & Pass Rate")

    path = os.path.join(OUT_DIR, "dashboard1_overview.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"  ✅ Saved: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD 2: Heatmaps + Distributions
# ─────────────────────────────────────────────────────────────────────────────
def plot_dashboard2(data: dict):
    style()
    fig = plt.figure(figsize=(18, 11), facecolor=DARK_BG)
    fig.suptitle(
        "DETAILED ANALYSIS — Heatmaps, Distributions & At-Risk",
        fontsize=16, fontweight="bold", color=TEXT_PRI, y=0.98,
    )

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38,
                           left=0.06, right=0.97, top=0.92, bottom=0.07)

    # ── [0, 0:2] Dept × Subject heatmap ──────────────────────────────────────
    ax0 = fig.add_subplot(gs[0, :2])
    pivot = data["heatmap"]
    cmap  = LinearSegmentedColormap.from_list(
        "custom", [RED, ORANGE, "#FADF7F", GREEN], N=256)
    im = ax0.imshow(pivot.values, cmap=cmap, aspect="auto",
                    vmin=40, vmax=90, interpolation="nearest")
    ax0.set_xticks(range(len(pivot.columns)))
    ax0.set_xticklabels(pivot.columns, rotation=35, ha="right", fontsize=8.5)
    ax0.set_yticks(range(len(pivot.index)))
    ax0.set_yticklabels(pivot.index, fontsize=9)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            ax0.text(j, i, f"{val:.1f}", ha="center", va="center",
                     fontsize=8, color="white" if val < 65 else DARK_BG, fontweight="bold")
    cb = fig.colorbar(im, ax=ax0, shrink=0.85)
    cb.ax.tick_params(colors=TEXT_SEC)
    cb.set_label("Avg Marks", color=TEXT_SEC)
    panel_title(ax0, "🔥 Department × Subject Performance Heatmap")

    # ── [0,2] GPA histogram ───────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 2])
    students = data["students"]
    ax1.hist(students["gpa"], bins=20, color=ACCENT, edgecolor=DARK_BG,
             linewidth=0.6, alpha=0.9)
    ax1.axvline(students["gpa"].mean(), color=ORANGE, lw=2,
                label=f"Mean: {students['gpa'].mean():.2f}")
    ax1.axvline(2.0, color=RED, lw=1.5, ls="--", label="At-Risk (<2.0)")
    ax1.set_xlabel("GPA"); ax1.set_ylabel("Students")
    ax1.yaxis.grid(True); ax1.set_axisbelow(True)
    ax1.legend(fontsize=8, framealpha=0.2)
    panel_title(ax1, "📊 GPA Distribution")

    # ── [1,0] Marks histogram ─────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.hist(data["marks"]["marks"], bins=25, color=PURPLE,
             edgecolor=DARK_BG, linewidth=0.5, alpha=0.9)
    ax2.axvline(50, color=RED, lw=1.5, ls="--", label="Pass line (50)")
    ax2.axvline(data["marks"]["marks"].mean(), color=GREEN, lw=2,
                label=f"Mean: {data['marks']['marks'].mean():.1f}")
    ax2.set_xlabel("Marks"); ax2.set_ylabel("Frequency")
    ax2.yaxis.grid(True); ax2.set_axisbelow(True)
    ax2.legend(fontsize=8, framealpha=0.2)
    panel_title(ax2, "📉 Overall Marks Distribution")

    # ── [1,1] Pass rate per subject ───────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    sp = data["subj_perf"].sort_values("pass_rate")
    colors_sp = [GREEN if p >= 80 else ORANGE if p >= 65 else RED
                 for p in sp["pass_rate"]]
    ax3.barh(sp["subject"], sp["pass_rate"], color=colors_sp,
             edgecolor=DARK_BG, height=0.55)
    ax3.axvline(80, color=GREEN, ls="--", lw=1, alpha=0.5)
    ax3.set_xlabel("Pass Rate (%)"); ax3.xaxis.grid(True)
    ax3.set_axisbelow(True); ax3.set_xlim(0, 105)
    for i, (_, row) in enumerate(sp.iterrows()):
        ax3.text(row["pass_rate"] + 0.5, i, f"{row['pass_rate']:.1f}%",
                 va="center", fontsize=8, color=TEXT_PRI)
    panel_title(ax3, "✅ Pass Rate by Subject")

    # ── [1,2] At-risk by department ───────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 2])
    dept = data["dept_analysis"].copy()
    dept["at_risk_pct"] = (dept["at_risk_count"] / dept["students"] * 100).round(1)
    dept_sorted = dept.sort_values("at_risk_pct", ascending=True)
    bar_c = [RED if p > 20 else ORANGE if p > 10 else GREEN
             for p in dept_sorted["at_risk_pct"]]
    ax4.barh(dept_sorted["department"], dept_sorted["at_risk_pct"],
             color=bar_c, edgecolor=DARK_BG, height=0.55)
    ax4.set_xlabel("At-Risk Students (%)"); ax4.xaxis.grid(True)
    ax4.set_axisbelow(True)
    for i, (_, row) in enumerate(dept_sorted.iterrows()):
        ax4.text(row["at_risk_pct"] + 0.3, i, f"{row['at_risk_pct']:.1f}%",
                 va="center", fontsize=8.5, color=TEXT_PRI)
    panel_title(ax4, "⚠️  At-Risk % by Department")

    path = os.path.join(OUT_DIR, "dashboard2_heatmaps.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"  ✅ Saved: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD 3: Scatter & Correlations
# ─────────────────────────────────────────────────────────────────────────────
def plot_dashboard3(data: dict):
    style()
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor=DARK_BG)
    fig.suptitle("CORRELATION & SCATTER ANALYSIS",
                 fontsize=15, fontweight="bold", color=TEXT_PRI, y=1.01)

    students = data["students"]

    # ── Scatter: Attendance vs GPA ────────────────────────────────────────────
    ax = axes[0]
    sc = ax.scatter(students["attendance_pct"], students["gpa"],
                    c=students["gpa"], cmap="RdYlGn",
                    alpha=0.55, s=22, linewidths=0)
    fig.colorbar(sc, ax=ax, label="GPA").ax.tick_params(colors=TEXT_SEC)
    ax.set_xlabel("Attendance (%)"); ax.set_ylabel("GPA")
    m, b = np.polyfit(students["attendance_pct"], students["gpa"], 1)
    xline = np.linspace(students["attendance_pct"].min(), students["attendance_pct"].max(), 200)
    ax.plot(xline, m*xline + b, color=ACCENT, lw=1.8, ls="--",
            label=f"r = {data['att_corr']:.3f}")
    ax.legend(fontsize=9, framealpha=0.2)
    ax.yaxis.grid(True); ax.xaxis.grid(True); ax.set_axisbelow(True)
    panel_title(ax, "📅 Attendance vs GPA (r=corr)")

    # ── Box plot: GPA by year ─────────────────────────────────────────────────
    ax2 = axes[1]
    years   = sorted(students["year"].unique())
    bp_data = [students[students["year"] == y]["gpa"].values for y in years]
    bp = ax2.boxplot(bp_data, patch_artist=True,
                     medianprops=dict(color=RED, lw=2),
                     whiskerprops=dict(color=TEXT_SEC),
                     capprops=dict(color=TEXT_SEC),
                     flierprops=dict(marker="o", color=ACCENT, markersize=3, alpha=0.5))
    colors_bp = [ACCENT, GREEN, ORANGE, PURPLE]
    for patch, col in zip(bp["boxes"], colors_bp):
        patch.set_facecolor(col); patch.set_alpha(0.55)
    ax2.set_xticklabels([f"Year {y}" for y in years])
    ax2.set_ylabel("GPA"); ax2.yaxis.grid(True); ax2.set_axisbelow(True)
    panel_title(ax2, "📦 GPA Distribution by Year")

    # ── Pie: scholarship vs non-scholarship pass rate ─────────────────────────
    ax3 = axes[2]
    sch_pass    = students[students["scholarship"] == True]["avg_marks"].mean()
    nosch_pass  = students[students["scholarship"] == False]["avg_marks"].mean()
    sch_cnt     = students["scholarship"].value_counts()
    wedge_colors = [ACCENT, ORANGE]
    wedges, texts, autotexts = ax3.pie(
        [sch_cnt.get(True, 0), sch_cnt.get(False, 0)],
        labels=["Scholarship", "Non-Scholarship"],
        colors=wedge_colors, autopct="%1.1f%%",
        pctdistance=0.7, startangle=140,
        wedgeprops=dict(edgecolor=DARK_BG, linewidth=1.5),
    )
    for t in texts + autotexts:
        t.set_color(TEXT_PRI); t.set_fontsize(9)
    ax3.set_facecolor(PANEL_BG)
    ax3.text(0, -1.4,
             f"Scholarship avg marks: {sch_pass:.1f}\nNon-scholarship avg marks: {nosch_pass:.1f}",
             ha="center", va="center", color=TEXT_SEC, fontsize=8.5)
    panel_title(ax3, "🎓 Scholarship Split")

    plt.tight_layout(pad=2)
    path = os.path.join(OUT_DIR, "dashboard3_correlations.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"  ✅ Saved: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("\n🚀  Running Student Performance Dashboard …\n")

    # 1. Generate data
    print("📦  Generating synthetic data …")
    import subprocess, sys as _sys
    subprocess.run([_sys.executable,
                    os.path.join(ROOT, "data", "generate_data.py")], check=True)

    # 2. Load analysis
    print("🔍  Running Pandas analysis …")
    data = run_full_analysis(os.path.join(ROOT, "data"))

    # 3. SQL queries
    print("🗄️   Running SQL queries …")
    conn    = get_connection(data["students"], data["marks"])
    sql_res = run_all(conn)
    print("   Grade distribution (SQL):")
    print(sql_res["grade_dist"].to_string(index=False))
    print("\n   Department GPA (SQL):")
    print(sql_res["dept_gpa"].to_string(index=False))
    print("\n   Attendance → GPA buckets (SQL):")
    print(sql_res["att_gpa"].to_string(index=False))

    # 4. Print KPIs
    kpis = data["kpis"]
    print("\n📊  Key Performance Indicators:")
    for k, v in kpis.items():
        print(f"   {k:.<35} {v}")

    # 5. Plot dashboards
    print("\n🎨  Generating dashboards …")
    plot_dashboard1(data)
    plot_dashboard2(data)
    plot_dashboard3(data)

    print(f"\n✅  All dashboards saved to: {OUT_DIR}/")
    print("   dashboard1_overview.png")
    print("   dashboard2_heatmaps.png")
    print("   dashboard3_correlations.png\n")


if __name__ == "__main__":
    main()

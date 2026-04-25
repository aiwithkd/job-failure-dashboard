"""
Parses raw batch job logs and produces aggregated summary data for the dashboard.

Covers:
  - SLA breach detection using duration vs per-job thresholds
  - Regex-based error code extraction and classification
  - Daily failure and SLA trend aggregations
  - Per-job execution time analysis and unstable job ranking
  - Timestamp anomaly flagging (jobs running outside expected windows)

Output: data/summary.json — consumed by index.html
"""

import pandas as pd
import numpy as np
import re
import json
from datetime import datetime

# ── Load raw logs ──────────────────────────────────────────────────────────────
df = pd.read_csv("data/job_logs.csv", parse_dates=["start_time", "end_time", "run_date"])

print(f"Loaded {len(df)} job log records")
print(f"Date range: {df['run_date'].min().date()} → {df['run_date'].max().date()}")

# ── SLA breach detection ───────────────────────────────────────────────────────
# Flag any job where actual duration exceeded its defined SLA threshold
df["sla_breached"] = df["duration_min"] > df["sla_limit_min"]
df["breach_delta"] = df["duration_min"] - df["sla_limit_min"]  # how far over SLA

# ── Error code classification via Regex ───────────────────────────────────────
# RC codes indicate controlled failures; ABEND codes indicate system-level crashes
rc_pattern    = re.compile(r"^RC=(\d+)$")
abend_pattern = re.compile(r"^ABEND\s+(\S+)$")

def classify_error(code):
    if not code or pd.isna(code) or code == "":
        return "NONE"
    if rc_pattern.match(str(code)):
        return "RETURN_CODE"
    if abend_pattern.match(str(code)):
        return "ABEND"
    if "JCL" in str(code):
        return "JCL_ERROR"
    return "OTHER"

df["error_class"] = df["error_code"].apply(classify_error)

# ── Timestamp anomaly detection ───────────────────────────────────────────────
# Jobs running between midnight and 4am are flagged as off-window
df["hour"] = df["start_time"].dt.hour
df["off_window"] = df["hour"].between(0, 4)

# ── Daily aggregations ────────────────────────────────────────────────────────
df["run_date_str"] = df["run_date"].dt.strftime("%Y-%m-%d")

daily_failures = (
    df[df["status"].isin(["FAILED", "ABENDED"])]
    .groupby("run_date_str")
    .size()
    .reset_index(name="count")
)

daily_sla = (
    df[df["sla_breached"]]
    .groupby("run_date_str")
    .size()
    .reset_index(name="count")
)

# ── Per-job aggregations ───────────────────────────────────────────────────────
job_stats = (
    df.groupby("job_name")
    .agg(
        total_runs      = ("status", "count"),
        failures        = ("status", lambda x: (x.isin(["FAILED", "ABENDED"])).sum()),
        sla_breaches    = ("sla_breached", "sum"),
        avg_duration    = ("duration_min", "mean"),
        max_duration    = ("duration_min", "max"),
        sla_limit       = ("sla_limit_min", "first"),
        off_window_runs = ("off_window", "sum")
    )
    .reset_index()
)

job_stats["failure_rate_pct"] = (job_stats["failures"] / job_stats["total_runs"] * 100).round(1)
job_stats["avg_duration"]     = job_stats["avg_duration"].round(1)

# Instability score: weighted combination of failure rate + SLA breach rate
job_stats["sla_breach_rate"] = (job_stats["sla_breaches"] / job_stats["total_runs"] * 100).round(1)
job_stats["instability_score"] = (
    job_stats["failure_rate_pct"] * 0.6 + job_stats["sla_breach_rate"] * 0.4
).round(1)

top_unstable = job_stats.sort_values("instability_score", ascending=False).head(10)

# ── Error code distribution ────────────────────────────────────────────────────
error_dist = (
    df[df["error_code"].notna() & (df["error_code"] != "")]
    .groupby("error_code")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)

# ── Overall KPIs ──────────────────────────────────────────────────────────────
total_runs    = len(df)
total_failed  = df["status"].isin(["FAILED", "ABENDED"]).sum()
total_sla     = int(df["sla_breached"].sum())
failure_rate  = round(total_failed / total_runs * 100, 1)
avg_breach_delta = round(df[df["sla_breached"]]["breach_delta"].mean(), 1)

print(f"\nKPIs:")
print(f"  Total runs    : {total_runs:,}")
print(f"  Failures      : {total_failed:,} ({failure_rate}%)")
print(f"  SLA breaches  : {total_sla:,}")
print(f"  Avg breach delta: {avg_breach_delta} min over SLA")

# ── Recent log sample for table ────────────────────────────────────────────────
log_sample = (
    df.sort_values("start_time", ascending=False)
    .head(300)
    [["job_name", "status", "start_time", "duration_min", "sla_limit_min", "sla_breached", "error_code", "error_class"]]
    .copy()
)
log_sample["start_time"] = log_sample["start_time"].dt.strftime("%Y-%m-%d %H:%M")
log_sample["sla_breached"] = log_sample["sla_breached"].astype(bool)

# ── Assemble summary JSON ──────────────────────────────────────────────────────
summary = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kpis": {
        "total_runs":        total_runs,
        "total_failed":      int(total_failed),
        "total_sla_breaches": total_sla,
        "failure_rate_pct":  failure_rate,
        "avg_breach_delta_min": avg_breach_delta,
        "unique_jobs":       int(df["job_name"].nunique())
    },
    "daily_failures": daily_failures.to_dict(orient="records"),
    "daily_sla_breaches": daily_sla.to_dict(orient="records"),
    "top_unstable_jobs": top_unstable[[
        "job_name", "failures", "sla_breaches", "failure_rate_pct",
        "sla_breach_rate", "instability_score", "avg_duration", "sla_limit"
    ]].to_dict(orient="records"),
    "all_job_stats": job_stats[[
        "job_name", "total_runs", "failures", "sla_breaches",
        "avg_duration", "sla_limit", "instability_score"
    ]].to_dict(orient="records"),
    "error_distribution": error_dist.to_dict(orient="records"),
    "log_sample": log_sample.to_dict(orient="records")
}

with open("data/summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\nSummary written → data/summary.json")
print(f"Top 3 unstable jobs:")
print(top_unstable[["job_name", "instability_score", "failure_rate_pct"]].head(3).to_string(index=False))

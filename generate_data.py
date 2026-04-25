"""
Generates simulated batch job execution logs for a financial processing environment.
Produces data/job_logs.csv — raw input for process.py
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

JOB_NAMES = [
    "PORTF_RPT_DAILY", "CASH_FLOW_EXTRACT", "INVEST_RECON_JOB",
    "CLIENT_STMT_GEN", "SLA_MONITOR_BATCH", "TRANS_LOG_PARSER",
    "POSITION_SYNC", "RISK_CALC_JOB", "DIVIDEND_PROC", "FX_RATE_LOAD",
    "NAV_CALC_BATCH", "TRADE_SETTLE_CHK", "PERF_ATTR_JOB", "COMPLIANCE_RPT",
    "EOD_CLOSE_PROC"
]

STATUSES = ["SUCCESS", "FAILED", "ABENDED", "RUNNING", "LATE"]
STATUS_WEIGHTS = [0.65, 0.15, 0.08, 0.05, 0.07]

SLA_MINUTES = {
    "PORTF_RPT_DAILY": 30, "CASH_FLOW_EXTRACT": 20, "INVEST_RECON_JOB": 45,
    "CLIENT_STMT_GEN": 60, "SLA_MONITOR_BATCH": 15, "TRANS_LOG_PARSER": 25,
    "POSITION_SYNC": 20,   "RISK_CALC_JOB": 40,    "DIVIDEND_PROC": 30,
    "FX_RATE_LOAD": 10,    "NAV_CALC_BATCH": 50,   "TRADE_SETTLE_CHK": 35,
    "PERF_ATTR_JOB": 45,   "COMPLIANCE_RPT": 55,   "EOD_CLOSE_PROC": 70
}

ERROR_CODES = ["RC=8", "RC=12", "ABEND S0C7", "ABEND S222", "JCL ERROR"]

def generate_logs(n=5000):
    records = []
    base_date = datetime(2024, 1, 1)

    for _ in range(n):
        job    = random.choice(JOB_NAMES)
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        sla    = SLA_MINUTES[job]
        start  = base_date + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        if status in ("FAILED", "ABENDED"):
            duration = random.randint(1, max(1, sla // 2))
        elif status == "LATE":
            duration = random.randint(sla + 5, sla + 60)
        else:
            duration = random.randint(5, max(6, sla - 1))

        records.append({
            "job_name":     job,
            "status":       status,
            "start_time":   start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time":     (start + timedelta(minutes=duration)).strftime("%Y-%m-%d %H:%M:%S"),
            "duration_min": duration,
            "sla_limit_min": sla,
            "sla_breached": duration > sla,
            "error_code":   random.choice(ERROR_CODES) if status in ("FAILED", "ABENDED") else "",
            "run_date":     start.strftime("%Y-%m-%d")
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df = generate_logs(5000)
    df.to_csv("data/job_logs.csv", index=False)
    print(f"Generated {len(df)} records → data/job_logs.csv")
    print(df["status"].value_counts())

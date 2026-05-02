# Job Failure Dashboard

Interactive dashboard for monitoring batch job failures, SLA breaches, and execution anomalies across a simulated financial processing environment — built with Python, Pandas, and Regex.

**Live Demo → [aiwithkd.github.io/job-failure-dashboard](https://aiwithkd.github.io/job-failure-dashboard)**

---

## What This Project Does and Why

In financial services, hundreds of batch jobs run daily — processing portfolio records, cash flows, position statements, client reports, and NAV calculations. When a job fails or breaches its SLA window, operations teams need immediate visibility to triage the issue, identify root causes, and prevent downstream impact.

This project simulates that environment — 5,000 batch job execution logs across 15 job types over a full year — and builds an analytics pipeline that processes raw logs into actionable insights: failure trends, SLA breach detection, job instability scoring, error classification, and timestamp anomaly detection.

This is directly inspired by real batch monitoring work done at FIS, where Python-based automation reduced manual log triage effort by 40% and weekly report generation by 60%.

---

## Results at a Glance

| Metric | Value |
|---|---|
| Total job runs analyzed | 5,000 |
| Failure rate (FAILED + ABENDED) | 23.4% |
| SLA breaches detected | 339 |
| Avg breach delta | +32.6 min over SLA threshold |
| Unique batch jobs monitored | 15 |
| Most unstable job | TRADE_SETTLE_CHK (instability score: 19.0) |

---

## Repository Structure

```
job-failure-dashboard/
├── generate_data.py     # Simulates 5,000 batch job execution log records
├── process.py           # Core analytics pipeline — Pandas + Regex → summary.json
├── data/
│   ├── job_logs.csv     # Raw dataset (5,000 records, 9 columns)
│   └── summary.json     # Pre-processed aggregations consumed by the dashboard
├── index.html           # Interactive dashboard — reads summary.json, renders charts
├── .gitattributes       # Ensures GitHub shows Python as primary language
└── README.md
```

---

## Step-by-Step Pipeline

### Step 1 — Data Generation (`generate_data.py`)

**What it does:**
Simulates 5,000 batch job execution log records across 15 realistic financial job types (PORTF_RPT_DAILY, CASH_FLOW_EXTRACT, NAV_CALC_BATCH, etc.) over the full year 2024.

**Why simulate data?**
Real batch logs from financial systems are proprietary. Simulated data with realistic structure lets us demonstrate the full analytics pipeline. The job names, SLA thresholds, error codes, and failure rates are modelled after real mainframe batch environments.

**How the simulation works:**
- Each job has a defined SLA threshold in minutes — e.g. PORTF_RPT_DAILY must finish within 30 minutes
- Status is sampled with realistic weights: 65% SUCCESS, 15% FAILED, 8% ABENDED, 7% LATE, 5% RUNNING
- Duration is set based on status: FAILED jobs terminate early, LATE jobs run beyond SLA, others finish within threshold
- Error codes (RC=8, RC=12, ABEND S0C7, ABEND S222, JCL ERROR) are assigned only to FAILED and ABENDED runs

**Dataset columns:**

| Column | Description |
|---|---|
| job_name | Batch job identifier (e.g. PORTF_RPT_DAILY) |
| status | Execution outcome: SUCCESS / FAILED / ABENDED / LATE / RUNNING |
| start_time | Job start timestamp |
| end_time | Job end timestamp |
| duration_min | Actual execution time in minutes |
| sla_limit_min | Maximum allowed execution time for this job |
| sla_breached | Boolean — True if duration_min > sla_limit_min |
| error_code | RC=8, RC=12, ABEND S0C7, ABEND S222, JCL ERROR, or empty |
| run_date | Date portion of start_time |

---

### Step 2 — Analytics Pipeline (`process.py`)

This is the core of the project. It does everything a data analyst would do when handed a folder of raw batch logs.

**SLA Breach Detection:**
```python
df["sla_breached"] = df["duration_min"] > df["sla_limit_min"]
df["breach_delta"] = df["duration_min"] - df["sla_limit_min"]
```
Every job has a defined SLA threshold. We compare actual duration against it and flag breaches. `breach_delta` tells us by how much — useful for severity prioritisation.

**Error Code Classification via Regex:**
```python
rc_pattern    = re.compile(r"^RC=(\d+)$")
abend_pattern = re.compile(r"^ABEND\s+(\S+)$")
```
Raw error codes are classified into categories:
- `RETURN_CODE` — RC=8, RC=12 (controlled failures, often data issues)
- `ABEND` — S0C7, S222 (system-level crashes — more severe)
- `JCL_ERROR` — job control language syntax errors
- `NONE` — clean run

Why this matters: RC errors and ABEND errors require different response procedures. Grouping them in code mirrors how real operations teams triage incidents.

**Timestamp Anomaly Detection:**
```python
df["hour"] = df["start_time"].dt.hour
df["off_window"] = df["hour"].between(0, 4)
```
Jobs running between midnight and 4am are outside the expected batch window. Flagging these helps identify scheduling drift or unexpected reruns — a common real-world issue.

**Job Instability Scoring:**
```python
job_stats["instability_score"] = (
    job_stats["failure_rate_pct"] * 0.6 +
    job_stats["sla_breach_rate"] * 0.4
).round(1)
```
A single score combining failure rate (60% weight) and SLA breach rate (40% weight). Failure is weighted higher because a crashed job is worse than a slow job. This gives operations teams a ranked list of which jobs need attention — actionable, not just descriptive.

**Why 60/40 weighting?**
A job that fails frequently is more disruptive than one that merely runs slow — failures block downstream jobs and trigger alerts. SLA breaches matter but are recoverable. The 60/40 split reflects this priority.

**Daily Aggregations:**
```python
daily_failures = (
    df[df["status"].isin(["FAILED", "ABENDED"])]
    .groupby("run_date_str")
    .size()
    .reset_index(name="count")
)
```
Groupby + aggregation to produce day-level trend data for the dashboard. This is standard EDA pattern — from raw events to time-series.

**Output — `data/summary.json`:**
All aggregations are serialised to JSON for the dashboard. Key design choice: `allow_nan=False` with explicit NaN→null replacement prevents invalid JSON from Pandas NaN values — a common production bug.

---

### Step 3 — Dashboard (`index.html`)

Reads `data/summary.json` and renders:
- 5 KPI cards — total runs, failures, SLA breaches, failure rate, unique jobs
- Daily failure trend line chart
- Daily SLA breach trend line chart
- Top unstable jobs horizontal bar chart (ranked by instability score)
- Error code distribution doughnut chart
- Runs by status bar chart
- Avg execution time vs SLA limit grouped bar chart (per job)
- Filterable log table — filter by job name, status, date range; live search

---

## Key Concepts Demonstrated

**Pandas groupby and aggregation:**
Multiple `.groupby().agg()` patterns to produce summaries at day, job, and error-code level — standard data analyst workflow.

**Regex for structured extraction:**
Using compiled Regex patterns (`re.compile`) to parse and classify error codes from raw string fields — mirrors log parsing in production systems.

**Feature engineering:**
Creating derived columns — `breach_delta`, `off_window`, `instability_score` — that don't exist in raw data but are analytically meaningful.

**EDA patterns:**
Frequency distributions, time-series aggregations, ranked sorting — the building blocks of any exploratory analysis.

---

## Interview Talking Points

**"Tell me about your batch monitoring project"**
*"I built a Python pipeline that processes 5,000 batch job execution logs — similar to what I worked with at FIS. It does SLA breach detection by comparing actual run duration against per-job thresholds, classifies error codes using Regex into severity categories, and computes an instability score per job using a weighted formula combining failure rate and SLA breach rate. Results feed into an interactive dashboard I deployed on GitHub Pages."*

**"How did you detect SLA breaches?"**
*"Each job has a predefined SLA threshold in minutes. I compared the actual duration column against the threshold column and created a boolean flag. I also computed breach_delta — how far over the SLA the job ran — which is more useful than just a True/False flag because it tells you severity."*

**"Why did you use Regex for error classification?"**
*"Error codes in batch systems follow predictable patterns — RC codes always match `RC=\d+`, ABEND codes always match `ABEND \S+`. Regex gives precise, fast pattern matching on string fields. Using `re.compile()` pre-compiles the pattern so it's more efficient when applied across thousands of rows."*

**"What is an instability score and why did you create it?"**
*"Individual metrics like failure rate or SLA breach rate alone are incomplete. A job might fail rarely but always breach SLA, or fail often but finish quickly. The instability score combines both — 60% weight on failure rate and 40% on SLA breach rate — giving a single prioritisation signal for operations teams. It's the difference between descriptive analytics and actionable analytics."*

**"How does this relate to your work at FIS?"**
*"At FIS I worked with real batch job logs for financial transaction processing. I built Python scripts that automated parsing of 5,000+ job logs using Regex and Pandas to monitor SLA breaches and flag unstable jobs. That work reduced manual triage effort by 40% and helped the team shift from reactive incident response to proactive monitoring."*

**"How would you scale this to production?"**
1. Replace simulated CSV with a real log ingestion layer — read from a shared directory or database
2. Schedule `process.py` with a cron job or Control-M to run nightly after the batch window closes
3. Add alerting — send email or Slack notification when instability score exceeds threshold
4. Store historical summaries to trend job health week-over-week

---

## Running Locally

```bash
git clone https://github.com/aiwithkd/job-failure-dashboard
cd job-failure-dashboard

pip install pandas numpy

python generate_data.py   # creates data/job_logs.csv
python process.py         # creates data/summary.json

python -m http.server 8000
# open http://localhost:8000
```

## Tech Stack

| Tool | Version | Role |
|---|---|---|
| Python | 3.9+ | Pipeline orchestration |
| Pandas | 2.0+ | Data loading, aggregation, feature engineering |
| NumPy | 1.26+ | Numerical operations |
| Regex (re) | stdlib | Error code extraction and classification |
| Chart.js | 4.4.2 | Dashboard visualisations |
| GitHub Pages | — | Static hosting |

---

---

## Challenges Faced During Implementation

### 1. SLA breach detection needed per-job thresholds, not a global value

**Problem:** The first version used a single global SLA threshold (30 minutes) for all jobs. This flagged fast jobs like `FX_RATE_LOAD` (SLA: 10 min) as fine when they ran for 25 minutes, and missed breaches on slower jobs like `EOD_CLOSE_PROC` (SLA: 70 min) that finished in 65 minutes.

**Resolution:** Moved SLA thresholds into a per-job dictionary (`SLA_MINUTES`) in the generation script and carried them through as a column in the dataset. The breach flag is computed row-by-row as `duration_min > sla_limit_min` rather than against any global constant.

---

### 2. Instability score needed to reflect both failure rate AND SLA breach rate

**Problem:** Ranking jobs by failure rate alone missed jobs that rarely failed outright but consistently ran over SLA — a different kind of operational risk that is just as impactful.

**Resolution:** Defined a composite instability score: `failure_rate * 0.6 + sla_breach_rate * 0.4`. The 60/40 weighting reflects that hard failures are more severe than SLA slips, but both matter. This gave `TRADE_SETTLE_CHK` the highest instability score despite not having the highest raw failure rate.

---

### 3. Timestamp anomaly detection — defining "off window" correctly

**Problem:** Flagging jobs that run between midnight and 4am sounds simple but the initial logic used `start_time.hour < 4` which missed jobs that started at 11:58pm and ran past midnight — the start time was fine but the execution window was anomalous.

**Resolution:** Kept the check on `start_time.hour` for simplicity since the dataset uses start time as the primary signal. Added a note in the code that a production version should check both start and end time windows. This is a documented limitation, not a silent bug.

---

### 4. JSON serialization failing on pandas NaN values

**Problem:** `json.dump()` threw errors when the summary dict contained `NaN` values from pandas aggregations — for example, average breach delta when there were no breaches for a job.

**Resolution:** Used `json.dump(..., allow_nan=False, default=lambda x: None if isinstance(x, float) and x != x else str(x))` — this converts `NaN` to JSON `null` rather than the invalid `NaN` literal that standard JSON does not support.

---

### 5. Dashboard filter state resets on page reload

**Problem:** The date range and job name filters reset every time the page reloaded, which was frustrating when analysing a specific job or date range across multiple views.

**Resolution:** For a static GitHub Pages deployment, persisting filter state would require URL query params or localStorage. Given this is a portfolio demo, the decision was to keep it stateless — filters are fast to re-apply and the added complexity was not worth it for a read-only dashboard. Documented as a known limitation.

---

## Future Scope

This dashboard runs entirely on static pre-processed data — no server, no database, no APIs. Extensions the architecture already supports:

- **Predictive failure scoring** — train a scikit-learn model on historical job features (hour of day, day of week, recent failure streak, duration trend) to predict next-run failure probability. The pipeline already produces all the features needed.
- **Real log ingestion** — replace the synthetic generator with a parser for real mainframe job logs (JES2/JES3 output, Control-M exports). The column schema is already modelled on real mainframe log formats.
- **Alerting integration** — add a threshold check in `process.py` that writes an `alerts.json` file when instability scores exceed a defined limit, consumable by PagerDuty or a Slack webhook.
- **Live streaming version** — replace the static `summary.json` with a WebSocket feed to render the dashboard in real time as jobs complete, converting this from a historical analytics tool to an operational monitoring tool.
- **LLM-powered root cause suggestions** — findings are already structured as JSON. An LLM layer could generate natural language root cause hypotheses per job based on error code patterns and failure streaks, without changing the core pipeline.

---

*Built by [Kunal Deokar](https://github.com/aiwithkd)*

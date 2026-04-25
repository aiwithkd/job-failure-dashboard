# Job Failure Dashboard

Interactive dashboard for monitoring batch job failures, SLA breaches, and execution anomalies across a simulated financial processing environment.

**Live Demo → [aiwithkd.github.io/job-failure-dashboard](https://aiwithkd.github.io/job-failure-dashboard)**

---

## What This Project Does

Parses and analyzes 5,000 simulated batch job execution logs using Python, Pandas, and Regex — then visualizes the results in an interactive browser-based dashboard.

The analysis covers:
- SLA breach detection by comparing actual run duration against per-job thresholds
- Regex-based error code extraction and classification (RC codes, ABEND types, JCL errors)
- Instability scoring per job — weighted combination of failure rate and SLA breach rate
- Timestamp anomaly flagging for jobs running outside expected execution windows
- Daily trend aggregations for failures and SLA breaches across the year

## Repository Structure

```
job-failure-dashboard/
├── generate_data.py     # Generates 5,000 simulated job log records → data/job_logs.csv
├── process.py           # Core analytics: Pandas + Regex processing → data/summary.json
├── data/
│   ├── job_logs.csv     # Raw dataset (5,000 records)
│   └── summary.json     # Pre-processed aggregations consumed by the dashboard
├── index.html           # Dashboard UI — reads summary.json, renders charts
└── README.md
```

## How to Use the Dashboard

Open the [live link](https://aiwithkd.github.io/job-failure-dashboard) — no setup needed.

- Use the filters at the top to narrow by **Job Name**, **Status**, or **Date Range**
- Click **Apply Filters** to refresh the log table
- Charts reflect the full pre-processed dataset from `process.py`

## Running Locally

```bash
git clone https://github.com/aiwithkd/job-failure-dashboard
cd job-failure-dashboard

pip install pandas numpy

python generate_data.py   # creates data/job_logs.csv
python process.py         # creates data/summary.json

# serve locally (required for fetch to work)
python -m http.server 8000
# open http://localhost:8000
```

## Tech Stack

| Tool | Role |
|---|---|
| Python | Data generation and analytics pipeline |
| Pandas | Aggregations, groupby, feature engineering |
| NumPy | Numerical operations |
| Regex | Error code extraction and classification |
| Chart.js | Dashboard visualizations |
| GitHub Pages | Static hosting |

---

*Built by [Kunal Deokar](https://github.com/aiwithkd)*

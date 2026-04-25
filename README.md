# Job Failure Dashboard

An interactive dashboard for monitoring batch job failures, SLA breaches, and execution anomalies — built with Python (Pyodide) running entirely in the browser. No server, no setup.

**Live Demo → [aiwithkd.github.io/job-failure-dashboard](https://aiwithkd.github.io/job-failure-dashboard)**

---

## What This Project Does

Simulates 5,000 batch job execution logs from a financial processing environment and provides real-time visual analysis of:

- Daily failure trends across the year
- SLA breach frequency per job
- Top unstable jobs ranked by failure count
- Error code breakdown (RC=8, RC=12, ABEND S0C7, etc.)
- Average execution time vs SLA limit per job
- Filterable log table with status badges

## How to Use the Dashboard

1. Open the [live link](https://aiwithkd.github.io/job-failure-dashboard)
2. Wait ~10 seconds for the Python runtime (Pyodide) to load in your browser
3. Use the filters at the top to narrow by **Job Name**, **Status**, or **Date Range**
4. Click **Apply** to refresh all charts and the log table

All processing happens in your browser — no data is sent to any server.

## How It Works

| Layer | Technology |
|---|---|
| Data generation | Python (NumPy, Pandas) via Pyodide |
| Charts | Chart.js |
| Hosting | GitHub Pages (static) |
| UI | Vanilla HTML/CSS/JS |

[Pyodide](https://pyodide.org) compiles CPython to WebAssembly, letting real Python code run directly in the browser. The dataset of 5,000 job logs is generated fresh on each page load using seeded random values, so results are always consistent.

## Repository Structure

```
job-failure-dashboard/
└── index.html    # entire app — data generation, charts, filters, table
```

## Running Locally

No build step needed. Just open the file:

```bash
git clone https://github.com/aiwithkd/job-failure-dashboard
cd job-failure-dashboard
open index.html   # or double-click the file
```

Requires an internet connection to load Pyodide and Chart.js from CDN.

---

*Built by [Kunal Deokar](https://github.com/aiwithkd)*

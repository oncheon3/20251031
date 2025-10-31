# temp.csv Dataset Overview

This repository contains a single dataset, `temp.csv`, with daily price and volume data for three tickers:

- **005930.KS** – Samsung Electronics Co., Ltd. (KRX)
- **AAPL** – Apple Inc. (NASDAQ)
- **NVDA** – NVIDIA Corporation (NASDAQ)

Each trading day lists the close, high, low, open, and volume figures for every ticker. The file follows a multi-row header where the first row enumerates the metric, the second row provides the ticker symbol, and the third row starts the actual date-indexed records.

## File Structure

| Column group | Description |
| --- | --- |
| `Date` | Trading date in ISO format (`YYYY-MM-DD`). |
| `Close`, `High`, `Low`, `Open`, `Volume` (per ticker) | Market data for each ticker. The columns appear in blocks, one metric at a time, following the pattern `Close`, `High`, `Low`, `Open`, `Volume` for Samsung (`005930.KS`), Apple (`AAPL`), and NVIDIA (`NVDA`). |

The dataset covers **2023-10-16** through **2025-10-10**, providing 516 trading days in total (some tickers have fewer records due to missing values).【F:temp.csv†L1-L515】

## Summary Statistics

The table below summarizes key statistics for each ticker and metric, including the most recent values on **2025-10-10**.

### 005930.KS (Samsung Electronics)

| Metric | Count | Mean | Min | Max | Latest (2025-10-10) |
|---|---:|---:|---:|---:|---:|
| Close | 482 | 66,471.53 | 48,968.97 | 94,400.00 | 94,400.00 |
| High | 482 | 67,202.08 | 50,784.92 | 94,500.00 | 94,500.00 |
| Low | 482 | 65,822.65 | 48,968.97 | 92,700.00 | 92,700.00 |
| Open | 482 | 66,509.00 | 49,263.38 | 94,000.00 | 94,000.00 |
| Volume | 482 | 19,481,204.69 | 2,957,915.00 | 57,691,266.00 | 35,269,748.00 |

### AAPL (Apple)

| Metric | Count | Mean | Min | Max | Latest (2025-10-10) |
|---|---:|---:|---:|---:|---:|
| Close | 499 | 209.52 | 163.82 | 258.10 | 245.27 |
| High | 499 | 211.47 | 165.21 | 259.24 | 256.38 |
| Low | 499 | 207.33 | 162.91 | 256.72 | 244.00 |
| Open | 499 | 209.29 | 164.17 | 257.99 | 254.94 |
| Volume | 499 | 56,558,297.39 | 23,234,700.00 | 318,679,900.00 | 61,782,400.00 |

### NVDA (NVIDIA)

| Metric | Count | Mean | Min | Max | Latest (2025-10-10) |
|---|---:|---:|---:|---:|---:|
| Close | 499 | 115.60 | 40.30 | 192.57 | 183.16 |
| High | 499 | 117.54 | 40.85 | 195.62 | 195.62 |
| Low | 499 | 113.41 | 39.21 | 191.06 | 182.05 |
| Open | 499 | 115.59 | 40.43 | 193.51 | 193.51 |
| Volume | 499 | 325,122,504.81 | 105,157,000.00 | 1,142,269,000.00 | 266,534,400.00 |

## How to Reproduce the Summary

Use Python’s standard library to parse the multi-row header and compute summary statistics:

```python
import csv
from collections import defaultdict

path = "temp.csv"
metrics = ["Close", "High", "Low", "Open", "Volume"]

with open(path) as f:
    reader = csv.reader(f)
    header = next(reader)
    tickers = next(reader)
    next(reader)  # skip the blank header row
    rows = [row for row in reader if row and any(cell.strip() for cell in row)]

col_info = [(idx, tkr, metric) for idx, (metric, tkr) in enumerate(zip(header[1:], tickers[1:]), start=1)]
values = defaultdict(lambda: {m: [] for m in metrics})

for row in rows:
    for idx, ticker, metric in col_info:
        if idx < len(row) and row[idx]:
            values[ticker][metric].append(float(row[idx]))
```

The resulting `values` dictionary can be used to calculate counts, means, minimums, maximums, and any additional analytics required.

## Efficient Frontier Web App

An interactive Flask dashboard renders the efficient frontier based on the same dataset. To run it locally:

1. Install dependencies: `pip install -r requirements.txt`
2. Start the development server: `python app.py`
3. Open your browser at http://localhost:5000 to explore the chart and portfolio breakdowns.

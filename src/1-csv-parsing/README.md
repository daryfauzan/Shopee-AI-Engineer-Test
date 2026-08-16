# CSV Parsing & Analysis

Parses and analyzes a customer dataset provided as two CSV files of different sizes, demonstrating two different strategies:

- **Small file (100K rows)** — load fully into memory with `pandas` and explore interactively in a notebook.
- **Large file (2M rows)** — stream the file in chunks with `pandas`' `chunksize`, aggregating statistics on the fly so peak memory stays flat regardless of file size.

## Table of contents

1. [Project structure](#project-structure)
2. [Setup](#setup)
3. [Usage](#usage)
4. [Small vs. large file parsing](#small-vs-large-file-parsing)
5. [Key insights (customer-100000.csv)](#key-insights-customer-100000csv)

## Project structure

```
1-csv-parsing/
├── main.py                        # Downloads both datasets, loads the small CSV
├── notebook/
│   └── customer_analysis.ipynb    # Full EDA on customer-100000.csv
├── scripts/
│   ├── download_data.py           # Downloads (and unzips, if needed) a CSV from a URL via gdown
│   ├── parse_small_csv.py         # Full-file loader (pandas.read_csv)
│   └── parse_large_csv.py         # Chunked/streaming parser with memory profiling
├── data/                          # Downloaded CSVs (gitignored, created on first run)
├── .env                           # Local config (gitignored, see Setup)
├── pyproject.toml
└── README.md
```

## Setup

1. Requires Python 3.11+ (see `.python-version`) and [uv](https://github.com/astral-sh/uv).
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Create a `.env` file in this folder with the dataset locations:
   ```
   SMALL_CSV_FILE_URL=<url to customer-100000.csv (or a zip containing it)>
   SMALL_CSV_FILE_NAME=customer-100000.csv
   LARGE_CSV_FILE_URL=<url to customer-2000000.csv (or a zip containing it)>
   LARGE_CSV_FILE_NAME=customer-2000000.csv
   DATA_DIR_PATH=.
   ```
   `download_data()` skips re-downloading if the target file already exists under `data/`.

## Usage

- `uv run main.py` — downloads both datasets into `data/` and loads the small CSV.
- `uv run jupyter lab notebook/customer_analysis.ipynb` — full EDA on the small dataset.
- `cd scripts && uv run python parse_large_csv.py` — streams the large dataset in 50,000-row chunks, aggregating stats without loading the whole file into memory, printing per-chunk memory usage.
  > Run from `scripts/` since the script loads `../.env` relative to its own location.

## Small vs. large file parsing

| | Small CSV (100K rows) | Large CSV (2M rows) |
|---|---|---|
| Where | `notebook/customer_analysis.ipynb` | `scripts/parse_large_csv.py` |
| Method | `pandas.read_csv` (full load) | `pandas.read_csv(..., chunksize=50_000)` streaming |
| Columns loaded | all | only what's needed for aggregation (`usecols`) |
| Aggregation | computed once over the full DataFrame | accumulated incrementally per chunk (`collections.Counter`) |
| Memory | not measured — full 100K-row frame held at once | tracked per chunk with `tracemalloc` |
| Output | rich EDA: plots, dtype/missing/duplicate breakdowns | streaming aggregates: country counts, subscription-month counts, missing values, invalid/duplicate emails |

### Memory profile (large CSV, chunk size = 50,000 rows)

Peak memory plateaus around ~30 MB after the first couple of chunks and stays flat through all 2,000,000 rows / 40 chunks — confirming the streaming approach scales independently of file size:

| Chunk | Rows processed | Current memory | Peak memory |
|---|---|---|---|
| 1 | 50,000 | 14.88 MB | 17.94 MB |
| 2 | 100,000 | 14.91 MB | 30.12 MB |
| 10 | 500,000 | 14.91 MB | 30.15 MB |
| 20 | 1,000,000 | 14.92 MB | 30.16 MB |
| 30 | 1,500,000 | 14.93 MB | 30.16 MB |
| 40 | 2,000,000 | 14.41 MB | 30.17 MB |

<details>
<summary>Full per-chunk log (40 chunks)</summary>

| Chunk | Rows processed | Current memory | Peak memory |
|---|---|---|---|
| 1 | 50,000 | 14.88 MB | 17.94 MB |
| 2 | 100,000 | 14.91 MB | 30.12 MB |
| 3 | 150,000 | 14.89 MB | 30.13 MB |
| 4 | 200,000 | 14.90 MB | 30.13 MB |
| 5 | 250,000 | 14.91 MB | 30.13 MB |
| 6 | 300,000 | 14.91 MB | 30.13 MB |
| 7 | 350,000 | 14.92 MB | 30.14 MB |
| 8 | 400,000 | 14.43 MB | 30.14 MB |
| 9 | 450,000 | 14.92 MB | 30.15 MB |
| 10 | 500,000 | 14.91 MB | 30.15 MB |
| 11 | 550,000 | 14.90 MB | 30.15 MB |
| 12 | 600,000 | 14.92 MB | 30.15 MB |
| 13 | 650,000 | 14.91 MB | 30.15 MB |
| 14 | 700,000 | 14.92 MB | 30.15 MB |
| 15 | 750,000 | 14.93 MB | 30.16 MB |
| 16 | 800,000 | 14.92 MB | 30.16 MB |
| 17 | 850,000 | 14.91 MB | 30.16 MB |
| 18 | 900,000 | 14.90 MB | 30.16 MB |
| 19 | 950,000 | 14.93 MB | 30.16 MB |
| 20 | 1,000,000 | 14.92 MB | 30.16 MB |
| 21 | 1,050,000 | 14.92 MB | 30.16 MB |
| 22 | 1,100,000 | 14.44 MB | 30.16 MB |
| 23 | 1,150,000 | 14.92 MB | 30.16 MB |
| 24 | 1,200,000 | 14.92 MB | 30.16 MB |
| 25 | 1,250,000 | 14.92 MB | 30.16 MB |
| 26 | 1,300,000 | 14.92 MB | 30.16 MB |
| 27 | 1,350,000 | 14.93 MB | 30.16 MB |
| 28 | 1,400,000 | 14.92 MB | 30.16 MB |
| 29 | 1,450,000 | 14.90 MB | 30.16 MB |
| 30 | 1,500,000 | 14.93 MB | 30.16 MB |
| 31 | 1,550,000 | 14.91 MB | 30.16 MB |
| 32 | 1,600,000 | 14.91 MB | 30.16 MB |
| 33 | 1,650,000 | 14.93 MB | 30.16 MB |
| 34 | 1,700,000 | 14.94 MB | 30.17 MB |
| 35 | 1,750,000 | 14.93 MB | 30.17 MB |
| 36 | 1,800,000 | 14.93 MB | 30.17 MB |
| 37 | 1,850,000 | 14.93 MB | 30.17 MB |
| 38 | 1,900,000 | 14.93 MB | 30.17 MB |
| 39 | 1,950,000 | 14.93 MB | 30.17 MB |
| 40 | 2,000,000 | 14.41 MB | 30.17 MB |

</details>

## Key insights (customer-100000.csv)

Full analysis in [`notebook/customer_analysis.ipynb`](notebook/customer_analysis.ipynb). Summary below.

### Data quality

| Metric | Value |
|---|---|
| Total rows | 100,000 |
| Duplicate rows | 0 |
| Duplicate Customer IDs | 0 |
| Duplicate emails | 5 |
| Invalid emails | 0 |
| Rows with any missing value | 0 |

### Geographic concentration

Top 5 countries represent only **3.03%** of customers — the customer base is broadly distributed geographically, with no single country or small set of countries dominating.

### Subscription trends

- Subscription dates range from **2020-01-01** to **2022-05-29**.
- Year-over-year:

  | Year | Customers | Growth |
  |---|---|---|
  | 2020 | 41,898 | — |
  | 2021 | 41,211 | -1.64% |
  | 2022 | 16,891 | -59.01% |

  The 2022 drop reflects a partial year (data ends in May 2022), not necessarily a real decline in subscriptions.

## Notes

- `.env`, `.venv`, and `data/` are gitignored. `data/` is populated on first run by `download_data()` (via `main.py` or the notebook) and re-download is skipped if the file already exists.

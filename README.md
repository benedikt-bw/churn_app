# Music Streaming Churn Dashboard

A Streamlit dashboard for exploring user-level churn snapshots from a music
streaming dataset. The dashboard focuses on clean data loading, snapshot
filtering, churn metrics, and simple visual analysis.

## Requirements

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/)
- The local Parquet dataset described below

## Setup

Install the project dependencies and create the local environment with:

```bash
uv sync
```

The project uses `pyproject.toml` for dependency declarations and `uv.lock` to
keep installations reproducible.

## Data

The application expects this file:

```text
data/03_10_day_window_sliced.parquet
```

The file is intentionally excluded from Git because it is a processed dataset.
Place a local copy in the `data/` directory before starting the application.
The repository also contains `data/train_sample.csv`, a small raw event-data
sample for reference; it is not loaded by the dashboard.

The Parquet dataset must contain the columns used by the dashboard:

- `userId`
- `snapshot_day`
- `label` (`0` or `1`)
- `active_days`
- `gender`
- `operating_system`

The application validates these columns and their values when loading the data.

## Run the dashboard

Start Streamlit with:

```bash
uv run streamlit run app.py
```

The dashboard lets you select a snapshot day and displays:

- User count, churn rate, and average active days
- Gender and operating-system distributions
- Churned versus non-churned users
- Churn rate across snapshot days
- A preview of the selected snapshot data

## Run with Docker

Build the image from the project root:

```bash
docker build -t music-churn-dashboard .
```

The image does not include the ignored dataset. Mount the local `data/`
directory when starting the container:

```bash
docker run --rm -p 8501:8501 \
  -v "$(pwd)/data:/app/data:ro" \
  music-churn-dashboard
```

Open <http://localhost:8501> in a browser.

## Test and quality checks

Run the test suite with coverage:

```bash
uv run pytest --cov=.
```

Run Ruff formatting and lint checks:

```bash
uv run ruff format .
uv run ruff check .
```

## Project structure

```text
.
├── app.py                         # Streamlit application
├── dashboard.py                   # Data loading and metric utilities
├── data/                          # Local datasets, excluded from Git
├── tests/test_app.py              # Data-layer unit tests
├── Dockerfile                     # Container image definition
├── .gitlab-ci.yml                 # CI quality and test pipeline
├── pyproject.toml                 # Project and tool configuration
├── uv.lock                        # Locked dependency versions
└── README.md                      # Project documentation
```

## Current scope

This project currently provides an exploratory dashboard over prepared churn
snapshots. Model training, prediction, and automated data-pipeline generation
are outside the current application scope.

[![CI](https://github.com/benedikt-bw/churn_app/actions/workflows/ci.yml/badge.svg)](https://github.com/benedikt-bw/churn_app/actions/workflows/ci.yml)

# Music Streaming Churn Dashboard

A containerized Streamlit dashboard for exploring prepared user-level churn
snapshots from a music streaming dataset. The project focuses on reproducible
data loading, validation, filtering, aggregation, and visual analysis. Machine
learning is intentionally outside its scope.

## Quick start

Requirements:

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/)

Install the locked dependencies and start the application:

```bash
uv sync
uv run streamlit run app.py
```

Open <http://localhost:8501>. No external data download is required: a small,
identifier-remapped sample is committed so the application works from a fresh
clone.

The project uses `pyproject.toml` for dependency declarations and `uv.lock` for
reproducible installations. Matplotlib is included because the risk matrix
uses Pandas Styler's `background_gradient`.

## Data

By default, the application chooses its input in this order:

1. The path in the `CHURN_DATA_PATH` environment variable
2. The ignored full dataset at `data/03_10_day_window_sliced.parquet`
3. The committed sample at `data/churn_sample.parquet`

The bundled sample contains 1,000 rows: 250 deterministic, label-stratified
rows from each available snapshot day. It includes only dashboard fields, and
source user identifiers are remapped to sequential values. See
[`data/README.md`](data/README.md) for its schema, generation method, and
provenance notes.

The full engineered dataset was created by the project author from an
unrestricted, publicly available music-streaming source dataset for a final
machine-learning project at École Polytechnique. The upstream raw event data is
not distributed in this repository.

To use another compatible Parquet file:

```bash
CHURN_DATA_PATH=/absolute/path/to/dataset.parquet \
  uv run streamlit run app.py
```

The dataset must contain:

- `userId`
- `snapshot_day`
- `label` (`0` or `1`)
- `active_days`
- `gender`
- `operating_system`
- `browser`
- `last_level`
- `avg_songs_session`
- `hours_since_last_session`
- `is_new_user`

The application rejects empty data, missing columns or values, invalid labels,
negative snapshot days, and incompatible numeric types before rendering.

### Regenerate the sample

With the ignored full dataset available at its default path, run:

```bash
uv run python -m scripts.create_sample
```

The script uses a fixed seed and remaps user identifiers, so its output is
repeatable. The full dataset remains excluded from version control.

## Dashboard features

The snapshot selector controls the snapshot-specific metrics and charts. The
dashboard provides:

- User count, churn rate, and average active days
- Gender and operating-system distributions
- Churned versus non-churned users
- Churn rate across snapshot days
- Churn rates by subscription level, browser, and operating system
- Churn rates across active-day engagement bands
- Engagement and inactivity trends
- A new-user versus subscription-level churn risk matrix
- An optional preview of the selected data

When the bundled sample is active, the page displays a notice. The visual theme
in `.streamlit/config.toml` coordinates the page, charts, metrics, and tables.

## Docker

Build and run the self-contained image from the project root:

```bash
docker build -t music-churn-dashboard .
docker run --rm -p 8501:8501 music-churn-dashboard
```

The image includes the bundled sample, so no volume is required. To use a full
dataset instead, mount the file and select it with the environment variable:

```bash
docker run --rm -p 8501:8501 \
  -v "/absolute/path/to/dataset.parquet:/app/data/full.parquet:ro" \
  -e CHURN_DATA_PATH=/app/data/full.parquet \
  music-churn-dashboard
```

## Tests and quality checks

Run the required checks with:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest --cov=.
```

Tests cover data loading, path resolution, schema validation, filtering,
aggregations, sample generation, and the committed sample itself. The
Streamlit rendering script is excluded from unit coverage because importing it
starts the interactive page.

GitHub Actions repeats the formatting, lint, coverage, and Docker build checks
on every push and pull request. The workflow is defined in
`.github/workflows/ci.yml`.

## Project structure

```text
.
├── app.py                         # Streamlit presentation layer
├── dashboard.py                   # Data loading and aggregation layer
├── .streamlit/config.toml         # Shared dark theme and chart palette
├── data/
│   ├── README.md                  # Sample schema and provenance
│   └── churn_sample.parquet       # Committed runnable sample
├── scripts/create_sample.py        # Reproducible sample generator
├── tests/test_app.py               # Data-layer and sample tests
├── Dockerfile                     # Container image definition
├── .github/workflows/ci.yml       # CI quality and build pipeline
├── pyproject.toml                 # Dependencies and tool configuration
├── uv.lock                        # Exact dependency resolution
└── README.md                      # Project documentation
```

## Reproducibility and scope

- Runtime and development dependencies are locked with `uv.lock`.
- The sample and its generation process are included in the repository.
- Input data is validated before use.
- Aggregation and filtering behavior is unit tested.
- CI checks formatting, linting, tests, coverage, and the Docker build.
- The container runs with committed data and can accept a mounted full dataset.

The project provides exploratory analysis over prepared churn snapshots. Model
training, prediction, and automated raw-data pipelines are not included.

## Repository

GitHub: <https://github.com/benedikt-bw/churn_app>

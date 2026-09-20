"""Load, validate, and aggregate data for the churn dashboard."""

import os
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
FULL_DATA_PATH = PROJECT_ROOT / "data/03_10_day_window_sliced.parquet"
SAMPLE_DATA_PATH = PROJECT_ROOT / "data/churn_sample.parquet"
DATA_PATH_ENV_VAR = "CHURN_DATA_PATH"
REQUIRED_COLUMNS = {
    "userId": "integer",
    "snapshot_day": "integer",
    "label": "integer",
    "active_days": "numeric",
    "gender": "categorical",
    "operating_system": "categorical",
    "browser": "categorical",
    "last_level": "categorical",
    "avg_songs_session": "numeric",
    "hours_since_last_session": "numeric",
    "is_new_user": "integer",
}


def resolve_data_path(configured_path: Path | None = None) -> Path:
    """Resolve the configured, full, or bundled sample dataset path."""
    if configured_path is not None:
        if configured_path.exists():
            return configured_path
        raise FileNotFoundError(
            f"Configured churn dataset not found: {configured_path}."
        )

    environment_path = os.getenv(DATA_PATH_ENV_VAR)
    if environment_path:
        path = Path(environment_path).expanduser()
        if path.exists():
            return path
        raise FileNotFoundError(
            f"Dataset configured by {DATA_PATH_ENV_VAR} not found: {path}."
        )

    for path in (FULL_DATA_PATH, SAMPLE_DATA_PATH):
        if path.exists():
            return path

    raise FileNotFoundError(
        "No churn dataset found. Add the full dataset at "
        f"{FULL_DATA_PATH} or restore the bundled sample at {SAMPLE_DATA_PATH}."
    )


def validate_data(df: pd.DataFrame) -> None:
    """Validate the columns and values required by the dashboard."""
    if df.empty:
        raise ValueError("The churn dataset is empty.")

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"The churn dataset is missing required columns: {missing}.")

    for column, expected_type in REQUIRED_COLUMNS.items():
        dtype = df[column].dtype
        if expected_type == "integer" and not pd.api.types.is_integer_dtype(dtype):
            raise TypeError(f"Column '{column}' must contain integer values.")
        if expected_type == "numeric" and not pd.api.types.is_numeric_dtype(dtype):
            raise TypeError(f"Column '{column}' must contain numeric values.")

    required_values = df[list(REQUIRED_COLUMNS)]
    if required_values.isna().any().any():
        columns = ", ".join(required_values.columns[required_values.isna().any()])
        raise ValueError(f"Required columns contain missing values: {columns}.")

    labels = set(df["label"].unique())
    if not labels.issubset({0, 1}):
        raise ValueError("Column 'label' must contain only 0 or 1.")

    if (df["snapshot_day"] < 0).any():
        raise ValueError("Column 'snapshot_day' must contain non-negative values.")


def load_data(path: Path) -> pd.DataFrame:
    """Load the engineered churn dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Churn dataset not found: {path}.")

    try:
        df = pd.read_parquet(path)
    except (OSError, ValueError) as error:
        raise ValueError(f"Could not read the Parquet dataset at {path}.") from error

    validate_data(df)
    return df


def filter_snapshot(df: pd.DataFrame, snapshot_day: int) -> pd.DataFrame:
    """Filter the dataset to one snapshot day."""
    return df[df["snapshot_day"] == snapshot_day]


def calculate_metrics(df: pd.DataFrame) -> tuple[int, float, float]:
    """Calculate user count, churn rate, and average active days."""
    unique_users = df["userId"].nunique()
    churn_rate = df["label"].mean() * 100
    avg_active_days = df["active_days"].mean()
    return unique_users, churn_rate, avg_active_days


def calculate_churn_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the churn rate for each snapshot day."""
    return (
        df.groupby("snapshot_day")["label"]
        .mean()
        .mul(100)
        .reset_index(name="Churn Rate (%)")
    )


def calculate_churn_by_group(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Calculate users and churn rate for each group."""
    result = (
        df.groupby(group_column, observed=True, dropna=False)
        .agg(Users=("userId", "nunique"), churn_rate=("label", "mean"))
        .reset_index()
    )
    result["Churn Rate (%)"] = result.pop("churn_rate") * 100
    return result.sort_values("Churn Rate (%)", ascending=False).reset_index(drop=True)


def calculate_engagement_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate average engagement signals for each snapshot day."""
    return (
        df.groupby("snapshot_day", as_index=False)
        .agg(
            **{
                "Avg Active Days": ("active_days", "mean"),
                "Avg Songs / Session": ("avg_songs_session", "mean"),
                "Avg Hours Since Last Session": (
                    "hours_since_last_session",
                    "mean",
                ),
            }
        )
        .sort_values("snapshot_day")
    )


def calculate_activity_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate churn across active-day bands."""
    bands = pd.cut(
        df["active_days"],
        bins=[0, 3, 7, 14, float("inf")],
        labels=["1–3 days", "4–7 days", "8–14 days", "15+ days"],
    )
    activity_data = df.assign(activity_band=bands)
    result = (
        activity_data.groupby("activity_band", observed=False)
        .agg(Users=("userId", "nunique"), churn_rate=("label", "mean"))
        .reset_index()
        .dropna(subset=["activity_band"])
        .query("Users > 0")
    )
    result["Churn Rate (%)"] = result.pop("churn_rate") * 100
    result = result.rename(columns={"activity_band": "Activity Band"})
    return result


def calculate_churn_matrix(
    df: pd.DataFrame, row_column: str, column_column: str
) -> pd.DataFrame:
    """Calculate a churn-rate matrix for two user segments."""
    return (
        pd.pivot_table(
            df,
            index=row_column,
            columns=column_column,
            values="label",
            aggfunc="mean",
            observed=True,
        )
        .mul(100)
        .sort_index()
    )

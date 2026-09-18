from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/03_10_day_window_sliced.parquet")
REQUIRED_COLUMNS = {
    "userId": "integer",
    "snapshot_day": "integer",
    "label": "integer",
    "active_days": "numeric",
    "gender": "categorical",
    "operating_system": "categorical",
}


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

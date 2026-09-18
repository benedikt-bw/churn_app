from pathlib import Path

import pandas as pd
import pytest

from app import (
    calculate_churn_by_day,
    calculate_metrics,
    filter_snapshot,
    load_data,
    validate_data,
)


def make_valid_data() -> pd.DataFrame:
    """Create a valid minimal dataset for dashboard tests."""
    return pd.DataFrame(
        {
            "userId": [1, 2, 3],
            "snapshot_day": [9, 9, 19],
            "label": [0, 1, 0],
            "active_days": [2, 4, 6],
            "gender": ["F", "M", "F"],
            "operating_system": ["Macintosh", "Windows", "Linux"],
        }
    )


def test_load_data_reads_valid_parquet(tmp_path: Path) -> None:
    """Load and validate a valid Parquet dataset."""
    source = make_valid_data()
    path = tmp_path / "dataset.parquet"
    source.to_parquet(path)

    result = load_data(path)

    pd.testing.assert_frame_equal(result, source)


def test_load_data_raises_for_missing_file(tmp_path: Path) -> None:
    """Raise a clear error when the dataset file is missing."""
    with pytest.raises(FileNotFoundError, match="not found"):
        load_data(tmp_path / "missing.parquet")


def test_filter_snapshot_returns_selected_day() -> None:
    """Return only rows belonging to the selected snapshot day."""
    data = make_valid_data()

    result = filter_snapshot(data, 9)

    assert result["userId"].tolist() == [1, 2]


def test_calculate_metrics_returns_dashboard_values() -> None:
    """Calculate the dashboard's summary metrics."""
    data = make_valid_data()

    users, churn_rate, active_days = calculate_metrics(data)

    assert users == 3
    assert churn_rate == pytest.approx(100 / 3)
    assert active_days == pytest.approx(4.0)


def test_calculate_churn_by_day_returns_percentages() -> None:
    """Calculate churn percentages for each snapshot day."""
    data = make_valid_data()

    result = calculate_churn_by_day(data)

    expected = pd.DataFrame(
        {
            "snapshot_day": [9, 19],
            "Churn Rate (%)": [50.0, 0.0],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_validate_data_accepts_valid_data() -> None:
    """Accept data that satisfies the dashboard contract."""
    validate_data(make_valid_data())


def test_validate_data_rejects_missing_columns() -> None:
    """Reject data without all required columns."""
    data = make_valid_data().drop(columns="label")

    with pytest.raises(ValueError, match="missing required columns: label"):
        validate_data(data)


def test_validate_data_rejects_invalid_labels() -> None:
    """Reject labels outside the binary churn contract."""
    data = make_valid_data()
    data["label"] = [0, 1, 2]

    with pytest.raises(ValueError, match="only 0 or 1"):
        validate_data(data)


def test_validate_data_rejects_missing_required_values() -> None:
    """Reject missing values in required columns."""
    data = make_valid_data()
    data.loc[0, "active_days"] = None

    with pytest.raises(ValueError, match="missing values: active_days"):
        validate_data(data)


def test_validate_data_rejects_invalid_snapshot_day() -> None:
    """Reject negative snapshot days."""
    data = make_valid_data()
    data.loc[0, "snapshot_day"] = -1

    with pytest.raises(ValueError, match="non-negative"):
        validate_data(data)


def test_validate_data_rejects_wrong_numeric_types() -> None:
    """Reject non-numeric values in numeric columns."""
    data = make_valid_data()
    data["active_days"] = ["two", "four", "six"]

    with pytest.raises(TypeError, match="active_days.*numeric"):
        validate_data(data)

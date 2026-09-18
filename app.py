from pathlib import Path

import pandas as pd
import streamlit as st

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


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(page_title="Music Churn", page_icon="🎵", layout="wide")

# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
<style>

/* Main background */
.stApp {
    background-color: #071A33;
    color: #F5F7FA;
}

/* Streamlit top header */
[data-testid="stHeader"] {
    background-color: #071A33;
}

/* Main content area */
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Main title */
h1 {
    color: #F5F7FA;
    font-weight: 700;
}

/* Other headings */
h2, h3 {
    color: #F5F7FA;
}

/* Normal text */
p {
    color: #B8C7DB;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #27496D;
    border-radius: 10px;
    overflow: hidden;
}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Load data
# --------------------------------------------------

df = load_data(DATA_PATH)

# --------------------------------------------------
# Main page
# --------------------------------------------------

st.title("🎵 Music Streaming Churn Analysis")

st.markdown("Explore the data. Discover patterns. Understand your listeners.")

st.divider()

# --------------------------------------------------
# Key metrics
# --------------------------------------------------

snapshot = st.selectbox("Select snapshot day", sorted(df["snapshot_day"].unique()))

filtered_df = filter_snapshot(df, int(snapshot))
unique_users, churn_rate, avg_active_days = calculate_metrics(filtered_df)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Users", value=f"{unique_users:,}")

with col2:
    st.metric(label="Churn Rate", value=f"{churn_rate:.1f}%")

with col3:
    st.metric(label="Avg. Active Days", value=f"{avg_active_days:.1f}")

# --------------------------------------------------
# User Overview
# --------------------------------------------------

st.divider()
st.subheader("User Overview")

col1, col2 = st.columns(2)

# Gender distribution
with col1:
    st.markdown("#### Gender Distribution")

    gender_counts = (
        filtered_df["gender"]
        .map({"F": "Female", "M": "Male"})
        .value_counts()
        .reset_index()
    )
    gender_counts.columns = ["Gender", "Users"]

    st.bar_chart(gender_counts, x="Gender", y="Users")


# Operating system distribution
with col2:
    st.markdown("#### Operating System")

    os_counts = filtered_df["operating_system"].value_counts().reset_index()
    os_counts.columns = ["Operating System", "Users"]

    st.bar_chart(os_counts, x="Operating System", y="Users")


# --------------------------------------------------
# Churn Overview
# --------------------------------------------------

st.divider()
st.subheader("Churn Overview")

col1, col2 = st.columns(2)

# Churn distribution for selected snapshot
with col1:
    st.markdown("#### Churn Distribution")

    churn_counts = (
        filtered_df["label"]
        .map({0: "No Churn", 1: "Churn"})
        .value_counts()
        .reset_index()
    )

    churn_counts.columns = ["Status", "Users"]

    st.bar_chart(churn_counts, x="Status", y="Users")


# Churn rate across snapshot days
with col2:
    st.markdown("#### Churn Rate Over Time")

    churn_by_day = calculate_churn_by_day(df)

    st.line_chart(churn_by_day, x="snapshot_day", y="Churn Rate (%)")


# --------------------------------------------------
# Dataset
# --------------------------------------------------

st.divider()

st.subheader("🗄️ Dataset Preview")
st.caption("A sample of the raw training data.")

st.dataframe(filtered_df.head(10), use_container_width=True)

st.caption(
    f"Showing 10 rows · {len(filtered_df):,} observations on snapshot day {snapshot}"
)

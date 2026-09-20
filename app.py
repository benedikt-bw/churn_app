import streamlit as st

from dashboard import (
    DATA_PATH,
    calculate_activity_bands,
    calculate_churn_by_day,
    calculate_churn_by_group,
    calculate_churn_matrix,
    calculate_engagement_trends,
    calculate_metrics,
    filter_snapshot,
    load_data,
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
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Main title */
h1 {
    color: #F5F7FA;
    font-weight: 700;
    letter-spacing: -0.03em;
}

/* Other headings */
h2, h3 {
    color: #F5F7FA;
}

/* Normal text */
p {
    color: #B8C7DB;
}

/* Dividers */
hr {
    border-color: #1C3C5C;
    margin: 1.5rem 0;
}

/* Metrics */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0D2542 0%, #102E4F 100%);
    border: 1px solid #1F4D70;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
}

[data-testid="stMetricLabel"] {
    color: #9AB3CC;
}

[data-testid="stMetricValue"] {
    color: #63D7FF;
}

/* Charts */
[data-testid="stVegaLiteChart"] {
    background-color: #0D2542;
    border: 1px solid #1F4D70;
    border-radius: 14px;
    padding: 0.65rem 0.75rem 0.35rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Selectors */
[data-baseweb="select"] > div {
    background-color: #0D2542;
    border-color: #1F4D70;
    border-radius: 10px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: #0D2542;
    border: 1px solid #1F4D70;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Captions */
[data-testid="stCaptionContainer"] {
    color: #89A6C1;
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

snapshot_days = sorted(df["snapshot_day"].unique())

snapshot = st.select_slider(
    "Select snapshot day",
    options=snapshot_days,
    value=snapshot_days[0],
)

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
# Risk Segments
# --------------------------------------------------

st.divider()
st.subheader("Risk Segments")
st.caption("Compare churn rates across different listener profiles.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Churn by Subscription Level")
    level_churn = calculate_churn_by_group(filtered_df, "last_level")
    st.bar_chart(level_churn, x="last_level", y="Churn Rate (%)")

with col2:
    st.markdown("#### Churn by Browser")
    browser_churn = calculate_churn_by_group(filtered_df, "browser")
    st.bar_chart(browser_churn, x="browser", y="Churn Rate (%)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Churn by Operating System")
    os_churn = calculate_churn_by_group(filtered_df, "operating_system")
    st.bar_chart(os_churn, x="operating_system", y="Churn Rate (%)")

with col2:
    st.markdown("#### Churn by Active Days")
    activity_bands = calculate_activity_bands(filtered_df)
    st.bar_chart(activity_bands, x="Activity Band", y="Churn Rate (%)")


# --------------------------------------------------
# Engagement Signals
# --------------------------------------------------

st.divider()
st.subheader("Engagement Signals")
st.caption("Track how listener activity changes across the available snapshots.")

engagement_trends = calculate_engagement_trends(df)
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Engagement Trend")
    st.line_chart(
        engagement_trends.set_index("snapshot_day")[
            ["Avg Active Days", "Avg Songs / Session"]
        ]
    )

with col2:
    st.markdown("#### Inactivity Trend")
    st.area_chart(
        engagement_trends.set_index("snapshot_day")[["Avg Hours Since Last Session"]]
    )

st.markdown("#### New User and Subscription Risk Matrix")
risk_matrix = calculate_churn_matrix(filtered_df, "is_new_user", "last_level")
risk_matrix.index = risk_matrix.index.map({0: "Returning User", 1: "New User"})
st.dataframe(
    risk_matrix.style.format("{:.1f}%").background_gradient(
        cmap="RdYlGn_r", vmin=0, vmax=100
    ),
    use_container_width=True,
)


# --------------------------------------------------
# Dataset
# --------------------------------------------------

st.divider()
if st.checkbox('Show raw data'):
    st.subheader("🗄️ Dataset Preview")
    st.caption("A sample of the prepared churn snapshot data.")

    st.dataframe(filtered_df.head(10), use_container_width=True)

    st.caption(
        f"Showing 10 rows · {len(filtered_df):,} observations on snapshot day {snapshot}"
)

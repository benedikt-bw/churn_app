import pandas as pd
import streamlit as st

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Music Churn",
    page_icon="🎵",
    layout="wide"
)

# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown("""
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
""", unsafe_allow_html=True)

# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv("data/train_sample.csv")

# --------------------------------------------------
# Main page
# --------------------------------------------------

st.title("🎵 Music Streaming Churn Analysis")

st.markdown(
    "Explore the data. Discover patterns. Understand your listeners."
)

st.divider()

st.subheader("🗄️ Dataset Preview")
st.caption("A sample of the raw training data.")

st.dataframe(
    df.head(10),
    use_container_width=True
)

st.caption(f"Showing 10 rows · Total sample size: {len(df):,} rows")
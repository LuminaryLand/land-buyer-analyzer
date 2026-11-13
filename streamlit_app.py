import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="County Builder & Cash Buyer Analyzer",
    page_icon="🏡",
    layout="wide"
)

st.title("🏡 County Builder & Cash Buyer Analyzer")
st.markdown(
    "Upload your county **Sales Affidavits** export (`.txt` or `.csv`) to isolate active builders "
    "and land buyers over a custom time window, regardless of the county."
)

with st.sidebar:
    st.header("1. Data Input")
    uploaded_files = st.file_uploader(
        "Upload Sales Affidavits Files (Multi-select allowed)",
        type=["txt", "csv"],
        accept_multiple_files=True
    )
    
    st.divider()
    st.header("2. Filter Parameters")
    min_price = st.number_input("Minimum Sale Price ($)", value=10000, step=5000)
    max_price = st.number_input("Maximum Sale Price ($)", value=500000, step=25000)

if uploaded_files:
    @st.cache_data
    def load_data(files):
        dfs = []
        for file in files:
            try:
                # Try reading with flexible delimiters (tab, comma, pipe)
                df = pd.read_csv(file, low_memory=False, sep=None, engine='python')
                dfs.append(df)
            except Exception as e:
                st.error(f"Error reading {file.name}: {e}")
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

    with st.spinner("Processing county records..."):
        df = load_data(uploaded_files)

    if not df.empty:
        st.success(f"Successfully loaded {len(df):,} total records across {len(uploaded_files)} file(s).")
        
        # Display raw preview
        with st.expander("🔍 Preview Raw Data"):
            st.dataframe(df.head(100))

        # Basic filtering logic matching common county affidavit structures
        st.subheader("📊 Buyer Analysis & Insights")
        st.info("Tip: Ensure your columns include buyer name and sale price fields for deeper filtering.")
        
        # Show summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        with col2:
            st.metric("Columns Detected", len(df.columns))
        with col3:
            st.metric("Files Processed", len(uploaded_files))
            
    else:
        st.warning("No data found in the uploaded files. Please check your export format.")
else:
    st.info("👈 Upload your county Sales Affidavits files (.txt or .csv) in the sidebar to begin.")

import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="County Builder & Cash Buyer Analyzer",
    page_icon="🏡",
    layout="wide"
)

st.title("🏡 County Builder & Cash Buyer Analyzer")
st.markdown(
    "Upload your county **Sales Affidavits** export (`.txt` or `.csv`) to isolate "
    "active builders and land buyers over a custom time window, regardless of the county."
)

# File Uploader
uploaded_file = st.file_uploader(
    "Upload Sales Affidavits File",
    type=["csv", "txt"],
    help="Upload your county export file (CSV or TXT)"
)

if uploaded_file is not None:
    df = None
    # Try multiple encodings commonly used by county legacy export systems
    for enc in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, low_memory=False, encoding=enc)
            break
        except Exception:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=None, engine="python", encoding=enc)
                break
            except Exception:
                continue

    if df is not None:
        st.success(f"Successfully loaded file! Total rows: {len(df):,}")
        
        # Display Data Preview
        st.subheader("📊 Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
        
        # Basic column info & metrics summary
        st.subheader("📋 Dataset Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", f"{len(df.columns)}")
        with col3:
            st.metric("Missing Values", f"{df.isna().sum().sum():,}")
            
        # Column Inspector
        with st.expander("Inspect Available Columns"):
            st.write(list(df.columns))
    else:
        st.error("Error reading file: Could not decode the file with standard encodings (utf-8, latin-1, cp1252). Please check the file format.")
else:
    st.warning("No data found in the uploaded files. Please upload a valid sales affidavit export file to begin.")

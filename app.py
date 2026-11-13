import streamlit as st
import pandas as pd
import io

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

# File Uploader (now supports Excel formats just in case)
uploaded_file = st.file_uploader(
    "Upload Sales Affidavits File",
    type=["csv", "txt", "xlsx", "xls"],
    help="Upload your county export file (CSV, TXT, or Excel)"
)

if uploaded_file is not None:
    df = None
    file_bytes = uploaded_file.getvalue()
    
    # 1. Try reading as an Excel file (in case a county export is an .xlsx/.xls renamed to .txt)
    try:
        df = pd.read_excel(io.BytesIO(file_bytes))
    except Exception:
        pass

    # 2. If not Excel, try robust text/CSV parsing with auto-delimiter and encoding fallback
    if df is None:
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1", "utf-16", "utf-16le"]
        delimiters = [",", "\t", "|", ";", None]
        
        for enc in encodings:
            for sep in delimiters:
                try:
                    uploaded_file.seek(0)
                    if sep is None:
                        df = pd.read_csv(
                            uploaded_file, 
                            encoding=enc, 
                            engine="python", 
                            on_bad_lines="skip", 
                            low_memory=False
                        )
                    else:
                        df = pd.read_csv(
                            uploaded_file, 
                            sep=sep, 
                            encoding=enc, 
                            engine="python", 
                            on_bad_lines="skip", 
                            low_memory=False
                        )
                    # Verify we got actual columns/data rather than a single malformed column
                    if df is not None and len(df.columns) > 1:
                        break
                except Exception:
                    continue
            if df is not None and len(df.columns) > 1:
                break

    if df is not None and len(df) > 0:
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
        st.error(
            "Could not automatically parse this file format. County exports often use "
            "pipe-delimiters (`|`), custom headers, or fixed-width columns. Please verify the file format."
        )
else:
    st.warning("No data found in the uploaded files. Please upload a valid sales affidavit export file to begin.")

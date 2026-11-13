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

# File Uploader
uploaded_file = st.file_uploader(
    "Upload Sales Affidavits File",
    type=["csv", "txt", "xlsx", "xls"],
    help="Upload your county export file (CSV, TXT, or Excel)"
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    
    # Sidebar manual parsing controls
    st.sidebar.header("⚙️ Parsing Options")
    delimiter_choice = st.sidebar.selectbox(
        "Delimiter", 
        ["Pipe (|)", "Auto-Detect", "Tab (\\t)", "Comma (,)", "Semicolon (;)"]
    )
    skip_rows = st.sidebar.number_input("Skip Header Rows", min_value=0, max_value=20, value=0)

    df = None
    sep_map = {
        "Tab (\\t)": "\t",
        "Pipe (|)": "|",
        "Comma (,)": ",",
        "Semicolon (;)": ";"
    }

    try:
        chosen_sep = sep_map.get(delimiter_choice, "|")
        
        if delimiter_choice != "Auto-Detect":
            for enc in ["utf-8", "latin-1", "cp1252", "utf-16", "utf-16le"]:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(
                        uploaded_file, 
                        sep=chosen_sep, 
                        skiprows=skip_rows, 
                        encoding=enc, 
                        engine="python", 
                        on_bad_lines="skip", 
                        low_memory=False,
                        skipinitialspace=True
                    )
                    if df is not None and len(df.columns) > 1:
                        break
                except Exception:
                    continue
        else:
            # Auto-detect loop
            for enc in ["utf-8", "latin-1", "cp1252", "iso-8859-1", "utf-16", "utf-16le"]:
                for sep in ["|", "\t", ",", ";"]:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(
                            uploaded_file, 
                            sep=sep, 
                            skiprows=skip_rows, 
                            encoding=enc, 
                            engine="python", 
                            on_bad_lines="skip", 
                            low_memory=False,
                            skipinitialspace=True
                        )
                        if df is not None and len(df.columns) > 1:
                            break
                    except Exception:
                        continue
                if df is not None and len(df.columns) > 1:
                    break

        # Fallback: Manual line-by-line split if standard pandas read fails on giant pipe-delimited files
        if (df is None or len(df.columns) <= 1) and delimiter_choice == "Pipe (|)":
            uploaded_file.seek(0)
            lines = []
            text_stream = io.TextIOWrapper(uploaded_file, encoding="latin-1", errors="replace")
            for i, line in enumerate(text_stream):
                if i < skip_rows:
                    continue
                parts = [p.strip() for p in line.strip().split("|")]
                if len(parts) > 1:
                    lines.append(parts)
            if len(lines) > 1:
                df = pd.DataFrame(lines[1:], columns=lines[0])

    except Exception as e:
        st.error(f"Parsing error: {e}")

    if df is not None and len(df) > 0 and len(df.columns) > 1:
        # Clean column names of any whitespace
        df.columns = [str(c).strip() for c in df.columns]
        
        st.success(f"Successfully loaded file! Total rows: {len(df):,}, Columns: {len(df.columns)}")
        
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
            "Could not parse this file format automatically. Please verify that the "
            "delimiter in the sidebar matches your file format."
        )
else:
    st.warning("No data found in the uploaded files. Please upload a valid sales affidavit export file to begin.")

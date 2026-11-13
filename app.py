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
        ["Auto-Detect", "Tab (\\t)", "Pipe (|)", "Comma (,)", "Semicolon (;)"]
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
        if delimiter_choice != "Auto-Detect":
            chosen_sep = sep_map[delimiter_choice]
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
                        low_memory=False
                    )
                    if df is not None and len(df.columns) > 0:
                        break
                except Exception:
                    continue
        else:
            # 1. Try Excel first
            try:
                df = pd.read_excel(io.BytesIO(file_bytes), skiprows=skip_rows)
            except Exception:
                pass

            # 2. Try standard text delimiters
            if df is None:
                encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1", "utf-16", "utf-16le"]
                delimiters = ["\t", "|", ",", ";"]
                
                for enc in encodings:
                    for sep in delimiters:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(
                                uploaded_file, 
                                sep=sep, 
                                skiprows=skip_rows, 
                                encoding=enc, 
                                engine="python", 
                                on_bad_lines="skip", 
                                low_memory=False
                            )
                            if df is not None and len(df.columns) > 1:
                                break
                        except Exception:
                            continue
                    if df is not None and len(df.columns) > 1:
                        break

    except Exception as e:
        st.error(f"Parsing error: {e}")

    if df is not None and len(df) > 0 and len(df.columns) > 1:
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
            "Could not automatically parse this file format. "
            "Check the sidebar **Parsing Options** to manually select your delimiter (Tab or Pipe) or skip extra title rows."
        )
        
        # Show raw preview to help diagnose the layout
        with st.expander("🔍 View Raw File Preview (First 10 lines)"):
            try:
                uploaded_file.seek(0)
                raw_text = uploaded_file.read(2000).decode("latin-1", errors="replace")
                st.code(raw_text)
            except Exception as ex:
                st.write("Could not read raw text preview:", ex)
else:
    st.warning("No data found in the uploaded files. Please upload a valid sales affidavit export file to begin.")

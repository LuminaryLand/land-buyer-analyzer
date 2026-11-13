from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Land & Builder Activity Analyzer", page_icon="🏡", layout="wide"
)

st.title("🏡 Maricopa County Builder & Cash Buyer Analyzer")
st.markdown(
    "Upload your Maricopa County **Sales Affidavits** export (.txt or .csv) to"
    " isolate active builders and land buyers over a custom time window."
)

st.sidebar.header("1. Data Input")
uploaded_files = st.sidebar.file_uploader(
    "Upload Sales Affidavits Files (Multi-select allowed)",
    type=["csv", "xlsx", "txt"],
    accept_multiple_files=True,
)

if uploaded_files:
  try:
    dfs = []
    for uploaded_file in uploaded_files:
      file_name = uploaded_file.name.lower()
      if file_name.endswith(".csv"):
        temp_df = pd.read_csv(uploaded_file, low_memory=False)
      elif file_name.endswith(".txt"):
        # Maricopa GIS open data exports are pipe-delimited
        temp_df = pd.read_csv(uploaded_file, sep="|", low_memory=False)
      else:
        temp_df = pd.read_excel(uploaded_file)
      dfs.append(temp_df)

    # Combine all uploaded affidavit files into one master dataframe
    df = pd.concat(dfs, ignore_index=True)

    # Standardize column names to uppercase for easier matching
    df.columns = [str(col).strip() for col in df.columns]

    st.success(
        f"Successfully loaded {len(dfs)} file(s) combining {len(df):,} total"
        f" transaction records."
    )

    with st.expander("🔍 Preview Raw Data"):
      st.dataframe(df.head(10))

    st.sidebar.header("2. Map Data Columns")
    columns = list(df.columns)


    def find_col(keywords):
      for col in columns:
        if any(k in col.lower() for k in keywords):
          return col
      return columns[0]


    buyer_col = st.sidebar.selectbox(
        "Buyer / Grantee Column",
        columns,
        index=columns.index(
            find_col(["grantee", "buyer", "owner", "name", "owner_name"])
        ),
    )
    date_col = st.sidebar.selectbox(
        "Sale / Recording Date Column",
        columns,
        index=columns.index(
            find_col(["sale_date", "date", "rec_date", "recording"])
        ),
    )
    price_col = st.sidebar.selectbox(
        "Sale Price Column (Optional)",
        ["None"] + columns,
        index=(
            columns.index(
                find_col(["sale_price", "price", "consideration", "amt"])
            )
            + 1
            if find_col(["sale_price", "price", "consideration"]) in columns
            else 0
        ),
    )

    st.sidebar.header("3. Filter Criteria")

    # Time Range Filter (Default to last 6 months)
    if date_col in df.columns:
      df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
      valid_dates = df[date_col].dropna()

      if not valid_dates.empty:
        max_date = valid_dates.max()
        default_start = max_date - timedelta(days=180)  # 6 months ago

        start_date, end_date = st.sidebar.date_input(
            "Transaction Date Window",
            value=(default_start, max_date),
            min_value=valid_dates.min(),
            max_value=max_date,
        )

        # Apply filter
        df = df[(df[date_col] >= pd.Timestamp(start_date)) & (df[date_col] <= pd.Timestamp(end_date))]
        st.sidebar.info(
            f"Filtered down to {len(df):,} transactions between {start_date} and"
            f" {end_date}."
        )

    min_acquisitions = st.sidebar.slider(
        "Minimum Acquisitions in Window (Filter Repeat Buyers)", 1, 10, 1
    )

    st.divider()
    col1, col2, col3 = st.columns(3)
    total_records = len(df)
    unique_buyers = (
        df[buyer_col].nunique() if buyer_col in df.columns else total_records
    )

    col1.metric("Filtered Transactions", f"{total_records:,}")
    col2.metric("Unique Buyer Entities", f"{unique_buyers:,}")
    col3.metric("Target Focus", "Active Builders & Investors")

    if buyer_col in df.columns:
      st.subheader("🏆 Top Active Builders & Buyers in Selected Window")
      buyer_counts = (
          df.groupby(buyer_col)
          .size()
          .reset_index(name="Acquisitions_Count")
          .sort_values(by="Acquisitions_Count", ascending=False)
      )

      filtered_buyers = buyer_counts[
          buyer_counts["Acquisitions_Count"] >= min_acquisitions
      ]

      st.dataframe(filtered_buyers.head(50), use_container_width=True)

      csv = filtered_buyers.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Download Filtered Builder List as CSV",
          data=csv,
          file_name="active_builders_last_6_months.csv",
          mime="text/csv",
      )

  except Exception as e:
    st.error(f"Error processing files: {e}")

else:
  st.info(
      "👈 Upload your Maricopa County Sales Affidavits files (.txt or .csv) in"
      " the sidebar to begin."
  )

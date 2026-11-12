import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Land Wholesaling & Buyer Analyzer", page_icon="🏡", layout="wide"
)

st.title("🏡 Land Wholesaling & Cash Buyer Analyzer")
st.markdown(
    "Upload your county assessor files (supports CSV, Excel, or Maricopa"
    " pipe-delimited .txt files) to isolate active cash land buyers,"
    " builders, and LLCs."
)

st.sidebar.header("1. Data Input")
uploaded_file = st.sidebar.file_uploader(
    "Upload County Records / Buyers List (.csv, .xlsx, or .txt)",
    type=["csv", "xlsx", "txt"],
)

if uploaded_file is not None:
  try:
    file_name = uploaded_file.name.lower()

    # Automatically handle Maricopa's pipe-delimited format vs standard csv/excel
    if file_name.endswith(".csv"):
      df = pd.read_csv(uploaded_file, low_memory=False)
    elif file_name.endswith(".txt"):
      # Maricopa County GIS open data downloads are pipe-delimited text files
      df = pd.read_csv(uploaded_file, sep="|", low_memory=False)
    else:
      df = pd.read_excel(uploaded_file)

    st.success(
        f"Successfully loaded {len(df):,} rows and {len(df.columns)} columns."
    )

    with st.expander("🔍 Preview Raw Data"):
      st.dataframe(df.head(10))

    st.sidebar.header("2. Map Your Data Columns")
    columns = list(df.columns)


    def find_col(keywords):
      for col in columns:
        if any(k in str(col).lower() for k in keywords):
          return col
      return columns[0]


    owner_col = st.sidebar.selectbox(
        "Owner / Buyer Name Column",
        columns,
        index=columns.index(
            find_col(["owner", "buyer", "name", "grantee", "owner_name"])
        ),
    )
    address_col = st.sidebar.selectbox(
        "Mailing Address Column",
        columns,
        index=columns.index(
            find_col(["mail", "address", "situs", "mail_addr"])
        ),
    )

    st.sidebar.header("3. Filter Criteria")
    min_parcels = st.sidebar.slider(
        "Minimum Parcels Owned (Filter Repeat Investors)", 1, 10, 1
    )

    st.divider()
    col1, col2, col3 = st.columns(3)
    total_records = len(df)
    unique_buyers = (
        df[owner_col].nunique() if owner_col in df.columns else total_records
    )

    col1.metric("Total Records Analyzed", f"{total_records:,}")
    col2.metric("Unique Buyer Entities", f"{unique_buyers:,}")
    col3.metric("Target Focus", "Vacant Land / Cash")

    if owner_col in df.columns:
      st.subheader("🏆 Top Active Buyers & Investors in County")
      buyer_counts = (
          df.groupby(owner_col)
          .size()
          .reset_index(name="Parcels_Acquired")
          .sort_values(by="Parcels_Acquired", ascending=False)
      )

      filtered_buyers = buyer_counts[
          buyer_counts["Parcels_Acquired"] >= min_parcels
      ]

      st.dataframe(filtered_buyers.head(50), use_container_width=True)

      csv = filtered_buyers.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Download Filtered Buyer List as CSV",
          data=csv,
          file_name="qualified_land_buyers.csv",
          mime="text/csv",
      )

  except Exception as e:
    st.error(f"Error processing file: {e}")

else:
  st.info(
      "👈 Upload your Maricopa dataset (.txt or .csv) using the sidebar to"
      " begin analysis."
  )

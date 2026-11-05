import streamlit as st
import pandas as pd
import pdfplumber
import io
import zipfile

# Inject custom CSS to increase the file uploader label size
st.markdown("""
    <style>
    /* Target the label specifically inside the file uploader widget */
    [data-testid="stFileUploader"] label p {
        font-size: 2rem !important; /* Change to your preferred size (e.g., 24px, 2rem) */
        font-weight: bold;         /* Optional: Make it bold */
    }
    </style>
    """, unsafe_allow_html=True)

uploaded_filed = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_filed is not None:
    dfs_list = []
    table_names = []
    zip_buffer = io.BytesIO()
    
    with pdfplumber.open(uploaded_filed) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if table and len(table) > 1:
                    # Convert this individual table to its own DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    dfs_list.append(df)
                    table_name = df.columns[0].replace(" ", "_")
                    table_name = df.columns[0].replace("/", "_")
                    table_names.append(f"{table_name}.csv")

    st.write(f"Tables extracted: {len(dfs_list)}")
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for df, table_name in zip(dfs_list, table_names):
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            zf.writestr(table_name, csv_bytes)
    zip_buffer.seek(0)
    st.download_button(
        label="Download all tables as ZIP",
        data=zip_buffer,
        file_name="Facilities_tables.zip",
        mime="application/zip"
    )
"""
app.py
This module provides a Streamlit-based web application for extracting data from uploaded bill PDFs.
The application allows users to upload multiple PDF files, extract relevant data,
and download the results as a CSV file.
Functions:
    main(): The main function that initializes the Streamlit app, handles file uploads, 
    processes the data, and provides a download option for the extracted data.
"""

import streamlit as st
from helpers import create_docs


def main():
    """
    Main function to run the Streamlit app.
    It sets up the page configuration, title, and file uploader for PDF bills.
    When the user clicks the extract button, it processes the uploaded files,
    extracts the relevant data, and displays it in a table.
    It also provides an option to download the extracted data as a CSV file.
    """
    st.set_page_config(page_title="Bill Extractor")
    st.title("Bill Extractor AI Assistant...🤖")
    # Upload Bills
    pdf_files = st.file_uploader("Upload your bills in PDF format only",
                                 type=["pdf"],
                                 accept_multiple_files=True)
    extract_button = st.button("Extract bill data...")

    if extract_button:
        with st.spinner("Extracting... it takes time..."):
            data_frame = create_docs(pdf_files)
            st.write(data_frame.head())
            data_frame["AMOUNT"] = data_frame["AMOUNT"].str.replace(
                r"[$,]", "", regex=True).astype(float)
            st.write("Average bill amount: ", data_frame['AMOUNT'].mean())

            # convert to csv
            convert_to_csv = data_frame.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download data as CSV",
            convert_to_csv,
            "CSV_Bills.csv",
            "text/csv",
            key="download-csv"
        )
        st.success("Success!!")


# Invoking main function
if __name__ == '__main__':
    main()

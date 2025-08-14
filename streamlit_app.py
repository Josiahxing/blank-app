import streamlit as st
import fitz  # PyMuPDF
import os
import re
import tempfile
from zipfile import ZipFile

st.title("Bill of Lading PDF Renamer")

st.markdown("""
Upload a PDF file containing multiple Bill of Lading pages.  
This app will extract each page, find the 15-digit Bill of Lading Number, and rename the page accordingly.  
You will be able to download a ZIP file containing all renamed PDFs.
""")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    with tempfile.TemporaryDirectory() as temp_dir:
        input_pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(input_pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        doc = fitz.open(input_pdf_path)
        saved_files = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()

            match = re.search(r'\b\d{15}\b', text)
            if match:
                bol_number = match.group(0)
                output_path = os.path.join(temp_dir, f"{bol_number}.pdf")

                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                new_doc.save(output_path)
                new_doc.close()

                saved_files.append(output_path)
            else:
                st.warning(f"No Bill of Lading Number found on page {page_num + 1}")

        doc.close()

        zip_path = os.path.join(temp_dir, "renamed_bols.zip")
        with ZipFile(zip_path, 'w') as zipf:
            for file_path in saved_files:
                zipf.write(file_path, arcname=os.path.basename(file_path))

        with open(zip_path, "rb") as f:
            st.download_button(
                label="Download Renamed PDFs as ZIP",
                data=f,
                file_name="renamed_bols.zip",
                mime="application/zip"
            )

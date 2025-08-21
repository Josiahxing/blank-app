import streamlit as st
import pandas as pd
import requests
from lxml import html
from io import BytesIO

def fetch_carton_data(carton_id):
    session = requests.Session()
    url = "http://207.141.233.26/PM/rpttssbycartonidblank.asp"
    session.get(url)
    data = {
        "partnos": carton_id,
        "bMouseOver": "TRUE",
        "btnSubmit": "Submit"
    }
    response = session.post(url, data=data)
    tree = html.fromstring(response.content)

    fields = {
        "SO": "//table[2]/tr/td[1]/h4/text()",
        "SS": "//table[2]/tr/td[2]/h4/text()",
        "CONE NO": "//table[2]/tr/td[3]/h4/text()",
        "FCD": "//table[2]/tr/td[4]/h4/text()",
        "BISI Date": "//table[2]/tr/td[5]/h4/text()",
        "Carton Qty": "//table[3]/tr/td/h4/text()",
        "Order No": "//table[4]/tr[3]/td[1]/font/b/text()",
        "Line": "//table[4]/tr[3]/td[2]/font/b/text()",
        "BU": "//table[4]/tr[3]/td[3]/font/b/text()",
        "Workorder": "//table[4]/tr[3]/td[4]/a/font/b/text()",
        "SKU": "//table[4]/tr[3]/td[5]/font/b/text()",
        "Complete?": "//table[4]/tr[3]/td[6]/font/b/text()",
        "Total Cartons": "//table[4]/tr[3]/td[7]/font/b/text()",
        "Finished Cartons": "//table[4]/tr[3]/td[8]/font/b/text()"
    }

    result = {}
    for label, xpath in fields.items():
        extracted = tree.xpath(xpath)
        result[label] = extracted[0].strip() if extracted else "Not Found"
    return result

st.title("📦 Carton ID Data Enrichment Tool")

uploaded_file = st.file_uploader("Upload your file with Carton IDs", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    if "Carton_ID" not in df.columns:
        st.error("The uploaded file must contain a 'Carton_ID' column.")
    else:
        st.info("Processing carton IDs. This may take a moment...")

        enriched_data = []
        for carton_id in df["Carton_ID"]:
            enriched_data.append(fetch_carton_data(str(carton_id)))

        enriched_df = pd.DataFrame(enriched_data)
        final_df = pd.concat([df.reset_index(drop=True), enriched_df], axis=1)

        st.subheader("Enriched Data Preview")
        st.dataframe(final_df)

        output = BytesIO()
        final_df.to_excel(output, index=False, engine="openpyxl")
        st.download_button("Download Enriched File", data=output.getvalue(), file_name="enriched_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

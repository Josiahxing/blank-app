import streamlit as st
import pandas as pd
import requests
from lxml import html
from io import StringIO

# Function to fetch data for a single carton ID
def fetch_carton_data(carton_id):
    try:
        session = requests.Session()
        url = "http://207.141.233.26/PM/rpttssbycartonidblank.asp"
        session.get(url, timeout=10)
        data = {
            "partnos": carton_id,
            "bMouseOver": "TRUE",
            "btnSubmit": "Submit"
        }
        response = session.post(url, data=data, timeout=10)
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

        result = {"Carton_ID": carton_id}
        for label, xpath in fields.items():
            extracted = tree.xpath(xpath)
            result[label] = extracted[0].strip() if extracted else "Not Found"
        return result
    except Exception as e:
        return {"Carton_ID": carton_id, "Error": str(e)}

# Streamlit UI
st.title("📦 Carton ID Data Extractor")

st.write("Paste your list of Carton IDs below (one per line):")
carton_input = st.text_area("Carton IDs", height=200)

if st.button("Run Extraction"):
    carton_ids = [line.strip() for line in carton_input.splitlines() if line.strip()]
    if not carton_ids:
        st.warning("Please enter at least one Carton ID.")
    else:
        st.info(f"Processing {len(carton_ids)} Carton IDs...")
        results = []
        progress = st.progress(0)
        for i, carton_id in enumerate(carton_ids):
            results.append(fetch_carton_data(carton_id))
            progress.progress((i + 1) / len(carton_ids))
        df = pd.DataFrame(results)
        st.success("Extraction complete!")
        st.dataframe(df)

        csv_data = df.to_csv(index=False)
        st.download_button("Download CSV", data=csv_data, file_name="carton_data.csv", mime="text/csv")

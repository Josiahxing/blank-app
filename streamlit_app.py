import streamlit as st
import requests
from lxml import etree
import csv
import io

def process_order_numbers(order_numbers):
    # Base URL
    base_url = 'https://customeraccess.trans-expedite.com/Tracking/Login/Login.aspx?QuickViewNumber='

    # Initialize a dictionary to store all extracted data
    data_dict = {order_number: {"ACTUAL DELIVERY DATE": "", "EXPECTED DELIVERY DATE": "", "ALL REFERENCES": "", "SIGNATURE": ""} for order_number in order_numbers}

    # Loop through each order number and extract data
    for order_number in order_numbers:
        url = f"{base_url}{order_number}"

        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content with lxml
            dom = etree.HTML(response.content)

            # Use XPath to find the specific data
            actual_delivery_date_xpath = '//*[@id="AUTOGENBOOKMARK_6_b2a17b72-d1fb-49fc-b9da-27a6e5efe7e8"]/td[2]/div[3]'
            expected_delivery_date_xpath = '//*[@id="AUTOGENBOOKMARK_6_b2a17b72-d1fb-49fc-b9da-27a6e5efe7e8"]/td[2]/div[1]'
            all_references_xpath = '//*[@id="__bookmark_3"]'
            signature_xpath = '//*[@id="AUTOGENBOOKMARK_17_fddaeca7-7857-4206-b07d-303cd52f9975"]/tbody/tr[4]/td[2]/div'

            actual_delivery_date_elements = dom.xpath(actual_delivery_date_xpath)
            expected_delivery_date_elements = dom.xpath(expected_delivery_date_xpath)
            all_references_elements = dom.xpath(all_references_xpath)
            signature_elements = dom.xpath(signature_xpath)

            # Extract Actual Delivery Date
            for element in actual_delivery_date_elements:
                actual_delivery_date = element.text.strip() if element.text else ''
                data_dict[order_number]["ACTUAL DELIVERY DATE"] = actual_delivery_date

            # Extract Expected Delivery Date
            for element in expected_delivery_date_elements:
                expected_delivery_date = element.text.strip() if element.text else ''
                data_dict[order_number]["EXPECTED DELIVERY DATE"] = expected_delivery_date

            # Extract All References, format as comma-separated values, and replace / with -
            for element in all_references_elements:
                all_references_lines = [line.strip().replace('/', '-') for line in element.itertext() if line.strip()]
                all_references = ', '.join(all_references_lines)
                data_dict[order_number]["ALL REFERENCES"] = all_references

            # Extract Signature
            for element in signature_elements:
                signature = element.text.strip() if element.text else ''
                data_dict[order_number]["SIGNATURE"] = signature
        else:
            st.error(f"Failed to retrieve data for order number {order_number}. Status code: {response.status_code}")

    # Save the extracted data to a CSV file with headers
    output_csv = io.StringIO()
    writer = csv.writer(output_csv)
    # Write the header
    header = ["Tracking Information", "ACTUAL DELIVERY DATE", "EXPECTED DELIVERY DATE", "ALL REFERENCES", "SIGNATURE"]
    writer.writerow(header)
    
    # Write the data rows
    for order_number in order_numbers:
        row = [order_number, 
               data_dict[order_number]["ACTUAL DELIVERY DATE"], 
               data_dict[order_number]["EXPECTED DELIVERY DATE"], 
               data_dict[order_number]["ALL REFERENCES"], 
               data_dict[order_number]["SIGNATURE"]]
        writer.writerow(row)

    output_csv.seek(0)
    return output_csv

st.title("Order Tracking Information Extractor")

order_numbers_input = st.text_area("Scan or Enter Order Numbers (one per line)")

if st.button("Process Order Numbers"):
    if order_numbers_input:
        order_numbers = [num.strip() for num in order_numbers_input.split('\n') if num.strip()]
        output_csv = process_order_numbers(order_numbers)
        st.success("Data has been successfully processed!")
        st.download_button(
            label="Download Processed CSV",
            data=output_csv,
            file_name="output.csv",
            mime="text/csv"
        )
    else:
        st.error("Please enter or scan order numbers.")

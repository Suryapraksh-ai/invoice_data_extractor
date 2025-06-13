import streamlit as st
import PyPDF2
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Invoice Data Extractor", layout="wide")
st.title("📄 Amazon/Flipkart Invoice Data Extractor ")


def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"PDF reading error: {str(e)}")
    return text

def clean_amount(amount_str):
    """₹50,000.00 → 50000.00 में कन्वर्ट करता है"""
    if not amount_str:
        return ""
    cleaned = re.sub(r'[^\d.]', '', str(amount_str))
    try:
        return float(cleaned) if cleaned else ""
    except ValueError:
        return ""

def parse_amazon_invoice(text):
    data = {
        "Source": "Amazon",
        "Order ID": "",
        "Order Date": "",
        "Total Amount": "",
        "Invoice Number": "",
        "Seller": ""
    }
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        # Amazon-Specific Patterns
        if "Order Number:" in line:
            data["Order ID"] = line.split("Order Number:")[-1].strip().split()[0]
        elif "Order Date:" in line:
            data["Order Date"] = line.split("Order Date:")[-1].strip().split()[0]
        elif "Invoice Number :" in line:
            data["Invoice Number"] = line.split("Invoice Number :")[-1].strip()
        elif "Sold By :" in line and i+1 < len(lines):
            data["Seller"] = lines[i+1].strip()
        
        # TOTAL AMOUNT Extraction (3 Methods)
        if "TOTAL:" in line and i+1 < len(lines):
            next_line = lines[i+1]
            if "Amount in Words:" in next_line:
                amount_part = next_line.split("Amount in Words:")[0].strip()
                data["Total Amount"] = clean_amount(amount_part)
        
        if "Invoice Value:" in line and not data["Total Amount"]:
            data["Total Amount"] = clean_amount(line.split("Invoice Value:")[-1].strip())
        
        if "|" in line and "Apple iPhone" in line:  # Product line in table
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 9:  # Ensure correct column
                data["Total Amount"] = clean_amount(parts[-1])
    
    return data

def parse_flipkart_invoice(text):
    data = {
        "Source": "Flipkart",
        "Order ID": "",
        "Order Date": "",
        "Grand Total": "",  # Flipkart uses "Grand Total"
        "Invoice Number": "",
        "Seller": ""
    }
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        # Flipkart-Specific Patterns
        if "Order ID:" in line:
            data["Order ID"] = line.split("Order ID:")[-1].strip()
        elif "Order Date:" in line:
            data["Order Date"] = line.split("Order Date:")[-1].strip()
        elif "Invoice Number #" in line:
            data["Invoice Number"] = line.split("Invoice Number #")[-1].strip()
        elif "Sold By:" in line:
            data["Seller"] = line.split("Sold By:")[-1].strip().rstrip(',')
        
        # GRAND TOTAL Extraction (2 Methods)
        if "Grand Total" in line and i+1 < len(lines):
            next_line = lines[i+1]
            if "₹" in next_line:
                data["Grand Total"] = clean_amount(next_line.split("₹")[-1].strip())
        
        if "Total ₹" in line and not data["Grand Total"]:
            data["Grand Total"] = clean_amount(line.split("₹")[-1].strip())
    
    return data

def parse_invoice_data(text, filename):
    if any(kw in text.lower() for kw in ["amazon", "appario", "asspl"]):
        return parse_amazon_invoice(text)
    elif any(kw in text.lower() for kw in ["flipkart", "consulting rooms"]):
        return parse_flipkart_invoice(text)
    else:
        return {"Source": "Unknown"}

# Streamlit UI
uploaded_files = st.file_uploader("Upload PDF Invoices", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        with st.expander(f"🔍 {uploaded_file.name}", expanded=True):
            text = extract_text_from_pdf(uploaded_file)
            invoice_data = parse_invoice_data(text, uploaded_file.name)
            
            if invoice_data["Source"] != "Unknown":
                st.success("✅ Perfectly Extracted:")
                st.json(invoice_data)
                all_data.append(invoice_data)
            else:
                st.warning("⚠ Unsupported Format (Amazon/Flipkart only)")

    if all_data:
        df = pd.DataFrame(all_data)
        
        # Combine both amount columns for cleaner output
        df["Amount"] = df["Total Amount"].fillna(df["Grand Total"])
        df = df.drop(["Total Amount", "Grand Total"], axis=1, errors="ignore")
        
        st.subheader("📊 Final Results")
        st.dataframe(df)
        
        # Excel Download
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button(
            "💾 Download Excel",
            excel_buffer.getvalue(),
            "invoice_data.xlsx",
            "application/vnd.ms-excel"
        )
    else:
        st.warning("No valid invoices found")
else:
    st.info("📤 Upload Amazon/Flipkart PDF invoices to start")
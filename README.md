# invoice_data_extractor
# 📄 Amazon/Flipkart Invoice Data Extractor

A Streamlit application that automatically extracts key information from Amazon and Flipkart invoice PDFs, including order details, amounts, and seller information.

## Features ✨

- **Automatic PDF Parsing**: Extracts text from uploaded invoice PDFs
- **Platform Detection**: Identifies Amazon or Flipkart invoices
- **Key Data Extraction**:
  - Order ID
  - Order Date
  - Total Amount (Amazon) / Grand Total (Flipkart)
  - Invoice Number
  - Seller Information
- **Excel Export**: Download extracted data in spreadsheet format

## Supported Invoice Types ✅

| Platform | Sample Fields Extracted |
|----------|-------------------------|
| Amazon   | `Order Number:`, `Invoice Value:`, `TOTAL:` |
| Flipkart | `Order ID:`, `Grand Total`, `Invoice Number #` |

## Requirements 📦
Python 3.7+

Streamlit

PyPDF2

pandas

openpyxl

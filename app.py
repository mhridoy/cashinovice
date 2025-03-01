import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import io
import base64
from fpdf import FPDF
import numpy as np
import seaborn as sns
import traceback

# Set page configuration
st.set_page_config(page_title="Business Transaction Manager", layout="wide", initial_sidebar_state="collapsed")

# Apply custom CSS
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: 'Poppins', sans-serif; }
    .card { background-color: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .stButton>button { background-color: #1e40af; color: white; border-radius: 6px; padding: 0.6rem 1.2rem; font-weight: 600; }
    .stButton>button:hover { background-color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%); padding: 2rem; border-radius: 16px; color: white; text-align: center;">
    <h1 style="font-size: 2.5rem; font-weight: 700;">Business Transaction Manager</h1>
    <p style="font-size: 1.25rem;">Track your daily transactions</p>
</div>
""", unsafe_allow_html=True)

# Date selector
st.markdown('<div class="card">', unsafe_allow_html=True)
selected_date = st.date_input("Transaction Date", date.today())
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if 'purchase_df' not in st.session_state:
    st.session_state.purchase_df = pd.DataFrame({'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Customer Name': [''], 'Amount': [0], 'Purchase Description': ['']})
if 'expense_df' not in st.session_state:
    st.session_state.expense_df = pd.DataFrame({'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Expense Type': [''], 'Amount': [0], 'Expense Description': ['']})
if 'sales_df' not in st.session_state:
    st.session_state.sales_df = pd.DataFrame({'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Customer Name': ['Starting Balance'], 'Amount': [0], 'Sales Description': ['Opening Balance']})
if 'customer_names' not in st.session_state:
    st.session_state.customer_names = set()

# Helper functions
def ensure_valid_dataframe(df, default_structure, name="DataFrame"):
    if not isinstance(df, pd.DataFrame):
        return default_structure.copy()
    try:
        return pd.DataFrame(df.to_dict('records'))
    except Exception:
        return default_structure.copy()

def update_date(df, date_val):
    df_copy = df.copy()
    df_copy['Date'] = date_val.strftime('%Y-%m-%d')
    return df_copy

def update_customer_names():
    for df, col in [(st.session_state.purchase_df, 'Customer Name'), (st.session_state.sales_df, 'Customer Name')]:
        if col in df:
            st.session_state.customer_names.update(df[col].dropna().unique())

def submit_purchase():
    st.session_state.purchase_df = ensure_valid_dataframe(st.session_state.purchase_editor, st.session_state.purchase_df, "Purchase")
    st.session_state.purchase_df = update_date(st.session_state.purchase_df, selected_date)
    update_customer_names()

def submit_expense():
    st.session_state.expense_df = ensure_valid_dataframe(st.session_state.expense_editor, st.session_state.expense_df, "Expense")
    st.session_state.expense_df = update_date(st.session_state.expense_df, selected_date)

def submit_sales():
    st.session_state.sales_df = ensure_valid_dataframe(st.session_state.sales_editor, st.session_state.sales_df, "Sales")
    st.session_state.sales_df = update_date(st.session_state.sales_df, selected_date)
    update_customer_names()

def create_pdf(purchase_df, expense_df, sales_df, date_val, purchase_total, expense_total, sales_total, balance):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Business Transaction Report", 1, 1, "C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"Date: {date_val.strftime('%Y-%m-%d')}", 0, 1, "L")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Summary:", 0, 1, "L")
    pdf.ln(2)
    pdf.set_font("Arial", "", 12)
    pdf.cell(95, 10, f"Total Purchase: Tk {purchase_total:,.2f}", 1, 0, "L")
    pdf.cell(95, 10, f"Total Expense: Tk {expense_total:,.2f}", 1, 1, "L")
    pdf.cell(95, 10, f"Total Sales: Tk {sales_total:,.2f}", 1, 0, "L")
    pdf.cell(95, 10, f"Today's Balance: Tk {balance:,.2f}", 1, 1, "L")
    pdf.ln(10)

    for title, df, cols, desc_col in [
        ("Purchase Transactions:", purchase_df, ['SL', 'Date', 'Customer Name', 'Amount'], 'Purchase Description'),
        ("Expense Transactions:", expense_df, ['SL', 'Date', 'Expense Type', 'Amount'], 'Expense Description'),
        ("Sales Transactions:", sales_df, ['SL', 'Date', 'Customer Name', 'Amount'], 'Sales Description')
    ]:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, title, 0, 1, "L")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(15, 10, "SL", 1, 0, "C")
        pdf.cell(35, 10, "Date", 1, 0, "C")
        pdf.cell(50, 10, "Name/Type", 1, 0, "C")
        pdf.cell(40, 10, "Amount", 1, 0, "C")
        pdf.cell(50, 10, "Description", 1, 1, "C")
        pdf.set_font("Arial", "", 10)
        for i, row in df.iterrows():
            pdf.cell(15, 10, str(row.get('SL', '')), 1, 0, "C")
            pdf.cell(35, 10, str(row.get('Date', '')), 1, 0, "C")
            name = str(row.get(cols[2], ''))
            if len(name) > 20: name = name[:17] + "..."
            pdf.cell(50, 10, name, 1, 0, "L")
            amount = f"Tk {float(row.get('Amount', 0)):,.2f}"
            pdf.cell(40, 10, amount, 1, 0, "R")
            desc = str(row.get(desc_col, ''))
            if len(desc) > 20: desc = desc[:17] + "..."
            pdf.cell(50, 10, desc, 1, 1, "L")
        pdf.ln(10)

    return pdf.output(dest='S').encode('latin1')

# Tabs
tab1, tab2, tab3 = st.tabs(["Data Entry", "Dashboard", "Export"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Purchase Entry")
        edited_purchase_df = st.data_editor(
            st.session_state.purchase_df,
            num_rows="dynamic",
            key="purchase_editor",
            use_container_width=True,
            hide_index=True,
            column_config={
                "SL": st.column_config.NumberColumn(width="small"),
                "Date": st.column_config.DateColumn(width="medium", disabled=True),
                "Customer Name": st.column_config.TextColumn(width="large"),
                "Amount": st.column_config.NumberColumn(width="medium"),
                "Purchase Description": st.column_config.TextColumn(width="large"),
            }
        )
        if st.button("Save Purchase Data", key="save_purchase", on_click=submit_purchase):
            st.success("✅ Purchase data saved! Check the Dashboard tab.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Expense Entry")
        edited_expense_df = st.data_editor(
            st.session_state.expense_df,
            num_rows="dynamic",
            key="expense_editor",
            use_container_width=True,
            hide_index=True,
            column_config={
                "SL": st.column_config.NumberColumn(width="small"),
                "Date": st.column_config.DateColumn(width="medium", disabled=True),
                "Expense Type": st.column_config.TextColumn(width="large"),
                "Amount": st.column_config.NumberColumn(width="medium"),
                "Expense Description": st.column_config.TextColumn(width="large"),
            }
        )
        if st.button("Save Expense Data", key="save_expense", on_click=submit_expense):
            st.success("✅ Expense data saved! Check the Dashboard tab.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Sales Entry")
        edited_sales_df = st.data_editor(
            st.session_state.sales_df,
            num_rows="dynamic",
            key="sales_editor",
            use_container_width=True,
            hide_index=True,
            column_config={
                "SL": st.column_config.NumberColumn(width="small"),
                "Date": st.column_config.DateColumn(width="medium", disabled=True),
                "Customer Name": st.column_config.TextColumn(width="large"),
                "Amount": st.column_config.NumberColumn(width="medium"),
                "Sales Description": st.column_config.TextColumn(width="large"),
            }
        )
        if st.button("Save Sales Data", key="save_sales", on_click=submit_sales):
            st.success("✅ Sales data saved! Check the Dashboard tab.")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    clean_purchase_df = ensure_valid_dataframe(st.session_state.purchase_df, st.session_state.purchase_df, "Purchase")
    clean_expense_df = ensure_valid_dataframe(st.session_state.expense_df, st.session_state.expense_df, "Expense")
    clean_sales_df = ensure_valid_dataframe(st.session_state.sales_df, st.session_state.sales_df, "Sales")
    
    clean_purchase_df['Amount'] = pd.to_numeric(clean_purchase_df['Amount'], errors='coerce').fillna(0)
    clean_expense_df['Amount'] = pd.to_numeric(clean_expense_df['Amount'], errors='coerce').fillna(0)
    clean_sales_df['Amount'] = pd.to_numeric(clean_sales_df['Amount'], errors='coerce').fillna(0)
    
    purchase_total = clean_purchase_df['Amount'].sum()
    expense_total = clean_expense_df['Amount'].sum()
    sales_total = clean_sales_df['Amount'].sum()
    balance = sales_total - (purchase_total + expense_total)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Business Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Purchase", f"৳{purchase_total:,.2f}")
    col2.metric("Total Expense", f"৳{expense_total:,.2f}")
    col3.metric("Total Sales", f"৳{sales_total:,.2f}")
    col4.metric("Today's Balance", f"৳{balance:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Recent Transactions")
    purchase_display = clean_purchase_df.copy()
    purchase_display['Type'] = 'Purchase'
    purchase_display = purchase_display.rename(columns={'Purchase Description': 'Description'})
    
    expense_display = clean_expense_df.copy()
    expense_display['Type'] = 'Expense'
    expense_display['Customer Name'] = expense_display['Expense Type']
    expense_display = expense_display.rename(columns={'Expense Description': 'Description'})
    
    sales_display = clean_sales_df.copy()
    sales_display['Type'] = 'Sales'
    sales_display = sales_display.rename(columns={'Sales Description': 'Description'})
    
    combined_df = pd.concat([purchase_display, expense_display, sales_display])[["SL", "Date", "Type", "Customer Name", "Amount", "Description"]]
    if not combined_df.empty:
        st.dataframe(
            combined_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SL": st.column_config.NumberColumn(width="small"),
                "Date": st.column_config.DateColumn(width="medium"),
                "Type": st.column_config.TextColumn(width="medium"),
                "Customer Name": st.column_config.TextColumn(width="large"),
                "Amount": st.column_config.NumberColumn(width="medium"),
                "Description": st.column_config.TextColumn(width="large"),
            }
        )
    else:
        st.info("No transactions recorded.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Export Data")
    if st.button("Generate PDF Report"):
        if clean_purchase_df.empty and clean_expense_df.empty and clean_sales_df.empty:
            st.error("No data available for PDF.")
        else:
            pdf_data = create_pdf(clean_purchase_df, clean_expense_df, clean_sales_df, selected_date, purchase_total, expense_total, sales_total, balance)
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=f"report_{selected_date.strftime('%Y-%m-%d')}.pdf",
                mime="application/pdf"
            )
    st.markdown('</div>', unsafe_allow_html=True)

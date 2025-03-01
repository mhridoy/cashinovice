import streamlit as st
import pandas as pd
from datetime import date
import io
from fpdf import FPDF

# Set page configuration
st.set_page_config(page_title="Business Transaction Manager", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: 'Arial', sans-serif; }
    .card { background-color: white; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #1e40af; color: white; border-radius: 6px; padding: 0.5rem 1rem; }
    .stButton>button:hover { background-color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 style='text-align: center; color: #1e40af;'>Business Transaction Manager</h1>", unsafe_allow_html=True)

# Date selector
st.markdown('<div class="card">', unsafe_allow_html=True)
selected_date = st.date_input("Transaction Date", date.today())
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state DataFrames
if 'purchase_df' not in st.session_state:
    st.session_state.purchase_df = pd.DataFrame({'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Customer Name': [''], 'Amount': [0.0], 'Purchase Description': ['']})
if 'expense_df' not in st.session_state:
    st.session_state.expense_df = pd.DataFrame({'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Expense Type': [''], 'Amount': [0.0], 'Expense Description': ['']})
if 'sales_df' not in st.session_state:
    st.session_state.sales_df = pd.DataFrame({'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Customer Name': ['Starting Balance'], 'Amount': [0.0], 'Sales Description': ['Opening Balance']})

# Helper function to update dates
def update_date(df, date_val):
    df['Date'] = date_val.strftime('%Y-%m-%d')
    return df

# PDF generation function
def create_pdf(purchase_df, expense_df, sales_df, date_val, purchase_total, expense_total, sales_total, balance):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Business Transaction Report", 1, 1, "C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"Date: {date_val.strftime('%Y-%m-%d')}", 0, 1, "L")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(95, 10, f"Total Purchase: Tk {purchase_total:,.2f}", 1, 0, "L")
    pdf.cell(95, 10, f"Total Expense: Tk {expense_total:,.2f}", 1, 1, "L")
    pdf.cell(95, 10, f"Total Sales: Tk {sales_total:,.2f}", 1, 0, "L")
    pdf.cell(95, 10, f"Today's Balance: Tk {balance:,.2f}", 1, 1, "L")
    pdf.ln(10)
    
    for title, df, cols, desc_col in [
        ("Purchases", purchase_df, ['SL', 'Date', 'Customer Name', 'Amount'], 'Purchase Description'),
        ("Expenses", expense_df, ['SL', 'Date', 'Expense Type', 'Amount'], 'Expense Description'),
        ("Sales", sales_df, ['SL', 'Date', 'Customer Name', 'Amount'], 'Sales Description')
    ]:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, title, 0, 1, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(20, 10, "SL", 1, 0)
        pdf.cell(40, 10, "Date", 1, 0)
        pdf.cell(50, 10, cols[2], 1, 0)
        pdf.cell(30, 10, "Amount", 1, 0)
        pdf.cell(50, 10, "Description", 1, 1)
        for _, row in df.iterrows():
            pdf.cell(20, 10, str(row['SL']), 1, 0)
            pdf.cell(40, 10, str(row['Date']), 1, 0)
            pdf.cell(50, 10, str(row[cols[2]]), 1, 0)
            pdf.cell(30, 10, f"{row['Amount']:,.2f}", 1, 0)
            pdf.cell(50, 10, str(row[desc_col]), 1, 1)
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin1')

# Tabs
tab1, tab2, tab3 = st.tabs(["Data Entry", "Dashboard", "Export"])

with tab1:
    # Purchase Entry
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Purchase Entry")
    purchase_editor = st.data_editor(
        st.session_state.purchase_df,
        num_rows="dynamic",
        key="purchase_editor",
        use_container_width=True,
        hide_index=True,
        column_config={"Amount": st.column_config.NumberColumn(format="%.2f")}
    )
    if st.button("Save Purchase", key="save_purchase"):
        st.session_state.purchase_df = update_date(purchase_editor, selected_date)
        st.success("Purchase data saved!")
    st.markdown('</div>', unsafe_allow_html=True)

    # Expense Entry
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Expense Entry")
    expense_editor = st.data_editor(
        st.session_state.expense_df,
        num_rows="dynamic",
        key="expense_editor",
        use_container_width=True,
        hide_index=True,
        column_config={"Amount": st.column_config.NumberColumn(format="%.2f")}
    )
    if st.button("Save Expense", key="save_expense"):
        st.session_state.expense_df = update_date(expense_editor, selected_date)
        st.success("Expense data saved!")
    st.markdown('</div>', unsafe_allow_html=True)

    # Sales Entry
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sales Entry")
    sales_editor = st.data_editor(
        st.session_state.sales_df,
        num_rows="dynamic",
        key="sales_editor",
        use_container_width=True,
        hide_index=True,
        column_config={"Amount": st.column_config.NumberColumn(format="%.2f")}
    )
    if st.button("Save Sales", key="save_sales"):
        st.session_state.sales_df = update_date(sales_editor, selected_date)
        st.success("Sales data saved!")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Dashboard")
    purchase_total = st.session_state.purchase_df['Amount'].sum()
    expense_total = st.session_state.expense_df['Amount'].sum()
    sales_total = st.session_state.sales_df['Amount'].sum()
    balance = sales_total - (purchase_total + expense_total)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Purchase", f"Tk {purchase_total:,.2f}")
    col2.metric("Total Expense", f"Tk {expense_total:,.2f}")
    col3.metric("Total Sales", f"Tk {sales_total:,.2f}")
    col4.metric("Balance", f"Tk {balance:,.2f}")
    
    st.subheader("All Transactions")
    combined_df = pd.concat([
        st.session_state.purchase_df.assign(Type="Purchase").rename(columns={"Purchase Description": "Description"}),
        st.session_state.expense_df.assign(Type="Expense").rename(columns={"Expense Type": "Customer Name", "Expense Description": "Description"}),
        st.session_state.sales_df.assign(Type="Sales").rename(columns={"Sales Description": "Description"})
    ])
    st.dataframe(combined_df[["Type", "Date", "Customer Name", "Amount", "Description"]], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Export")
    if st.button("Generate PDF"):
        pdf_data = create_pdf(
            st.session_state.purchase_df, st.session_state.expense_df, st.session_state.sales_df,
            selected_date, purchase_total, expense_total, sales_total, balance
        )
        st.download_button(
            "Download PDF",
            data=pdf_data,
            file_name=f"report_{selected_date.strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf"
        )
    st.markdown('</div>', unsafe_allow_html=True)

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

# Apply Tailwind CSS and custom styling
def load_css():
    return """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background-color: #f8fafc;
            font-family: 'Poppins', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif;
        }
        
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Poppins', sans-serif;
        }
        
        .dataframe th {
            background-color: #0f172a;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        
        .dataframe td {
            padding: 10px;
            border: 1px solid #e2e8f0;
        }
        
        .dataframe tr:nth-child(even) {
            background-color: #f8fafc;
        }
        
        .dataframe tr:hover {
            background-color: #dbeafe;
        }
        
        .stButton>button {
            background-color: #1e40af;
            color: white;
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: none;
            font-family: 'Poppins', sans-serif;
        }
        
        .stButton>button:hover {
            background-color: #1e3a8a;
            transform: translateY(-2px);
        }
        
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s;
        }
        
        .card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        .stat-card {
            background-color: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        .header-bg {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        /* Custom CSS for date input */
        div[data-baseweb="input"] {
            font-family: 'Poppins', sans-serif !important;
        }
        
        /* Beautiful scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #94a3b8;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #64748b;
        }
        
        /* Custom Select Box */
        div[data-baseweb="select"] {
            font-family: 'Poppins', sans-serif !important;
        }
        
        /* Custom tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8fafc;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #dbeafe;
            border-bottom: 2px solid #1e40af;
        }
        
        /* Remove unnecessary white boxes */
        .css-12oz5g7 {
            padding: 0 !important;
        }
        
        .css-1d391kg {
            padding: 0 !important;
        }
        
        /* Autocomplete styling */
        .autocomplete-suggestions {
            border: 1px solid #ddd;
            background: white;
            overflow: auto;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-radius: 6px;
            z-index: 9999;
        }
        
        .autocomplete-suggestion {
            padding: 8px 10px;
            white-space: nowrap;
            overflow: hidden;
            cursor: pointer;
        }
        
        .autocomplete-selected {
            background: #f0f0f0;
        }
        
        .autocomplete-group {
            padding: 8px 10px;
            background: #f8fafc;
            font-weight: bold;
        }
    </style>
    <script>
        // Function to add autocomplete suggestions to input fields
        function addAutocompleteBehavior() {
            const inputs = document.querySelectorAll('[data-testid="stDataEditorCell"] input');
            
            inputs.forEach(input => {
                if (input.getAttribute('autocomplete') !== 'on') {
                    input.setAttribute('autocomplete', 'on');
                    input.setAttribute('list', 'customer-names');
                }
            });
        }
        
        // Run on page load and periodically
        document.addEventListener('DOMContentLoaded', function() {
            setInterval(addAutocompleteBehavior, 1000);
        });
    </script>
    """

st.markdown(load_css(), unsafe_allow_html=True)

# App header with professional design
st.markdown("""
<div class="header-bg">
    <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">Business Transaction Manager</h1>
    <p style="font-size: 1.25rem; opacity: 0.9; margin-bottom: 0;">Track your daily business transactions with ease</p>
</div>
""", unsafe_allow_html=True)

# Date selector for all entries
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #334155; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">Select Date for All Entries</h3>', unsafe_allow_html=True)
selected_date = st.date_input("Transaction Date", date.today())
st.markdown('</div>', unsafe_allow_html=True)

# Initialize customer name suggestions list if not exists
if 'customer_names' not in st.session_state:
    st.session_state.customer_names = set()

# Initialize session state for dataframes if they don't exist
if 'purchase_df' not in st.session_state:
    st.session_state.purchase_df = pd.DataFrame({
        'SL': [1],
        'Date': [date.today().strftime('%Y-%m-%d')],
        'Customer Name': [''],
        'Amount': [0],
        'Purchase Description': ['']
    })

if 'sales_df' not in st.session_state:
    st.session_state.sales_df = pd.DataFrame({
        'SL': [1],
        'Date': [date.today().strftime('%Y-%m-%d')],
        'Customer Name': ['Starting Balance'],
        'Amount': [0],
        'Sales Description': ['Opening Balance']
    })

if 'expense_df' not in st.session_state:
    st.session_state.expense_df = pd.DataFrame({
        'SL': [1],
        'Date': [date.today().strftime('%Y-%m-%d')],
        'Expense Type': [''],
        'Amount': [0],
        'Expense Description': ['']
    })

# Function to ensure valid DataFrame structure before using data_editor
def ensure_valid_dataframe(df, default_structure, name="DataFrame"):
    try:
        # If not a DataFrame, convert it
        if not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
            except Exception as e:
                st.warning(f"Error converting {name} to DataFrame: {str(e)}")
                return default_structure.copy()
        
        # Clean data by converting to records and back
        try:
            records = df.to_dict('records')
            return pd.DataFrame(records)
        except Exception as e:
            st.warning(f"Error cleaning {name} data: {str(e)}")
            return default_structure.copy()
    except Exception as e:
        st.error(f"Unexpected error in {name}: {str(e)}")
        return default_structure.copy()

# Function to update date in dataframe
def update_date(df, date_val):
    # Create a copy to avoid SettingWithCopyWarning
    df_copy = df.copy()
    df_copy['Date'] = date_val.strftime('%Y-%m-%d')
    return df_copy

# Function to extract customer names from dataframes
def update_customer_names():
    # Extract customer names from purchase dataframe
    if 'purchase_df' in st.session_state and 'Customer Name' in st.session_state.purchase_df:
        purchase_customers = set(st.session_state.purchase_df['Customer Name'].dropna().unique())
        st.session_state.customer_names.update(purchase_customers)
    
    # Extract customer names from sales dataframe
    if 'sales_df' in st.session_state and 'Customer Name' in st.session_state.sales_df:
        sales_customers = set(st.session_state.sales_df['Customer Name'].dropna().unique())
        st.session_state.customer_names.update(sales_customers)

# Handle form submissions - Purchase
def submit_purchase():
    # Update the session state with clean data
    st.session_state.purchase_df = ensure_valid_dataframe(
        st.session_state.purchase_editor,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Purchase Description': ['']
        }),
        name="Purchase"
    )
    # Update all dates
    st.session_state.purchase_df = update_date(st.session_state.purchase_df, selected_date)
    # Update customer names list
    update_customer_names()

# Handle form submissions - Expense
def submit_expense():
    # Update the session state with clean data
    st.session_state.expense_df = ensure_valid_dataframe(
        st.session_state.expense_editor,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Expense Type': [''],
            'Amount': [0],
            'Expense Description': ['']
        }),
        name="Expense"
    )
    # Update all dates
    st.session_state.expense_df = update_date(st.session_state.expense_df, selected_date)

# Handle form submissions - Sales
def submit_sales():
    # Update the session state with clean data
    st.session_state.sales_df = ensure_valid_dataframe(
        st.session_state.sales_editor,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': ['Starting Balance'],
            'Amount': [0],
            'Sales Description': ['Opening Balance']
        }),
        name="Sales"
    )
    # Update all dates
    st.session_state.sales_df = update_date(st.session_state.sales_df, selected_date)
    # Update customer names list
    update_customer_names()

# Cleaned-up Create PDF function with improved error handling
def create_pdf(purchase_df, expense_df, sales_df, date_val, purchase_total, expense_total, sales_total, balance):
    try:
        # First, ensure clean DataFrames with valid data types
        purchase_df = ensure_valid_dataframe(purchase_df, 
            pd.DataFrame({
                'SL': [1],
                'Date': [date.today().strftime('%Y-%m-%d')],
                'Customer Name': [''],
                'Amount': [0],
                'Purchase Description': ['']
            }),
            name="Purchase for PDF"
        )
        
        expense_df = ensure_valid_dataframe(expense_df, 
            pd.DataFrame({
                'SL': [1],
                'Date': [date.today().strftime('%Y-%m-%d')],
                'Expense Type': [''],
                'Amount': [0],
                'Expense Description': ['']
            }),
            name="Expense for PDF"
        )
        
        sales_df = ensure_valid_dataframe(sales_df, 
            pd.DataFrame({
                'SL': [1],
                'Date': [date.today().strftime('%Y-%m-%d')],
                'Customer Name': ['Starting Balance'],
                'Amount': [0],
                'Sales Description': ['Opening Balance']
            }),
            name="Sales for PDF"
        )
        
        # Ensure Amount columns have numeric values
        purchase_df['Amount'] = pd.to_numeric(purchase_df['Amount'], errors='coerce').fillna(0)
        expense_df['Amount'] = pd.to_numeric(expense_df['Amount'], errors='coerce').fillna(0)
        sales_df['Amount'] = pd.to_numeric(sales_df['Amount'], errors='coerce').fillna(0)
        
        # Create new PDF with fixed encoding
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", "B", 16)
        
        # Title
        pdf.cell(190, 10, "Business Transaction Report", 1, 1, "C")
        pdf.ln(10)
        
        # Date
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"Date: {date_val.strftime('%Y-%m-%d')}", 0, 1, "L")
        pdf.ln(5)
        
        # Summary Section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Summary:", 0, 1, "L")
        pdf.ln(2)
        
        # Use proper currency formatting with Tk symbol for Bengali Taka
        pdf.set_font("Arial", "", 12)
        pdf.cell(95, 10, f"Total Purchase: Tk {purchase_total:,.2f}", 1, 0, "L")
        pdf.cell(95, 10, f"Total Expense: Tk {expense_total:,.2f}", 1, 1, "L")
        pdf.cell(95, 10, f"Total Sales: Tk {sales_total:,.2f}", 1, 0, "L")
        
        # Balance (may be positive or negative)
        balance_label = "Today's Balance"
        pdf.cell(95, 10, f"{balance_label}: Tk {balance:,.2f}", 1, 1, "L")
        pdf.ln(10)
        
        # Purchase Table
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Purchase Transactions:", 0, 1, "L")
        pdf.ln(2)
        
        # Table header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(15, 10, "SL", 1, 0, "C")
        pdf.cell(35, 10, "Date", 1, 0, "C")
        pdf.cell(50, 10, "Customer Name", 1, 0, "C")
        pdf.cell(40, 10, "Amount", 1, 0, "C")
        pdf.cell(50, 10, "Description", 1, 1, "C")
        
        # Table content with safe string handling
        pdf.set_font("Arial", "", 10)
        for i, row in purchase_df.iterrows():
            pdf.cell(15, 10, str(row.get('SL', '')), 1, 0, "C")
            pdf.cell(35, 10, str(row.get('Date', '')), 1, 0, "C")
            
            # Safely truncate customer name if too long
            customer_name = str(row.get('Customer Name', ''))
            if len(customer_name) > 20:
                customer_name = customer_name[:17] + "..."
            pdf.cell(50, 10, customer_name, 1, 0, "L")
            
            # Format amount with error handling
            amount = row.get('Amount', 0)
            try:
                amount_str = f"Tk {float(amount):,.2f}"
            except (ValueError, TypeError):
                amount_str = "Tk 0.00"
            pdf.cell(40, 10, amount_str, 1, 0, "R")
            
            # Safely truncate description if too long
            description = str(row.get('Purchase Description', ''))
            if len(description) > 20:
                description = description[:17] + "..."
            pdf.cell(50, 10, description, 1, 1, "L")
        
        pdf.ln(10)
        
        # Expense Table
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Expense Transactions:", 0, 1, "L")
        pdf.ln(2)
        
        # Table header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(15, 10, "SL", 1, 0, "C")
        pdf.cell(35, 10, "Date", 1, 0, "C")
        pdf.cell(50, 10, "Expense Type", 1, 0, "C")
        pdf.cell(40, 10, "Amount", 1, 0, "C")
        pdf.cell(50, 10, "Description", 1, 1, "C")
        
        # Table content with safe string handling
        pdf.set_font("Arial", "", 10)
        for i, row in expense_df.iterrows():
            pdf.cell(15, 10, str(row.get('SL', '')), 1, 0, "C")
            pdf.cell(35, 10, str(row.get('Date', '')), 1, 0, "C")
            
            # Safely truncate expense type if too long
            expense_type = str(row.get('Expense Type', ''))
            if len(expense_type) > 20:
                expense_type = expense_type[:17] + "..."
            pdf.cell(50, 10, expense_type, 1, 0, "L")
            
            # Format amount with error handling
            amount = row.get('Amount', 0)
            try:
                amount_str = f"Tk {float(amount):,.2f}"
            except (ValueError, TypeError):
                amount_str = "Tk 0.00"
            pdf.cell(40, 10, amount_str, 1, 0, "R")
            
            # Safely truncate description if too long
            description = str(row.get('Expense Description', ''))
            if len(description) > 20:
                description = description[:17] + "..."
            pdf.cell(50, 10, description, 1, 1, "L")
        
        pdf.ln(10)
        
        # Sales Table
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Sales Transactions:", 0, 1, "L")
        pdf.ln(2)
        
        # Table header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(15, 10, "SL", 1, 0, "C")
        pdf.cell(35, 10, "Date", 1, 0, "C")
        pdf.cell(50, 10, "Customer Name", 1, 0, "C")
        pdf.cell(40, 10, "Amount", 1, 0, "C")
        pdf.cell(50, 10, "Description", 1, 1, "C")
        
        # Table content with safe string handling
        pdf.set_font("Arial", "", 10)
        for i, row in sales_df.iterrows():
            pdf.cell(15, 10, str(row.get('SL', '')), 1, 0, "C")
            pdf.cell(35, 10, str(row.get('Date', '')), 1, 0, "C")
            
            # Safely truncate customer name if too long
            customer_name = str(row.get('Customer Name', ''))
            if len(customer_name) > 20:
                customer_name = customer_name[:17] + "..."
            pdf.cell(50, 10, customer_name, 1, 0, "L")
            
            # Format amount with error handling
            amount = row.get('Amount', 0)
            try:
                amount_str = f"Tk {float(amount):,.2f}"
            except (ValueError, TypeError):
                amount_str = "Tk 0.00"
            pdf.cell(40, 10, amount_str, 1, 0, "R")
            
            # Safely truncate description if too long
            description = str(row.get('Sales Description', ''))
            if len(description) > 20:
                description = description[:17] + "..."
            pdf.cell(50, 10, description, 1, 1, "L")
        
        # Footer
        pdf.ln(20)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "Business Transaction Manager - Generated on " + date.today().strftime("%Y-%m-%d"), 0, 0, "C")
        
        # Return the PDF as bytes with ASCII encoding
        return pdf.output(dest='S').encode('latin1')
    
    except Exception as e:
        # Detailed error logging
        st.error(f"PDF Generation Error: {str(e)}")
        st.error(f"Error Details: {traceback.format_exc()}")
        raise Exception(f"PDF creation failed: {str(e)}")

# Create a datalist for customer name autocomplete
customer_list_html = "<datalist id='customer-names'>"
for name in st.session_state.customer_names:
    if name and name != 'Starting Balance':
        customer_list_html += f"<option value='{name}'>"
customer_list_html += "</datalist>"
st.markdown(customer_list_html, unsafe_allow_html=True)

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Data Entry", "📈 Dashboard", "📋 Export"])

with tab1:
    col1, col2 = st.columns(2)
    
    # Purchase Section
    with col1:
        st.markdown('<div class="card" style="border-left: 5px solid #1e40af;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #1e40af; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">💸 Purchase Entry</h2>', unsafe_allow_html=True)
        
        # Clean the DataFrame before using data_editor
        clean_purchase_df = ensure_valid_dataframe(
            st.session_state.purchase_df,
            pd.DataFrame({
                'SL': [1],
                'Date': [date.today().strftime('%Y-%m-%d')],
                'Customer Name': [''],
                'Amount': [0],
                'Purchase Description': ['']
            }),
            name="Purchase"
        )
        
        # Display current purchase data
        edited_purchase_df = st.data_editor(
            clean_purchase_df,
            num_rows="dynamic",
            key="purchase_editor",
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("Save Purchase Data", key="save_purchase", on_click=submit_purchase):
            st.success("✅ Purchase data saved successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Expense Section
        st.markdown('<div class="card" style="border-left: 5px solid #be123c;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #be123c; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">💸 Expense Entry</h2>', unsafe_allow_html=True)
        
        # Clean the DataFrame before using data_editor
        clean_expense_df = ensure_valid_dataframe(
            st.session_state.expense_df,
            pd.DataFrame({
                'SL': [1],
                'Date': [date.today().strftime('%Y-%m-%d')],
                'Expense Type': [''],
                'Amount': [0],
                'Expense Description': ['']
            }),
            name="Expense"
        )
        
        # Display current expense data
        edited_expense_df = st.data_editor(
            clean_expense_df,
            num_rows="dynamic",
            key="expense_editor",
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("Save Expense Data", key="save_expense", on_click=submit_expense):
            st.success("✅ Expense data saved successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sales Section
    with col2:
        st.markdown('<div class="card" style="border-left: 5px solid #047857;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #047857; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">💰 Sales Entry</h2>', unsafe_allow_html=True)
        
        # Clean the DataFrame before using data_editor
        clean_sales_df = ensure_valid_dataframe(
            st.session_state.sales_df,
            pd.DataFrame({
                'SL': [1],
                'Date': [date.today().strftime('%Y-%m-%d')],
                'Customer Name': ['Starting Balance'],
                'Amount': [0],
                'Sales Description': ['Opening Balance']
            }),
            name="Sales"
        )
        
        # Display current sales data with starting balance row
        edited_sales_df = st.data_editor(
            clean_sales_df,
            num_rows="dynamic",
            key="sales_editor",
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("Save Sales Data", key="save_sales", on_click=submit_sales):
            st.success("✅ Sales data saved successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    # Ensure clean data for calculations
    clean_purchase_df = ensure_valid_dataframe(
        st.session_state.purchase_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Purchase Description': ['']
        }),
        name="Purchase"
    )
    
    clean_expense_df = ensure_valid_dataframe(
        st.session_state.expense_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Expense Type': [''],
            'Amount': [0],
            'Expense Description': ['']
        }),
        name="Expense"
    )
    
    clean_sales_df = ensure_valid_dataframe(
        st.session_state.sales_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': ['Starting Balance'],
            'Amount': [0],
            'Sales Description': ['Opening Balance']
        }),
        name="Sales"
    )
    
    # Ensure Amount columns are numeric
    clean_purchase_df['Amount'] = pd.to_numeric(clean_purchase_df['Amount'], errors='coerce').fillna(0)
    clean_expense_df['Amount'] = pd.to_numeric(clean_expense_df['Amount'], errors='coerce').fillna(0)
    clean_sales_df['Amount'] = pd.to_numeric(clean_sales_df['Amount'], errors='coerce').fillna(0)
    
    # Calculate totals and balance
    purchase_total = clean_purchase_df['Amount'].sum()
    expense_total = clean_expense_df['Amount'].sum()
    sales_total = clean_sales_df['Amount'].sum()
    balance = sales_total - (purchase_total + expense_total)
    
    # Summary Stats
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Business Overview</h2>', unsafe_allow_html=True)
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid #1e40af;">
                <h3 style="color: #1e40af; font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem;">Total Purchase</h3>
                <p style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">৳{purchase_total:,.2f}</p>
                <div style="width: 60px; height: 4px; background-color: #bfdbfe; border-radius: 2px; margin-top: 0.5rem;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col_stat2:
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid #be123c;">
                <h3 style="color: #be123c; font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem;">Total Expense</h3>
                <p style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">৳{expense_total:,.2f}</p>
                <div style="width: 60px; height: 4px; background-color: #fecdd3; border-radius: 2px; margin-top: 0.5rem;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col_stat3:
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid #047857;">
                <h3 style="color: #047857; font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem;">Total Sales</h3>
                <p style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">৳{sales_total:,.2f}</p>
                <div style="width: 60px; height: 4px; background-color: #a7f3d0; border-radius: 2px; margin-top: 0.5rem;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col_stat4:
        balance_label = "Today's Balance"
        border_color = "#047857" if balance >= 0 else "#be123c"
        text_color = "#047857" if balance >= 0 else "#be123c"
        bar_color = "#a7f3d0" if balance >= 0 else "#fecdd3"
        
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid {border_color};">
                <h3 style="color: {text_color}; font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem;">{balance_label}</h3>
                <p style="font-size: 2rem; font-weight: 700; color: {text_color}; margin: 0;">৳{balance:,.2f}</p>
                <div style="width: 60px; height: 4px; background-color: {bar_color}; border-radius: 2px; margin-top: 0.5rem;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data Visualizations
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Data Visualization</h2>', unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Bar chart for comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = ['Purchase', 'Expense', 'Sales']
        values = [purchase_total, expense_total, sales_total]
        
        bars = ax.bar(categories, values, color=['#1e40af', '#be123c', '#047857'])
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'৳{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
        
        ax.set_title('Transaction Comparison', fontsize=16, fontweight='bold')
        ax.set_ylabel('Amount (৳)', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add balance annotation
        balance_text = f"Today's Balance: ৳{balance:,.0f}"
        balance_color = '#047857' if balance >= 0 else '#be123c'
        ax.annotate(balance_text, 
                   xy=(0.5, 0.9), 
                   xycoords='axes fraction',
                   fontsize=12,
                   fontweight='bold',
                   color=balance_color,
                   bbox=dict(boxstyle="round,pad=0.5", fc='#f8fafc', ec=balance_color, alpha=0.8))
        
        st.pyplot(fig)
    
    with col_chart2:
        if purchase_total > 0 or expense_total > 0 or sales_total > 0:
            # Create a custom donut chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Data
            labels = ['Purchase', 'Expense', 'Sales']
            sizes = [purchase_total, expense_total, sales_total]
            colors = ['#1e40af', '#be123c', '#047857']
            
            # Create a circle for the center
            centre_circle = plt.Circle((0, 0), 0.7, fc='white')
            
            # Create donut plot
            wedges, texts, autotexts = ax.pie(sizes, labels=None, colors=colors,
                   autopct=lambda p: f'৳{p * sum(sizes)/100:,.0f}',
                   startangle=90, pctdistance=0.85,
                   wedgeprops=dict(width=0.3, edgecolor='w'))
            
            # Add the center circle
            fig.gca().add_artist(centre_circle)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Add title
            ax.set_title('Transaction Distribution', fontsize=16, fontweight='bold')
            
            # Add custom legend
            ax.legend(wedges, labels, loc="center", bbox_to_anchor=(0.5, 0.5), frameon=False)
            
            st.pyplot(fig)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transactions Table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Recent Transactions</h2>', unsafe_allow_html=True)
    
    # Show all transactions
    if not clean_purchase_df.empty and 'Purchase Description' in clean_purchase_df.columns:
        purchase_display = clean_purchase_df.copy()
        purchase_display['Type'] = 'Purchase'
        purchase_display = purchase_display.rename(columns={'Purchase Description': 'Description'})
    else:
        purchase_display = pd.DataFrame(columns=['SL', 'Date', 'Customer Name', 'Amount', 'Description', 'Type'])
    
    if not clean_expense_df.empty and 'Expense Description' in clean_expense_df.columns:
        expense_display = clean_expense_df.copy()
        expense_display['Type'] = 'Expense'
        expense_display['Customer Name'] = expense_display['Expense Type']  # For consistent columns
        expense_display = expense_display.rename(columns={'Expense Description': 'Description'})
        expense_display = expense_display[['SL', 'Date', 'Customer Name', 'Amount', 'Description', 'Type']]
    else:
        expense_display = pd.DataFrame(columns=['SL', 'Date', 'Customer Name', 'Amount', 'Description', 'Type'])
    
    if not clean_sales_df.empty and 'Sales Description' in clean_sales_df.columns:
        sales_display = clean_sales_df.copy()
        sales_display['Type'] = 'Sales'
        sales_display = sales_display.rename(columns={'Sales Description': 'Description'})
    else:
        sales_display = pd.DataFrame(columns=['SL', 'Date', 'Customer Name', 'Amount', 'Description', 'Type'])
    
    # Combine and display all transactions
    combined_df = pd.concat([purchase_display, expense_display, sales_display])
    combined_df = combined_df[['SL', 'Date', 'Type', 'Customer Name', 'Amount', 'Description']]
    
    if not combined_df.empty:
        st.dataframe(combined_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions recorded yet.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Export Data</h2>', unsafe_allow_html=True)
    
    col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
    
    # Ensure clean data for downloads
    clean_purchase_df = ensure_valid_dataframe(
        st.session_state.purchase_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Purchase Description': ['']
        }),
        name="Purchase"
    )
    
    clean_expense_df = ensure_valid_dataframe(
        st.session_state.expense_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Expense Type': [''],
            'Amount': [0],
            'Expense Description': ['']
        }),
        name="Expense"
    )
    
    clean_sales_df = ensure_valid_dataframe(
        st.session_state.sales_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': ['Starting Balance'],
            'Amount': [0],
            'Sales Description': ['Opening Balance']
        }),
        name="Sales"
    )
    
    # Ensure Amount columns are numeric for exports
    clean_purchase_df['Amount'] = pd.to_numeric(clean_purchase_df['Amount'], errors='coerce').fillna(0)
    clean_expense_df['Amount'] = pd.to_numeric(clean_expense_df['Amount'], errors='coerce').fillna(0)
    clean_sales_df['Amount'] = pd.to_numeric(clean_sales_df['Amount'], errors='coerce').fillna(0)
    
    with col_exp1:
        if st.button("Download Purchase Data (CSV)", key="download_purchase"):
            csv = clean_purchase_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Click to Download Purchase CSV",
                data=csv,
                file_name=f"purchase_data_{selected_date.strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp2:
        if st.button("Download Expense Data (CSV)", key="download_expense"):
            csv = clean_expense_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Click to Download Expense CSV",
                data=csv,
                file_name=f"expense_data_{selected_date.strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp3:
        if st.button("Download Sales Data (CSV)", key="download_sales"):
            csv = clean_sales_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Click to Download Sales CSV",
                data=csv,
                file_name=f"sales_data_{selected_date.strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp4:
        if st.button("Generate Complete Report (PDF)", key="generate_pdf"):
            try:
                # Verify the data is valid before trying to generate PDF
                valid_purchase_data = not clean_purchase_df.empty and 'Purchase Description' in clean_purchase_df.columns
                valid_expense_data = not clean_expense_df.empty and 'Expense Description' in clean_expense_df.columns
                valid_sales_data = not clean_sales_df.empty and 'Sales Description' in clean_sales_df.columns
                
                if not (valid_purchase_data or valid_expense_data or valid_sales_data):
                    st.error("No valid transaction data available. Please add some transactions first.")
                else:
                    # Calculate totals for PDF with proper numeric handling
                    purchase_total = clean_purchase_df['Amount'].sum()
                    expense_total = clean_expense_df['Amount'].sum()
                    sales_total = clean_sales_df['Amount'].sum()
                    balance = sales_total - (purchase_total + expense_total)
                    
                    # Show progress information
                    with st.spinner("Generating PDF report..."):
                        # Generate PDF with improved error handling
                        pdf_data = create_pdf(
                            clean_purchase_df,
                            clean_expense_df,
                            clean_sales_df,
                            selected_date,
                            purchase_total,
                            expense_total,
                            sales_total,
                            balance
                        )
                        
                        # Offer download
                        st.success("PDF generated successfully!")
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_data,
                            file_name=f"business_report_{selected_date.strftime('%Y-%m-%d')}.pdf",
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.error("If the problem persists, try using simplified data or exporting as CSV instead.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Preview section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Report Preview</h2>', unsafe_allow_html=True)
    
    # Create tabs for different views
    preview_tab1, preview_tab2, preview_tab3 = st.tabs(["Purchase Data", "Expense Data", "Sales Data"])
    
    with preview_tab1:
        if not clean_purchase_df.empty:
            st.dataframe(clean_purchase_df, use_container_width=True)
        else:
            st.info("No purchase data available.")
    
    with preview_tab2:
        if not clean_expense_df.empty:
            st.dataframe(clean_expense_df, use_container_width=True)
        else:
            st.info("No expense data available.")
    
    with preview_tab3:
        if not clean_sales_df.empty:
            st.dataframe(clean_sales_df, use_container_width=True)
        else:
            st.info("No sales data available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background: linear-gradient(90deg, #1e3a8a, #1e40af); border-radius: 8px; color: white;">
    <p style="margin-bottom: 0.5rem; font-weight: 500;">Business Transaction Manager</p>
    <p style="font-size: 0.875rem; opacity: 0.9; margin: 0;">© 2025 | Made with ❤️ for your business</p>
</div>
""", unsafe_allow_html=True)

# Add required packages to requirements.txt
requirements = """
streamlit
pandas
matplotlib
fpdf
seaborn
numpy
"""

with open("requirements.txt", "w") as f:
    f.write(requirements)

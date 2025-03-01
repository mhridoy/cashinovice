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
        
        // Run periodically
        setInterval(addAutocompleteBehavior, 1000);
    </script>
    """

st.markdown(load_css(), unsafe_allow_html=True)

# App header
st.markdown("""
<div class="header-bg">
    <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">Business Transaction Manager</h1>
    <p style="font-size: 1.25rem; opacity: 0.9; margin-bottom: 0;">Track your daily business transactions with ease</p>
</div>
""", unsafe_allow_html=True)

# Date selector
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #334155; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">Select Date for All Entries</h3>', unsafe_allow_html=True)
selected_date = st.date_input("Transaction Date", date.today())
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if 'customer_names' not in st.session_state:
    st.session_state.customer_names = set()

if 'purchase_df' not in st.session_state:
    st.session_state.purchase_df = pd.DataFrame({
        'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Customer Name': [''], 'Amount': [0], 'Purchase Description': ['']
    })

if 'sales_df' not in st.session_state:
    st.session_state.sales_df = pd.DataFrame({
        'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Customer Name': ['Starting Balance'], 'Amount': [0], 'Sales Description': ['Opening Balance']
    })

if 'expense_df' not in st.session_state:
    st.session_state.expense_df = pd.DataFrame({
        'SL': [1], 'Date': [date.today().strftime('%Y-%m-%d')], 'Expense Type': [''], 'Amount': [0], 'Expense Description': ['']
    })

# Define column configurations
purchase_column_config = {
    "SL": st.column_config.NumberColumn(width="small"),
    "Date": st.column_config.DateColumn(width="medium", disabled=True),
    "Customer Name": st.column_config.TextColumn(width="large"),
    "Amount": st.column_config.NumberColumn(width="medium"),
    "Purchase Description": st.column_config.TextColumn(width="large"),
}

expense_column_config = {
    "SL": st.column_config.NumberColumn(width="small"),
    "Date": st.column_config.DateColumn(width="medium", disabled=True),
    "Expense Type": st.column_config.TextColumn(width="large"),
    "Amount": st.column_config.NumberColumn(width="medium"),
    "Expense Description": st.column_config.TextColumn(width="large"),
}

sales_column_config = {
    "SL": st.column_config.NumberColumn(width="small"),
    "Date": st.column_config.DateColumn(width="medium", disabled=True),
    "Customer Name": st.column_config.TextColumn(width="large"),
    "Amount": st.column_config.NumberColumn(width="medium"),
    "Sales Description": st.column_config.TextColumn(width="large"),
}

# Helper functions
def ensure_valid_dataframe(df, default_structure, name="DataFrame"):
    try:
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        records = df.to_dict('records')
        return pd.DataFrame(records)
    except Exception as e:
        st.warning(f"Error in {name}: {str(e)}")
        return default_structure.copy()

def update_date(df, date_val):
    df_copy = df.copy()
    df_copy['Date'] = date_val.strftime('%Y-%m-%d')
    return df_copy

def update_customer_names():
    if 'purchase_df' in st.session_state and 'Customer Name' in st.session_state.purchase_df:
        st.session_state.customer_names.update(st.session_state.purchase_df['Customer Name'].dropna().unique())
    if 'sales_df' in st.session_state and 'Customer Name' in st.session_state.sales_df:
        st.session_state.customer_names.update(st.session_state.sales_df['Customer Name'].dropna().unique())

def submit_purchase():
    st.session_state.purchase_df = ensure_valid_dataframe(
        st.session_state.purchase_editor, st.session_state.purchase_df, "Purchase"
    )
    st.session_state.purchase_df = update_date(st.session_state.purchase_df, selected_date)
    update_customer_names()

def submit_expense():
    st.session_state.expense_df = ensure_valid_dataframe(
        st.session_state.expense_editor, st.session_state.expense_df, "Expense"
    )
    st.session_state.expense_df = update_date(st.session_state.expense_df, selected_date)

def submit_sales():
    st.session_state.sales_df = ensure_valid_dataframe(
        st.session_state.sales_editor, st.session_state.sales_df, "Sales"
    )
    st.session_state.sales_df = update_date(st.session_state.sales_df, selected_date)
    update_customer_names()

def create_pdf(purchase_df, expense_df, sales_df, date_val, purchase_total, expense_total, sales_total, balance):
    try:
        purchase_df['Amount'] = pd.to_numeric(purchase_df['Amount'], errors='coerce').fillna(0)
        expense_df['Amount'] = pd.to_numeric(expense_df['Amount'], errors='coerce').fillna(0)
        sales_df['Amount'] = pd.to_numeric(sales_df['Amount'], errors='coerce').fillna(0)
        
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
        
        # Purchase Table
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Purchase Transactions:", 0, 1, "L")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(15, 10, "SL", 1, 0, "C")
        pdf.cell(35, 10, "Date", 1, 0, "C")
        pdf.cell(50, 10, "Customer Name", 1, 0, "C")
        pdf.cell(40, 10, "Amount", 1, 0, "C")
        pdf.cell(50, 10, "Description", 1, 1, "C")
        pdf.set_font("Arial", "", 10)
        for i, row in purchase_df.iterrows():
            pdf.cell(15, 10, str(row.get('SL', '')), 1, 0, "C")
            pdf.cell(35, 10, str(row.get('Date', '')), 1, 0, "C")
            customer_name = str(row.get('Customer Name', ''))[:20] + "..." if len(str(row.get('Customer Name', ''))) > 20 else str(row.get('Customer Name', ''))
            pdf.cell(50, 10, customer_name, 1, 0, "L")
            pdf.cell(40, 10, f"Tk {float(row.get('Amount', 0)):,.2f}", 1, 0, "R")
            description = str(row.get('Purchase Description', ''))[:20] + "..." if len(str(row.get('Purchase Description', ''))) > 20 else str(row.get('Purchase Description', ''))
            pdf.cell(50, 10, description, 1, 1, "L")
        pdf.ln(10)
        
        # Expense Table
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Expense Transactions:", 0, 1, "L")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(15, 10, "SL", 1, 0, "C")
        pdf.cell(35, 10, "Date", 1, 0, "C")
        pdf.cell(50, 10, "Expense Type", 1, 0, "C")
        pdf.cell(40, 10, "Amount", 1, 0, "C")
        pdf.cell(50, 10, "Description", 1, 1, "C")
        pdf.set_font("Arial", "", 10)
        for i, row in expense_df.iterrows():
            pdf.cell(15, 10, str(row.get('SL', '')), 1, 0, "C")
            pdf.cell(35, 10, str(row.get('Date', '')), 1, 0, "C")
            expense_type = str(row.get('Expense Type', ''))[:20] + "..." if len(str(row.get('Expense Type', ''))) > 20 else str(row.get('Expense Type', ''))
            pdf.cell(50, 10, expense_type, 1, 0, "L")
            pdf.cell(40, 10, f"Tk {float(row.get('Amount', 0)):,.2f}", 1, 0, "R")
            description = str(row.get('Expense Description', ''))[:20] + "..." if len(str(row.get('Expense Description', ''))) > 20 else str(row.get('Expense Description', ''))
            pdf.cell(50, 10, description, 1, 1, "L")
        pdf.ln(10)
        
        # Sales Table
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Sales Transactions:", 0, 1, "L")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(15, 10, "SL", 1, 0, "C")
        pdf.cell(35, 10, "Date", 1, 0, "C")
        pdf.cell(50, 10, "Customer Name", 1, 0, "C")
        pdf.cell(40, 10, "Amount", 1, 0, "C")
        pdf.cell(50, 10, "Description", 1, 1, "C")
        pdf.set_font("Arial", "", 10)
        for i, row in sales_df.iterrows():
            pdf.cell(15, 10, str(row.get('SL', '')), 1, 0, "C")
            pdf.cell(35, 10, str(row.get('Date', '')), 1, 0, "C")
            customer_name = str(row.get('Customer Name', ''))[:20] + "..." if len(str(row.get('Customer Name', ''))) > 20 else str(row.get('Customer Name', ''))
            pdf.cell(50, 10, customer_name, 1, 0, "L")
            pdf.cell(40, 10, f"Tk {float(row.get('Amount', 0)):,.2f}", 1, 0, "R")
            description = str(row.get('Sales Description', ''))[:20] + "..." if len(str(row.get('Sales Description', ''))) > 20 else str(row.get('Sales Description', ''))
            pdf.cell(50, 10, description, 1, 1, "L")
        
        pdf.ln(20)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "Generated on " + date.today().strftime("%Y-%m-%d"), 0, 0, "C")
        
        return pdf.output(dest='S').encode('latin1')
    except Exception as e:
        st.error(f"PDF Generation Error: {str(e)}")
        raise

# Autocomplete datalist
customer_list_html = "<datalist id='customer-names'>"
for name in st.session_state.customer_names:
    if name and name != 'Starting Balance':
        customer_list_html += f"<option value='{name}'>"
customer_list_html += "</datalist>"
st.markdown(customer_list_html, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Data Entry", "📈 Dashboard", "📋 Export"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Purchase Entry
        st.markdown('<div class="card" style="border-left: 5px solid #1e40af;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #1e40af; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">💸 Purchase Entry</h2>', unsafe_allow_html=True)
        st.info("Note: The 'Date' column will be set to the selected date when saving.")
        clean_purchase_df = ensure_valid_dataframe(st.session_state.purchase_df, st.session_state.purchase_df, "Purchase")
        st.data_editor(
            clean_purchase_df,
            num_rows="dynamic",
            key="purchase_editor",
            use_container_width=True,
            hide_index=True,
            column_config=purchase_column_config
        )
        if st.button("Save Purchase Data", key="save_purchase", on_click=submit_purchase):
            st.success("✅ Purchase data saved!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Expense Entry
        st.markdown('<div class="card" style="border-left: 5px solid #be123c;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #be123c; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">💸 Expense Entry</h2>', unsafe_allow_html=True)
        st.info("Note: The 'Date' column will be set to the selected date when saving.")
        clean_expense_df = ensure_valid_dataframe(st.session_state.expense_df, st.session_state.expense_df, "Expense")
        st.data_editor(
            clean_expense_df,
            num_rows="dynamic",
            key="expense_editor",
            use_container_width=True,
            hide_index=True,
            column_config=expense_column_config
        )
        if st.button("Save Expense Data", key="save_expense", on_click=submit_expense):
            st.success("✅ Expense data saved!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Sales Entry
        st.markdown('<div class="card" style="border-left: 5px solid #047857;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #047857; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">💰 Sales Entry</h2>', unsafe_allow_html=True)
        st.info("Note: The 'Date' column will be set to the selected date when saving.")
        clean_sales_df = ensure_valid_dataframe(st.session_state.sales_df, st.session_state.sales_df, "Sales")
        st.data_editor(
            clean_sales_df,
            num_rows="dynamic",
            key="sales_editor",
            use_container_width=True,
            hide_index=True,
            column_config=sales_column_config
        )
        if st.button("Save Sales Data", key="save_sales", on_click=submit_sales):
            st.success("✅ Sales data saved!")
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
    
    # Summary Stats
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Business Overview</h2>', unsafe_allow_html=True)
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown(f'<div class="stat-card" style="border-top: 4px solid #1e40af;"><h3 style="color: #1e40af;">Total Purchase</h3><p style="font-size: 2rem; font-weight: 700; color: #0f172a;">৳{purchase_total:,.2f}</p></div>', unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f'<div class="stat-card" style="border-top: 4px solid #be123c;"><h3 style="color: #be123c;">Total Expense</h3><p style="font-size: 2rem; font-weight: 700; color: #0f172a;">৳{expense_total:,.2f}</p></div>', unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f'<div class="stat-card" style="border-top: 4px solid #047857;"><h3 style="color: #047857;">Total Sales</h3><p style="font-size: 2rem; font-weight: 700; color: #0f172a;">৳{sales_total:,.2f}</p></div>', unsafe_allow_html=True)
    with col_stat4:
        color = "#047857" if balance >= 0 else "#be123c"
        st.markdown(f'<div class="stat-card" style="border-top: 4px solid {color};"><h3 style="color: {color};">Today\'s Balance</h3><p style="font-size: 2rem; font-weight: 700; color: {color};">৳{balance:,.2f}</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Data Visualization</h2>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(['Purchase', 'Expense', 'Sales'], [purchase_total, expense_total, sales_total], color=['#1e40af', '#be123c', '#047857'])
        for bar in bars:
            ax.annotate(f'৳{bar.get_height():,.0f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), xytext=(0, 3), textcoords="offset points", ha='center', fontweight='bold')
        ax.set_title('Transaction Comparison')
        ax.set_ylabel('Amount (৳)')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
    with col_chart2:
        if purchase_total + expense_total + sales_total > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.pie([purchase_total, expense_total, sales_total], labels=['Purchase', 'Expense', 'Sales'], colors=['#1e40af', '#be123c', '#047857'], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3))
            centre_circle = plt.Circle((0, 0), 0.7, fc='white')
            fig.gca().add_artist(centre_circle)
            ax.set_title('Transaction Distribution')
            st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transactions Table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Recent Transactions</h2>', unsafe_allow_html=True)
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
    combined_df = pd.concat([purchase_display, expense_display, sales_display])[['SL', 'Date', 'Type', 'Customer Name', 'Amount', 'Description']]
    if not combined_df.empty:
        st.dataframe(combined_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions recorded.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Export Data</h2>', unsafe_allow_html=True)
    col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
    clean_purchase_df = ensure_valid_dataframe(st.session_state.purchase_df, st.session_state.purchase_df, "Purchase")
    clean_expense_df = ensure_valid_dataframe(st.session_state.expense_df, st.session_state.expense_df, "Expense")
    clean_sales_df = ensure_valid_dataframe(st.session_state.sales_df, st.session_state.sales_df, "Sales")
    
    with col_exp1:
        if st.button("Download Purchase CSV", key="download_purchase"):
            csv = clean_purchase_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download", data=csv, file_name=f"purchase_{selected_date.strftime('%Y-%m-%d')}.csv", mime="text/csv")
    with col_exp2:
        if st.button("Download Expense CSV", key="download_expense"):
            csv = clean_expense_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download", data=csv, file_name=f"expense_{selected_date.strftime('%Y-%m-%d')}.csv", mime="text/csv")
    with col_exp3:
        if st.button("Download Sales CSV", key="download_sales"):
            csv = clean_sales_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download", data=csv, file_name=f"sales_{selected_date.strftime('%Y-%m-%d')}.csv", mime="text/csv")
    with col_exp4:
        if st.button("Generate PDF Report", key="generate_pdf"):
            if clean_purchase_df.empty and clean_expense_df.empty and clean_sales_df.empty:
                st.error("No data available for PDF.")
            else:
                with st.spinner("Generating PDF..."):
                    pdf_data = create_pdf(clean_purchase_df, clean_expense_df, clean_sales_df, selected_date, purchase_total, expense_total, sales_total, balance)
                    st.download_button(label="Download PDF", data=pdf_data, file_name=f"report_{selected_date.strftime('%Y-%m-%d')}.pdf", mime="application/pdf")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background: linear-gradient(90deg, #1e3a8a, #1e40af); border-radius: 8px; color: white;">
    <p style="margin-bottom: 0.5rem; font-weight: 500;">Business Transaction Manager</p>
    <p style="font-size: 0.875rem; opacity: 0.9; margin: 0;">© 2025 | Made with ❤️ for your business</p>
</div>
""", unsafe_allow_html=True)

# Requirements
with open("requirements.txt", "w") as f:
    f.write("streamlit\npandas\nmatplotlib\nfpdf\nseaborn\nnumpy\n")

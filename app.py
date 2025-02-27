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
import os

# Set page configuration
st.set_page_config(page_title="Sales & Purchase Tracker", layout="wide", initial_sidebar_state="collapsed")

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
            padding: 8px;
            text-align: left;
            font-weight: 600;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        
        .dataframe td {
            padding: 8px;
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
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: none;
            font-family: 'Poppins', sans-serif;
        }
        
        .stButton>button:hover {
            background-color: #1e3a8a;
            transform: translateY(-1px);
        }
        
        .card {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card {
            background-color: white;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        
        .header-bg {
            background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            color: white;
            text-align: center;
        }
        
        div[data-baseweb="input"], div[data-baseweb="select"] {
            font-family: 'Poppins', sans-serif !important;
        }
        
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #94a3b8;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: #f8fafc;
            border-radius: 4px 4px 0px 0px;
            padding: 8px 16px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #dbeafe;
            border-bottom: 2px solid #1e40af;
        }
    </style>
    """

st.markdown(load_css(), unsafe_allow_html=True)

# App header
st.markdown("""
<div class="header-bg">
    <h1 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">Business Transaction Manager</h1>
    <p style="font-size: 1rem; opacity: 0.9; margin-bottom: 0;">Track your daily business transactions</p>
</div>
""", unsafe_allow_html=True)

# Date selector with persistence
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()

col_date = st.columns(1)[0]
with col_date:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #334155; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Select Date</h3>', unsafe_allow_html=True)
    selected_date = st.date_input("Transaction Date", value=st.session_state.selected_date, key="date_input")
    st.session_state.selected_date = selected_date  # Persist the selected date
    st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state for dataframes
if 'purchase_df' not in st.session_state:
    if os.path.exists("purchase_data.csv"):
        st.session_state.purchase_df = pd.read_csv("purchase_data.csv")
    else:
        st.session_state.purchase_df = pd.DataFrame({
            'SL': [1],
            'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Purchase Description': ['']
        })

if 'sales_df' not in st.session_state:
    if os.path.exists("sales_data.csv"):
        st.session_state.sales_df = pd.read_csv("sales_data.csv")
    else:
        st.session_state.sales_df = pd.DataFrame({
            'SL': [1],
            'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
            'Customer Name': ['Starting Balance'],
            'Amount': [0],
            'Sales Description': ['Initial Balance']
        })

if 'expense_df' not in st.session_state:
    if os.path.exists("expense_data.csv"):
        st.session_state.expense_df = pd.read_csv("expense_data.csv")
    else:
        st.session_state.expense_df = pd.DataFrame({
            'SL': [1],
            'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Expense Description': ['']
        })

# Function to ensure valid DataFrame structure
def ensure_valid_dataframe(df, default_structure, name="DataFrame"):
    try:
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        records = df.to_dict('records')
        return pd.DataFrame(records)
    except Exception as e:
        st.warning(f"Error in {name}: {str(e)}")
        return default_structure.copy()

# Function to update date in dataframe
def update_date(df, date_val):
    df_copy = df.copy()
    df_copy['Date'] = date_val.strftime('%Y-%m-%d')
    return df_copy

# Handle form submissions
def submit_purchase():
    st.session_state.purchase_df = ensure_valid_dataframe(
        st.session_state.purchase_editor,
        pd.DataFrame({
            'SL': [1],
            'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Purchase Description': ['']
        }),
        name="Purchase"
    )
    st.session_state.purchase_df = update_date(st.session_state.purchase_df, st.session_state.selected_date)
    st.session_state.purchase_df.to_csv("purchase_data.csv", index=False)

def submit_sales():
    st.session_state.sales_df = ensure_valid_dataframe(
        st.session_state.sales_editor,
        pd.DataFrame({
            'SL': [1],
            'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
            'Customer Name': ['Starting Balance'],
            'Amount': [0],
            'Sales Description': ['Initial Balance']
        }),
        name="Sales"
    )
    st.session_state.sales_df = update_date(st.session_state.sales_df, st.session_state.selected_date)
    st.session_state.sales_df.to_csv("sales_data.csv", index=False)

def submit_expense():
    st.session_state.expense_df = ensure_valid_dataframe(
        st.session_state.expense_editor,
        pd.DataFrame({
            'SL': [1],
            'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Expense Description': ['']
        }),
        name="Expense"
    )
    st.session_state.expense_df = update_date(st.session_state.expense_df, st.session_state.selected_date)
    st.session_state.expense_df.to_csv("expense_data.csv", index=False)

# Simplified PDF creation
def create_pdf(purchase_df, sales_df, expense_df, date_val, purchase_total, sales_total, expense_total, balance):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    # Title
    pdf.cell(190, 10, "Daily Transaction Report", 1, 1, "C")
    pdf.ln(5)
    
    # Date
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 8, f"Date: {date_val.strftime('%Y-%m-%d')}", 0, 1, "L")
    pdf.ln(5)
    
    # Two-column layout
    pdf.set_font("Arial", "B", 10)
    # Left Column (Purchase + Expense)
    pdf.cell(95, 8, "Purchase Transactions", 1, 1, "C")
    pdf.set_font("Arial", "", 8)
    pdf.cell(10, 8, "SL", 1, 0, "C")
    pdf.cell(20, 8, "Customer", 1, 0, "C")
    pdf.cell(25, 8, "Amount", 1, 0, "C")
    pdf.cell(40, 8, "Description", 1, 1, "C")
    for i, row in purchase_df.iterrows():
        pdf.cell(10, 8, str(row['SL']), 1, 0, "C")
        customer = str(row['Customer Name'])[:10] + "..." if len(str(row['Customer Name'])) > 10 else str(row['Customer Name'])
        pdf.cell(20, 8, customer, 1, 0, "L")
        pdf.cell(25, 8, f"Tk {float(row['Amount']):,.0f}", 1, 0, "R")
        desc = str(row['Purchase Description'])[:15] + "..." if len(str(row['Purchase Description'])) > 15 else str(row['Purchase Description'])
        pdf.cell(40, 8, desc, 1, 1, "L")
    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "Expense Transactions", 1, 1, "C")
    pdf.set_font("Arial", "", 8)
    pdf.cell(10, 8, "SL", 1, 0, "C")
    pdf.cell(20, 8, "Customer", 1, 0, "C")
    pdf.cell(25, 8, "Amount", 1, 0, "C")
    pdf.cell(40, 8, "Description", 1, 1, "C")
    for i, row in expense_df.iterrows():
        pdf.cell(10, 8, str(row['SL']), 1, 0, "C")
        customer = str(row['Customer Name'])[:10] + "..." if len(str(row['Customer Name'])) > 10 else str(row['Customer Name'])
        pdf.cell(20, 8, customer, 1, 0, "L")
        pdf.cell(25, 8, f"Tk {float(row['Amount']):,.0f}", 1, 0, "R")
        desc = str(row['Expense Description'])[:15] + "..." if len(str(row['Expense Description'])) > 15 else str(row['Expense Description'])
        pdf.cell(40, 8, desc, 1, 1, "L")
    
    # Right Column (Sales)
    pdf.set_xy(105, 25)  # Move to right column
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "Sales Transactions", 1, 1, "C")
    pdf.set_font("Arial", "", 8)
    pdf.cell(10, 8, "SL", 1, 0, "C")
    pdf.cell(20, 8, "Customer", 1, 0, "C")
    pdf.cell(25, 8, "Amount", 1, 0, "C")
    pdf.cell(40, 8, "Description", 1, 1, "C")
    for i, row in sales_df.iterrows():
        pdf.cell(10, 8, str(row['SL']), 1, 0, "C")
        customer = str(row['Customer Name'])[:10] + "..." if len(str(row['Customer Name'])) > 10 else str(row['Customer Name'])
        pdf.cell(20, 8, customer, 1, 0, "L")
        pdf.cell(25, 8, f"Tk {float(row['Amount']):,.0f}", 1, 0, "R")
        desc = str(row['Sales Description'])[:15] + "..." if len(str(row['Sales Description'])) > 15 else str(row['Sales Description'])
        pdf.cell(40, 8, desc, 1, 1, "L")
    
    # Summary at bottom
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, f"Purchase: Tk {purchase_total:,.0f} | Expense: Tk {expense_total:,.0f} | Sales: Tk {sales_total:,.0f} | Balance: Tk {balance:,.0f}", 1, 1, "C")
    
    return pdf.output(dest='S').encode('latin1')

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Data Entry", "📈 Dashboard", "📋 Export"])

with tab1:
    col1, col2, col3 = st.columns(3)
    
    # Purchase Section
    with col1:
        st.markdown('<div class="card" style="border-left: 4px solid #1e40af;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #1e40af; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">💸 Purchase</h2>', unsafe_allow_html=True)
        clean_purchase_df = ensure_valid_dataframe(
            st.session_state.purchase_df,
            pd.DataFrame({
                'SL': [1],
                'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
                'Customer Name': [''],
                'Amount': [0],
                'Purchase Description': ['']
            }),
            name="Purchase"
        )
        edited_purchase_df = st.data_editor(
            clean_purchase_df,
            num_rows="dynamic",
            key="purchase_editor",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Customer Name": st.column_config.TextColumn("Customer Name", help="Enter customer name")
            }
        )
        if st.button("Save Purchase", key="save_purchase", on_click=submit_purchase):
            st.success("Purchase data saved!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sales Section
    with col2:
        st.markdown('<div class="card" style="border-left: 4px solid #047857;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #047857; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">💰 Sales</h2>', unsafe_allow_html=True)
        clean_sales_df = ensure_valid_dataframe(
            st.session_state.sales_df,
            pd.DataFrame({
                'SL': [1],
                'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
                'Customer Name': ['Starting Balance'],
                'Amount': [0],
                'Sales Description': ['Initial Balance']
            }),
            name="Sales"
        )
        edited_sales_df = st.data_editor(
            clean_sales_df,
            num_rows="dynamic",
            key="sales_editor",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Customer Name": st.column_config.TextColumn("Customer Name", help="Enter customer name")
            }
        )
        if st.button("Save Sales", key="save_sales", on_click=submit_sales):
            st.success("Sales data saved!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Expense Section
    with col3:
        st.markdown('<div class="card" style="border-left: 4px solid #be123c;">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #be123c; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">📉 Expense</h2>', unsafe_allow_html=True)
        clean_expense_df = ensure_valid_dataframe(
            st.session_state.expense_df,
            pd.DataFrame({
                'SL': [1],
                'Date': [st.session_state.selected_date.strftime('%Y-%m-%d')],
                'Customer Name': [''],
                'Amount': [0],
                'Expense Description': ['']
            }),
            name="Expense"
        )
        edited_expense_df = st.data_editor(
            clean_expense_df,
            num_rows="dynamic",
            key="expense_editor",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Customer Name": st.column_config.TextColumn("Customer Name", help="Enter customer name")
            }
        )
        if st.button("Save Expense", key="save_expense", on_click=submit_expense):
            st.success("Expense data saved!")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    clean_purchase_df = ensure_valid_dataframe(st.session_state.purchase_df, st.session_state.purchase_df, "Purchase")
    clean_sales_df = ensure_valid_dataframe(st.session_state.sales_df, st.session_state.sales_df, "Sales")
    clean_expense_df = ensure_valid_dataframe(st.session_state.expense_df, st.session_state.expense_df, "Expense")
    
    clean_purchase_df['Amount'] = pd.to_numeric(clean_purchase_df['Amount'], errors='coerce').fillna(0)
    clean_sales_df['Amount'] = pd.to_numeric(clean_sales_df['Amount'], errors='coerce').fillna(0)
    clean_expense_df['Amount'] = pd.to_numeric(clean_expense_df['Amount'], errors='coerce').fillna(0)
    
    purchase_total = clean_purchase_df['Amount'].sum()
    sales_total = clean_sales_df['Amount'].sum()
    expense_total = clean_expense_df['Amount'].sum()
    balance = sales_total - (purchase_total + expense_total)
    
    # Summary Stats
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1rem;">Business Overview</h2>', unsafe_allow_html=True)
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid #1e40af;">
                <h3 style="color: #1e40af; font-size: 1rem; font-weight: 500;">Purchase</h3>
                <p style="font-size: 1.5rem; font-weight: 700; color: #0f172a;">৳{purchase_total:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid #be123c;">
                <h3 style="color: #be123c; font-size: 1rem; font-weight: 500;">Expense</h3>
                <p style="font-size: 1.5rem; font-weight: 700; color: #0f172a;">৳{expense_total:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_stat3:
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid #047857;">
                <h3 style="color: #047857; font-size: 1rem; font-weight: 500;">Sales</h3>
                <p style="font-size: 1.5rem; font-weight: 700; color: #0f172a;">৳{sales_total:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col_stat4:
        color = "#047857" if balance >= 0 else "#be123c"
        label = "Balance" if balance >= 0 else "Loss"
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid {color};">
                <h3 style="color: {color}; font-size: 1rem; font-weight: 500;">{label}</h3>
                <p style="font-size: 1.5rem; font-weight: 700; color: {color};">৳{abs(balance):,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Bar Chart
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    categories = ['Purchase', 'Expense', 'Sales', 'Balance']
    values = [purchase_total, expense_total, sales_total, balance]
    colors = ['#1e40af', '#be123c', '#047857', '#047857' if balance >= 0 else '#be123c']
    bars = ax.bar(categories, values, color=colors)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'৳{height:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),
                    textcoords="offset points", ha='center', va='bottom', fontweight='bold')
    ax.set_title('Daily Overview', fontsize=14, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1rem;">Export Data</h2>', unsafe_allow_html=True)
    
    col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)
    
    clean_purchase_df = ensure_valid_dataframe(st.session_state.purchase_df, st.session_state.purchase_df, "Purchase")
    clean_sales_df = ensure_valid_dataframe(st.session_state.sales_df, st.session_state.sales_df, "Sales")
    clean_expense_df = ensure_valid_dataframe(st.session_state.expense_df, st.session_state.expense_df, "Expense")
    
    with col_exp1:
        if st.button("Download Purchase CSV", key="download_purchase"):
            csv = clean_purchase_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download",
                data=csv,
                file_name=f"purchase_{st.session_state.selected_date.strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp2:
        if st.button("Download Sales CSV", key="download_sales"):
            csv = clean_sales_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download",
                data=csv,
                file_name=f"sales_{st.session_state.selected_date.strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp3:
        if st.button("Download Expense CSV", key="download_expense"):
            csv = clean_expense_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download",
                data=csv,
                file_name=f"expense_{st.session_state.selected_date.strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp4:
        if st.button("Generate PDF Report", key="generate_pdf"):
            purchase_total = clean_purchase_df['Amount'].sum()
            sales_total = clean_sales_df['Amount'].sum()
            expense_total = clean_expense_df['Amount'].sum()
            balance = sales_total - (purchase_total + expense_total)
            pdf_data = create_pdf(clean_purchase_df, clean_sales_df, clean_expense_df, st.session_state.selected_date,
                                  purchase_total, sales_total, expense_total, balance)
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=f"report_{st.session_state.selected_date.strftime('%Y-%m-%d')}.pdf",
                mime="application/pdf"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 1rem; padding: 1rem; background: linear-gradient(90deg, #1e3a8a, #1e40af); border-radius: 8px; color: white;">
    <p style="margin: 0; font-weight: 500;">© 2025 Business Transaction Manager</p>
</div>
""", unsafe_allow_html=True)

# Requirements
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

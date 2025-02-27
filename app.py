import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import io
import base64
from fpdf import FPDF
import numpy as np
import seaborn as sns

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
    </style>
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
col_date, col_empty1, col_empty2 = st.columns([1, 1, 1])
with col_date:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #334155; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">Select Date for All Entries</h3>', unsafe_allow_html=True)
    selected_date = st.date_input("Transaction Date", date.today())
    st.markdown('</div>', unsafe_allow_html=True)

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
        'Customer Name': [''],
        'Amount': [0],
        'Sales Description': ['']
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

# Handle form submissions - Sales
def submit_sales():
    # Update the session state with clean data
    st.session_state.sales_df = ensure_valid_dataframe(
        st.session_state.sales_editor,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Sales Description': ['']
        }),
        name="Sales"
    )
    # Update all dates
    st.session_state.sales_df = update_date(st.session_state.sales_df, selected_date)

# Create PDF function
def create_pdf(purchase_df, sales_df, date_val, purchase_total, sales_total, profit):
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
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(95, 10, f"Total Purchase: ৳{purchase_total:,.2f}", 1, 0, "L")
    pdf.cell(95, 10, f"Total Sales: ৳{sales_total:,.2f}", 1, 1, "L")
    
    profit_label = "Profit" if profit >= 0 else "Loss"
    pdf.cell(190, 10, f"Total {profit_label}: ৳{abs(profit):,.2f}", 1, 1, "L")
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
    
    # Table content
    pdf.set_font("Arial", "", 10)
    for i, row in purchase_df.iterrows():
        pdf.cell(15, 10, str(row['SL']), 1, 0, "C")
        pdf.cell(35, 10, str(row['Date']), 1, 0, "C")
        pdf.cell(50, 10, str(row['Customer Name']), 1, 0, "L")
        pdf.cell(40, 10, f"৳{row['Amount']:,.2f}" if isinstance(row['Amount'], (int, float)) else str(row['Amount']), 1, 0, "R")
        pdf.cell(50, 10, str(row['Purchase Description']), 1, 1, "L")
    
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
    
    # Table content
    pdf.set_font("Arial", "", 10)
    for i, row in sales_df.iterrows():
        pdf.cell(15, 10, str(row['SL']), 1, 0, "C")
        pdf.cell(35, 10, str(row['Date']), 1, 0, "C")
        pdf.cell(50, 10, str(row['Customer Name']), 1, 0, "L")
        pdf.cell(40, 10, f"৳{row['Amount']:,.2f}" if isinstance(row['Amount'], (int, float)) else str(row['Amount']), 1, 0, "R")
        pdf.cell(50, 10, str(row['Sales Description']), 1, 1, "L")
    
    # Footer
    pdf.ln(20)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "Business Transaction Manager - Generated on " + date.today().strftime("%Y-%m-%d"), 0, 0, "C")
    
    return pdf.output(dest='S').encode('latin1')

# Create two columns for Purchase and Sales data entry
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
                'Customer Name': [''],
                'Amount': [0],
                'Sales Description': ['']
            }),
            name="Sales"
        )
        
        # Display current sales data
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
    
    clean_sales_df = ensure_valid_dataframe(
        st.session_state.sales_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Sales Description': ['']
        }),
        name="Sales"
    )
    
    # Calculate totals
    purchase_total = clean_purchase_df['Amount'].sum() if 'Amount' in clean_purchase_df.columns else 0
    sales_total = clean_sales_df['Amount'].sum() if 'Amount' in clean_sales_df.columns else 0
    profit = sales_total - purchase_total
    
    # Summary Stats
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Business Overview</h2>', unsafe_allow_html=True)
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
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
            <div class="stat-card" style="border-top: 4px solid #047857;">
                <h3 style="color: #047857; font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem;">Total Sales</h3>
                <p style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">৳{sales_total:,.2f}</p>
                <div style="width: 60px; height: 4px; background-color: #a7f3d0; border-radius: 2px; margin-top: 0.5rem;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col_stat3:
        profit_label = "Profit" if profit >= 0 else "Loss"
        border_color = "#047857" if profit >= 0 else "#be123c"
        text_color = "#047857" if profit >= 0 else "#be123c"
        bar_color = "#a7f3d0" if profit >= 0 else "#fecdd3"
        
        st.markdown(
            f"""
            <div class="stat-card" style="border-top: 4px solid {border_color};">
                <h3 style="color: {text_color}; font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem;">{profit_label}</h3>
                <p style="font-size: 2rem; font-weight: 700; color: {text_color}; margin: 0;">৳{abs(profit):,.2f}</p>
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
        categories = ['Purchase', 'Sales']
        values = [purchase_total, sales_total]
        
        bars = ax.bar(categories, values, color=['#1e40af', '#047857'])
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'৳{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
        
        ax.set_title('Purchase vs Sales Comparison', fontsize=16, fontweight='bold')
        ax.set_ylabel('Amount (৳)', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add profit/loss annotation
        profit_text = f'{"Profit" if profit >= 0 else "Loss"}: ৳{abs(profit):,.0f}'
        profit_color = '#047857' if profit >= 0 else '#be123c'
        ax.annotate(profit_text, 
                   xy=(0.5, 0.9), 
                   xycoords='axes fraction',
                   fontsize=12,
                   fontweight='bold',
                   color=profit_color,
                   bbox=dict(boxstyle="round,pad=0.5", fc='#f8fafc', ec=profit_color, alpha=0.8))
        
        st.pyplot(fig)
    
    with col_chart2:
        if purchase_total > 0 or sales_total > 0:
            # Create a custom donut chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Data
            labels = ['Purchase', 'Sales']
            sizes = [purchase_total, sales_total]
            colors = ['#1e40af', '#047857']
            
            # Create a circle for the center
            centre_circle = plt.Circle((0, 0), 0.7, fc='white')
            
            # Create donut plot
            ax.pie(sizes, labels=None, colors=colors,
                   autopct=lambda p: f'৳{p * sum(sizes)/100:,.0f}',
                   startangle=90, pctdistance=0.85,
                   wedgeprops=dict(width=0.3, edgecolor='w'))
            
            # Add the center circle
            fig.gca().add_artist(centre_circle)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Add title
            ax.set_title('Revenue Distribution', fontsize=16, fontweight='bold')
            
            # Add custom legend
            ax.legend(labels, loc="center", bbox_to_anchor=(0.5, 0.5), frameon=False)
            
            st.pyplot(fig)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transactions Table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Recent Transactions</h2>', unsafe_allow_html=True)
    
    # Show both transactions
    if not clean_purchase_df.empty and 'Purchase Description' in clean_purchase_df.columns:
        purchase_display = clean_purchase_df.copy()
        purchase_display['Type'] = 'Purchase'
        purchase_display = purchase_display.rename(columns={'Purchase Description': 'Description'})
    else:
        purchase_display = pd.DataFrame(columns=['SL', 'Date', 'Customer Name', 'Amount', 'Description', 'Type'])
    
    if not clean_sales_df.empty and 'Sales Description' in clean_sales_df.columns:
        sales_display = clean_sales_df.copy()
        sales_display['Type'] = 'Sales'
        sales_display = sales_display.rename(columns={'Sales Description': 'Description'})
    else:
        sales_display = pd.DataFrame(columns=['SL', 'Date', 'Customer Name', 'Amount', 'Description', 'Type'])
    
    # Combine and display all transactions
    combined_df = pd.concat([purchase_display, sales_display])
    combined_df = combined_df[['SL', 'Date', 'Type', 'Customer Name', 'Amount', 'Description']]
    
    if not combined_df.empty:
        st.dataframe(combined_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions recorded yet.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Export Data</h2>', unsafe_allow_html=True)
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
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
    
    clean_sales_df = ensure_valid_dataframe(
        st.session_state.sales_df,
        pd.DataFrame({
            'SL': [1],
            'Date': [date.today().strftime('%Y-%m-%d')],
            'Customer Name': [''],
            'Amount': [0],
            'Sales Description': ['']
        }),
        name="Sales"
    )
    
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
        if st.button("Download Sales Data (CSV)", key="download_sales"):
            csv = clean_sales_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Click to Download Sales CSV",
                data=csv,
                file_name=f"sales_data_{selected_date.strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )
    
    with col_exp3:
        if st.button("Generate Complete Report (PDF)", key="generate_pdf"):
            try:
                # Calculate totals for PDF
                purchase_total = clean_purchase_df['Amount'].sum() if 'Amount' in clean_purchase_df.columns else 0
                sales_total = clean_sales_df['Amount'].sum() if 'Amount' in clean_sales_df.columns else 0
                profit = sales_total - purchase_total
                
                # Generate PDF
                pdf_data = create_pdf(
                    clean_purchase_df, 
                    clean_sales_df,
                    selected_date,
                    purchase_total,
                    sales_total,
                    profit
                )
                
                # Offer download
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"business_report_{selected_date.strftime('%Y-%m-%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error generating PDF: Please make sure you have valid data and try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Preview section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #334155; font-size: 1.5rem; font-weight: 600; text-align: center; margin-bottom: 1.5rem;">Report Preview</h2>', unsafe_allow_html=True)
    
    # Create tabs for different views
    preview_tab1, preview_tab2 = st.tabs(["Purchase Data", "Sales Data"])
    
    with preview_tab1:
        if not clean_purchase_df.empty:
            st.dataframe(clean_purchase_df, use_container_width=True)
        else:
            st.info("No purchase data available.")
    
    with preview_tab2:
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

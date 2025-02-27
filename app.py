import streamlit as st
import pandas as pd
from datetime import date
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(page_title="Sales & Purchase Tracker", layout="wide")

# Apply Tailwind CSS
def load_css():
    return """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .stApp {
            background-color: #f3f4f6;
        }
        .dataframe {
            width: 100%;
            border-collapse: collapse;
        }
        .dataframe th {
            background-color: #1e40af;
            color: white;
            padding: 8px;
            text-align: left;
        }
        .dataframe td {
            padding: 8px;
            border: 1px solid #e5e7eb;
        }
        .dataframe tr:nth-child(even) {
            background-color: #f9fafb;
        }
        .stButton>button {
            background-color: #1e40af;
            color: white;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #1e3a8a;
        }
        .total-box {
            padding: 1rem;
            background-color: #dbeafe;
            border-radius: 0.375rem;
            margin-bottom: 1rem;
        }
    </style>
    """

st.markdown(load_css(), unsafe_allow_html=True)

# App title
st.markdown("<h1 class='text-2xl font-bold text-center text-blue-800 mb-6'>Sales & Purchase Tracker</h1>", unsafe_allow_html=True)

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

# Create two columns for Purchase and Sales
col1, col2 = st.columns(2)

# Purchase Section
with col1:
    st.markdown("<h2 class='text-xl font-semibold text-blue-700'>Purchase Entry</h2>", unsafe_allow_html=True)
    
    # Display current purchase data
    edited_purchase_df = st.data_editor(
        st.session_state.purchase_df,
        num_rows="dynamic",
        key="purchase_editor"
    )
    
    # Update the session state when the dataframe is edited
    st.session_state.purchase_df = edited_purchase_df
    
    # Calculate purchase total
    purchase_total = edited_purchase_df['Amount'].sum()
    
    # Display purchase total
    st.markdown(
        f"""
        <div class='total-box'>
            <h3 class='text-lg font-semibold text-blue-700'>Total Purchase: ৳{purchase_total:,.2f}</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Sales Section
with col2:
    st.markdown("<h2 class='text-xl font-semibold text-green-700'>Sales Entry</h2>", unsafe_allow_html=True)
    
    # Display current sales data
    edited_sales_df = st.data_editor(
        st.session_state.sales_df,
        num_rows="dynamic",
        key="sales_editor"
    )
    
    # Update the session state when the dataframe is edited
    st.session_state.sales_df = edited_sales_df
    
    # Calculate sales total
    sales_total = edited_sales_df['Amount'].sum()
    
    # Display sales total
    st.markdown(
        f"""
        <div class='total-box'>
            <h3 class='text-lg font-semibold text-green-700'>Total Sales: ৳{sales_total:,.2f}</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Summary Section
st.markdown("<h2 class='text-xl font-semibold text-purple-700 mt-8'>Daily Summary</h2>", unsafe_allow_html=True)

# Create two columns for the summary
sum_col1, sum_col2, sum_col3 = st.columns(3)

with sum_col1:
    st.markdown(
        f"""
        <div class='total-box bg-blue-100'>
            <h3 class='text-lg font-semibold text-blue-700'>Total Purchase</h3>
            <p class='text-2xl font-bold text-blue-800'>৳{purchase_total:,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with sum_col2:
    st.markdown(
        f"""
        <div class='total-box bg-green-100'>
            <h3 class='text-lg font-semibold text-green-700'>Total Sales</h3>
            <p class='text-2xl font-bold text-green-800'>৳{sales_total:,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with sum_col3:
    profit = sales_total - purchase_total
    color_class = "text-green-800 bg-green-100" if profit >= 0 else "text-red-800 bg-red-100"
    profit_label = "Profit" if profit >= 0 else "Loss"
    
    st.markdown(
        f"""
        <div class='total-box {color_class}'>
            <h3 class='text-lg font-semibold'>{profit_label}</h3>
            <p class='text-2xl font-bold'>৳{abs(profit):,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Export buttons
st.markdown("<h2 class='text-xl font-semibold text-gray-700 mt-8'>Export Data</h2>", unsafe_allow_html=True)
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    if st.button("Download Purchase Data (CSV)"):
        csv = st.session_state.purchase_df.to_csv(index=False)
        st.download_button(
            label="Click to Download",
            data=csv,
            file_name=f"purchase_data_{date.today().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )

with col_exp2:
    if st.button("Download Sales Data (CSV)"):
        csv = st.session_state.sales_df.to_csv(index=False)
        st.download_button(
            label="Click to Download",
            data=csv,
            file_name=f"sales_data_{date.today().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )

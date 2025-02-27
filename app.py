import streamlit as st
import pandas as pd
from datetime import date
import streamlit.components.v1 as components
import uuid

# Set page configuration
st.set_page_config(page_title="Sales & Purchase Tracker", layout="wide")

# Apply Tailwind CSS and custom styling
def load_css():
    return """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .stApp {
            background-color: #f0f4f8;
        }
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .dataframe th {
            background-color: #2563eb;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-radius: 4px 4px 0 0;
        }
        .dataframe td {
            padding: 10px;
            border: 1px solid #ddd;
        }
        .dataframe tr:nth-child(even) {
            background-color: #f8fafc;
        }
        .dataframe tr:hover {
            background-color: #e0e7ff;
        }
        .stButton>button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
            transform: translateY(-2px);
        }
        .total-box {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s;
        }
        .total-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .main-title {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1.5rem;
            font-size: 2.5rem;
            font-weight: 800;
        }
        .section-title {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 700;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        /* Custom styling for date input */
        .date-input {
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 8px 12px;
            width: 100%;
            margin-bottom: 1rem;
        }
        /* Animated background */
        @keyframes gradient {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .header-bg {
            background: linear-gradient(-45deg, #3b82f6, #60a5fa, #8b5cf6, #a78bfa);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
    </style>
    """

st.markdown(load_css(), unsafe_allow_html=True)

# App header with animated background
st.markdown("""
<div class="header-bg">
    <h1 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">📊 Sales & Purchase Tracker</h1>
    <p style="font-size: 1.25rem; opacity: 0.9;">Track your daily business transactions efficiently</p>
</div>
""", unsafe_allow_html=True)

# Date selector for all entries
col_date, col_empty1, col_empty2 = st.columns([1, 1, 1])
with col_date:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title" style="color: #4b5563;">Select Date for All Entries</h3>', unsafe_allow_html=True)
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

# Function to update date in dataframe
def update_date(df, date_val):
    # Create a copy to avoid SettingWithCopyWarning
    df_copy = df.copy()
    df_copy['Date'] = date_val.strftime('%Y-%m-%d')
    return df_copy

# Handle form submissions - Purchase
def submit_purchase():
    # Update the session state
    st.session_state.purchase_df = st.session_state.purchase_editor
    # Update all dates
    st.session_state.purchase_df = update_date(st.session_state.purchase_df, selected_date)

# Handle form submissions - Sales
def submit_sales():
    # Update the session state
    st.session_state.sales_df = st.session_state.sales_editor
    # Update all dates
    st.session_state.sales_df = update_date(st.session_state.sales_df, selected_date)

# Create two columns for Purchase and Sales
col1, col2 = st.columns(2)

# Purchase Section
with col1:
    st.markdown('<div class="card" style="border-left: 5px solid #3b82f6;">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" style="color: #3b82f6;">📥 Purchase Entry</h2>', unsafe_allow_html=True)
    
    # Display current purchase data
    edited_purchase_df = st.data_editor(
        st.session_state.purchase_df,
        num_rows="dynamic",
        key="purchase_editor",
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("Save Purchase Data", key="save_purchase", on_click=submit_purchase):
        st.success("✅ Purchase data saved successfully!")
    
    # Calculate purchase total
    purchase_total = st.session_state.purchase_df['Amount'].sum()
    
    # Display purchase total
    st.markdown(
        f"""
        <div class='total-box bg-blue-100'>
            <h3 style='color: #3b82f6; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;'>Total Purchase</h3>
            <p style='font-size: 1.75rem; font-weight: 700; color: #1e3a8a;'>৳{purchase_total:,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Sales Section
with col2:
    st.markdown('<div class="card" style="border-left: 5px solid #10b981;">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" style="color: #10b981;">📤 Sales Entry</h2>', unsafe_allow_html=True)
    
    # Display current sales data
    edited_sales_df = st.data_editor(
        st.session_state.sales_df,
        num_rows="dynamic",
        key="sales_editor",
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("Save Sales Data", key="save_sales", on_click=submit_sales):
        st.success("✅ Sales data saved successfully!")
    
    # Calculate sales total
    sales_total = st.session_state.sales_df['Amount'].sum()
    
    # Display sales total
    st.markdown(
        f"""
        <div class='total-box bg-green-100'>
            <h3 style='color: #10b981; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;'>Total Sales</h3>
            <p style='font-size: 1.75rem; font-weight: 700; color: #065f46;'>৳{sales_total:,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Summary Section
st.markdown('<div class="card" style="background: linear-gradient(to right, #f9fafb, #f3f4f6);">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title" style="color: #4f46e5; text-align: center;">📊 Daily Summary</h2>', unsafe_allow_html=True)

# Create three columns for the summary
sum_col1, sum_col2, sum_col3 = st.columns(3)

with sum_col1:
    st.markdown(
        f"""
        <div class='total-box bg-blue-100'>
            <h3 style='color: #3b82f6; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;'>📥 Total Purchase</h3>
            <p style='font-size: 1.75rem; font-weight: 700; color: #1e3a8a;'>৳{purchase_total:,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with sum_col2:
    st.markdown(
        f"""
        <div class='total-box bg-green-100'>
            <h3 style='color: #10b981; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;'>📤 Total Sales</h3>
            <p style='font-size: 1.75rem; font-weight: 700; color: #065f46;'>৳{sales_total:,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with sum_col3:
    profit = sales_total - purchase_total
    color_class = "bg-green-100" if profit >= 0 else "bg-red-100"
    text_color = "color: #065f46;" if profit >= 0 else "color: #7f1d1d;"
    icon = "📈" if profit >= 0 else "📉"
    profit_label = "Profit" if profit >= 0 else "Loss"
    
    st.markdown(
        f"""
        <div class='total-box {color_class}'>
            <h3 style='color: #4f46e5; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;'>{icon} {profit_label}</h3>
            <p style='font-size: 1.75rem; font-weight: 700; {text_color}'>৳{abs(profit):,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# Visual representation of data
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title" style="color: #4f46e5; text-align: center;">📈 Visual Comparison</h2>', unsafe_allow_html=True)

# Simple visual representation
col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    # Create a simple bar chart
    if not st.session_state.purchase_df.empty and not st.session_state.sales_df.empty:
        data = pd.DataFrame({
            'Category': ['Purchase', 'Sales', 'Profit' if profit >= 0 else 'Loss'],
            'Amount': [purchase_total, sales_total, abs(profit)]
        })
        st.bar_chart(data.set_index('Category'))

with col_viz2:
    # Create a simple pie chart to show the proportion
    if purchase_total > 0 or sales_total > 0:
        labels = ["Purchase", "Sales"]
        values = [purchase_total, sales_total]
        
        # Convert to DataFrame for the chart
        pie_data = pd.DataFrame({
            'Category': labels,
            'Value': values
        })
        st.write("Proportion of Purchase vs Sales")
        st.pie_chart(pie_data.set_index('Category'))
st.markdown('</div>', unsafe_allow_html=True)

# Export buttons
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title" style="color: #4f46e5; text-align: center;">📁 Export Data</h2>', unsafe_allow_html=True)
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    if st.button("Download Purchase Data (CSV)", key="download_purchase"):
        csv = st.session_state.purchase_df.to_csv(index=False)
        st.download_button(
            label="Click to Download Purchase Data",
            data=csv,
            file_name=f"purchase_data_{selected_date.strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )

with col_exp2:
    if st.button("Download Sales Data (CSV)", key="download_sales"):
        csv = st.session_state.sales_df.to_csv(index=False)
        st.download_button(
            label="Click to Download Sales Data",
            data=csv,
            file_name=f"sales_data_{selected_date.strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f8fafc; border-radius: 8px;">
    <p style="color: #6b7280; font-size: 0.875rem;">© 2025 Sales & Purchase Tracker | Made with ❤️</p>
</div>
""", unsafe_allow_html=True)

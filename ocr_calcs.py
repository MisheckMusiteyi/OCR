# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Outstanding Claims Reserve (OCR) Calculator", layout="wide")

# ---------- CUSTOM CSS (African Actuarial Consultants theme) ----------
st.markdown("""
<style>
    /* Global */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Calisto MT', serif;
        font-size: 11pt;
    }
    
    /* Apply Calisto MT to all text elements */
    body, p, h1, h2, h3, h4, h5, h6, div, span, label, .stMarkdown, 
    .stTextInput label, .stDateInput label, .stSelectbox label, .stMultiSelect label,
    .stButton button, .stDownloadButton button, .stFileUploader label,
    .stAlert, .stInfo, .stWarning, .stError, .stSuccess, .stSpinner, 
    .stProgress, .stToast, .stSidebar, .stMetric, .stExpander {
        font-family: 'Calisto MT', serif !important;
    }
    
    /* Header / Navigation */
    .header {
        background-color: #000000;
        padding: 1rem 2rem;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        border-bottom: 3px solid #D4AF37;
    }
    .nav-links a {
        color: #FFFFFF;
        margin-left: 2rem;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s;
        font-family: 'Calisto MT', serif;
    }
    .nav-links a:hover {
        color: #D4AF37;
    }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: #FFFFFF;
        padding: 2rem 2rem;
        text-align: center;
        border-bottom: 3px solid #D4AF37;
    }
    .hero h1 {
        color: #D4AF37;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-family: 'Calisto MT', serif;
    }
    .hero p {
        font-size: 1.2rem;
        max-width: 800px;
        margin: 0 auto;
        font-family: 'Calisto MT', serif;
    }
    
    /* Main container */
    .main-container {
        max-width: 1400px;
        margin: 2rem auto;
        padding: 0 2rem;
    }
    
    /* Required Column Containers */
    .required-container {
        background-color: #F9F9F9;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        min-height: 120px;
        height: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        width: 100%;
    }
    .required-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .required-container p {
        color: #666666;
        font-size: 0.85rem;
        margin-bottom: 0;
        line-height: 1.3;
    }
    
    /* Cards */
    .card {
        background-color: #F9F9F9;
        border: 1px solid #D4AF37;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .card h3 {
        color: #D4AF37;
        margin-top: 0;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 0.5rem;
        font-family: 'Calisto MT', serif;
    }
    
    /* Footer */
    .footer {
        background-color: #000000;
        color: #FFFFFF;
        text-align: center;
        padding: 1.5rem;
        border-top: 3px solid #D4AF37;
        margin-top: 3rem;
    }
    .footer a {
        color: #D4AF37;
        text-decoration: none;
        font-family: 'Calisto MT', serif;
    }
    
    /* Streamlit element overrides */
    .stButton > button, .stDownloadButton > button {
        background-color: #D4AF37;
        color: #000000;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
        font-family: 'Calisto MT', serif !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #B8960F;
        color: #FFFFFF;
    }
    
    .stFileUploader {
        border: 2px dashed #D4AF37;
        border-radius: 5px;
        padding: 1rem;
    }
    
    .stMultiSelect [data-baseweb="select"], 
    .stSelectbox [data-baseweb="select"] {
        border: 1px solid #D4AF37;
        border-radius: 4px;
    }
    
    .dataframe {
        border: 1px solid #D4AF37;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Fix for select box container */
    .stSelectbox div[data-baseweb="select"] {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="header">
    <div class="nav-links">
        <a href="#">Home</a>
        <a href="#">Services</a>
        <a href="#">Tools</a>
        <a href="#">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
<div class="hero">
    <h1>Outstanding Claims Reserve (OCR) Calculator</h1>
    <p>Upload your CSV or Excel file. Map your columns to the required fields below. The app groups by Line of Business and sums the selected numeric columns to produce a downloadable Outstanding Claims Reserve report.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Main Container ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Client name input
client_name = st.text_input("Client Name (for file name)", value="Client").strip()

# File uploader (now accepts CSV and Excel)
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Read file based on extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp1252')
                st.info("File read with Windows-1252 encoding.")
        else:
            df = pd.read_excel(uploaded_file)

        # Drop unnamed columns
        unnamed = [c for c in df.columns if c.startswith('Unnamed:')]
        if unnamed:
            df = df.drop(columns=unnamed)
            st.info(f"Dropped {len(unnamed)} unnamed column(s).")

        # Preview
        st.markdown("#### Preview of uploaded data")
        st.dataframe(df.head())
        st.markdown("---")

        # --- Column Mapping Section ---
        st.markdown("### Map Your Columns to Required Fields")
        st.markdown("The calculator requires a 'Line of Business' column. Select the column in your data that identifies the line of business:")

        # Get all column names for selection
        all_columns = df.columns.tolist()
        
        # Create a single container for Line of Business mapping
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class="required-container">
                <h3>Line_of_Business</h3>
                <p>The category/segment for grouping results (e.g., Motor, Property, Health)</p>
            </div>
            """, unsafe_allow_html=True)
            lob_col = st.selectbox(
                "Select your Line of Business column",
                options=[""] + all_columns,
                key="lob",
                label_visibility="collapsed"
            )
            if lob_col == "":
                lob_col = None

        st.markdown("---")

        # Validate Line of Business mapping
        if not lob_col:
            st.error("Please map the Line of Business column.")
            st.stop()

        # Numeric columns selection
        st.markdown("### Select Numeric Columns for OCR Calculation")
        st.markdown("Select which numeric columns (claim amounts, reserves, etc.) you want to sum by Line of Business:")
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove the mapped Line of Business column if it appears in numeric columns
        if lob_col in numeric_columns:
            numeric_columns.remove(lob_col)
        
        if not numeric_columns:
            st.error("No numeric columns found in your data. Please ensure your file contains numeric columns for OCR calculation.")
            st.stop()
        
        selected_value_cols = st.multiselect(
            "Choose the numeric columns you want to sum:",
            options=numeric_columns,
            default=numeric_columns[:min(5, len(numeric_columns))] if numeric_columns else [],
            help="Examples: Claim Amount, Paid Losses, Outstanding Reserves, etc."
        )

        if not selected_value_cols:
            st.warning("Please select at least one numeric column for OCR calculation.")
            st.stop()

        # Show mapping summary button
        if st.button("View Column Mapping Summary", use_container_width=False):
            mapping_data = {
                'Required Field': ['Line_of_Business'],
                'Your Column': [lob_col],
                'Description': ['Category for grouping results']
            }
            mapping_df = pd.DataFrame(mapping_data)
            st.dataframe(mapping_df, use_container_width=True)
            
            if selected_value_cols:
                st.markdown("**Selected numeric columns for OCR calculation:**")
                st.write(selected_value_cols)

        # --- Rename columns for internal processing ---
        df_processed = df.rename(columns={
            lob_col: 'Line_Of_Business'
        })

        # Keep original numeric column names
        original_value_cols = selected_value_cols

        # Group by Line_Of_Business and sum only selected columns
        grouped = df_processed.groupby('Line_Of_Business')[original_value_cols].sum().reset_index()

        # Display results in a card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Outstanding Reserve by Line of Business")
        
        # Format for display (add thousand separators)
        display_result = grouped.copy()
        for col in display_result.columns:
            if col != 'Line_Of_Business':
                display_result[col] = display_result[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
        
        st.dataframe(display_result, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Prepare Excel download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            grouped.to_excel(writer, index=False, sheet_name='OCR_Results')
        output.seek(0)

        # Build filename with client name
        safe_client = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if safe_client:
            file_name = f"{safe_client}_Outstanding_Reserve.xlsx"
        else:
            file_name = "Outstanding_Reserve.xlsx"

        st.download_button(
            label="Download Excel Report",
            data=output,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Please check your file format and column selections.")

st.markdown('</div>', unsafe_allow_html=True)  # close main-container

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved. | <a href="#">Privacy</a> | <a href="#">Terms</a></p>
    <p style="margin-top: 0.5rem; font-size: 0.9rem;">Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)

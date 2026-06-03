# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import re

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
    
    /* Grouping Columns Container */
    .grouping-container {
        background-color: #F9F9F9;
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .grouping-container h3 {
        color: #D4AF37;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
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
    
    /* Data Check Containers */
    .data-check-container {
        background-color: #E3F2FD;
        border: 2px solid #2196F3;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .data-check-warning {
        background-color: #FFF3E0;
        border: 2px solid #FF9800;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .data-check-error {
        background-color: #FFEBEE;
        border: 2px solid #F44336;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
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
    <p>Upload your CSV or Excel file. Select grouping columns and numeric columns. The app calculates outstanding reserves grouped by your selected columns.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Main Container ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Client name input
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name (for file name)", value="Client").strip()
with col2:
    pass

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        original_filename = uploaded_file.name
        base_filename = re.sub(r'\.[^.]*$', '', original_filename)

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

        # Get all column names for selection
        all_columns = df.columns.tolist()
        
        # --- Grouping Columns Selection ---
        st.markdown("""
        <div class="grouping-container">
            <h3>📊 Grouping Columns</h3>
            <p>Select the columns you want to group by (e.g., Line_of_Business, Region, Product Type). Results will be aggregated by these columns.</p>
        </div>
        """, unsafe_allow_html=True)
        
        grouping_cols = st.multiselect(
            "Choose columns to group by (at least one required):",
            options=all_columns,
            default=[all_columns[0]] if all_columns else [],
            help="Select one or more columns. The OCR results will be aggregated by these columns."
        )
        
        if not grouping_cols:
            st.error("Please select at least one grouping column.")
            st.stop()

        st.markdown("---")

        # Numeric columns selection
        st.markdown("### Select Numeric Columns for OCR Calculation")
        st.markdown("Select which numeric columns (claim amounts, reserves, etc.) you want to sum by the selected grouping columns:")
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove grouping columns from numeric selection if they appear
        numeric_columns = [col for col in numeric_columns if col not in grouping_cols]
        
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

        # ============================================================
        # DATA QUALITY CHECKS
        # ============================================================
        st.markdown("### Data Quality Checks")
        
        all_selected_cols = grouping_cols + selected_value_cols
        df_original_len = len(df)
        
        # -----------------------------------------------------------------
        # 1. MISSING VALUES CHECK (CRITICAL - STOPS CALCULATION)
        # -----------------------------------------------------------------
        st.markdown("#### 1. Missing Values Check")
        
        missing_summary = {}
        missing_in_selected = False
        
        for col in all_selected_cols:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                missing_summary[col] = missing_count
                if missing_count > 0:
                    missing_in_selected = True
        
        missing_df = pd.DataFrame(list(missing_summary.items()), columns=['Column', 'Missing Values'])
        st.dataframe(missing_df, use_container_width=True)
        
        if missing_in_selected:
            st.markdown("""
            <div class="data-check-error">
                <b>❌ CRITICAL ERROR: Missing values found in selected columns.</b><br>
                Please fix the missing values in your data and re-upload the file.<br>
                Calculation cannot proceed with missing values.
            </div>
            """, unsafe_allow_html=True)
            
            # Show rows with missing values
            with st.expander("View rows with missing values (first 20)"):
                missing_rows = df[df[all_selected_cols].isna().any(axis=1)]
                st.dataframe(missing_rows.head(20))
            
            st.stop()  # STOP CALCULATION HERE
            
        else:
            st.success("✅ No missing values found in selected columns.")
        
        # -----------------------------------------------------------------
        # 2. DUPLICATE ROWS CHECK (REMOVE AUTOMATICALLY)
        # -----------------------------------------------------------------
        st.markdown("#### 2. Duplicate Rows Check")
        
        duplicate_rows = df[df.duplicated()]
        duplicate_count = len(duplicate_rows)
        
        if duplicate_count > 0:
            df = df.drop_duplicates()
            st.success(f"✅ Removed {duplicate_count} duplicate row(s). {len(df)} rows remaining.")
        else:
            st.success("✅ No duplicate rows found.")
        
        # -----------------------------------------------------------------
        # 3. NON-NUMERIC VALUES CHECK (CONVERT AUTOMATICALLY)
        # -----------------------------------------------------------------
        st.markdown("#### 3. Non-Numeric Values Check")
        
        def clean_numeric(series):
            """Convert problematic numeric strings to numbers"""
            if series.dtype == 'object':
                # Remove currency symbols and commas
                cleaned = series.astype(str).str.replace(r'[$,€£]', '', regex=True)
                cleaned = cleaned.str.replace(r',', '', regex=False)
                # Convert parentheses to negative: (500) -> -500
                cleaned = cleaned.str.replace(r'^\((.+)\)$', r'-\1', regex=True)
                cleaned = cleaned.str.strip()
                cleaned = cleaned.replace('', np.nan)
                return pd.to_numeric(cleaned, errors='coerce')
            else:
                return pd.to_numeric(series, errors='coerce')
        
        conversion_issues = []
        for col in selected_value_cols:
            if col in df.columns:
                test_conversion = clean_numeric(df[col])
                failed_mask = test_conversion.isna() & df[col].notna()
                failed_count = failed_mask.sum()
                if failed_count > 0:
                    problematic_values = df[col][failed_mask].head(3).tolist()
                    conversion_issues.append(f"Column '{col}': {failed_count} non-numeric values (e.g., {problematic_values})")
        
        if conversion_issues:
            st.info("ℹ️ Converting non-numeric values to numbers:")
            for issue in conversion_issues:
                st.write(f"  • {issue}")
            # Perform conversion
            for col in selected_value_cols:
                df[col] = clean_numeric(df[col])
                df[col] = df[col].fillna(0)
            st.success("✅ Non-numeric values converted successfully.")
        else:
            st.success("✅ All selected numeric columns contain valid numbers.")
        
        # -----------------------------------------------------------------
        # SUMMARY
        # -----------------------------------------------------------------
        st.markdown("#### 📋 Data Quality Summary")
        
        rows_removed = df_original_len - len(df)
        if rows_removed > 0 or conversion_issues:
            st.markdown('<div class="data-check-warning">', unsafe_allow_html=True)
            st.markdown("**⚠️ Data adjustments applied:**")
            if rows_removed > 0:
                st.write(f"• Removed {rows_removed} duplicate row(s)")
            if conversion_issues:
                st.write(f"• Converted non-numeric values in {len(conversion_issues)} column(s)")
            st.markdown('</div>')
        else:
            st.markdown('<div class="data-check-container">', unsafe_allow_html=True)
            st.markdown("**✅ All data quality checks passed!**")
            st.markdown('</div>')
        
        st.markdown("---")
        
        # ============================================================
        # PROCESS DATA
        # ============================================================
        
        # Create processed dataframe with only selected columns
        df_processed = df[grouping_cols + selected_value_cols].copy()
        
        # Ensure numeric columns are properly typed
        for col in selected_value_cols:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0)
        
        # Group by selected grouping columns and sum numeric columns
        grouped = df_processed.groupby(grouping_cols)[selected_value_cols].sum().reset_index()
        
        # Display results
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Outstanding Reserve Results")
        st.markdown(f"**Grouped by:** {', '.join(grouping_cols)}")
        
        # Format for display (add thousand separators)
        display_result = grouped.copy()
        for col in selected_value_cols:
            display_result[col] = display_result[col].apply(lambda x: f"{x:,.2f}")
        
        st.dataframe(display_result, use_container_width=True)
        
        # Show row count summary
        st.caption(f"Original rows: {df_original_len} | After cleaning: {len(df_processed)} | Grouped results: {len(grouped)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Prepare Excel download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            grouped.to_excel(writer, index=False, sheet_name='OCR_Results')
        output.seek(0)
        
        # Build filename: ClientName_OriginalFileName_OCR_Results.xlsx
        safe_client = re.sub(r'[\\/*?:"<>|]', "", client_name).strip()
        safe_client = safe_client if safe_client else "Client"
        safe_original = re.sub(r'[\\/*?:"<>|]', "", base_filename).strip()
        safe_original = safe_original if safe_original else "Data"
        
        file_name = f"{safe_client}_{safe_original}_OCR_Results.xlsx"
        
        st.download_button(
            label="Download Excel Report",
            data=output,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Please check your file format and column selections.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("""
<div class="footer">
    <p>© 2026 African Actuarial Consultants. All rights reserved. | <a href="#">Privacy</a> | <a href="#">Terms</a></p>
    <p style="margin-top: 0.5rem; font-size: 0.9rem;">Powered by Vanababa</p>
</div>
""", unsafe_allow_html=True)

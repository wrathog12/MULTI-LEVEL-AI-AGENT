import streamlit as st
from agents.executive_agent import ExecutiveAgent
import time
import os
import logging

# Define supported companies and metrics for dropdowns
SUPPORTED_COMPANIES = [
    "TCS", "Infosys", "Wipro", "Tata Motors", "Mahindra & Mahindra",
    "Maruti Suzuki", "HDFC Bank", "HUL", "Reliance", "Adani Ports"
]

SUPPORTED_METRICS = [
    "PE Ratio", "EPS", "ROE", "Debt-to-Equity", "Dividend Yield", "CAGR"
]

st.set_page_config(page_title="AI Investment Report Generator", layout="wide")
st.title("Multi-Level AI Investment Report Generator")

executive_agent = ExecutiveAgent()

st.markdown("""
**Note:**  
Due to time constraints and the lightweight nature of this app, **NLP parsing has been removed**.  
Please select companies and metrics from the lists below.
""")

with st.form("input_form"):
    st.markdown("### Choose between the following 10 companies:")
    selected_companies = st.multiselect("", SUPPORTED_COMPANIES)
    
    st.markdown("### Choose between the following financial metrics:")
    selected_metrics = st.multiselect("", SUPPORTED_METRICS)

    # Removed the free-text user input area as NLP parsing is disabled
    # user_input = st.text_area(
    #     "Or enter your query about companies or financial metrics (e.g., 'Compare Infosys and Wipro', or 'Tell me PE ratio of TCS'):",
    #     height=120
    # )
    
    submit = st.form_submit_button("Generate Report")

if submit:
    companies_to_use = selected_companies if selected_companies else []
    metrics_to_use = selected_metrics if selected_metrics else []

    if not companies_to_use:
        st.error("Please select at least one valid company.")
    else:
        try:
            with st.spinner("Processing your request..."):
                html_report, pdf_path = executive_agent.generate_report(companies_to_use, metrics_to_use)
                time.sleep(1)  # For spinner effect

            st.markdown("### Report Preview:")
            st.components.v1.html(html_report, height=800, scrolling=True)

            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="Download Report PDF",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )
            else:
                st.warning("PDF generation is unavailable at the moment due to pdf library error.")
        except Exception as e:
            st.error(f"Error generating report: {e}")
            logging.error(f"Report generation failed: {e}")

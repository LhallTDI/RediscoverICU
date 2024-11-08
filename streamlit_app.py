import streamlit as st
import requests
import difflib
from transformers import pipeline  # Import the summarization pipeline

# Define URLs for each script type
SCRIPTS = {
    "Cohort Script": "https://github.com/LhallTDI/RediscoverICU/blob/141fd9ccaf1f5fbbb8e2985f9e16b769c9c6fe40/Baseline%20Scripts/B_SEPSIS_Cohort.sql",
    "Ingredient Script": "https://github.com/LhallTDI/RediscoverICU/blob/141fd9ccaf1f5fbbb8e2985f9e16b769c9c6fe40/Baseline%20Scripts/B_SEPSIS_INGREDIENT_Profile.sql",
    "Unmapped Drugs Script": "https://github.com/LhallTDI/RediscoverICU/blob/141fd9ccaf1f5fbbb8e2985f9e16b769c9c6fe40/Baseline%20Scripts/B_SEPSIS_UNMAPPED_DRUG.sql",
    "Mapped Drug Script": "https://github.com/LhallTDI/RediscoverICU/blob/141fd9ccaf1f5fbbb8e2985f9e16b769c9c6fe40/Baseline%20Scripts/B_SEPSIS_MAPPED_DRUG.sql",
    "Measurements Script": "https://github.com/LhallTDI/RediscoverICU/blob/141fd9ccaf1f5fbbb8e2985f9e16b769c9c6fe40/Baseline%20Scripts/B_SEPSIS_MEASUREMENT.sql",
    "Device Script": "https://github.com/LhallTDI/RediscoverICU/blob/141fd9ccaf1f5fbbb8e2985f9e16b769c9c6fe40/Baseline%20Scripts/B_SEPSIS_DEVICE.sql",
    "Condition Script": "https://github.com/LhallTDI/RediscoverICU/blob/141fd9ccaf1f5fbbb8e2985f9e16b769c9c6fe40/Baseline%20Scripts/B_SEPSIS_CONDITION.sql"
}

# Fetching content from a given URL
def fetch_file_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Error fetching file: {response.status_code}")
        return None

# Comparing two versions of the file
def compare_versions(baseline, updated):
    d = difflib.Differ()
    diff = list(d.compare(baseline.splitlines(), updated.splitlines()))
    return diff

# Initialize Hugging Face summarization pipeline
summarizer = pipeline("summarization", model="t5-small")

# Summarizing changes with Hugging Face, truncated to 512 characters
def summarize_changes(diff):
    diff_text = "\n".join(diff)
    truncated_diff = diff_text[:512]  # Ensure input is within model's acceptable range
    try:
        summary = summarizer(truncated_diff, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error generating summary: {e}"

# Streamlit app title and description
st.title("Script Change Tracker with AI-Powered Summaries")
st.markdown("""
Monitor the changes to the SQL scripts between updates. This tool compares the baseline SQL script with the latest version, highlights differences, and explains them in simple terms with AI support.
""")

# Dropdown menu for selecting script type
script_type = st.selectbox("Select Script Type", list(SCRIPTS.keys()))

# Defining the baseline permalink
BASELINE_URL = SCRIPTS[script_type]
LIVE_URL = BASELINE_URL  # Placeholder for real-time URLs

# Fetching baseline and live versions of the SQL file
baseline_sql = fetch_file_content(BASELINE_URL)
live_sql = fetch_file_content(LIVE_URL)

if baseline_sql and live_sql:
    # Compare the baseline and live versions
    diff = compare_versions(baseline_sql, live_sql)
    
    # Display AI-powered summary at the top
    st.subheader("AI-Powered Summary of Changes")
    st.text_area("Summary", summarize_changes(diff), height=150)

    # Display scripts and differences in a row with three columns
    st.subheader("Scripts Comparison")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Baseline Script**")
        st.code(baseline_sql[:300] + '...', language='sql')  # Show a truncated preview

    with col2:
        st.markdown("**Latest Script**")
        st.code(live_sql[:300] + '...', language='sql')  # Show a truncated preview

    with col3:
        st.markdown("**Changes**")
        st.code("\n".join(diff[:10]) + '...', language='diff')  # Show a truncated diff preview
else:
    st.warning("Failed to load SQL scripts for comparison.")

import streamlit as st
import requests
import difflib
from transformers import pipeline  

SCRIPTS = {
    "Cohort Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Baseline%20Scripts/B_SEPSIS_Cohort.sql",
    "Ingredient Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Baseline%20Scripts/B_SEPSIS_INGREDIENT_Profile.sql",
    "Unmapped Drugs Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Baseline%20Scripts/B_SEPSIS_UNMAPPED_DRUG.sql",
    "Mapped Drug Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Baseline%20Scripts/B_SEPSIS_MAPPED_DRUG.sql",
    "Measurements Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Baseline%20Scripts/B_SEPSIS_MEASUREMENT.sql",
    "Device Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Baseline%20Scripts/B_SEPSIS_DEVICE.sql",
    "Condition Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Baseline%20Scripts/B_SEPSIS_CONDITION.sql"
}

LIVE_SCRIPTS = {
    "Cohort Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Test%20Scripts/T_SEPSIS_Cohort.sql",
    "Ingredient Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Test%20Scripts/T_SEPSIS_INGREDIENT_Profile.sql",
    "Unmapped Drugs Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Test%20Scripts/T_SEPSIS_UNMAPPED_DRUG.sql",
    "Mapped Drug Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Test%20Scripts/T_SEPSIS_MAPPED_DRUG.sql",
    "Measurements Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Test%20Scripts/T_SEPSIS_MEASUREMENT.sql",
    "Device Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Test%20Scripts/T_SEPSIS_DEVICE.sql",
    "Condition Script": "https://raw.githubusercontent.com/LhallTDI/RediscoverICU/refs/heads/main/Test%20Scripts/T_SEPSIS_CONDITION.sql"
}

def fetch_file_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Error fetching file: {response.status_code}")
        return None

def compare_versions(baseline, updated):
    d = difflib.Differ()
    diff = list(d.compare(baseline.splitlines(), updated.splitlines()))
    return diff

#Huggingface
summarizer = pipeline("summarization", model="t5-small")

# Truncating to 512 Char for better performance on summary
def summarize_changes(diff):
    diff_text = "\n".join(diff)
    truncated_diff = diff_text[:512] 
    try:
        summary = summarizer(truncated_diff, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error generating summary: {e}"

st.title("Sepsis Script Synchronizer with AI Summaries")
st.markdown("""
This tool compares the baseline SQL script with the latest version, highlights differences, and explains them in simple terms with AI support.
""")

#Dropdown menu
script_type = st.selectbox("Select Script Type", list(SCRIPTS.keys()))

# Fetching URL for baseline and live
BASELINE_URL = SCRIPTS[script_type]
LIVE_URL = LIVE_SCRIPTS[script_type]

# Fetching baseline and live versions of the SQL file
baseline_sql = fetch_file_content(BASELINE_URL)
live_sql = fetch_file_content(LIVE_URL)

if baseline_sql and live_sql:
    # Compare the baseline and live versions
    diff = compare_versions(baseline_sql, live_sql)
    
    # Displaying AI summary at the top
    st.subheader("AI Summary of Changes")
    st.text_area("Summary", summarize_changes(diff), height=200)

    #Naming Comparison and UI Interface
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
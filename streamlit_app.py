import streamlit as st
import requests
import difflib
from transformers import pipeline  
import urllib.parse

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

# Huggingface Summarizer
summarizer = pipeline("summarization", model="t5-small")

def summarize_changes(diff):
    diff_text = "\n".join(diff)
    truncated_diff = diff_text[:512]
    try:
        summary = summarizer(truncated_diff, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error generating summary: {e}"

def generate_mailto_link(recipient, subject, body):
    mailto_link = f"mailto:{recipient}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    return mailto_link

# Streamlit App
st.title("Sepsis Script Synchronizer with AI Summaries")

script_type = st.selectbox("Select Script Type", list(SCRIPTS.keys()))

# Fetch URLs for baseline and live scripts
BASELINE_URL = SCRIPTS[script_type]
LIVE_URL = LIVE_SCRIPTS[script_type]

baseline_sql = fetch_file_content(BASELINE_URL)
live_sql = fetch_file_content(LIVE_URL)

if baseline_sql and live_sql:
    diff = compare_versions(baseline_sql, live_sql)
    summary = summarize_changes(diff)
    diff_text = "\n".join(diff)

    st.subheader("AI Summary of Changes")
    st.text_area("Summary", summary, height=150, key="summary_text")

    st.subheader("Scripts Comparison")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Baseline Script**")
        st.code(baseline_sql[:300] + '...', language='sql')

    with col2:
        st.markdown("**Latest Script**")
        st.code(live_sql[:300] + '...', language='sql')

    with col3:
        st.markdown("**Changes**")
        st.code("\n".join(diff[:10]) + '...', language='diff')

    # Generate Mailto Link
    recipient_email = "luke.c.hall.gr@dartmouth.edu"
    subject = "Sepsis Script Changes and Summary"
    body = f"""
    Here are the latest changes to the SQL script:

    Summary of Changes:
    {summary}

    Detailed Changes:
    {diff_text}
    """

    mailto_link = generate_mailto_link(recipient_email, subject, body)
    st.markdown(f'[📧 Send Changes via Email]({mailto_link})', unsafe_allow_html=True)
else:
    st.warning("Failed to load SQL scripts for comparison.")

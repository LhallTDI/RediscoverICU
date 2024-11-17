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

# Truncating to 512 characters and summary
def summarize_changes(diff):
    diff_text = "\n".join(diff)
    truncated_diff = diff_text[:512]  # Ensure input is within model's acceptable range
    try:
        summary = summarizer(truncated_diff, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error generating summary: {e}"

st.title("Sepsis Script Synchronizer with AI-Powered Summaries")
st.markdown("""
This tool compares the baseline SQL script with the latest version, highlights differences, and explains them in simple terms with AI support.
""")

#Dropdown menu
script_type = st.selectbox("Select Script Type", list(SCRIPTS.keys()))

# Fetching URLs for baseline and live
BASELINE_URL = SCRIPTS[script_type]
LIVE_URL = LIVE_SCRIPTS[script_type]

# Fetching baseline and live versions of the SQL file
baseline_sql = fetch_file_content(BASELINE_URL)
live_sql = fetch_file_content(LIVE_URL)

if baseline_sql and live_sql:
    # Compare the baseline and live versions
    diff = compare_versions(baseline_sql, live_sql)
    
    # Display AI-powered summary at the top
    st.subheader("AI Summary of Changes")
    st.text_area("Summary", summarize_changes(diff), height=150)

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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(summary, diff_text):
    recipient_email = "luke.c.hall.gr@dartmouth.edu"
    subject = "Sepsis Script Changes and Summary"
    
    # Create the email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Add the lay summary and script changes to the email
    body = f"""
    Here are the latest changes to the SQL script:

    **Summary of Changes**:
    {summary}

    **Detailed Changes**:
    {diff_text}
    """
    message.attach(MIMEText(body, "plain"))
    
    # Sending the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        st.success("Email sent successfully to luke.c.hall.gr@dartmouth.edu!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Button for email with the changes and summary
if st.button("Send Changes to My Email"):
    if baseline_sql and live_sql:
        diff_text = "\n".join(compare_versions(baseline_sql, live_sql))
        summary = summarize_changes(compare_versions(baseline_sql, live_sql))
        send_email(summary, diff_text)
    else:
        st.warning("Unable to send email. Please ensure scripts are loaded successfully.")


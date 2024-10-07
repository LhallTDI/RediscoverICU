import streamlit as st
import requests
import difflib

# Define the baseline permalink
BASELINE_URL = "https://raw.githubusercontent.com/OHDSI/CureIdRegistry/ffa799b9eb1460080c110ea6cf3cac8efb68d25a/Cohort%20curation%20scripts/SEPSIS/01A_SEPSIS_Cohort_V4.sql"

# Define the most recent file from the main branch (live file)
LIVE_URL = "https://raw.githubusercontent.com/OHDSI/CureIdRegistry/main/Cohort%20curation%20scripts/SEPSIS/01A_SEPSIS_Cohort_V4.sql"

# Fetch content from a given URL
def fetch_file_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Error fetching file: {response.status_code}")
        return None

# Compare two versions of the file
def compare_versions(baseline, updated):
    d = difflib.Differ()
    diff = list(d.compare(baseline.splitlines(), updated.splitlines()))
    return diff

# Explain changes in simple terms
def explain_changes(diff):
    added = [line[2:] for line in diff if line.startswith("+ ")]
    removed = [line[2:] for line in diff if line.startswith("- ")]

    explanation = ""
    if added:
        explanation += "New lines added:\n" + "\n".join(added) + "\n\n"
    if removed:
        explanation += "Lines removed:\n" + "\n".join(removed)
    return explanation if explanation else "No significant changes."

# Streamlit GUI
st.title("SEPSIS Cohort Script Change Tracker")
st.markdown("""
Monitor the changes to the SEPSIS cohort curation script between townhall updates. This tool compares the baseline SQL script with the latest version, highlighting key differences and explaining them in simple terms.
""")

# Fetch baseline and live versions of the SQL file
baseline_sql = fetch_file_content(BASELINE_URL)
live_sql = fetch_file_content(LIVE_URL)

# Display the baseline and live content for reference
if baseline_sql and live_sql:
    st.subheader("Baseline Version (Permalink)")
    st.code(baseline_sql, language='sql')
    
    st.subheader("Latest Version")
    st.code(live_sql, language='sql')

    # Compare the baseline and live versions
    diff = compare_versions(baseline_sql, live_sql)
    
    # Display differences
    st.subheader("Changes Detected")
    st.code("\n".join(diff), language='diff')

    # Display explanation in layman's terms
    st.subheader("Explanation of Changes (Layman's Terms)")
    st.text_area("Layman's Explanation", explain_changes(diff), height=200)

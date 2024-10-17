import streamlit as st
import requests
import difflib

# Define URLs for each script type
SCRIPTS = {
    "Cohort Script": "https://raw.githubusercontent.com/OHDSI/CureIdRegistry/main/Cohort%20curation%20scripts/SEPSIS/01A_SEPSIS_Cohort_V4.sql",
    "Ingredient Script": "https://example.com/ingredient_script.sql",
    "Unmapped Drugs Script": "https://example.com/unmapped_drugs_script.sql",
    "Mapped Drug Script": "https://example.com/mapped_drug_script.sql",
    "Measurements Script": "https://example.com/measurements_script.sql",
    "Device Script": "https://example.com/device_script.sql",
    "Condition Script": "https://example.com/condition_script.sql"
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

# Explaining changes in simple terms
def explain_changes(diff):
    added = [line[2:] for line in diff if line.startswith("+ ")]
    removed = [line[2:] for line in diff if line.startswith("- ")]

    explanation = ""
    if added:
        explanation += "New lines added:\n" + "\n".join(added) + "\n\n"
    if removed:
        explanation += "Lines removed:\n" + "\n".join(removed)
    return explanation if explanation else "No significant changes."

# Streamlit app title and description
st.title("Script Change Tracker")
st.markdown("""
Monitor the changes to the SQL scripts between updates. This tool compares the baseline SQL script with the latest version, highlighting key differences and explaining them in simple terms.
""")

# Dropdown menu for selecting script type
script_type = st.selectbox("Select Script Type", list(SCRIPTS.keys()))

# Defining the baseline permalink (hardcoded for demonstration, can be adapted)
BASELINE_URL = SCRIPTS[script_type]
LIVE_URL = BASELINE_URL  # Placeholder for live URL; can be adapted for real-time live URLs

# Fetching baseline and live versions of the SQL file
baseline_sql = fetch_file_content(BASELINE_URL)
live_sql = fetch_file_content(LIVE_URL)

# Displaying the baseline and live content for reference
if baseline_sql and live_sql:
    st.subheader(f"Baseline Version - {script_type}")
    st.code(baseline_sql, language='sql')
    
    st.subheader(f"Latest Version - {script_type}")
    st.code(live_sql, language='sql')

    # Compare the baseline and live versions
    diff = compare_versions(baseline_sql, live_sql)
    
    # Display differences
    st.subheader("Changes Detected")
    st.code("\n".join(diff), language='diff')

    # Display explanation in layman's terms
    st.subheader("Explanation of Changes (Layman's Terms)")
    st.text_area("Layman's Explanation", explain_changes(diff), height=200)

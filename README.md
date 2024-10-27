# Sespsis Script Synchronizer
This is a web-based tool designed to monitor changes to SQL scripts used in the Rediscover-ICU study, particularly focused on SEPSIS cohort curation. It fetches and compares the latest SQL script from GitHub and highlights the differences between the baseline version and the live version, explaining the changes in simple terms.

## Features
- Automatically fetches the SEPSIS cohort curation SQL script from GitHub.
- Compares the baseline (permalink) with the most recent version in the main branch.
- Highlights added, removed, or changed lines.
- Provides a layman-friendly explanation of changes.
- Ideal for technical and non-technical users involved in the Rediscover-ICU project.

## How to Access the Live Application

You can access the live SEPSIS Cohort Script Change Tracker application by clicking the link below:

[**Open the SEPSIS Cohort Script Change Tracker**](https://rediscover.streamlit.app/)

This will open the app directly in your browser.

## Running it on your own machine

If you prefer to run the app locally on your machine, follow these steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/LhallTDI/RediscoverICU.git
   cd RediscoverICU

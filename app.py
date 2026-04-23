import streamlit as st
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Job Search Pro", layout="wide")

# --- HEADER SECTION ---
st.title("🚀 Professional Job Search Tool")
st.subheader("by Gauravkumar Patel")
st.markdown("Search LinkedIn, Indeed, Google, Glassdoor, and ZipRecruiter in one click.")
st.divider()

# --- MAIN INPUT SECTION (Moved from Sidebar to Here) ---
st.header("🔍 Search Filters")

# Row 1: Keywords and City
col1, col2 = st.columns(2)
with col1:
    keywords = st.text_input("Keywords", value='CyberArk', help='Example: "CyberArk" OR "IAM"')
with col2:
    city = st.text_input("City (Optional)", placeholder="e.g. Riyadh")

# Row 2: Country and Company
col3, col4 = st.columns(2)
with col3:
    country = st.text_input("Country (Mandatory)", value="saudi arabia")
with col4:
    companies = st.text_input("Company Filter (Optional)", placeholder="e.g. Deloitte OR Google")

# Row 3: Slider and Button
results_count = st.slider("Results per site", 10, 100, 50)
search_button = st.button("Search Jobs", type="primary", use_container_width=True)

st.divider()

# --- SEARCH LOGIC ---
if search_button:
    all_jobs = [] 
    sites = ["linkedin", "indeed", "google", "glassdoor", "zip_recruiter"]
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, site in enumerate(sites):
        status_text.text(f"Searching {site}...")
        try:
            res = scrape_jobs(
                site_name=[site],
                search_term=keywords,
                location=city if city else country,
                country_indeed=country.lower().strip(),
                results_wanted=results_count,
            )
            if not res.empty:
                all_jobs.append(res)
        except Exception as e:
            # Displays a small notification if a board is unavailable
            st.info(f"Note: {site} skipped for this location.")
        
        progress_bar.progress((index + 1) / len(sites))

    status_text.text("Finishing up...")

    if all_jobs:
        jobs = pd.concat(all_jobs, ignore_index=True)

        if companies.strip():
            target_list = [c.strip() for c in companies.upper().split('OR')]
            jobs = jobs[jobs['company'].str.upper().str.contains('|'.join(target_list), na=False)]

        if not jobs.empty:
            st.success(f"✅ Found {len(jobs)} total jobs!")
            
            # Interactive Table
            display_df = jobs[['site', 'title', 'company', 'location', 'date_posted', 'job_url']]
            st.dataframe(
                display_df, 
                column_config={"job_url": st.column_config.LinkColumn("Apply Link")},
                use_container_width=True,
                hide_index=True
            )
            
            # Download Section
            csv = jobs.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results (CSV)", data=csv, file_name="jobs.csv", mime="text/csv")
        else:
            st.warning("No jobs matched your company filter.")
    else:
        st.error("No jobs found on any compatible boards.")

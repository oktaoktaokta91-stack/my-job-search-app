import streamlit as st
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Job Search Pro", layout="wide")

st.title("🚀 Professional Job Search Tool")
st.subheader("by Gauravkumar Patel")
st.markdown("Search LinkedIn, Indeed, Google, Glassdoor, and ZipRecruiter in one click.")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Search Filters")
    keywords = st.text_input("Keywords", value='CyberArk')
    city = st.text_input("City (Optional)", placeholder="e.g. Riyadh")
    country = st.text_input("Country (Mandatory)", value="saudi arabia")
    companies = st.text_input("Company Filter (Optional)", placeholder="e.g. Deloitte OR Google")
    results_count = st.slider("Results per site", 10, 100, 50)
    
    search_button = st.button("Search Jobs", type="primary")

# --- SEARCH LOGIC ---
if search_button:
    all_jobs = [] # List to hold results from each board
    sites = ["linkedin", "indeed", "google", "glassdoor", "zip_recruiter"]
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Loop through each site one by one
    for index, site in enumerate(sites):
        status_text.text(f"Searching {site}...")
        try:
            # Scrape a single site
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
            # If one site fails (like Glassdoor in SA), it just shows a small warning and continues
            st.sidebar.warning(f"Skipped {site}: Not available for this location.")
        
        progress_bar.progress((index + 1) / len(sites))

    status_text.text("Finishing up...")

    if all_jobs:
        # Combine all successful results into one table
        jobs = pd.concat(all_jobs, ignore_index=True)

        # Apply Company Filter
        if companies.strip():
            target_list = [c.strip() for c in companies.upper().split('OR')]
            jobs = jobs[jobs['company'].str.upper().str.contains('|'.join(target_list), na=False)]

        if not jobs.empty:
            st.success(f"Found {len(jobs)} total jobs!")
            display_df = jobs[['site', 'title', 'company', 'location', 'date_posted', 'job_url']]
            st.dataframe(
                display_df, 
                column_config={"job_url": st.column_config.LinkColumn("Apply Link")},
                use_container_width=True,
                hide_index=True
            )
            csv = jobs.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="jobs.csv", mime="text/csv")
        else:
            st.warning("No jobs matched your company filter.")
    else:
        st.error("No jobs found on any compatible boards.")

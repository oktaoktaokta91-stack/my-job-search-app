import streamlit as st
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Job Search Pro", layout="wide")

# --- 1. TITLE WITH YOUR NAME ---
st.title("🚀 Professional Job Search Tool")
st.subheader("by Gauravkumar Patel")
st.markdown("Search LinkedIn, Indeed, Google, Glassdoor, and ZipRecruiter in one click.")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Search Filters")
    keywords = st.text_input("Keywords", value='"CyberArk" OR "IAM"')
    city = st.text_input("City (Optional)", placeholder="e.g. Riyadh")
    country = st.text_input("Country (Mandatory)", value="saudi arabia")
    companies = st.text_input("Company Filter (Optional)", placeholder="e.g. Deloitte OR Google")
    results_count = st.slider("Results per site", 10, 100, 50)
    
    search_button = st.button("Search Jobs", type="primary")

# --- SEARCH LOGIC ---
if search_button:
    with st.spinner("Searching multiple job boards... please wait."):
        try:
            # --- 2. ADDED MORE BOARDS ---
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "google", "glassdoor", "zip_recruiter"],
                search_term=keywords,
                location=city if city else country,
                country_indeed=country.lower().strip(),
                results_wanted=results_count,
            )
            
            if not jobs.empty:
                if companies.strip():
                    target_list = [c.strip() for c in companies.upper().split('OR')]
                    jobs = jobs[jobs['company'].str.upper().str.contains('|'.join(target_list), na=False)]

                if not jobs.empty:
                    st.success(f"Found {len(jobs)} jobs!")
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
                st.error("No jobs found. Try broader keywords.")
        except Exception as e:
            st.error(f"Error: {e}")

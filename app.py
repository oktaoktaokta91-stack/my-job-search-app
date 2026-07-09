import streamlit as st
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Job Search Pro", layout="wide")

# --- HEADER SECTION ---
st.title("🚀 Job Search Tool")
st.subheader("by Gauravkumar Patel")
st.markdown("Search LinkedIn, Indeed, Google, Glassdoor, and ZipRecruiter in one click.")
st.divider()

# --- MAIN INPUT SECTION ---
st.header("🔍 Search Filters")

# Row 1: Keywords and City
col1, col2 = st.columns(2)
with col1:
    keywords = st.text_input("Keywords", value="", placeholder='e.g. "CyberArk" OR "IAM"')
with col2:
    city = st.text_input("City (Optional)", value="", placeholder="e.g. Riyadh")

# Row 2: Country and Company
col3, col4 = st.columns(2)
with col3:
    country = st.text_input("Country (Mandatory)", value="", placeholder="e.g. saudi arabia")
with col4:
    companies = st.text_input("Company Filter (Optional)", value="", placeholder="e.g. Deloitte OR Google")

# Row 3: Slider and Button
results_count = st.slider("Results per site", 10, 100, 50)
search_button = st.button("Search Jobs", type="primary", use_container_width=True)

st.divider()

# --- SEARCH LOGIC ---
if search_button:
    if not country:
        st.error("Please enter a Country to begin the search.")
    else:
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
                st.info(f"Note: {site} was skipped (likely not supported for this location).")
            
            progress_bar.progress((index + 1) / len(sites))

        status_text.text("Finishing up...")

        if all_jobs:
            jobs_df = pd.concat(all_jobs, ignore_index=True)

            if companies.strip():
                target_list = [c.strip() for c in companies.upper().split('OR')]
                jobs_df = jobs_df[jobs_df['company'].str.upper().str.contains('|'.join(target_list), na=False)]

            # Save data securely to Streamlit session state so interactive widgets don't clear the data
            st.session_state['raw_jobs'] = jobs_df
            st.success(f"✅ Successfully loaded {len(jobs_df)} total jobs!")
        else:
            st.error("No jobs found on any compatible boards for these keywords.")

# --- INTERACTIVE DASHBOARD AND FILTER SECTION ---
if 'raw_jobs' in st.session_state and not st.session_state['raw_jobs'].empty:
    df = st.session_state['raw_jobs'].copy()
    
    st.header("📊 Job Market Insights & Interactive View")
    
    # NEW FEATURE PART 1: High-Level Analytics Metrics
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Total Unique Openings", len(df))
    m_col2.metric("Top Platform", df['site'].value_counts().idxmax().title() if 'site' in df.columns else "N/A")
    m_col3.metric("Top Hiring Company", df['company'].value_counts().idxmax() if 'company' in df.columns else "N/A")
    
    # NEW FEATURE PART 2: Visual Charts Dashboard
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("📌 Distribution by Platform")
        site_counts = df['site'].value_counts()
        st.bar_chart(site_counts, horizontal=True)
        
    with chart_col2:
        st.subheader("🏢 Top 10 Hiring Companies")
        company_counts = df['company'].value_counts().head(10)
        st.bar_chart(company_counts)

    st.subheader("🎯 Refine View Dynamically")
    
    # NEW FEATURE PART 3: Post-Search Interactive Filtering
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        # Filter data dynamically by specific platform selection
        available_sites = df['site'].unique().tolist()
        selected_sites = st.multiselect("Filter by Platforms", options=available_sites, default=available_sites)
    with f_col2:
        # Search directly inside title text without reloading scraping logic
        title_query = st.text_input("Filter Titles by Word", value="", placeholder="e.g. Senior, Engineer, Lead")

    # Apply interactive changes to the data
    filtered_df = df[df['site'].isin(selected_sites)]
    if title_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(title_query, case=False, na=False)]

    st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** jobs matching your dashboard filter conditions:")

    # Interactive Table with clickable links
    display_df = filtered_df[['site', 'title', 'company', 'location', 'date_posted', 'job_url']]
    st.dataframe(
        display_df, 
        column_config={"job_url": st.column_config.LinkColumn("Apply Link")},
        use_container_width=True,
        hide_index=True
    )
    
    # Dynamic Download Button matching filtered states
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Filtered Results (CSV)", data=csv, file_name="filtered_job_results.csv", mime="text/csv")

# Footer info
st.markdown("---")
st.caption("Tip: Use double quotes for phrases in keywords (e.g. \"Cyber Security\").")

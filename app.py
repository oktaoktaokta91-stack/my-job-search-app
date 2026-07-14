import streamlit as st
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime

# Page configuration
st.set_page_config(page_title="JobHunter Pro", layout="wide", initial_sidebar_state="expanded")

# --- HEADER ---
col_t1, col_t2 = st.columns([1, 8])
with col_t1:
    st.title("🚀")
with col_t2:
    st.title("Professionl Job Search Tool")
    st.caption("Developed by Gauravkumar | Version 2.1")

st.divider()

# --- INPUT SECTION ---
st.subheader("🔍 Search Filters")
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        keywords = st.text_input("🎯 Keywords", placeholder='e.g. "CyberArk" OR "IAM"')
    with c2:
        city = st.text_input("📍 City (Optional)", placeholder="e.g. Riyadh")
    with c3:
        country = st.text_input("🌍 Country (Mandatory)", placeholder="e.g. saudi arabia")

    with st.expander("⚙️ Advanced Filters (Company, Results Count)"):
        ca, cb = st.columns(2)
        with ca:
            companies = st.text_input("🏢 Company Filter", placeholder="e.g. Deloitte OR Google")
        with cb:
            results_count = st.slider("Max results per site", 10, 100, 30)

    search_button = st.button("🔍 START GLOBAL SEARCH", type="primary")

st.divider()

# --- SEARCH LOGIC ---
if search_button:
    if not country:
        st.error("⚠️ Please specify a country to begin.")
    else:
        all_jobs = []
        sites = ["linkedin", "indeed", "google", "glassdoor"]
        
        status = st.status("🚀 Initializing engines...", expanded=True)
        for site in sites:
            status.write(f"Searching {site}...")
            try:
                res = scrape_jobs(
                    site_name=[site], 
                    search_term=keywords, 
                    location=city if city else country,
                    country_indeed=country.lower().strip(), 
                    results_wanted=results_count
                )
                if not res.empty: 
                    all_jobs.append(res)
            except:
                status.write(f"⚠️ {site} skipped (not available).")
        
        if all_jobs:
            jobs = pd.concat(all_jobs, ignore_index=True)
            
            # Apply Company Filter
            if companies:
                targets = [c.strip().upper() for c in companies.split('OR')]
                jobs = jobs[jobs['company'].str.upper().str.contains('|'.join(targets), na=False)]
            
            status.update(label="✅ Search Complete!", state="complete", expanded=False)

            # --- UI IMPROVEMENTS: METRICS & TABS ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Matches", len(jobs))
            m2.metric("Sites Scanned", len(all_jobs))
            m3.metric("Location", country.title())

            tab1, tab2 = st.tabs(["📋 Job Listings", "📈 Market Analysis"])
            
            with tab1:
                # Display table with clickable links
                st.dataframe(
                    jobs[['site', 'title', 'company', 'location', 'date_posted', 'job_url']], 
                    column_config={"job_url": st.column_config.LinkColumn("Apply Link")},
                    use_container_width=True, 
                    hide_index=True
                )
                
                # Download Button
                csv = jobs.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Excel-Ready Report", data=csv, file_name=f"Jobs_{datetime.now().strftime('%Y%m%d')}.csv")

            with tab2:
                st.subheader("Top Hiring Companies")
                if not jobs.empty:
                    # Create a bar chart of company counts
                    company_counts = jobs['company'].value_counts().head(10)
                    st.bar_chart(company_counts)
                else:
                    st.write("No data available for analysis.")
        else:
            status.update(label="❌ No Results Found", state="error")

# --- FOOTER ---
st.markdown("---")
st.info("💡 **Pro Tip:** Use double quotes for exact phrases like \"Identity Management\". Use **OR** for multiple companies.")

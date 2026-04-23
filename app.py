import pandas as pd
from jobspy import scrape_jobs
import datetime
import os
import sys

# Setup terminal
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)

def run_search():
    print("====================================================")
    print("            PROFESSIONAL JOB SEARCH TOOL")
    print("====================================================\n")

    # Inputs
    print("--- STEP 1: KEYWORDS ---")
    keywords = input("Example: \"CyberArk\" OR \"IAM\"\nYour keywords: ")
    
    print("\n--- STEP 2: CITY/LOCATION ---")
    location = input("Example: Riyadh (or leave blank for whole country)\nYour location: ")
    
    print("\n--- STEP 3: COUNTRY (MANDATORY for Indeed) ---")
    print("Must match list: saudi arabia, india, malaysia, united arab emirates, etc.")
    country_input = input("Your country: ").strip().lower()

    print("\n--- STEP 4: COMPANY (OPTIONAL) ---")
    company_input = input("Example: Deloitte OR Google\nYour company choice: ").strip()

    print(f"\n[INFO] Searching LinkedIn, Indeed, and Google... Please wait.\n")

    try:
        # Fixed: location uses the city, country_indeed uses the full country string
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "google"],
            search_term=keywords,
            location=location if location else country_input,
            results_wanted=50,
            country_indeed=country_input 
        )

        # Company Filter
        if not jobs.empty and company_input:
            companies = [c.strip() for c in company_input.upper().split('OR')]
            jobs = jobs[jobs['company'].str.upper().str.contains('|'.join(companies), na=False)]

        # Results
        if not jobs.empty:
            print(f"--- FOUND {len(jobs)} JOBS ---")
            output = jobs[['site', 'title', 'company', 'location', 'date_posted']]
            print(output.to_string(index=False))
            
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
            filename = f"job_results_{timestamp}.csv"
            jobs.to_csv(filename, index=False)
            
            print(f"\n[SUCCESS] Full list with links saved to: {filename}")
        else:
            print("\n[NOTICE] No jobs found. Try broader keywords.")

    except Exception as e:
        print(f"\n[ERROR] Something went wrong: {e}")

    print("\n" + "="*52)
    input("SEARCH COMPLETE. Press ENTER to close this window...")

if __name__ == "__main__":
    run_search()

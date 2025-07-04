import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as soup
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
TARGET_BASE_URL = "https://www.glassdoor.co.in/Job/india-veteran-logistics-jobs-SRCH_IL.0,5_IN115_KO6,23.htm"
JOBS_CSV_PATH = "data/jobs.csv"

# --- Helper function to request page using Scrapingdog ---
def get_page_with_scrapingdog(url, api_key):
    payload = {'api_key': api_key, 'url': url}
    try:
        response = requests.get('https://api.scrapingdog.com/scrape', params=payload, timeout=60)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url} with Scrapingdog: {e}")
        return None

# --- Helper function to parse "posted x days ago" text ---
def parse_posted_date(text):
    today = datetime.today()
    text = text.lower()
    if "today" in text or "just posted" in text:
        return today
    elif "1 day ago" in text:
        return today - timedelta(days=1)
    elif "30+" in text or "30d+" in text:
        return today - timedelta(days=30)
    else:
        try:
            num_days = int(''.join(filter(str.isdigit, text)))
            return today - timedelta(days=num_days)
        except:
            return None

# --- Helper: Calculate Last Date to Apply as Post Date + 30 days ---
def compute_last_date_and_expiry(post_date):
    if not post_date:
        return None, None
    last_date = post_date + timedelta(days=30)
    if datetime.today().date() > last_date.date():
        status = "Expired"
    else:
        status = "Currently Open"
    return last_date.strftime('%Y-%m-%d'), status

# --- Main job scraping logic ---
def scrape_jobs():
    html_content = get_page_with_scrapingdog(TARGET_BASE_URL, SCRAPINGDOG_API_KEY)
    if not html_content:
        return pd.DataFrame()

    bsobj = soup(html_content, 'lxml')
    job_cards = bsobj.find_all('li', class_='JobsList_jobListItem__wjTHv')

    jobs = []

    for card in job_cards:
        title_tag = card.find('a', class_='JobCard_jobTitle__GLyJ1')
        job_title = title_tag.text.strip() if title_tag else None
        job_link = title_tag['href'] if title_tag and title_tag.has_attr('href') else None
        company = card.find('div', class_='EmployerProfile_profileContainer__63w3R')
        location = card.find('div', class_='JobCard_location__Ds1fM')
        salary = card.find('div', class_='JobCard_salaryEstimate__QpbTW')
        posted_text_tag = card.find('div', {'data-test': 'job-age'})
        posted_text = posted_text_tag.text.strip() if posted_text_tag else None
        post_date = parse_posted_date(posted_text) if posted_text else None
        job_age = (datetime.today() - post_date).days if post_date else None

        job_data = {
            "Job Title": job_title,
            "Job Link": job_link,
            "Company Name": company.text.strip() if company else None,
            "Location": location.text.strip() if location else None,
            "Salary": salary.text.strip() if salary else None,
            "Posted Text": posted_text,
            "Post Date": post_date.strftime('%Y-%m-%d') if post_date else None,
            "Job Age": job_age,
            "Job Description": "No description.",
            "Last Date to Apply": None,  # Temporary placeholder
            "Expired": None  # New column

        }

        print(f"Fetching description for job: {job_link}")
        if job_link:
            job_content = get_page_with_scrapingdog(job_link, SCRAPINGDOG_API_KEY)
            if job_content:
                job_bs = soup(job_content, 'lxml')
                desc = job_bs.find('div', class_='JobDetails_jobDescription__uW_fK')
                description_text = desc.text.strip() if desc else ""
                job_data["Job Description"] = description_text if description_text else "No description."

                # Compute last date from post_date if no extracted date found
                if not job_data["Last Date to Apply"] and post_date:
                    computed_last_date, is_expired = compute_last_date_and_expiry(post_date)
                    job_data["Last Date to Apply"] = computed_last_date
                    job_data["Expired"] = is_expired

        jobs.append(job_data)

    return pd.DataFrame(jobs)

# --- Save jobs to CSV file ---
def save_new_jobs_to_csv(new_df):
    os.makedirs(os.path.dirname(JOBS_CSV_PATH), exist_ok=True)

    if os.path.exists(JOBS_CSV_PATH):
        old_df = pd.read_csv(JOBS_CSV_PATH)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset=["Job Link"], inplace=True)
        combined_df.to_csv(JOBS_CSV_PATH, index=False)
        print(f"\nUpdated jobs file. Total jobs: {len(combined_df)}")
    else:
        new_df.to_csv(JOBS_CSV_PATH, index=False)
        print(f"\nJobs saved to new file: {JOBS_CSV_PATH}")

# --- Main Execution Block ---
if __name__ == "__main__":
    print("Scraping new job data...\n")
    scraped_df = scrape_jobs()

    if not scraped_df.empty:
        scraped_df["Post Date"] = pd.to_datetime(scraped_df["Post Date"], errors='coerce')
        latest_jobs = scraped_df.sort_values(by="Post Date", ascending=False).head(5)

        print("\nLatest Jobs:\n")
        print(latest_jobs[[ 
            "Job Title", "Company Name", "Location", "Salary", 
            "Posted Text", "Post Date", "Job Age", "Last Date to Apply",
            "Job Link", "Job Description"
        ]].to_string(index=False))

        save_new_jobs_to_csv(scraped_df)
        
        # Call expiry status updater
        from CheckExpiry import update_expiry_status
        update_expiry_status(JOBS_CSV_PATH)

    else:
        print("No jobs scraped.")

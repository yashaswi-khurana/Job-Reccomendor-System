import requests
import json
import os
import pandas as pd
from datetime import datetime

# API endpoint for remote tech jobs (free, public API)
REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_jobs.csv')

def strip_html(html_str):
    """Utility to strip HTML tags from descriptions."""
    from bs4 import BeautifulSoup
    if not html_str:
        return ""
    try:
        soup = BeautifulSoup(html_str, "html.parser")
        return soup.get_text(separator=' ').strip()
    except:
        return html_str

def fetch_jobs_from_api(limit=50, category='', search_query=''):
    """
    Fetches real-time job listings from the Remotive API.
    Returns a list of dictionaries.
    """
    try:
        url = REMOTIVE_API_URL if not category else f"{REMOTIVE_API_URL}?category={category}"
        if search_query:
            if '?' in url:
                url += f"&search={search_query}"
            else:
                url += f"?search={search_query}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])[:limit]
            
            structured_jobs = []
            for job in jobs:
                description = strip_html(job.get('description', ''))
                structured_jobs.append({
                    'job_id': job.get('id'),
                    'title': job.get('title'),
                    'company': job.get('company_name'),
                    'location': job.get('candidate_required_location', 'Remote'),
                    'description': description,
                    'url': job.get('url'),
                    'salary': job.get('salary', 'Not specified'),
                    # Extract skills roughly from tags if available
                    'skills_required': ", ".join(job.get('tags', []))
                })
            return structured_jobs
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Failed to fetch from API: {e}")
        return []

def get_mock_jobs():
    """Fallback mock jobs if API fails or offline testing is needed."""
    return [
        "Please connect to the internet."
    ]

def fetch_and_index_jobs(search_query=''):
    """
    Main function to fetch jobs and store them locally.
    """
    jobs = fetch_jobs_from_api(limit=100, search_query=search_query)
    if not jobs:
        print("Falling back to mock jobs.")
        jobs = get_mock_jobs()
    
    # Create Data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to CSV as our "index"
    index_path = os.path.join(data_dir, 'jobs_index.csv')
    df = pd.DataFrame(jobs)
    df.to_csv(index_path, index=False)
    print(f"Indexed {len(jobs)} jobs to {index_path}")
    return df

if __name__ == "__main__":
    df = fetch_and_index_jobs()
    print(df.head())

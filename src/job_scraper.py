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

def fetch_jobs_from_api(limit=50, category='software-dev'):
    """
    Fetches real-time job listings from the Remotive API.
    Returns a list of dictionaries.
    """
    try:
        response = requests.get(f"{REMOTIVE_API_URL}?category={category}", timeout=10)
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
        {
            'job_id': 'm1',
            'title': 'Senior Python Developer',
            'company': 'Tech Solutions',
            'location': 'Remote',
            'description': 'We are looking for a Senior Python Developer with 5+ years of experience in Python, AWS, and PostgreSQL. You will design scalable architectures...',
            'url': 'https://example.com/job/m1',
            'salary': '$120,000 - $150,000',
            'skills_required': 'Python, AWS, PostgreSQL, SQL'
        },
        {
            'job_id': 'm2',
            'title': 'Machine Learning Engineer',
            'company': 'AI Innovators',
            'location': 'New York, NY',
            'description': 'Seeking an ML Engineer proficient in Machine Learning, TensorFlow, PyTorch, and NLP. NLP experience with LLMs is a big plus.',
            'url': 'https://example.com/job/m2',
            'salary': '$130k - $160k',
            'skills_required': 'Machine Learning, TensorFlow, PyTorch, NLP, Python'
        },
        {
            'job_id': 'm3',
            'title': 'Data Analyst',
            'company': 'DataCorp',
            'location': 'San Francisco, CA',
            'description': 'Data Analyst role requiring strong SQL, Data Analysis, Pandas, and Excel skills. Must have good communication.',
            'url': 'https://example.com/job/m3',
            'salary': 'Not specified',
            'skills_required': 'SQL, Data Analysis, Pandas, Excel, Communication'
        },
        {
            'job_id': 'm4',
            'title': 'Frontend Web Developer',
            'company': 'DesignStudio',
            'location': 'Remote',
            'description': 'Looking for a React developer with deep knowledge of HTML, CSS, JavaScript, and Node.js.',
            'url': 'https://example.com/job/m4',
            'salary': '$90,000',
            'skills_required': 'React, JavaScript, HTML, CSS, Node.js'
        }
    ]

def fetch_and_index_jobs():
    """
    Main function to fetch jobs and store them locally.
    """
    jobs = fetch_jobs_from_api(limit=100)
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

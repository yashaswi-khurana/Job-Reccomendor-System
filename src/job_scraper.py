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

def fetch_jobs_from_api(limit=50, category=''):
    """
    Fetches real-time job listings from the Remotive API.
    Returns a list of dictionaries.
    """
    try:
        url = REMOTIVE_API_URL if not category else f"{REMOTIVE_API_URL}?category={category}"
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
            'title': 'Chief Medical Officer',
            'company': 'HealthCare Partners',
            'location': 'Remote / On-Site',
            'description': 'Leading patient care strategies, clinical research, and medical terminology standardizations. Requirements: MD, Surgery experience, EMR knowledge.',
            'url': 'https://example.com/job/m4',
            'salary': '$250,000+',
            'skills_required': 'Patient Care, Diagnosis, Surgery, EMR, Clinical Research'
        },
        {
            'job_id': 'm5',
            'title': 'Human Resources Manager',
            'company': 'PeopleFirst Inc',
            'location': 'Remote',
            'description': 'We need an experienced HR Manager for onboarding, payroll, talent management, and employee relations.',
            'url': 'https://example.com/job/m5',
            'salary': '$90,000 - $120,000',
            'skills_required': 'Recruitment, Employee Relations, Payroll, Onboarding, Talent Management'
        },
        {
            'job_id': 'm6',
            'title': 'Senior Financial Analyst',
            'company': 'Global Finance Corp',
            'location': 'New York, NY',
            'description': 'MBA highly preferred. Role involves financial modeling, strategic planning, budgeting, and Excel. Strong communication skills required.',
            'url': 'https://example.com/job/m6',
            'salary': '$110,000 - $140,000',
            'skills_required': 'Strategic Planning, Budgeting, Financial Modeling, Excel, Finance'
        },
        {
            'job_id': 'm7',
            'title': 'Chief Executive Officer',
            'company': 'Stealth Startup',
            'location': 'San Francisco, CA',
            'description': 'Seeking an experienced CEO for corporate strategy, executive management, mergers & acquisitions, and stakeholder management.',
            'url': 'https://example.com/job/m7',
            'salary': 'Equity + Base',
            'skills_required': 'Corporate Strategy, Executive Management, Mergers & Acquisitions, Leadership'
        },
        {
            'job_id': 'm8',
            'title': 'Civil Engineer',
            'company': 'BuildRight',
            'location': 'Austin, TX',
            'description': 'Civil Engineer needed for infrastructure projects. Proficiency in AutoCAD, SolidWorks, and project management.',
            'url': 'https://example.com/job/m8',
            'salary': '$95,000 - $125,000',
            'skills_required': 'Civil Engineering, AutoCAD, SolidWorks, Project Management'
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

import os
import json

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'feedback_cache.json')

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_feedback(feedback_data):
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=4)

def add_feedback(user_skills, job_id, is_relevant):
    data = load_feedback()
    data.append({
        'user_skills': user_skills,
        'job_id': job_id,
        'is_relevant': is_relevant
    })
    save_feedback(data)

def get_accuracy():
    data = load_feedback()
    if not data:
        return 0.0
    relevant_count = sum(1 for item in data if item['is_relevant'])
    return (relevant_count / len(data)) * 100

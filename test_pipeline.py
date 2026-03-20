import os
from src.resume_parser import parse_resume, COMMON_SKILLS
from src.job_scraper import fetch_and_index_jobs
from src.matcher import calculate_match_scores
from src.analyzer import identify_skill_gaps, recommend_courses, suggest_resume_improvements

def run_test():
    print("1. Creating dummy resume...")
    dummy_resume_text = "I am a Senior Machine Learning Engineer with 5 years of experience building NLP models. My skills include Python, TensorFlow, PyTorch, and NLP."
    test_resume_path = "temp_test_resume.txt"
    with open(test_resume_path, "w") as f:
        f.write(dummy_resume_text)
        
    print("2. Parsing Resume...")
    resume_data = parse_resume(test_resume_path)
    print("   Skills Found:", resume_data['skills'])
    
    print("3. Fetching Jobs...")
    jobs_df = fetch_and_index_jobs()
    print(f"   Fetched {len(jobs_df)} jobs.")
    
    if len(jobs_df) > 0:
        print("4. Calculating matches...")
        matched_jobs = calculate_match_scores(resume_data, jobs_df)
        top_job = matched_jobs.iloc[0]
        print(f"   Top Job: {top_job['title']} at {top_job['company']} (Score: {top_job['match_score_%']}%)")
        print(f"   url: {top_job['url']}")
        
        print("5. Skill Gaps...")
        gaps = identify_skill_gaps(resume_data['skills'], top_job['skills_required'])
        print("   Missing:", gaps['missing_skills'])
        
        print("6. Course Recommendations...")
        courses = recommend_courses(gaps['missing_skills'])
        for c in courses:
            print("   *", c['skill'], "->", c['course'])
            
    # Cleanup
    if os.path.exists(test_resume_path):
        os.remove(test_resume_path)

if __name__ == "__main__":
    run_test()

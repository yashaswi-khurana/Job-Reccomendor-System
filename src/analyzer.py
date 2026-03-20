def identify_skill_gaps(resume_skills, job_skills_str):
    """
    Compare resume skills and required job skills to find missing skills.
    `resume_skills` is a list of strings.
    `job_skills_str` is a comma-separated string of skills from the job listing.
    """
    r_skills_lower = set([s.lower().strip() for s in resume_skills])
    
    # Simple split by comma for job skills (assuming they are comma separated)
    j_skills = [s.lower().strip() for s in job_skills_str.split(',') if s.strip()]
    j_skills_set = set(j_skills)
    
    missing_skills = list(j_skills_set - r_skills_lower)
    matched_skills = list(j_skills_set.intersection(r_skills_lower))
    
    return {
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
        "match_percentage": round(len(matched_skills) / len(j_skills_set) * 100, 2) if j_skills_set else 100.0
    }

def recommend_courses(missing_skills):
    """
    Given a list of missing skills, recommend some general courses.
    In a production system, this would query a real API (like Coursera or Udemy).
    Here we use a generic mapping for demonstration.
    """
    recommendations = []
    
    course_map = {
        'python': 'Complete Python Bootcamp - Udemy',
        'java': 'Java Programming Masterclass - Udemy',
        'sql': 'The Complete SQL Bootcamp - Udemy',
        'machine learning': 'Machine Learning Specialization - Coursera (Stanford)',
        'react': 'React - The Complete Guide - Udemy',
        'aws': 'AWS Certified Solutions Architect - Udemy',
        'docker': 'Docker Mastery - Udemy',
        'kubernetes': 'Kubernetes for Beginners - Udemy',
        'pandas': 'Data Analysis with Pandas - Coursera',
        'tensorflow': 'Deep Learning Specialization - Coursera',
        'excel': 'Excel Skills for Business - Coursera',
    }
    
    for skill in missing_skills:
        # Match roughly
        course_found = None
        for key, course in course_map.items():
            if key in skill or skill in key:
                course_found = course
                break
                
        if course_found:
            recommendations.append({"skill": skill, "course": course_found})
        else:
            # Generic fallback
            recommendations.append({"skill": skill, "course": f"Intro to {skill.title()} - Coursera / Udemy"})
            
    return recommendations

def suggest_resume_improvements(missing_skills):
    """
    Generate actionable tips to improve the resume based on the gap.
    """
    suggestions = []
    
    if len(missing_skills) > 0:
        suggestions.append(f"Your resume is missing some key skills required by top jobs: {', '.join(missing_skills[:5])}.")
        suggestions.append("Consider adding these keywords to your resume summary or experience section if you have the experience.")
    else:
        suggestions.append("Great job! Your skills align very well with your target roles.")
        
    suggestions.append("Make sure to use action verbs (e.g., 'Developed', 'Managed', 'Engineered') to describe your achievements.")
    suggestions.append("Quantify your achievements with numbers and metrics where possible (e.g., 'Improved performance by 20%').")
    
    return suggestions

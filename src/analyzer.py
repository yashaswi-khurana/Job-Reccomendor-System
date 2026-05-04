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

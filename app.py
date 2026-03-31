import os
import streamlit as st
import pandas as pd
from PIL import Image

# Import custom modules
from src.resume_parser import parse_resume
from src.job_scraper import fetch_and_index_jobs
from src.matcher import calculate_match_scores
from src.analyzer import identify_skill_gaps, recommend_courses, suggest_resume_improvements

# --- Page Config ---
st.set_page_config(
    page_title="AI Job Recommender System",
    page_icon="🎯",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .big-font { font-size: 20px !important; font-weight: bold;}
    .report-card { 
        background-color: #f8f9fa; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #0056b3; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    }
    .skill-badge {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 14px;
        margin: 5px;
        display: inline-block;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3050/3050431.png", width=150)
st.sidebar.title("AI Job Recommender")
st.sidebar.markdown("""
This system automatically:
1. Extracts skills from your resume
2. Scrapes real-time remote jobs across all industries
3. Matches your profile using Semantic AI
4. Recommends skill improvements
""")

# --- Main App ---
st.title("🎯 Next-Gen Job Recommendation System")

st.markdown("Upload your resume in **PDF, DOCX, PNG, or JPG** format to begin.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "png", "jpg", "jpeg"])

@st.cache_data(ttl=3600)  # Cache jobs for 1 hour to avoid API limits
def load_jobs():
    return fetch_and_index_jobs()

if uploaded_file is not None:
    # Save uploaded file temporarily to process
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Create layout columns
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📄 Resume Analysis")
        with st.spinner("Parsing resume..."):
            try:
                resume_data = parse_resume(file_path)
                st.success("Resume parsed successfully!")
                
                with st.expander("Show Extracted Info", expanded=True):
                    st.markdown("**Found Skills:**")
                    if resume_data['skills']:
                        skills_html = "".join([f"<span class='skill-badge'>{skill}</span>" for skill in resume_data['skills']])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.warning("No standard skills detected. Try adding more keywords.")
                        
                    st.markdown("**Entities Detected:**")
                    st.json(resume_data['entities'])
            except Exception as e:
                st.error(f"Error parsing file: {e}")
                st.stop()
                
    with col2:
        st.subheader("🔍 Matching Jobs")
        with st.spinner("Fetching live jobs and computing AI similarity scores..."):
            jobs_df = load_jobs()
            
            if jobs_df.empty:
                st.error("Could not load job listings.")
            else:
                matched_jobs = calculate_match_scores(resume_data, jobs_df)
                st.success(f"Matched against {len(jobs_df)} active job listings.")

                # Show top 5 jobs
                st.markdown("### Top 5 Recommended Jobs")
                top_jobs = matched_jobs.head(5)
                
                for i, row in top_jobs.iterrows():
                    match_score = row['match_score_%']
                    color = "green" if match_score >= 80 else "orange" if match_score >= 50 else "red"
                    
                    st.markdown(f"""
                    <div class='report-card'>
                        <h4 style='margin-bottom:0px;'><a href="{row['url']}" target="_blank" style="text-decoration:none;">{row['title']}</a></h4>
                        <p style='color: gray; margin-top:2px;'><b>{row['company']}</b> | {row['location']} | {row['salary']}</p>
                        <p><strong>Required Skills:</strong> {row['skills_required']}</p>
                        <p><strong>Match Score:</strong> <span style='color:{color}; font-weight:bold; font-size:18px;'>{match_score}%</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("Recommendation Explanation"):
                        st.write(f"- Semantic Description Similarity: {row['semantic_match_%']}%")
                        st.write(f"- Keyword Skill Match: {row['keyword_match_%']}%")
                        st.write("- **Why matched?**: The AI compares your resume text to the job description for deep semantic meaning, and specific keywords for exact skill overlaps.")

    # Show Skill Gap Analysis globally
    st.markdown("---")
    st.header("📊 Skill Gap Analysis & Recommendations")
    
    if not jobs_df.empty:
        # Get the skills required by the Top 1 job for an aggressive target
        top_job_skills = top_jobs.iloc[0]['skills_required'] if not top_jobs.empty else ""
        
        gaps = identify_skill_gaps(resume_data['skills'], top_job_skills)
        missing = gaps['missing_skills']
        
        st.markdown(f"Compared to the top recommended job (**{top_jobs.iloc[0]['title']}**), here is your skill gap:")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**Missing Skills:** {', '.join([s.title() for s in missing]) if missing else 'None detected!'}")
            
            courses = recommend_courses(missing)
            if courses:
                st.markdown("### 🎓 Recommended Courses")
                for c in courses:
                    search_query = c['skill'].replace(' ', '%20')
                    st.write(f"- **{c['skill'].title()}**: [{c['course']}](https://www.udemy.com/courses/search/?src=ukw&q={search_query})")
            else:
                st.write("No specific courses needed.")
                
        with c2:
            st.markdown("### ✍️ Resume Improvements")
            tips = suggest_resume_improvements(missing)
            for tip in tips:
                st.warning(f"💡 {tip}")


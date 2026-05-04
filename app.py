import os
import streamlit as st
import pandas as pd
from PIL import Image

# Import custom modules
from src.resume_parser import extract_text_from_file, extract_years_of_experience, extract_entities, extract_skills
import re
from src.job_scraper import fetch_and_index_jobs
from src.matcher import calculate_match_scores
from src.analyzer import identify_skill_gaps, suggest_resume_improvements
from src.feedback_manager import add_feedback, get_accuracy

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
3. Matches your profile using Semantic AI and Collaborative Filtering
4. Recommends skill improvements
""")

st.sidebar.markdown("---")
acc = get_accuracy()
st.sidebar.metric("Engine Accuracy", f"{acc:.1f}%")

# --- Main App ---
st.title("🎯 Next-Gen Job Recommendation System")

st.markdown("Upload your resume in **PDF, DOCX, PNG, or JPG** format to begin.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "png", "jpg", "jpeg"])

@st.cache_data(ttl=3600)  # Cache jobs for 1 hour to avoid API limits
def load_jobs(search_query=''):
    return fetch_and_index_jobs(search_query=search_query)

if uploaded_file is not None:
    # Save uploaded file temporarily to process
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Analyzing resume and fetching live jobs..."):
        try:
            # 1. Basic Parse
            raw_text = extract_text_from_file(file_path)
            clean_text = re.sub(r'\s+', ' ', raw_text).strip()
            yoe = extract_years_of_experience(clean_text)
            entities = extract_entities(clean_text)
            
            # 2. Fetch Jobs
            search_query = f"{yoe} years experience" if yoe > 0 else ""
            jobs_df = load_jobs(search_query)
            
            # 3. Dynamic Skills
            dynamic_skills = set()
            if not jobs_df.empty:
                for skills_str in jobs_df['skills_required']:
                    if pd.notna(skills_str):
                        for s in str(skills_str).split(','):
                            s = s.strip().lower()
                            if s: dynamic_skills.add(s)
            
            # Store in session state
            st.session_state['dynamic_skills'] = list(dynamic_skills)
            
            # 4. Extract Skills
            user_skills = extract_skills(clean_text, list(dynamic_skills))
            
            resume_data = {
                'raw_text': clean_text,
                'skills': user_skills,
                'entities': entities,
                'years_of_experience': yoe
            }
            parse_success = True
        except Exception as e:
            st.error(f"Error processing file: {e}")
            parse_success = False

    if parse_success:
        # Create layout columns
        col1, col2 = st.columns([1, 2])
    
        with col1:
            st.subheader("📄 Resume Analysis")
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
                
                years_of_experience = resume_data.get('years_of_experience', 0)
                if years_of_experience > 0:
                    st.markdown(f"**Experience Found:** {years_of_experience} years")
                    
        with col2:
            st.subheader("🔍 Matching Jobs")
            if jobs_df.empty:
                st.error("Could not load job listings.")
            else:
                matched_jobs = calculate_match_scores(resume_data, jobs_df)
                st.success(f"Matched against {len(jobs_df)} active job listings using {len(dynamic_skills)} dynamic skills.")

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
                        st.write(f"- Semantic Description Similarity: {row.get('semantic_match_%', 0)}%")
                        st.write(f"- Keyword Skill Match: {row.get('keyword_match_%', 0)}%")
                        st.write(f"- Collaborative Match: {row.get('cf_match_%', 0)}%")
                        st.write("- **Why matched?**: The AI compares your resume text to the job description for deep semantic meaning, specific keywords for exact skill overlaps, and boosts jobs liked by similar candidates.")
                        
                    st.markdown("<small>Was this job relevant to you?</small>", unsafe_allow_html=True)
                    c_up, c_down = st.columns(2)
                    with c_up:
                        if st.button("👍 Yes", key=f"up_{row['job_id']}"):
                            add_feedback(resume_data['skills'], row['job_id'], True)
                            st.success("Feedback recorded!")
                            st.rerun()
                    with c_down:
                        if st.button("👎 No", key=f"down_{row['job_id']}"):
                            add_feedback(resume_data['skills'], row['job_id'], False)
                            st.success("Feedback recorded!")
                            st.rerun()

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

        with c2:
            st.markdown("### ✍️ Resume Improvements")
            tips = suggest_resume_improvements(missing)
            for tip in tips:
                st.warning(f"💡 {tip}")


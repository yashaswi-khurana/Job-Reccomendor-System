import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Load models safely
try:
    bert_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print("Could not load sentence-transformers model. Maybe it's still downloading? Error:", e)

def compute_semantic_similarity(text1, text2):
    """Compute cosine similarity between two texts using Sentence Transformers."""
    if not text1 or not text2:
        return 0.0
    try:
        embeddings1 = bert_model.encode([text1])
        embeddings2 = bert_model.encode([text2])
        score = cosine_similarity(embeddings1, embeddings2)[0][0]
        return max(0.0, min(1.0, float(score))) # Normalize 0 to 1
    except:
        return 0.0

def compute_keyword_similarity(skills1, skills2):
    """Compute similarity between two lists of skills using TF-IDF and Cosine Similarity."""
    # skills1 and skills2 can be strings or lists
    if isinstance(skills1, list):
        skills1 = " ".join(skills1)
    if isinstance(skills2, list):
        skills2 = " ".join(skills2)
        
    skills1 = skills1.replace(',', ' ').lower()
    skills2 = skills2.replace(',', ' ').lower()
    
    if not skills1.strip() or not skills2.strip():
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer().fit([skills1, skills2])
        vecs = vectorizer.transform([skills1, skills2])
        score = cosine_similarity(vecs[0:1], vecs[1:2])[0][0]
        return float(score)
    except:
        return 0.0

def calculate_match_scores(resume_data, jobs_df):
    """
    Given parsed resume data and a dataframe of jobs, 
    calculate match scores and return a ranked dataframe.
    """
    resume_text = resume_data.get('raw_text', '')
    resume_skills = resume_data.get('skills', [])
    
    # Store scores
    semantic_scores = []
    keyword_scores = []
    total_scores = []
    
    for _, job in jobs_df.iterrows():
        job_desc = str(job.get('description', ''))
        job_skills = str(job.get('skills_required', ''))
        
        # 1. Semantic meaning matching based on description & text
        # Only take first 2000 chars to avoid memory issues and speed up
        semantic_score = compute_semantic_similarity(resume_text[:2000], job_desc[:2000])
        
        # 2. Keyword/Skill matching
        keyword_score = compute_keyword_similarity(resume_skills, job_skills)
        
        # 3. Hybrid scoring (Weighted average)
        # We give a high weight to keyword matching if skills are explicit
        # Otherwise, fall back to semantic score
        w_semantic = 0.5
        w_keyword = 0.5
        
        final_score = (w_semantic * semantic_score) + (w_keyword * keyword_score)
        
        semantic_scores.append(round(semantic_score * 100, 2))
        keyword_scores.append(round(keyword_score * 100, 2))
        total_scores.append(round(final_score * 100, 2))
        
    # Add score columns to dataframe
    result_df = jobs_df.copy()
    result_df['semantic_match_%'] = semantic_scores
    result_df['keyword_match_%'] = keyword_scores
    result_df['match_score_%'] = total_scores
    
    # Sort by total score descending
    result_df = result_df.sort_values(by='match_score_%', ascending=False).reset_index(drop=True)
    return result_df

if __name__ == "__main__":
    pass

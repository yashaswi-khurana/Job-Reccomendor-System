# 🎯 AI Job Recommender System

An AI-powered job recommendation web app built with Streamlit. Upload your resume and get matched against real-time remote tech job listings, with skill gap analysis and personalized course recommendations.

## Features

- **Resume Parsing** — Supports PDF, DOCX, PNG, and JPG formats
- **NLP Skill Extraction** — Identifies skills from your resume using spaCy and regex pattern matching
- **Real-Time Job Fetching** — Pulls live job listings from the [Remotive API](https://remotive.com/api/remote-jobs) (falls back to mock data if unavailable)
- **Hybrid AI Matching** — Combines semantic similarity (Sentence Transformers) with keyword matching (TF-IDF cosine similarity) for accurate job ranking
- **Skill Gap Analysis** — Compares your skills against the top recommended job's requirements
- **Course Recommendations** — Suggests relevant Coursera/Udemy courses for missing skills
- **Resume Improvement Tips** — Actionable suggestions to strengthen your resume

## Project Structure

```
├── app.py                  # Streamlit frontend
├── src/
│   ├── resume_parser.py    # Text extraction and NLP-based skill/entity parsing
│   ├── job_scraper.py      # Remotive API integration and mock job fallback
│   ├── matcher.py          # Semantic and keyword-based job matching
│   └── analyzer.py         # Skill gap analysis and course recommendations
├── data/
│   └── jobs_index.csv      # Cached job listings (auto-generated on first run)
├── requirements.txt
└── test_pipeline.py        # CLI pipeline test script
```

## Requirements

- Python 3.9+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (required for image-based resume parsing)

  **Fedora/RHEL:**
  ```bash
  sudo dnf install tesseract
  ```
  **Ubuntu/Debian:**
  ```bash
  sudo apt install tesseract-ocr
  ```
  **macOS:**
  ```bash
  brew install tesseract
  ```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Job-Reccomendor-System
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the spaCy language model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

### Run the Web App

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser and upload your resume.

### Run the CLI Pipeline Test

```bash
python test_pipeline.py
```

This runs a full end-to-end test with a dummy resume — useful for verifying the setup without the UI.

## How It Works

1. **Resume Parsing** — Text is extracted from the uploaded file using `pdfplumber` (PDF), `docx2txt` (DOCX), or `pytesseract` (images). Skills are matched against a predefined list and entities (organizations, locations, dates) are extracted via spaCy.

2. **Job Fetching** — Up to 100 software development jobs are fetched from the Remotive API and cached locally as `data/jobs_index.csv` for 1 hour. If the API is unreachable, built-in mock jobs are used instead.

3. **Matching** — Each job is scored using:
   - **Semantic similarity** (50%): Cosine similarity between resume text and job description embeddings using `all-MiniLM-L6-v2`.
   - **Keyword similarity** (50%): TF-IDF cosine similarity between resume skills and job-required skills.

4. **Analysis** — The top job's required skills are compared against your resume skills to surface gaps, suggest courses, and provide resume writing tips.

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI |
| `spacy` | NLP entity extraction |
| `sentence-transformers` | Semantic similarity embeddings |
| `pdfplumber` | PDF text extraction |
| `pytesseract` | OCR for image resumes |
| `docx2txt` | DOCX text extraction |
| `beautifulsoup4` | HTML stripping from job descriptions |
| `scikit-learn` | TF-IDF vectorization and cosine similarity |
| `pandas` | Data handling |
| `requests` | API calls |

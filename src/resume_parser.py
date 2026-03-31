import os
import re
import spacy
import pdfplumber
import docx2txt
try:
    from PIL import Image
    import pytesseract
except ImportError:
    pass

# Load spaCy NLP model
nlp = None
try:
    nlp = spacy.load('en_core_web_sm')
except Exception:
    try:
        from spacy.cli import download
        download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
    except Exception as e:
        print(f"Warning: Could not load or download spacy model. Entities will not be extracted. {e}")

# A simple predefined list of skills for extraction (this can be expanded or loaded from a file/DB)
COMMON_SKILLS = [
    # Tech
    'python', 'java', 'c++', 'sql', 'javascript', 'react', 'node.js', 'html', 'css',
    'machine learning', 'data analysis', 'deep learning', 'nlp', 'computer vision',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'agile', 'scrum',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
    'tableau', 'power bi', 'excel', 'go', 'ruby', 'php', 'c#', 'swift', 'kotlin',
    'linux', 'bash', 'shell script', 'rest api', 'graphql', 'mongodb', 'postgresql',
    'mysql', 'redis', 'elasticsearch', 'kafka', 'rabbitmq',
    # Soft Skills & Management
    'communication', 'leadership', 'problem solving', 'project management', 'teamwork',
    # Medical & Healthcare
    'patient care', 'diagnosis', 'surgery', 'emr', 'clinical research', 'nursing', 'medical terminology',
    # HR
    'recruitment', 'employee relations', 'payroll', 'onboarding', 'talent management', 'human resources',
    # MBA & Business
    'strategic planning', 'budgeting', 'financial modeling', 'marketing', 'sales', 'product management', 'finance', 'accounting',
    # Executive & CEO
    'corporate strategy', 'executive management', 'mergers & acquisitions', 'stakeholder management', 'business development',
    # Other Engineering
    'autocad', 'solidworks', 'matlab', 'civil engineering', 'mechanical engineering', 'manufacturing', 'quality assurance'
]

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extract = page.extract_text()
            if extract:
                text += extract + "\n"
    return text

def extract_text_from_docx(docx_path):
    text = docx2txt.process(docx_path)
    return text

def extract_text_from_image(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.doc', '.docx']:
        return extract_text_from_docx(file_path)
    elif ext in ['.png', '.jpg', '.jpeg']:
        return extract_text_from_image(file_path)
    else:
        # Fallback for plain text
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            raise ValueError(f"Unsupported file format: {ext}")

def extract_skills(text):
    text_lower = text.lower()
    found_skills = set()
    for skill in COMMON_SKILLS:
        # Check if the skill is in the text as a standalone word/phrase
        # Using word boundaries to avoid partial matches (e.g., 'go' matching 'going')
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    return list(found_skills)

def extract_entities(text):
    """
    Extract generic entities like organizations (potential employers),
    GPE (locations), and dates (durations).
    """
    entities = {'ORG': [], 'GPE': [], 'DATE': [], 'PERSON': []}
    if nlp is None:
        return entities
        
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in entities:
            # avoiding very short or irrelevant matches
            if len(ent.text.strip()) > 2:
                # Add unique entities
                if ent.text.strip() not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text.strip())
    return entities

def parse_resume(file_path):
    """
    Main parsing function. Returns a dictionary containing raw text and extracted information.
    """
    text = extract_text_from_file(file_path)
    
    # Clean text slightly
    clean_text = re.sub(r'\\s+', ' ', text).strip()
    
    skills = extract_skills(clean_text)
    entities = extract_entities(clean_text)
    
    return {
        "raw_text": clean_text,
        "skills": skills,
        "entities": entities
    }

if __name__ == "__main__":
    # Small test
    sample_text = "I am a software engineer with 5 years of experience in Python, Java, and SQL. I have worked at Google."
    print("Skills:", extract_skills(sample_text))
    
    # Try parsing nlp
    try:
        doc = nlp(sample_text)
        print("Entities:", [(e.text, e.label_) for e in doc.ents])
    except:
        pass

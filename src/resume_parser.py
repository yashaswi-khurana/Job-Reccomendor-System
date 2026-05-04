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

def extract_skills(text, skills_list):
    text_lower = text.lower()
    found_skills = set()
    for skill in skills_list:
        skill_clean = skill.strip().lower()
        if not skill_clean:
            continue
        # Check if the skill is in the text as a standalone word/phrase
        # Using word boundaries to avoid partial matches (e.g., 'go' matching 'going')
        # We need to escape the skill for regex matching
        pattern = r'\b' + re.escape(skill_clean) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill_clean)
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

def extract_years_of_experience(text):
    """
    Extract the highest number of years of experience mentioned in the text.
    """
    pattern = r'(\d+)\+?\s*(?:years?|yrs?)(?:\s*of)?\s*experience'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        years = [int(m) for m in matches]
        return max(years)
    return 0

if __name__ == "__main__":
    # Small test
    sample_text = "I am a software engineer with 5 years of experience in Python, Java, and SQL. I have worked at Google."
    test_skills = ["python", "java", "sql", "c++", "go"]
    print("Skills:", extract_skills(sample_text, test_skills))
    
    # Try parsing nlp
    try:
        doc = nlp(sample_text)
        print("Entities:", [(e.text, e.label_) for e in doc.ents])
    except:
        pass

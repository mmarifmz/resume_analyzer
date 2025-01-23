import os
import sqlite3
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import openai
import docx
import pdfplumber
import requests
import re
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urlencode

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"docx", "pdf"}
app.secret_key = "your_secret_key"  # Replace with a secure key

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Replace with your OpenAI API key

# Register a custom Jinja2 filter for URL encoding
@app.template_filter('urlencode')
def urlencode_filter(s):
    return urlencode({"text": s})

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            match_percentage INTEGER,
            ats_score INTEGER,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

# File handling functions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
    return "\n".join(pages)

# Fetch job description from link
def fetch_job_description(job_link):
    try:
        response = requests.get(job_link, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Example selector: adjust based on job website structure
        job_description = soup.find("div", class_="job-description").get_text(strip=True)
        return job_description
    except Exception:
        return None

# Save results to the database
def save_result(email, match_percentage, ats_score, feedback):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO results (email, match_percentage, ats_score, feedback)
        VALUES (?, ?, ?, ?)
    ''', (email, match_percentage, ats_score, feedback))
    conn.commit()
    conn.close()

# Match Percentage Calculation
def calculate_match_percentage(resume_text, job_description):
    def extract_keywords(text):
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        words = text.lower().split()
        stop_words = {"the", "and", "a", "to", "of", "in", "for", "on", "with", "as", "by", "at", "an", "is", "it"}  # Extend with more stop words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return Counter(keywords)

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)
    common_keywords = set(resume_keywords.keys()) & set(job_keywords.keys())
    total_keywords = set(job_keywords.keys())
    match_percentage = (len(common_keywords) / len(total_keywords)) * 100 if total_keywords else 0
    return round(match_percentage, 2)

# ATS Score Calculation
def calculate_ats_score(resume_text, job_description):
    ats_score = 0
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', resume_text):  # Email pattern
        ats_score += 20
    if re.search(r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b', resume_text):  # Phone number pattern
        ats_score += 20

    match_percentage = calculate_match_percentage(resume_text, job_description)
    ats_score += min(match_percentage, 40)  # Add up to 40 points based on match percentage

    if not re.search(r'<[^>]+>', resume_text):  # No HTML tags
        ats_score += 10

    resume_length = len(resume_text.split())
    if 300 <= resume_length <= 800:  # Ideal resume length
        ats_score += 10

    return round(min(ats_score, 100), 2)  # Cap ATS score at 100

# Extract Specific Sections from Feedback
def extract_section(feedback, section_title):
    """
    Extract specific sections from the feedback using headings.
    """
    pattern = rf"{section_title}:(.*?)(?=\n\n|$)"
    match = re.search(pattern, feedback, re.DOTALL)
    return match.group(1).strip() if match else "No information available."

#Special text cleansing from feedback from AI
def clean_text(text):
    """
    Cleans the extracted text by:
    - Stripping leading/trailing whitespace or newlines.
    - Removing leading numbering, asterisks, dashes, and extra spaces.
    - Filtering out empty or invalid lines.
    Returns a list of cleaned lines.
    """
    import re
    if not text:
        return []
    
    # Strip overall whitespace and split into lines
    lines = text.strip().splitlines()
    
    # Clean each line and filter out empty lines
    cleaned_lines = [
        re.sub(r'^[\d\.\*\-\s]+', '', line).strip()  # Remove numbering, asterisks, etc.
        for line in lines if line.strip()  # Exclude empty or whitespace-only lines
    ]
    
    return cleaned_lines

# Resume analysis function
def analyze_resume(resume_text, job_description):
    messages = [
        {"role": "system", "content": "You are a professional career advisor."},
        {
            "role": "user",
            "content": f"""
            Analyze the following resume based on the given job description. Provide feedback including:
            1. Key Skills That Align With the Job.
            2. Missing Skills or Experience.
            3. Suggestions for Improvement.

            Resume:
            {resume_text}

            Job Description:
            {job_description}
            """
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    feedback = response["choices"][0]["message"]["content"]

    # Extract and clean feedback sections
    key_skills = clean_text(extract_section(feedback, "Key Skills That Align With the Job"))
    missing_skills = clean_text(extract_section(feedback, "Missing Skills or Experience"))
    suggestions = clean_text(extract_section(feedback, "Suggestions for Improvement"))

    # Calculate match percentage and ATS score
    match_percentage = calculate_match_percentage(resume_text, job_description)
    ats_score = calculate_ats_score(resume_text, job_description)

    return key_skills, missing_skills, suggestions, match_percentage, ats_score



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            email = request.form["email"]
            job_link = request.form.get("job_link", "").strip()
            job_description = request.form.get("job_description", "").strip()
            file = request.files["resume"]
        except KeyError as e:
            return f"Missing form field: {str(e)}", 400

        if not job_description and job_link:
            job_description = fetch_job_description(job_link)
            if not job_description:
                return "Failed to fetch job description from the provided link.", 400

        if not job_description:
            return "You must provide either a job description or a job link.", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            try:
                if filename.endswith(".docx"):
                    resume_text = extract_text_from_docx(file_path)
                elif filename.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(file_path)
                else:
                    return "Unsupported file format.", 400

                # Analyze resume and calculate dynamic scores
                key_skills, missing_skills, suggestions, match_percentage, ats_score = analyze_resume(
                    resume_text, job_description
                )

                # Save the result
                combined_feedback = f"Key Skills: {key_skills}\n\nMissing Skills: {missing_skills}\n\nSuggestions: {suggestions}"
                save_result(email, match_percentage, ats_score, combined_feedback)

                return render_template(
                    "result.html",
                    email=email,
                    key_skills=key_skills,
                    missing_skills=missing_skills,
                    suggestions=suggestions,
                    match_percentage=match_percentage,
                    ats_score=ats_score
                )
            finally:
                os.remove(file_path)
        else:
            return "Invalid file format.", 400

    return render_template("index.html")

if __name__ == "__main__":
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    init_db()
    app.run(debug=True)
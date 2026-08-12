from flask import Flask, request, render_template, jsonify
import PyPDF2
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Create uploads folder if it doesn't exist
try:
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
except OSError:
    pass

# Expanded skills list for better analysis
SKILLS_DB = {
    "Programming Languages": ["python", "javascript", "java", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin", "typescript"],
    "Web Frameworks & Tools": ["react", "node", "vue", "angular", "flask", "django", "express", "next.js", "tailwind", "bootstrap", "sass", "webpack"],
    "Databases": ["sql", "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "mariadb", "firebase"],
    "Data Science & ML": ["machine learning", "deep learning", "data analysis", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "nlp", "computer vision"],
    "Cloud & DevOps": ["aws", "azure", "docker", "kubernetes", "jenkins", "git", "ci/cd", "terraform", "gcp", "linux"]
}

def extract_text(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text.lower()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def analyze_resume(text):
    found_skills = {}
    total_found_count = 0
    
    for category, skills in SKILLS_DB.items():
        category_skills = []
        for skill in skills:
            # Simple word matching, can be improved with regex
            if skill.lower() in text:
                category_skills.append(skill.capitalize())
                total_found_count += 1
        if category_skills:
            found_skills[category] = category_skills
            
    # Calculate score (out of 100, though this is arbitrary)
    # Let's say we expect at least 10 skills for a "perfect" score
    score = min(total_found_count * 10, 100)
    
    # Simple recommendation logic
    recommendations = []
    if score < 40:
        recommendations.append("Consider adding more industry-specific technical skills.")
    if "Programming Languages" not in found_skills:
        recommendations.append("Highlight your proficiency in programming languages.")
    if "Cloud & DevOps" not in found_skills:
        recommendations.append("Familiarize yourself with Cloud tools or Version Control (Git).")
        
    return found_skills, score, recommendations

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'resume' not in request.files:
            return render_template("index.html", error="No file uploaded", skills=None, score=None)
        
        file = request.files["resume"]
        if file.filename == '':
            return render_template("index.html", error="No selected file", skills=None, score=None)
        
        if file and file.filename.endswith('.pdf'):
            text = extract_text(file)
            if not text:
                return render_template("index.html", error="Could not extract text from PDF", skills=None, score=None)
                
            skills_by_category, score, recommendations = analyze_resume(text)
            return render_template("index.html", 
                                 skills=skills_by_category, 
                                 score=score, 
                                 recommendations=recommendations,
                                 filename=file.filename)
        else:
            return render_template("index.html", error="Please upload a PDF file", skills=None, score=None)
            
    return render_template("index.html", skills=None, score=None)

if __name__ == "__main__":
    app.run(debug=True)

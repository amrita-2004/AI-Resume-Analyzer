import os
import io
import re
from flask import Flask, request, render_template, jsonify
import PyPDF2

from analyzer import analyze_resume_comprehensive, SKILLS_DB
from jd_matcher import calculate_jd_match
from ai_rewriter import rewrite_bullet_point, batch_rewrite_bullets
from interview_gen import generate_interview_questions

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp' if os.environ.get('VERCEL') else 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def extract_text_from_stream(pdf_file_stream):
    """Extracts text from PDF stream in-memory without requiring disk writes."""
    try:
        pdf_bytes = pdf_file_stream.read()
        pdf_file_like = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file_like)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'resume' not in request.files:
            return render_template("index.html", error="No file uploaded", analysis=None)
        
        file = request.files["resume"]
        jd_text = request.form.get("job_description", "").strip()
        
        if file.filename == '':
            return render_template("index.html", error="No selected file", analysis=None)
        
        if file and file.filename.lower().endswith('.pdf'):
            resume_text = extract_text_from_stream(file)
            if not resume_text:
                return render_template("index.html", error="Could not extract text from PDF. Ensure it contains selectable text.", analysis=None)
                
            # Perform comprehensive analysis
            comp_analysis = analyze_resume_comprehensive(resume_text)
            
            # Perform JD Matching if job description provided
            jd_analysis = calculate_jd_match(resume_text, jd_text) if jd_text else None
            
            # Generate Interview Questions
            interview_prep = generate_interview_questions(comp_analysis["all_skills"])
            
            # Initial Sample Bullet Rewrites from resume content
            bullets = [line.strip(' •-*') for line in resume_text.split('\n') if len(line.strip()) > 20][:3]
            sample_rewrites = batch_rewrite_bullets(bullets) if bullets else []
            
            analysis_result = {
                "filename": file.filename,
                "resume_text": resume_text[:1000],  # Truncated preview
                "comprehensive": comp_analysis,
                "jd_match": jd_analysis,
                "interview_prep": interview_prep,
                "sample_rewrites": sample_rewrites
            }
            
            return render_template("index.html", analysis=analysis_result, error=None)
        else:
            return render_template("index.html", error="Please upload a PDF file (.pdf)", analysis=None)
            
    return render_template("index.html", analysis=None, error=None)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """API endpoint for async or headless resume analysis."""
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files["resume"]
    jd_text = request.form.get("job_description", "").strip()
    
    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "PDF file required"}), 400
        
    text = extract_text_from_stream(file)
    if not text:
        return jsonify({"error": "Failed to extract text from PDF"}), 400
        
    comp = analyze_resume_comprehensive(text)
    jd_match = calculate_jd_match(text, jd_text) if jd_text else None
    interview = generate_interview_questions(comp["all_skills"])
    
    return jsonify({
        "status": "success",
        "filename": file.filename,
        "ats_score": comp["ats_score"],
        "breakdown": comp["score_breakdown"],
        "skills": comp["skills"],
        "recommendations": comp["recommendations"],
        "heatmap": comp["heatmap"],
        "career_recommendations": comp["career_recommendations"],
        "jd_match": jd_match,
        "interview_prep": interview
    })

@app.route("/api/rewrite-bullet", methods=["POST"])
def api_rewrite_bullet():
    """API endpoint for live bullet point rewriter tool."""
    data = request.get_json(silent=True) or request.form
    bullet = data.get("bullet", "").strip()
    if not bullet:
        return jsonify({"error": "No bullet text provided"}), 400
        
    res = rewrite_bullet_point(bullet)
    return jsonify(res)

@app.route("/api/interview-prep", methods=["POST"])
def api_interview_prep():
    """API endpoint to generate customized interview questions."""
    data = request.get_json(silent=True) or request.form
    skills = data.get("skills", [])
    role = data.get("role", "Software Engineer")
    
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
        
    res = generate_interview_questions(skills, role)
    return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

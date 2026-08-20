import os
import io
import re
import json
from flask import Flask, request, render_template, jsonify
import PyPDF2

from analyzer import analyze_resume_comprehensive, SKILLS_DB
from jd_matcher import calculate_jd_match
from ai_rewriter import rewrite_bullet_point, batch_rewrite_bullets
from interview_gen import generate_interview_questions
from recovery_engine import extract_text_from_file, analyze_job_readiness, compare_resumes

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp' if os.environ.get('VERCEL') else 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def extract_text_from_stream(pdf_file_stream):
    """Extracts text from PDF or DOCX file stream in-memory."""
    text, _ = extract_text_from_file(pdf_file_stream)
    return text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'resume' not in request.files:
            return render_template("index.html", error="No file uploaded", analysis=None)
        
        file = request.files["resume"]
        jd_text = request.form.get("job_description", "").strip()
        target_role = request.form.get("target_role", "").strip()
        
        if file.filename == '':
            return render_template("index.html", error="No selected file", analysis=None)
        
        allowed_exts = ('.pdf', '.docx')
        if file and file.filename.lower().endswith(allowed_exts):
            resume_text, filename = extract_text_from_file(file)
            if not resume_text:
                return render_template("index.html", error="Could not extract text from document. Ensure it contains selectable text.", analysis=None)
                
            # Perform Comprehensive & Job Readiness Analysis
            recovery_result = analyze_job_readiness(resume_text, jd_text, target_role)
            comp_analysis = recovery_result["comprehensive"]
            jd_analysis = recovery_result["jd_match"]
            
            # Initial Sample Bullet Rewrites from resume content
            bullets = [line.strip(' •-*') for line in resume_text.split('\n') if len(line.strip()) > 20][:3]
            sample_rewrites = batch_rewrite_bullets(bullets) if bullets else []
            
            analysis_result = {
                "filename": filename,
                "resume_text": resume_text[:1000],  # Truncated preview
                "comprehensive": comp_analysis,
                "jd_match": jd_analysis,
                "interview_prep": recovery_result["interview_prep"],
                "sample_rewrites": sample_rewrites,
                "recovery": recovery_result
            }
            
            return render_template("index.html", analysis=analysis_result, error=None)
        else:
            return render_template("index.html", error="Please upload a valid PDF or DOCX file (.pdf, .docx)", analysis=None)
            
    return render_template("index.html", analysis=None, error=None)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """API endpoint for async or headless resume analysis with recovery engine."""
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files["resume"]
    jd_text = request.form.get("job_description", "").strip()
    target_role = request.form.get("target_role", "").strip()
    
    allowed_exts = ('.pdf', '.docx')
    if not file or not file.filename.lower().endswith(allowed_exts):
        return jsonify({"error": "PDF or DOCX file required"}), 400
        
    text, filename = extract_text_from_file(file)
    if not text:
        return jsonify({"error": "Failed to extract text from document"}), 400
        
    recovery = analyze_job_readiness(text, jd_text, target_role)
    comp = recovery["comprehensive"]
    
    return jsonify({
        "status": "success",
        "filename": filename,
        "ats_score": comp["ats_score"],
        "job_readiness_score": recovery["readiness_score"],
        "readiness_tier": recovery["status_tier"],
        "breakdown": comp["score_breakdown"],
        "skills": comp["skills"],
        "recommendations": comp["recommendations"],
        "heatmap": comp["heatmap"],
        "career_recommendations": comp["career_recommendations"],
        "jd_match": recovery["jd_match"],
        "interview_prep": recovery["interview_prep"],
        "recovery": recovery
    })

@app.route("/api/reanalyze", methods=["POST"])
def api_reanalyze():
    """API endpoint to re-analyze an improved resume and compare with previous baseline."""
    if 'resume' not in request.files:
        return jsonify({"error": "No new resume file uploaded"}), 400
        
    file = request.files["resume"]
    jd_text = request.form.get("job_description", "").strip()
    target_role = request.form.get("target_role", "").strip()
    prev_analysis_json = request.form.get("previous_analysis", "")
    
    allowed_exts = ('.pdf', '.docx')
    if not file or not file.filename.lower().endswith(allowed_exts):
        return jsonify({"error": "PDF or DOCX file required"}), 400
        
    new_text, filename = extract_text_from_file(file)
    if not new_text:
        return jsonify({"error": "Could not extract text from uploaded resume file"}), 400
        
    prev_data = {}
    if prev_analysis_json:
        try:
            prev_data = json.loads(prev_analysis_json)
        except Exception:
            prev_data = {}
            
    # Calculate comparison
    comparison = compare_resumes(prev_data.get("recovery", prev_data), new_text, jd_text, target_role)
    
    return jsonify({
        "status": "success",
        "filename": filename,
        "comparison": comparison
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


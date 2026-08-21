import os
import re
import time
from werkzeug.utils import secure_filename
from recovery_engine import extract_text_from_file, analyze_job_readiness, compare_resumes
from services.socket_service import emit_progress
from models.analysis_model import AnalysisRecord

ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_and_extract_file(file_storage):
    """
    Validates uploaded file type (PDF/DOCX), checks file size,
    and extracts plain text in-memory.
    """
    if not file_storage or not file_storage.filename:
        return None, None, "No file selected."
        
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        return None, None, "Invalid file format. Only PDF (.pdf) and DOCX (.docx) files are supported."
        
    # Read bytes for size check and extraction
    file_bytes = file_storage.read()
    file_storage.seek(0)
    
    if len(file_bytes) > MAX_FILE_SIZE:
        return None, None, "File size exceeds 16MB limit."
        
    if len(file_bytes) == 0:
        return None, None, "Uploaded file is empty."
        
    # File header signature (magic bytes) validation
    is_pdf = filename.lower().endswith('.pdf')
    is_docx = filename.lower().endswith('.docx')
    
    if is_pdf and not file_bytes.startswith(b'%PDF'):
        return None, None, "Corrupted PDF file header."
        
    if is_docx and not (file_bytes.startswith(b'PK\x03\x04') or file_bytes.startswith(b'PK\x05\x06')):
        return None, None, "Corrupted DOCX file header."
        
    text, filename = extract_text_from_file(file_storage)
    
    if not text or len(text.strip()) < 20:
        return None, None, "Could not extract sufficient text from document. Ensure it is not a scanned image PDF."
        
    return text, filename, None

def sanitize_input_text(text):
    """Sanitizes text inputs by stripping script/html tags."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]*?>', '', str(text))
    return clean.strip()

def process_resume_analysis(file_storage, jd_text="", target_role="", user_id="anonymous", emit_ws=True):
    """
    Full pipeline execution for resume analysis with real-time WebSocket progress updates.
    Steps:
      10% Resume Uploaded
      30% Text Extracted
      50% NLP Processing
      70% ATS Scoring
      90% AI Recommendations
      100% Dashboard Ready
    """
    jd_text = sanitize_input_text(jd_text)
    target_role = sanitize_input_text(target_role) or "Software Engineer"
    
    if emit_ws:
        emit_progress(10, "Resume Uploaded & Validated...")
    time.sleep(0.1)
    
    text, filename, err = validate_and_extract_file(file_storage)
    if err:
        if emit_ws:
            emit_progress(0, f"Upload Failed: {err}")
        return None, err
        
    if emit_ws:
        emit_progress(30, "Text Extracted Successfully from Document.")
    time.sleep(0.1)
    
    if emit_ws:
        emit_progress(50, "Performing NLP Entity & Skill Keyword Processing...")
    time.sleep(0.1)
    
    # Run core recovery engine analysis
    recovery_result = analyze_job_readiness(text, jd_text, target_role)
    
    if emit_ws:
        emit_progress(70, "Calculating ATS Score & Job Readiness Breakdown...")
    time.sleep(0.1)
    
    if emit_ws:
        emit_progress(90, "Generating AI Rejection Vectors & Career Recommendations...")
    time.sleep(0.1)
    
    comp = recovery_result["comprehensive"]
    scores = recovery_result["scores"]
    status_tier = recovery_result["status_tier"]
    
    # Save to history storage
    record = AnalysisRecord({
        "user_id": user_id,
        "filename": filename,
        "target_role": target_role,
        "ats_score": comp["ats_score"],
        "readiness_score": recovery_result["readiness_score"],
        "status_tier": status_tier,
        "scores": scores,
        "skills": comp["skills"],
        "missing_skills": recovery_result["skill_gaps"]["all_missing"],
        "full_analysis": recovery_result
    })
    saved_data = record.save()
    
    if emit_ws:
        emit_progress(100, "Dashboard Ready!", data={"analysis_id": record.id, "readiness_score": recovery_result["readiness_score"]})
        
    return recovery_result, None

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask_login import current_user
from models.analysis_model import AnalysisRecord
from services.resume_service import validate_and_extract_file, process_resume_analysis
from ai_rewriter import batch_rewrite_bullets

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    error_msg = None
    analysis_result = None
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            error_msg = "No file uploaded."
        else:
            file = request.files['resume']
            jd_text = request.form.get('job_description', '').strip()
            target_role = request.form.get('target_role', '').strip()
            
            user_id = current_user.id if current_user.is_authenticated else "anonymous"
            result, err = process_resume_analysis(file, jd_text, target_role, user_id=user_id, emit_ws=True)
            
            if err:
                error_msg = err
            else:
                comp_analysis = result["comprehensive"]
                jd_analysis = result["jd_match"]
                
                bullets = [line.strip(' •-*') for line in comp_analysis.get("all_skills", []) if len(line.strip()) > 10][:3]
                sample_rewrites = batch_rewrite_bullets(bullets) if bullets else []
                
                analysis_result = {
                    "filename": file.filename,
                    "comprehensive": comp_analysis,
                    "jd_match": jd_analysis,
                    "interview_prep": result["interview_prep"],
                    "sample_rewrites": sample_rewrites,
                    "recovery": result
                }
                session['latest_analysis'] = result
                
    return render_template('index.html', analysis=analysis_result, error=error_msg)

@main_bp.route('/dashboard')
def dashboard():
    user_id = current_user.id if current_user.is_authenticated else "anonymous"
    history = AnalysisRecord.get_user_history(user_id=user_id, limit=1)
    
    analysis_data = None
    if history and len(history) > 0:
        analysis_data = history[0]["full_analysis"]
    elif 'latest_analysis' in session:
        analysis_data = session['latest_analysis']
        
    return render_template('dashboard.html', analysis=analysis_data)

@main_bp.route('/history')
def history():
    user_id = current_user.id if current_user.is_authenticated else "anonymous"
    records = AnalysisRecord.get_user_history(user_id=user_id, limit=20)
    return render_template('history.html', records=records)

@main_bp.route('/docs')
def docs():
    return render_template('docs.html')

import json
from flask import Blueprint, request, jsonify, session
from flask_login import current_user
from services.resume_service import process_resume_analysis, validate_and_extract_file, sanitize_input_text
from recovery_engine import calculate_jd_match, compare_resumes, analyze_job_readiness
from ai_rewriter import rewrite_bullet_point
from interview_gen import generate_interview_questions
from models.analysis_model import AnalysisRecord

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/analyze', methods=['POST'])
def api_analyze():
    """
    POST /api/analyze
    Analyzes uploaded resume (PDF/DOCX) against target role and optional job description.
    Returns full analysis JSON. Emits WebSocket progress events.
    """
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded. Key 'resume' is required."}), 400
        
    file = request.files['resume']
    jd_text = request.form.get('job_description', '').strip()
    target_role = request.form.get('target_role', '').strip()
    
    user_id = current_user.id if current_user.is_authenticated else "anonymous"
    
    result, err = process_resume_analysis(file, jd_text, target_role, user_id=user_id, emit_ws=True)
    if err:
        return jsonify({"error": err}), 400
        
    # Store latest analysis in session for easy dashboard viewing
    session['latest_analysis'] = result
    
    return jsonify({
        "status": "success",
        "message": "Analysis completed successfully",
        "ats_score": result["scores"]["ats_score"],
        "job_readiness_score": result["readiness_score"],
        "readiness_tier": result["status_tier"],
        "dashboard": {
            "ats_score": result["scores"]["ats_score"],
            "job_match_pct": result["scores"]["overall_match"],
            "skill_match_pct": result["scores"]["skills_match"],
            "experience_match_pct": result["scores"]["experience_match"],
            "job_readiness_score": result["readiness_score"],
            "missing_skills": result["skill_gaps"]["all_missing"],
            "resume_status": result["status_tier"]["tier"]
        },
        "breakdown": result["scores"],
        "skills": result["comprehensive"]["skills"],
        "recommendations": result["comprehensive"]["recommendations"],
        "rejection_reasons": result["rejection_reasons"],
        "skill_gaps": result["skill_gaps"],
        "recovery_plan": result["recovery_plan"],
        "project_rec": result["project_rec"],
        "resume_improvements": result["resume_improvements"],
        "interview_prep": result["interview_prep"],
        "action_rec": result["action_rec"]
    })

@api_bp.route('/job-match', methods=['POST'])
def api_job_match():
    """
    POST /api/job-match
    Calculates alignment, skill gap, and similarity between a resume text (or uploaded file) and job description.
    """
    jd_text = sanitize_input_text(request.form.get('job_description', '') or (request.get_json(silent=True) or {}).get('job_description', ''))
    resume_text = sanitize_input_text(request.form.get('resume_text', '') or (request.get_json(silent=True) or {}).get('resume_text', ''))
    
    if 'resume' in request.files:
        file = request.files['resume']
        extracted_text, filename, err = validate_and_extract_file(file)
        if err:
            return jsonify({"error": err}), 400
        resume_text = extracted_text
        
    if not resume_text:
        return jsonify({"error": "Resume text or uploaded resume file is required."}), 400
    if not jd_text:
        return jsonify({"error": "Job description text is required for matching."}), 400
        
    match_result = calculate_jd_match(resume_text, jd_text)
    return jsonify({
        "status": "success",
        "job_match": match_result
    })

@api_bp.route('/dashboard', methods=['GET'])
def api_dashboard():
    """
    GET /api/dashboard
    Returns real-time dashboard data cards and charts datasets.
    """
    user_id = current_user.id if current_user.is_authenticated else "anonymous"
    history = AnalysisRecord.get_user_history(user_id=user_id, limit=1)
    
    if history and len(history) > 0:
        latest = history[0]["full_analysis"]
    elif 'latest_analysis' in session:
        latest = session['latest_analysis']
    else:
        # Default empty/sample response
        return jsonify({
            "status": "no_data",
            "message": "No resume analysis recorded yet. Please upload a resume to view live dashboard.",
            "dashboard_cards": {
                "ats_score": 0,
                "job_match_pct": 0,
                "skill_match_pct": 0,
                "experience_match_pct": 0,
                "job_readiness_score": 0,
                "missing_skills": [],
                "resume_status": "Not Uploaded"
            }
        })
        
    scores = latest.get("scores", {})
    comp = latest.get("comprehensive", {})
    skill_gaps = latest.get("skill_gaps", {})
    status_tier = latest.get("status_tier", {})
    
    return jsonify({
        "status": "success",
        "dashboard_cards": {
            "ats_score": scores.get("ats_score", 0),
            "job_match_pct": scores.get("overall_match", 0),
            "skill_match_pct": scores.get("skills_match", 0),
            "experience_match_pct": scores.get("experience_match", 0),
            "job_readiness_score": latest.get("readiness_score", 0),
            "missing_skills": skill_gaps.get("all_missing", []),
            "resume_status": status_tier.get("tier", "Ready to Apply")
        },
        "charts": {
            "score_breakdown": comp.get("score_breakdown", {}),
            "skill_density": [cat for cat in comp.get("heatmap", {}).get("categories", [])],
            "readiness_breakdown": scores,
            "missing_skills": skill_gaps.get("all_missing", [])[:6]
        }
    })

@api_bp.route('/history', methods=['GET'])
def api_history():
    """
    GET /api/history
    Returns historical analysis records for candidate.
    """
    user_id = current_user.id if current_user.is_authenticated else "anonymous"
    records = AnalysisRecord.get_user_history(user_id=user_id, limit=20)
    return jsonify({
        "status": "success",
        "count": len(records),
        "history": records
    })

@api_bp.route('/reanalyze', methods=['POST'])
def api_reanalyze():
    """
    POST /api/reanalyze
    Compares newly uploaded resume against baseline analysis.
    """
    if 'resume' not in request.files:
        return jsonify({"error": "New resume file required for re-analysis."}), 400
        
    file = request.files['resume']
    jd_text = sanitize_input_text(request.form.get('job_description', ''))
    target_role = sanitize_input_text(request.form.get('target_role', ''))
    prev_json = request.form.get('previous_analysis', '')
    
    text, filename, err = validate_and_extract_file(file)
    if err:
        return jsonify({"error": err}), 400
        
    prev_data = {}
    if prev_json:
        try:
            prev_data = json.loads(prev_json)
        except Exception:
            pass
            
    if not prev_data:
        user_id = current_user.id if current_user.is_authenticated else "anonymous"
        history = AnalysisRecord.get_user_history(user_id=user_id, limit=1)
        if history:
            prev_data = history[0]["full_analysis"]
            
    comparison = compare_resumes(prev_data.get("recovery", prev_data), text, jd_text, target_role)
    return jsonify({
        "status": "success",
        "filename": filename,
        "comparison": comparison
    })

@api_bp.route('/rewrite-bullet', methods=['POST'])
def api_rewrite_bullet():
    data = request.get_json(silent=True) or request.form
    bullet = sanitize_input_text(data.get('bullet', ''))
    if not bullet:
        return jsonify({"error": "No bullet point text provided."}), 400
    res = rewrite_bullet_point(bullet)
    return jsonify(res)

@api_bp.route('/interview-prep', methods=['POST'])
def api_interview_prep():
    data = request.get_json(silent=True) or request.form
    skills = data.get('skills', [])
    role = sanitize_input_text(data.get('role', 'Software Engineer'))
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]
    res = generate_interview_questions(skills, role)
    return jsonify(res)

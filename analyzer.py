import re
from collections import Counter

# Comprehensive Skills Database
SKILLS_DB = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin", "scala", "r", "html", "css", "sql"
    ],
    "Web & Frameworks": [
        "react", "node.js", "node", "vue", "angular", "flask", "django", "express", "next.js", "tailwind", "bootstrap", "fastapi", "spring boot", "laravel", "asp.net"
    ],
    "Databases & Storage": [
        "sql", "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "dynamodb", "elasticsearch", "cassandra", "firebase", "snowflake"
    ],
    "Data Science & AI/ML": [
        "machine learning", "deep learning", "data analysis", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "nlp", "computer vision", "opencv", "data visualization", "power bi", "tableau"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd", "terraform", "ansible", "linux", "bash", "shell", "nginx", "prometheus", "grafana"
    ],
    "Tools & Architecture": [
        "rest api", "graphql", "microservices", "agile", "jira", "scrum", "system design", "unit testing", "pytest", "jest", "postman", "figma"
    ],
    "Leadership & Soft Skills": [
        "leadership", "team management", "project management", "communication", "problem solving", "cross-functional leadership", "mentorship", "strategic planning", "stakeholder management"
    ]
}

# Strong Action Verbs for ATS analysis
HIGH_IMPACT_VERBS = [
    "spearheaded", "engineered", "architected", "developed", "scaled", "optimized", "implemented", 
    "orchestrated", "lead", "led", "managed", "decreased", "increased", "boosted", "generated", 
    "built", "automated", "transformed", "redesigned", "pioneered", "launched", "streamlined",
    "accelerated", "designed", "created", "refactored", "deployed", "secured", "delivered"
]

WEAK_VERBS = ["responsible for", "worked on", "assisted with", "helped", "handled", "did", "tasked with"]

# Standard resume section headers
SECTION_HEADERS = {
    "summary": ["summary", "profile", "objective", "about me", "professional summary"],
    "experience": ["experience", "employment history", "work history", "professional experience", "work experience"],
    "skills": ["skills", "technical skills", "technologies", "core competencies", "expertise"],
    "education": ["education", "academic background", "qualifications", "education & certifications"],
    "projects": ["projects", "personal projects", "key projects", "academic projects"],
    "certifications": ["certifications", "licenses", "certificates", "credentials"]
}

# Predefined Career Profiles for Recommendations
CAREER_PROFILES = {
    "Full Stack Developer": {
        "required": ["javascript", "react", "node.js", "python", "html", "css", "sql", "git"],
        "recommended": ["typescript", "next.js", "docker", "mongodb", "postgresql"],
        "growth_path": ["Senior Full Stack Developer", "Tech Lead", "Engineering Manager"]
    },
    "Backend Engineer": {
        "required": ["python", "java", "sql", "rest api", "git", "postgresql", "docker"],
        "recommended": ["redis", "microservices", "aws", "kubernetes", "fastapi", "django"],
        "growth_path": ["Senior Backend Developer", "Principal Systems Architect", "Director of Engineering"]
    },
    "Data Scientist & AI Specialist": {
        "required": ["python", "sql", "pandas", "numpy", "scikit-learn", "machine learning"],
        "recommended": ["deep learning", "tensorflow", "pytorch", "nlp", "tableau", "aws"],
        "growth_path": ["Senior Data Scientist", "AI Lead Researcher", "Head of Data Science"]
    },
    "DevOps & Cloud Engineer": {
        "required": ["aws", "docker", "kubernetes", "git", "linux", "ci/cd", "bash"],
        "recommended": ["terraform", "jenkins", "ansible", "azure", "python", "prometheus"],
        "growth_path": ["Senior DevOps Engineer", "Cloud Solutions Architect", "VP of Infrastructure"]
    },
    "Frontend Specialist": {
        "required": ["javascript", "react", "html", "css", "typescript", "git"],
        "recommended": ["next.js", "tailwind", "vue", "figma", "jest", "webpack"],
        "growth_path": ["Senior Frontend Engineer", "UI Architecture Lead", "Head of Frontend"]
    }
}

def check_formatting_and_structure(text):
    """Evaluates ATS parseability, contact info presence, section headers, bullet counts."""
    text_lower = text.lower()
    
    # 1. Contact details detection
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    has_phone = bool(re.search(r'(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}', text))
    has_linkedin = "linkedin" in text_lower
    has_github = "github" in text_lower
    
    contact_score = (has_email * 30) + (has_phone * 30) + (has_linkedin * 20) + (has_github * 20)
    
    # 2. Section detection
    detected_sections = {}
    for sec_key, keywords in SECTION_HEADERS.items():
        found = any(kw in text_lower for kw in keywords)
        detected_sections[sec_key] = found
        
    found_sec_count = sum(detected_sections.values())
    structure_score = min(int((found_sec_count / len(SECTION_HEADERS)) * 100), 100)
    
    # 3. Readability & Metrics detection
    numbers_count = len(re.findall(r'\b\d+%\b|\$\d+|\b\d+\+\b|\b\d+\s?(users|clients|projects|team|percent)\b', text_lower))
    metrics_score = min(numbers_count * 20, 100)
    
    return {
        "contact_info": {
            "email": has_email,
            "phone": has_phone,
            "linkedin": has_linkedin,
            "github": has_github,
            "score": contact_score
        },
        "detected_sections": detected_sections,
        "structure_score": structure_score,
        "metrics_found": numbers_count,
        "metrics_score": metrics_score
    }

def analyze_action_verbs(text):
    """Analyzes impact verbs vs passive phrasing."""
    text_lower = text.lower()
    
    found_high_verbs = [v for v in HIGH_IMPACT_VERBS if v in text_lower]
    found_weak_verbs = [v for v in WEAK_VERBS if v in text_lower]
    
    score = min(len(found_high_verbs) * 15, 100)
    if found_weak_verbs:
        score = max(score - (len(found_weak_verbs) * 5), 10)
        
    return {
        "high_impact_verbs": found_high_verbs,
        "weak_verbs": found_weak_verbs,
        "verb_score": score
    }

def generate_heatmap_data(text):
    """Calculates visual section strength and keyword density heatmap."""
    text_lower = text.lower()
    
    heatmap_categories = []
    
    for category, skills in SKILLS_DB.items():
        found_in_cat = [s for s in skills if s in text_lower]
        density = round((len(found_in_cat) / len(skills)) * 100, 1)
        
        status = "High Impact" if density > 30 else ("Moderate" if density > 10 else "Low Density")
        heatmap_categories.append({
            "category": category,
            "count": len(found_in_cat),
            "density": density,
            "status": status,
            "skills": [s.capitalize() for s in found_in_cat]
        })
        
    fmt = check_formatting_and_structure(text)
    section_heat = [
        {"section": "Contact Information", "score": fmt["contact_info"]["score"], "status": "Strong" if fmt["contact_info"]["score"] >= 80 else "Needs Improvement"},
        {"section": "Professional Experience", "score": 90 if fmt["detected_sections"]["experience"] else 30, "status": "Strong" if fmt["detected_sections"]["experience"] else "Missing"},
        {"section": "Technical Skills", "score": 85 if fmt["detected_sections"]["skills"] else 40, "status": "Strong" if fmt["detected_sections"]["skills"] else "Missing"},
        {"section": "Education & Background", "score": 90 if fmt["detected_sections"]["education"] else 20, "status": "Strong" if fmt["detected_sections"]["education"] else "Missing"},
        {"section": "Quantifiable Metrics & Impact", "score": fmt["metrics_score"], "status": "High Impact" if fmt["metrics_score"] >= 60 else "Low Quantification"}
    ]
    
    return {
        "categories": heatmap_categories,
        "sections": section_heat
    }

def get_career_recommendations(extracted_skills_list):
    """Generates career path recommendations based on user skills."""
    user_skills_lower = set([s.lower() for s in extracted_skills_list])
    recommendations = []
    
    for role, data in CAREER_PROFILES.items():
        req_set = set(data["required"])
        matched_req = user_skills_lower.intersection(req_set)
        match_percentage = int((len(matched_req) / len(req_set)) * 100) if req_set else 0
        
        rec_skills = set(data["recommended"])
        missing_skills = list(req_set - user_skills_lower)[:4]
        
        recommendations.append({
            "role": role,
            "match_percentage": match_percentage,
            "matched_skills_count": len(matched_req),
            "missing_key_skills": [s.capitalize() for s in missing_skills],
            "growth_path": data["growth_path"]
        })
        
    recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
    return recommendations

def analyze_resume_comprehensive(text):
    """Main comprehensive resume analyzer combining all metrics."""
    text_lower = text.lower()
    found_skills = {}
    all_extracted_skills = []
    
    for category, skills in SKILLS_DB.items():
        cat_found = []
        for skill in skills:
            if skill in text_lower:
                cat_found.append(skill.capitalize())
                all_extracted_skills.append(skill)
        if cat_found:
            found_skills[category] = cat_found
            
    # Calculate Scores
    fmt_res = check_formatting_and_structure(text)
    verb_res = analyze_action_verbs(text)
    
    keyword_count = len(all_extracted_skills)
    keyword_score = min(keyword_count * 6, 100)
    format_score = (fmt_res["structure_score"] * 0.5) + (fmt_res["contact_info"]["score"] * 0.5)
    action_verb_score = verb_res["verb_score"]
    metrics_score = fmt_res["metrics_score"]
    
    # Composite ATS Score
    ats_score = int(
        (keyword_score * 0.35) + 
        (format_score * 0.25) + 
        (action_verb_score * 0.25) + 
        (metrics_score * 0.15)
    )
    ats_score = max(min(ats_score, 98), 15)
    
    # Tailored recommendations
    recommendations = []
    if ats_score < 60:
        recommendations.append("Increase technical skill keywords matching target job descriptions.")
    if not fmt_res["contact_info"]["linkedin"]:
        recommendations.append("Add your LinkedIn profile URL in the contact header for better recruiter reach.")
    if fmt_res["metrics_found"] < 3:
        recommendations.append("Quantify achievements using metrics (e.g. 'Increased speed by 35%', 'Managed $50K budget').")
    if len(verb_res["high_impact_verbs"]) < 4:
        recommendations.append("Replace passive phrases with strong action verbs like 'Spearheaded', 'Architected', 'Engineered'.")
    if not fmt_res["detected_sections"]["summary"]:
        recommendations.append("Add a concise Professional Summary section at the top of your resume.")
        
    heatmap = generate_heatmap_data(text)
    career_recs = get_career_recommendations(all_extracted_skills)
    
    return {
        "ats_score": ats_score,
        "score_breakdown": {
            "keywords": int(keyword_score),
            "formatting": int(format_score),
            "action_verbs": int(action_verb_score),
            "impact_metrics": int(metrics_score)
        },
        "skills": found_skills,
        "all_skills": [s.capitalize() for s in all_extracted_skills],
        "formatting_details": fmt_res,
        "verb_details": verb_res,
        "recommendations": recommendations,
        "heatmap": heatmap,
        "career_recommendations": career_recs
    }

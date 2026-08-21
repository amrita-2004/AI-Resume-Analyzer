import re
import math
from collections import Counter
from analyzer import SKILLS_DB

def extract_keywords_from_text(text):
    """Extracts known tech skills and key industry terms from text."""
    text_lower = text.lower()
    words = set(re.findall(r'\b[a-z0-9\.\+#]+\b', text_lower))
    
    extracted_skills = []
    for cat, skills in SKILLS_DB.items():
        for skill in skills:
            if skill.lower() in text_lower:
                extracted_skills.append(skill)
                
    return list(set(extracted_skills)), words

def compute_pure_tfidf_similarity(text1, text2):
    """Pure Python TF-IDF Cosine Similarity engine (lightweight & fast for Vercel)."""
    words1 = re.findall(r'\b[a-z0-9\.\+#]+\b', text1.lower())
    words2 = re.findall(r'\b[a-z0-9\.\+#]+\b', text2.lower())
    
    if not words1 or not words2:
        return 0
        
    vec1 = Counter(words1)
    vec2 = Counter(words2)
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0
    return int((float(numerator) / denominator) * 100 * 2.2)

def calculate_jd_match(resume_text, jd_text):
    """Calculates TF-IDF similarity and keyword overlap between Resume & Job Description."""
    if not jd_text or not jd_text.strip():
        return None
        
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    
    # Extract skills
    resume_skills, resume_words = extract_keywords_from_text(resume_lower)
    jd_skills, jd_words = extract_keywords_from_text(jd_lower)
    
    # 1. Similarity Calculation using pure Python TF-IDF engine
    similarity_score = min(max(compute_pure_tfidf_similarity(resume_lower, jd_lower), 10), 95)
    
    # 2. Skill Gap & Keyword Analysis
    resume_skills_set = set([s.lower() for s in resume_skills])
    jd_skills_set = set([s.lower() for s in jd_skills])
    
    matched_skills = [s.capitalize() for s in jd_skills_set.intersection(resume_skills_set)]
    missing_skills = [s.capitalize() for s in jd_skills_set - resume_skills_set]
    
    # Composite match percentage
    skill_overlap_ratio = len(matched_skills) / max(len(jd_skills_set), 1)
    composite_match = int((similarity_score * 0.4) + (skill_overlap_ratio * 100 * 0.6))
    composite_match = max(min(composite_match, 98), 10)
    
    # 3. Categorized Skill Gap
    strong_matches = matched_skills
    partial_matches = [s.capitalize() for s in resume_skills_set - jd_skills_set][:5]
    critical_missing = missing_skills[:6]
    
    # 4. Learning & Skill Roadmap
    roadmap = []
    for skill in critical_missing:
        roadmap.append({
            "skill": skill,
            "priority": "High Priority",
            "action": f"Build a practical project or complete target course covering {skill}.",
            "estimated_time": "1 - 2 weeks"
        })
        
    return {
        "match_percentage": composite_match,
        "similarity_score": similarity_score,
        "matched_keywords": matched_skills,
        "missing_keywords": missing_skills,
        "skill_gap": {
            "strong_match": strong_matches,
            "partial_skills": partial_matches,
            "critical_missing": critical_missing
        },
        "roadmap": roadmap
    }

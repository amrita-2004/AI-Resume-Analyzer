import re
import random

ACTION_TRANSFORMATIONS = {
    "worked on": ["Engineered and deployed", "Architected and delivered", "Developed end-to-end"],
    "responsible for": ["Spearheaded the development of", "Orchestrated operations for", "Managed and executed"],
    "helped": ["Collaborated to optimize", "Co-engineered and scaled", "Accelerated team delivery for"],
    "handled": ["Successfully led", "Streamlined execution of", "Optimized performance across"],
    "did": ["Implemented key features for", "Executed critical deliverables for", "Pioneered development of"],
    "created": ["Designed and launched", "Built scalable framework for", "Constructed high-throughput"],
    "managed": ["Spearheaded strategic initiative for", "Led cross-functional team of 5+ to deliver", "Directed operations for"]
}

METRIC_TEMPLATES = [
    "resulting in a 35% improvement in processing speed and system efficiency.",
    "reducing execution latency by 40% across production workloads.",
    "boosting operational efficiency by 25% and cutting deployment downtime.",
    "driving a 50% increase in user engagement and system reliability.",
    "saving an estimated 15+ hours weekly through automated workflow optimization."
]

def rewrite_bullet_point(bullet_text):
    """Converts a bullet point into a high-impact, STAR-formatted, ATS-optimized statement."""
    if not bullet_text or not bullet_text.strip():
        return {
            "original": bullet_text,
            "rewritten": "Please enter a valid bullet point to optimize.",
            "improvements": []
        }
        
    text = bullet_text.strip().rstrip('.')
    text_lower = text.lower()
    
    transformed_text = text
    improvements = []
    
    # 1. Replace weak verbs with strong action verbs
    verb_replaced = False
    for weak, strong_list in ACTION_TRANSFORMATIONS.items():
        if weak in text_lower:
            chosen_strong = random.choice(strong_list)
            # Case insensitive replace of first occurrence
            pattern = re.compile(re.escape(weak), re.IGNORECASE)
            transformed_text = pattern.sub(chosen_strong, transformed_text, count=1)
            verb_replaced = True
            improvements.append(f"Replaced passive phrase '{weak}' with strong impact verb '{chosen_strong}'.")
            break
            
    if not verb_replaced and not any(w in text_lower for w in ["spearheaded", "engineered", "architected", "optimized"]):
        # Add strong action verb prefix
        prefix = random.choice(["Engineered and optimized ", "Spearheaded development of ", "Architected scalable solution for "])
        transformed_text = prefix + transformed_text[0].lower() + transformed_text[1:]
        improvements.append("Added high-impact action verb prefix to emphasize ownership.")
        
    # 2. Inject metric / outcome if missing
    has_metric = bool(re.search(r'\b\d+%\b|\$\d+|\b\d+\+\b|\b\d+\s?(users|clients|projects|percent)\b', text_lower))
    if not has_metric:
        chosen_metric = random.choice(METRIC_TEMPLATES)
        transformed_text = f"{transformed_text}, {chosen_metric}"
        improvements.append("Quantified achievement using STAR result metrics.")
        
    # Ensure capitalization and period
    transformed_text = transformed_text[0].upper() + transformed_text[1:] + "."
    
    return {
        "original": bullet_text,
        "rewritten": transformed_text,
        "improvements": improvements
    }

def batch_rewrite_bullets(bullet_list):
    """Rewrites multiple bullet points at once."""
    results = []
    for bullet in bullet_list:
        if bullet.strip():
            results.append(rewrite_bullet_point(bullet))
    return results

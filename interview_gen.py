import random

TECH_QUESTION_BANK = {
    "python": [
        {
            "question": "How do Python memory management and garbage collection work under the hood?",
            "category": "Core Python",
            "key_points": ["Reference counting", "Generational garbage collection (gc module)", "Cyclic garbage collection", "Global Interpreter Lock (GIL) impact"]
        },
        {
            "question": "Explain the difference between deep copy and shallow copy in Python.",
            "category": "Core Python",
            "key_points": ["copy.copy vs copy.deepcopy", "Nested objects reference handling", "Mutable vs immutable objects"]
        }
    ],
    "javascript": [
        {
            "question": "Explain the JavaScript Event Loop, Microtask Queue, and Macrotask Queue.",
            "category": "Frontend Architecture",
            "key_points": ["Call stack execution", "Promises & process.nextTick in microtasks", "setTimeout/setInterval in macrotasks", "Non-blocking I/O"]
        }
    ],
    "react": [
        {
            "question": "How does React's Virtual DOM reconciliation (Fiber architecture) work?",
            "category": "React Ecosystem",
            "key_points": ["Diffing algorithm", "Key prop importance", "State batching", "Component rerender triggers"]
        }
    ],
    "sql": [
        {
            "question": "What is the difference between WHERE and HAVING in SQL, and how do database indexes work?",
            "category": "Database Engineering",
            "key_points": ["WHERE filters raw rows before aggregation", "HAVING filters aggregated groups", "B-Tree vs Hash indexes", "Index scan vs table scan"]
        }
    ],
    "aws": [
        {
            "question": "How would you design a highly available, fault-tolerant microservices architecture on AWS?",
            "category": "Cloud Architecture",
            "key_points": ["ECS / EKS container orchestration", "ALB load balancing", "Multi-AZ RDS deployments", "CloudFront CDN & S3"]
        }
    ],
    "docker": [
        {
            "question": "What are multi-stage Docker builds and how do they optimize container image size?",
            "category": "DevOps",
            "key_points": ["Separating build environment from runtime", "Minimizing attack surface", "Reducing image footprint from GB to MB"]
        }
    ],
    "machine learning": [
        {
            "question": "How do you detect and mitigate overfitting in deep learning models?",
            "category": "AI / ML Engineering",
            "key_points": ["L1/L2 Regularization", "Dropout layers", "Early stopping", "Data augmentation", "Cross-validation"]
        }
    ]
}

BEHAVIORAL_QUESTIONS = [
    {
        "question": "Tell me about a time you faced a critical production bug or technical obstacle. How did you resolve it?",
        "framework": "STAR (Situation, Task, Action, Result)",
        "key_points": ["Context & root cause analysis", "Immediate mitigation vs long-term fix", "Post-mortem & monitoring added"]
    },
    {
        "question": "Describe a scenario where you had a conflict with a teammate or stakeholder over technical design.",
        "framework": "STAR",
        "key_points": ["Objective evaluation of trade-offs", "Data-driven proof/prototyping", "Reaching alignment & team success"]
    },
    {
        "question": "How do you prioritize technical debt versus building new product features under tight deadlines?",
        "framework": "STAR",
        "key_points": ["Impact vs Effort matrix", "Communicating business risk to stakeholders", "Refactoring in incremental sprints"]
    }
]

def generate_interview_questions(extracted_skills, role_title="Software Engineer"):
    """Generates technical, behavioral, and resume-tailored interview questions."""
    skills_lower = [s.lower() for s in extracted_skills]
    
    technical_qs = []
    
    # Match skills to question bank
    for skill, q_list in TECH_QUESTION_BANK.items():
        if any(skill in s for s in skills_lower):
            technical_qs.extend(q_list)
            
    if not technical_qs:
        # Fallback technical questions
        technical_qs = [
            {
                "question": f"What are the core design patterns and architectural principles you follow as a {role_title}?",
                "category": "System Architecture",
                "key_points": ["SOLID principles", "Clean code practices", "Modularity & separation of concerns"]
            },
            {
                "question": "How do you write effective unit and integration tests for your codebase?",
                "category": "Software Quality",
                "key_points": ["Mocking external dependencies", "Test coverage goals", "CI/CD integration"]
            }
        ]
        
    # Sample random selection of technical questions
    selected_tech = random.sample(technical_qs, min(len(technical_qs), 4))
    selected_behavioral = random.sample(BEHAVIORAL_QUESTIONS, min(len(BEHAVIORAL_QUESTIONS), 2))
    
    # Resume Probing questions based on top skills
    top_skills_str = ", ".join([s.capitalize() for s in extracted_skills[:3]]) if extracted_skills else "software engineering"
    resume_probing = [
        {
            "question": f"I noticed experience with {top_skills_str}. Can you walk me through the most complex project where you utilized these technologies?",
            "category": "Resume Deep-Dive",
            "key_points": ["Architecture decisions", "Challenges faced", "Quantifiable business impact"]
        },
        {
            "question": "If you had to rewrite your recent project today, what architecture or performance choices would you change?",
            "category": "Resume Deep-Dive",
            "key_points": ["Reflection on trade-offs", "Lessons learned", "Modern alternative tools"]
        }
    ]
    
    return {
        "technical_questions": selected_tech,
        "behavioral_questions": selected_behavioral,
        "resume_probing_questions": resume_probing
    }

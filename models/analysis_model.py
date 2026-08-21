import uuid
from datetime import datetime
from models.db import HAS_MONGODB, get_db, local_db

class AnalysisRecord:
    def __init__(self, record_data):
        self.id = record_data.get("id") or str(uuid.uuid4())
        self.user_id = record_data.get("user_id") or "anonymous"
        self.filename = record_data.get("filename", "resume.pdf")
        self.target_role = record_data.get("target_role", "Software Engineer")
        self.ats_score = record_data.get("ats_score", 0)
        self.readiness_score = record_data.get("readiness_score", 0)
        self.status_tier = record_data.get("status_tier", {})
        self.scores = record_data.get("scores", {})
        self.skills = record_data.get("skills", {})
        self.missing_skills = record_data.get("missing_skills", [])
        self.created_at = record_data.get("created_at") or datetime.utcnow().isoformat()
        self.full_analysis = record_data.get("full_analysis", {})

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "target_role": self.target_role,
            "ats_score": self.ats_score,
            "readiness_score": self.readiness_score,
            "status_tier": self.status_tier,
            "scores": self.scores,
            "skills": self.skills,
            "missing_skills": self.missing_skills,
            "created_at": self.created_at,
            "full_analysis": self.full_analysis
        }

    def save(self):
        db_instance = get_db()
        data = self.to_dict()
        if HAS_MONGODB:
            db_instance.analyses.insert_one(data)
        else:
            local_db.save_analysis(data)
        return data

    @classmethod
    def get_user_history(cls, user_id=None, limit=20):
        db_instance = get_db()
        if HAS_MONGODB:
            query = {"user_id": user_id} if user_id else {}
            cursor = db_instance.analyses.find(query).sort("created_at", -1).limit(limit)
            return [cls(doc).to_dict() for doc in cursor]
        else:
            return local_db.get_user_analyses(user_id=user_id, limit=limit)

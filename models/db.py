import os
import json
import time
from datetime import datetime

IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

# Try PyMongo connection
try:
    from pymongo import MongoClient
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/ai_resume_analyzer")
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
    mongo_client.admin.command('ping')
    db = mongo_client.get_database()
    HAS_MONGODB = True
    print("[Database] Connected successfully to MongoDB.")
except Exception as e:
    HAS_MONGODB = False
    print(f"[Database] MongoDB connection unavailable ({e}). Using memory storage.")

# Fallback Memory/JSON Storage Engine
class LocalDocumentStore:
    def __init__(self, filename="storage.json"):
        if IS_VERCEL:
            self.filename = os.path.join("/tmp", filename)
        else:
            self.filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        self.data = {"users": {}, "analyses": []}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
        except Exception as e:
            print(f"[Storage] Could not load local storage: {e}")

    def _save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            # On read-only filesystems, proceed without crashing
            print(f"[Storage Warning] Read-only storage notice: {e}")

    def find_user_by_email(self, email):
        return self.data["users"].get(email.lower())

    def find_user_by_id(self, user_id):
        for email, user in self.data["users"].items():
            if user.get("id") == user_id:
                return user
        return None

    def save_user(self, user_dict):
        email = user_dict.get("email", "").lower()
        if email:
            self.data["users"][email] = user_dict
            self._save()
        return user_dict

    def save_analysis(self, analysis_dict):
        self.data["analyses"].insert(0, analysis_dict)
        self.data["analyses"] = self.data["analyses"][:100]
        self._save()
        return analysis_dict

    def get_user_analyses(self, user_id=None, limit=20):
        if not user_id:
            return self.data["analyses"][:limit]
        results = [a for a in self.data["analyses"] if a.get("user_id") == user_id]
        return results[:limit]

local_db = LocalDocumentStore()

def get_db():
    if HAS_MONGODB:
        return db
    return local_db

import uuid
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import HAS_MONGODB, get_db, local_db

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get("id") or str(uuid.uuid4())
        self.email = user_data.get("email", "").lower()
        self.password_hash = user_data.get("password_hash", "")
        self.totp_secret = user_data.get("totp_secret", "")
        self.is_2fa_enabled = user_data.get("is_2fa_enabled", False)
        self.failed_attempts = user_data.get("failed_attempts", 0)
        self.lockout_until = user_data.get("lockout_until", None)
        self.created_at = user_data.get("created_at") or datetime.utcnow().isoformat()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "password_hash": self.password_hash,
            "totp_secret": self.totp_secret,
            "is_2fa_enabled": self.is_2fa_enabled,
            "failed_attempts": self.failed_attempts,
            "lockout_until": self.lockout_until,
            "created_at": self.created_at
        }

    def save(self):
        db_instance = get_db()
        data = self.to_dict()
        if HAS_MONGODB:
            db_instance.users.update_one({"email": self.email}, {"$set": data}, upsert=True)
        else:
            local_db.save_user(data)

    @classmethod
    def get_by_email(cls, email):
        if not email:
            return None
        email = email.lower()
        db_instance = get_db()
        if HAS_MONGODB:
            data = db_instance.users.find_one({"email": email})
        else:
            data = local_db.find_user_by_email(email)
        return cls(data) if data else None

    @classmethod
    def get_by_id(cls, user_id):
        if not user_id:
            return None
        db_instance = get_db()
        if HAS_MONGODB:
            data = db_instance.users.find_one({"id": user_id})
        else:
            data = local_db.find_user_by_id(user_id)
        return cls(data) if data else None

    @classmethod
    def create_user(cls, email, password):
        if cls.get_by_email(email):
            return None, "User with this email already exists."
        user = cls({
            "id": str(uuid.uuid4()),
            "email": email.lower(),
            "created_at": datetime.utcnow().isoformat()
        })
        user.set_password(password)
        user.save()
        return user, None

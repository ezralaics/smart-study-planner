import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, GUID

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    student_type = db.Column(db.String(20), default='Other')
    role = db.Column(db.String(20), default='student', index=True, nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    avatar_url = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    courses = db.relationship('Course', backref='student', lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")
    schedules = db.relationship('Schedule', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password):
        """Hashes the password securely with Werkzeug."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verifies password. If stored password is legacy plaintext, auto-upgrades to hash."""
        if self.password.startswith(('scrypt:', 'pbkdf2:', 'bcrypt$')):
            return check_password_hash(self.password, raw_password)
        # Backward compatibility: legacy plaintext password match
        if self.password == raw_password:
            self.set_password(raw_password)
            from flask import has_app_context
            if has_app_context():
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
            return True
        return False

    def to_dict(self):
        return {
            "id": str(self.id) if self.id else None,
            "fullname": self.fullname,
            "username": self.username,
            "email": self.email,
            "student_type": self.student_type,
            "role": self.role,
            "avatar_url": self.avatar_url,
            "is_google_user": bool(self.google_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

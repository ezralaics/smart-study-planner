from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    student_type = db.Column(db.String(20), default='Other')
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    courses = db.relationship('Course', backref='student', lazy=True, cascade="all, delete-orphan")
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
            "id": self.id,
            "fullname": self.fullname,
            "username": self.username,
            "email": self.email,
            "student_type": self.student_type,
            "role": self.role
        }

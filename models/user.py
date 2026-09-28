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
    education_level = db.Column(db.String(20), default='university', nullable=False, index=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    avatar_url = db.Column(db.String(255), nullable=True)

    # General Profile Fields
    is_profile_completed = db.Column(db.Boolean, default=False, nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # Role-Specific: Student Metadata
    major_programme = db.Column(db.String(100), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    current_semester = db.Column(db.String(20), nullable=True)
    target_cgpa = db.Column(db.Float, nullable=True)

    # Role-Specific: Educator Metadata
    faculty_department = db.Column(db.String(100), nullable=True)
    office_location = db.Column(db.String(100), nullable=True)
    title_designation = db.Column(db.String(50), nullable=True)

    # Role-Specific: Administrator Metadata
    admin_department = db.Column(db.String(100), nullable=True)
    staff_id = db.Column(db.String(50), nullable=True)

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
            "education_level": self.education_level or 'university',
            "avatar_url": self.avatar_url,
            "is_profile_completed": self.is_profile_completed,
            "phone_number": self.phone_number,
            "bio": self.bio,
            "major_programme": self.major_programme,
            "academic_year": self.academic_year,
            "current_semester": self.current_semester,
            "target_cgpa": self.target_cgpa,
            "faculty_department": self.faculty_department,
            "office_location": self.office_location,
            "title_designation": self.title_designation,
            "admin_department": self.admin_department,
            "staff_id": self.staff_id,
            "is_google_user": bool(self.google_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

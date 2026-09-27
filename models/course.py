import uuid
from datetime import datetime, timezone
from extensions import db, GUID

class Course(db.Model):
    __tablename__ = 'courses'
    __table_args__ = (
        db.Index('ix_courses_user_completed', 'user_id', 'is_completed'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    course_name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20)) 
    credits = db.Column(db.Integer, default=3)
    target_grade = db.Column(db.Float, default=80.0)
    actual_grade = db.Column(db.String(5), nullable=True) 
    is_completed = db.Column(db.Boolean, default=False, nullable=False) 

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    tasks = db.relationship('Task', backref='course', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id) if self.id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "name": self.course_name,
            "semester": self.semester,
            "credits": self.credits,
            "target_grade": self.target_grade,
            "actual_grade": self.actual_grade,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tasks": [
                {
                    "id": str(t.id) if t.id else None,
                    "name": t.task_name,
                    "weight": float(t.weightage) if t.weightage else 0,
                    "deadline": str(t.due_date) if t.due_date else None
                } for t in self.tasks
            ]
        }

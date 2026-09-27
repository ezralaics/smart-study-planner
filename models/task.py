import uuid
from datetime import datetime, timezone
from extensions import db, GUID

class Task(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = (
        db.Index('ix_tasks_user_due_completed', 'user_id', 'due_date', 'is_completed'),
        db.Index('ix_tasks_course_due', 'course_id', 'due_date'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = db.Column(GUID(), db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=True, index=True) 
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True) 
    task_name = db.Column(db.String(100), nullable=False)
    weightage = db.Column(db.Numeric(5, 2), default=0)
    due_date = db.Column(db.Date, index=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    category = db.Column(db.String(50), default='Academic Task') 
    marks_obtained = db.Column(db.Numeric(5, 2), nullable=True) 

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        course_name = self.course.course_name.split('—')[0].strip() if self.course else "General"
        
        cat = "Other Task"
        if self.weightage and self.weightage > 0:
            cat = "Component"
        elif self.category == 'Academic Task' or self.course_id:
            cat = "Academic Task"
            
        if self.category == 'Other Task' and not self.course_id:
            cat = "Other Task"

        return {
            "id": str(self.id) if self.id else None,
            "course_id": str(self.course_id) if self.course_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "course_name": course_name,
            "task_name": self.task_name,
            "weightage": float(self.weightage) if self.weightage else 0,
            "due_date": str(self.due_date) if self.due_date else "",
            "is_completed": self.is_completed,
            "category": cat,
            "marks_obtained": float(self.marks_obtained) if self.marks_obtained is not None else None,
            "course_is_completed": self.course.is_completed if self.course else False,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

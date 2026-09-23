from datetime import datetime
from extensions import db

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20)) 
    credits = db.Column(db.Integer, default=3)
    target_grade = db.Column(db.Float, default=80.0)
    actual_grade = db.Column(db.String(5), nullable=True) 
    is_completed = db.Column(db.Boolean, default=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = db.relationship('Task', backref='course', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.course_name,
            "semester": self.semester,
            "credits": self.credits,
            "target_grade": self.target_grade,
            "actual_grade": self.actual_grade,
            "is_completed": self.is_completed,
            "tasks": [
                {
                    "name": t.task_name,
                    "weight": float(t.weightage) if t.weightage else 0,
                    "deadline": str(t.due_date) if t.due_date else None
                } for t in self.tasks
            ]
        }

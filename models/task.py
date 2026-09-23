from datetime import datetime
from extensions import db

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    task_name = db.Column(db.String(100), nullable=False)
    weightage = db.Column(db.Numeric(5, 2), default=0)
    due_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), default='Academic Task') 
    marks_obtained = db.Column(db.Numeric(5, 2), nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
            "id": self.id,
            "course_id": self.course_id,
            "course_name": course_name,
            "task_name": self.task_name,
            "weightage": float(self.weightage) if self.weightage else 0,
            "due_date": str(self.due_date) if self.due_date else "",
            "is_completed": self.is_completed,
            "category": cat,
            "marks_obtained": float(self.marks_obtained) if self.marks_obtained is not None else None,
            "course_is_completed": self.course.is_completed if self.course else False 
        }

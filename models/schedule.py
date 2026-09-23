from datetime import datetime
from extensions import db

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), default='Class') 
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False, default="09:00")
    venue = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    details = db.Column(db.Text, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "activity_type": self.activity_type,
            "day": self.day_of_week,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "venue": self.venue,
            "details": self.details,
            "start_date": str(self.start_date) if self.start_date else "", 
            "end_date": str(self.end_date) if self.end_date else ""
        }

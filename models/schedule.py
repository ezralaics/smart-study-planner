import uuid
from datetime import datetime, timezone
from extensions import db, GUID

class Schedule(db.Model):
    __tablename__ = 'schedules'
    __table_args__ = (
        db.Index('ix_schedules_user_day', 'user_id', 'day_of_week'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), default='Class') 
    day_of_week = db.Column(db.String(20), nullable=False, index=True)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False, default="09:00")
    venue = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    details = db.Column(db.Text, nullable=True) 

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id) if self.id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "title": self.title,
            "activity_type": self.activity_type,
            "day": self.day_of_week,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "venue": self.venue,
            "details": self.details,
            "start_date": str(self.start_date) if self.start_date else "", 
            "end_date": str(self.end_date) if self.end_date else "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

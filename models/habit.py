import uuid
from datetime import datetime, date, timezone
from extensions import db, GUID

class Habit(db.Model):
    __tablename__ = 'habits'
    __table_args__ = (
        db.Index('ix_habits_user_category', 'user_id', 'category'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    category = db.Column(db.String(50), default='general', nullable=False)  # health, learning, mindfulness, fitness, general
    frequency = db.Column(db.String(20), default='daily', nullable=False)   # daily, weekdays, weekly
    target_days_per_week = db.Column(db.Integer, default=7, nullable=False)
    streak_count = db.Column(db.Integer, default=0, nullable=False)
    icon = db.Column(db.String(50), default='bi-check2-circle', nullable=False)
    color = db.Column(db.String(20), default='#198754', nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    logs = db.relationship('HabitLog', backref='habit', cascade='all, delete-orphan', lazy=True)

    def to_dict(self, today_completed=None):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'frequency': self.frequency,
            'target_days_per_week': self.target_days_per_week,
            'streak_count': self.streak_count,
            'icon': self.icon,
            'color': self.color,
            'is_archived': self.is_archived,
            'today_completed': today_completed if today_completed is not None else False,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class HabitLog(db.Model):
    __tablename__ = 'habit_logs'
    __table_args__ = (
        db.Index('ix_habit_logs_habit_date', 'habit_id', 'log_date', unique=True),
        db.Index('ix_habit_logs_user_date', 'user_id', 'log_date'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    habit_id = db.Column(GUID(), db.ForeignKey('habits.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, default=date.today)
    is_completed = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'habit_id': str(self.habit_id),
            'user_id': str(self.user_id),
            'log_date': self.log_date.isoformat() if self.log_date else None,
            'is_completed': self.is_completed,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

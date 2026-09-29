import uuid
from datetime import datetime, date, timezone
from extensions import db, GUID

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    __table_args__ = (
        db.Index('ix_job_apps_user_status', 'user_id', 'status'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    company_name = db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default='wishlist', nullable=False)  # wishlist, applied, interviewing, offer, rejected
    location = db.Column(db.String(100), nullable=True)
    workplace_type = db.Column(db.String(30), default='hybrid', nullable=True)  # remote, on-site, hybrid
    salary_range = db.Column(db.String(100), nullable=True)
    job_url = db.Column(db.String(300), nullable=True)
    applied_date = db.Column(db.Date, nullable=True)
    deadline_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='medium', nullable=False)  # high, medium, low

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'company_name': self.company_name,
            'job_title': self.job_title,
            'status': self.status,
            'location': self.location,
            'workplace_type': self.workplace_type,
            'salary_range': self.salary_range,
            'job_url': self.job_url,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'deadline_date': self.deadline_date.isoformat() if self.deadline_date else None,
            'notes': self.notes,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

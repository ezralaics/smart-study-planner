import uuid
from datetime import datetime, date, timezone
from extensions import db, GUID

class UserInterestSource(db.Model):
    __tablename__ = 'user_interest_sources'
    __table_args__ = (
        db.Index('ix_interest_sources_user_cat', 'user_id', 'category'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    source_url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='general')  # finance, technology, sports, world_news, general
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'source_url': self.source_url,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DigestReport(db.Model):
    __tablename__ = 'digest_reports'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'report_type', 'report_date', name='uq_user_report_date_type'),
        db.Index('ix_digest_reports_user_date', 'user_id', 'report_date'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    report_type = db.Column(db.String(20), nullable=False, default='daily')  # 'daily', 'weekly'
    report_date = db.Column(db.Date, nullable=False, default=date.today)
    title = db.Column(db.String(200), nullable=False)
    summary_content = db.Column(db.Text, nullable=False)
    reading_time_mins = db.Column(db.Integer, default=3, nullable=False)
    source_citations = db.Column(db.JSON, default=list, nullable=False)  # Array of {title, url, snippet, category}
    email_sent = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'report_type': self.report_type,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'title': self.title,
            'summary_content': self.summary_content,
            'reading_time_mins': self.reading_time_mins,
            'source_citations': self.source_citations or [],
            'email_sent': self.email_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

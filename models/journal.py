import uuid
from datetime import datetime, date, timezone
from extensions import db, GUID

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    __table_args__ = (
        db.Index('ix_journal_user_date', 'user_id', 'entry_date'),
        db.Index('ix_journal_user_mood', 'user_id', 'mood'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(20), default='good', nullable=False)  # great, good, neutral, bad, stressed
    tags = db.Column(db.String(200), nullable=True)  # comma-separated e.g. "academics,goals,family"
    entry_date = db.Column(db.Date, nullable=False, default=date.today)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'title': self.title,
            'content': self.content,
            'mood': self.mood,
            'tags': [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else [],
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'is_pinned': self.is_pinned,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

import uuid
from datetime import datetime, timezone
from extensions import db, GUID

class Document(db.Model):
    __tablename__ = 'documents'
    __table_args__ = (
        db.Index('ix_documents_user_created', 'user_id', 'created_at'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = db.Column(GUID(), db.ForeignKey('courses.id', ondelete='SET NULL'), nullable=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=False, default='document')
    file_size = db.Column(db.Integer, default=0)
    extracted_text = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    course = db.relationship('Course', backref=db.backref('documents', lazy=True))

    def to_dict(self, include_text=False):
        word_count = len(self.extracted_text.split()) if self.extracted_text else 0
        data = {
            "id": str(self.id) if self.id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "course_id": str(self.course_id) if self.course_id else None,
            "course_name": self.course.course_name if self.course else "General Knowledge Base",
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "word_count": word_count,
            "summary": self.summary or (self.extracted_text[:200] + "..." if self.extracted_text and len(self.extracted_text) > 200 else self.extracted_text),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_text:
            data["extracted_text"] = self.extracted_text or ""
        return data

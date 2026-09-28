import uuid
from datetime import datetime, timezone
from extensions import db, GUID

class DirectMessage(db.Model):
    __tablename__ = 'direct_messages'
    __table_args__ = (
        db.Index('ix_dm_sender_recipient', 'sender_id', 'recipient_id', 'created_at'),
        db.Index('ix_dm_recipient_unread', 'recipient_id', 'is_read'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    sender_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_direct_messages', cascade='all, delete-orphan', lazy='dynamic'))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('received_direct_messages', cascade='all, delete-orphan', lazy='dynamic'))

    def to_dict(self, current_user_id=None):
        return {
            "id": str(self.id),
            "sender_id": str(self.sender_id),
            "recipient_id": str(self.recipient_id),
            "sender_name": self.sender.fullname if self.sender else "Unknown",
            "sender_email": self.sender.email if self.sender else "",
            "sender_avatar": self.sender.avatar_url if self.sender else None,
            "recipient_name": self.recipient.fullname if self.recipient else "Unknown",
            "recipient_email": self.recipient.email if self.recipient else "",
            "recipient_avatar": self.recipient.avatar_url if self.recipient else None,
            "content": self.content,
            "is_read": self.is_read,
            "is_mine": str(self.sender_id) == str(current_user_id) if current_user_id else False,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "timestamp_formatted": self.created_at.strftime('%b %d, %H:%M') if self.created_at else ""
        }

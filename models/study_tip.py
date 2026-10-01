import uuid
from datetime import datetime, date, timezone
from extensions import db, GUID

class StudyTip(db.Model):
    __tablename__ = 'study_tips'
    __table_args__ = (
        db.Index('ix_study_tips_user_date', 'user_id', 'tip_date'),
        db.Index('ix_study_tips_category', 'category'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    tip_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    category = db.Column(db.String(50), nullable=False, default='active_recall')
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    action_item = db.Column(db.String(255), nullable=False)
    source_reference = db.Column(db.String(100), nullable=True)
    is_ai_generated = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    interactions = db.relationship('UserTipInteraction', backref='tip', cascade='all, delete-orphan', lazy=True)

    def to_dict(self, interaction=None):
        data = {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'tip_date': self.tip_date.isoformat() if self.tip_date else None,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'action_item': self.action_item,
            'source_reference': self.source_reference,
            'is_ai_generated': self.is_ai_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_bookmarked': False,
            'reaction': None
        }
        if interaction:
            data['is_bookmarked'] = bool(interaction.is_bookmarked)
            data['reaction'] = interaction.reaction
        return data


class UserTipInteraction(db.Model):
    __tablename__ = 'user_tip_interactions'
    __table_args__ = (
        db.Index('ix_user_tip_unique', 'user_id', 'tip_id', unique=True),
        db.Index('ix_user_tip_bookmarked', 'user_id', 'is_bookmarked'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    tip_id = db.Column(GUID(), db.ForeignKey('study_tips.id', ondelete='CASCADE'), nullable=False, index=True)
    is_bookmarked = db.Column(db.Boolean, default=False, nullable=False)
    reaction = db.Column(db.String(20), nullable=True)  # 'helpful', 'unhelpful', 'neutral'
    interacted_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'tip_id': str(self.tip_id),
            'is_bookmarked': self.is_bookmarked,
            'reaction': self.reaction,
            'interacted_at': self.interacted_at.isoformat() if self.interacted_at else None
        }

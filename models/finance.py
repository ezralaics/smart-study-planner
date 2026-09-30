import uuid
from datetime import datetime, date, timezone
from extensions import db, GUID

class BudgetGoal(db.Model):
    __tablename__ = 'budget_goals'
    __table_args__ = (
        db.Index('ix_budget_goals_user_month', 'user_id', 'month_year', unique=True),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    month_year = db.Column(db.String(7), nullable=False)  # 'YYYY-MM', e.g. '2026-09'
    monthly_budget_limit = db.Column(db.Float, default=1000.0, nullable=False)
    savings_target = db.Column(db.Float, default=200.0, nullable=False)
    currency_symbol = db.Column(db.String(10), default='$', nullable=False)
    notes = db.Column(db.String(250), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'month_year': self.month_year,
            'monthly_budget_limit': round(self.monthly_budget_limit, 2),
            'savings_target': round(self.savings_target, 2),
            'currency_symbol': self.currency_symbol,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = (
        db.Index('ix_transactions_user_date', 'user_id', 'transaction_date'),
        db.Index('ix_transactions_user_type_cat', 'user_id', 'type', 'category'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False, default='expense')  # 'expense', 'income'
    category = db.Column(db.String(50), nullable=False, default='general')  # food, transport, books, entertainment, bills, tuition, income
    description = db.Column(db.String(200), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(50), default='card', nullable=True)  # card, cash, transfer

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'amount': round(self.amount, 2),
            'type': self.type,
            'category': self.category,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

from models.financial_account import FinancialAccount, FinancialTransaction

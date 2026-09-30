import uuid
from datetime import datetime, date, timezone
from extensions import db, GUID

class FinancialAccount(db.Model):
    __tablename__ = 'financial_accounts'
    __table_args__ = (
        db.Index('ix_fin_accounts_user_category', 'user_id', 'account_category'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    institution_name = db.Column(db.String(100), nullable=False)  # e.g. 'Touch n Go eWallet', 'Maybank', 'myASNB', 'Moomoo'
    account_category = db.Column(db.String(50), nullable=False)   # 'ewallet', 'bank_savings', 'investment_unit_trust', 'investment_stocks', 'credit_debt'
    account_nickname = db.Column(db.String(100), nullable=False)  # e.g. "Main Spending eWallet", "Emergency Fund"
    account_number_masked = db.Column(db.String(50), nullable=True) # e.g. "•••• 4821"
    current_balance = db.Column(db.Numeric(14, 2), default=0.00, nullable=False)
    currency = db.Column(db.String(3), default='MYR', nullable=False)
    last_synced_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    transactions = db.relationship('FinancialTransaction', backref='account', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id) if self.id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "institution_name": self.institution_name,
            "account_category": self.account_category,
            "account_nickname": self.account_nickname,
            "account_number_masked": self.account_number_masked or "••••",
            "current_balance": float(self.current_balance) if self.current_balance is not None else 0.0,
            "currency": self.currency,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "transaction_count": len(self.transactions)
        }

class FinancialTransaction(db.Model):
    __tablename__ = 'financial_transactions'
    __table_args__ = (
        db.Index('ix_fin_tx_user_date', 'user_id', 'transaction_date'),
        db.Index('ix_fin_tx_account_date', 'account_id', 'transaction_date'),
    )

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    account_id = db.Column(GUID(), db.ForeignKey('financial_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(GUID(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General') # Food & Dining, Groceries, Transport, Dividends, Transfer, Salary
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False, default='expense') # 'expense', 'income', 'transfer'
    merchant = db.Column(db.String(100), nullable=True)
    reference_id = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id) if self.id else None,
            "account_id": str(self.account_id) if self.account_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "institution_name": self.account.institution_name if self.account else "Unknown Account",
            "account_nickname": self.account.account_nickname if self.account else "Unknown",
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "description": self.description,
            "category": self.category,
            "amount": float(self.amount) if self.amount is not None else 0.0,
            "transaction_type": self.transaction_type,
            "merchant": self.merchant,
            "reference_id": self.reference_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

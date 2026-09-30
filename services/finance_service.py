import uuid
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from extensions import db
from models.financial_account import FinancialAccount, FinancialTransaction
from models.finance import BudgetGoal, Transaction

def get_net_worth_overview(user_id):
    """
    Computes aggregated wealth metrics for user:
    - Total Assets: ewallet, bank_savings, investment_unit_trust, investment_stocks
    - Total Liabilities: credit_debt
    - Net Worth = Total Assets - Total Liabilities
    - Category allocations & percentages
    - Cashflow velocity (Inflow, Outflow, Net Savings, Savings Rate)
    - Accounts list grouped by category
    """
    # 1. Fetch all accounts for user
    accounts = db.session.execute(
        db.select(FinancialAccount).where(FinancialAccount.user_id == user_id).order_by(FinancialAccount.institution_name.asc())
    ).scalars().all()

    category_map = {
        'ewallet': {'title': 'E-Wallets', 'total': Decimal('0.00'), 'accounts': [], 'icon': 'bi-phone', 'color': '#0dcaf0'},
        'bank_savings': {'title': 'Commercial Banks', 'total': Decimal('0.00'), 'accounts': [], 'icon': 'bi-bank', 'color': '#0d6efd'},
        'investment_unit_trust': {'title': 'Unit Trusts', 'total': Decimal('0.00'), 'accounts': [], 'icon': 'bi-safe', 'color': '#6f42c1'},
        'investment_stocks': {'title': 'Brokerages & Stocks', 'total': Decimal('0.00'), 'accounts': [], 'icon': 'bi-graph-up-arrow', 'color': '#10b981'},
        'credit_debt': {'title': 'Credit & Liabilities', 'total': Decimal('0.00'), 'accounts': [], 'icon': 'bi-credit-card-2-front', 'color': '#ef4444'}
    }

    total_assets = Decimal('0.00')
    total_liabilities = Decimal('0.00')

    for acc in accounts:
        balance = Decimal(str(acc.current_balance or 0.00))
        cat = acc.account_category if acc.account_category in category_map else 'bank_savings'
        category_map[cat]['total'] += balance
        category_map[cat]['accounts'].append(acc.to_dict())

        if cat == 'credit_debt':
            total_liabilities += abs(balance)
        else:
            total_assets += balance

    net_worth = total_assets - total_liabilities

    # Asset Allocation Percentages (over total assets)
    allocations = {}
    for cat_key, cat_data in category_map.items():
        if cat_key == 'credit_debt':
            continue
        amt = cat_data['total']
        pct = round(float((amt / total_assets) * 100), 1) if total_assets > Decimal('0.00') else 0.0
        allocations[cat_key] = {
            'title': cat_data['title'],
            'amount': float(amt),
            'percentage': pct,
            'color': cat_data['color'],
            'icon': cat_data['icon']
        }

    # 2. Cashflow Velocity (Past 30 Days)
    thirty_days_ago = date.today() - timedelta(days=30)
    
    # Financial transactions from linked accounts
    fin_txs = db.session.execute(
        db.select(FinancialTransaction).where(
            FinancialTransaction.user_id == user_id,
            FinancialTransaction.transaction_date >= thirty_days_ago
        )
    ).scalars().all()

    # Also include legacy transactions for full fidelity
    legacy_txs = db.session.execute(
        db.select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= thirty_days_ago
        )
    ).scalars().all()

    total_inflow = Decimal('0.00')
    total_outflow = Decimal('0.00')

    for tx in fin_txs:
        amt = Decimal(str(tx.amount or 0.00))
        if tx.transaction_type == 'income':
            total_inflow += amt
        elif tx.transaction_type == 'expense':
            total_outflow += amt

    for tx in legacy_txs:
        amt = Decimal(str(tx.amount or 0.00))
        if tx.type == 'income':
            total_inflow += amt
        elif tx.type == 'expense':
            total_outflow += amt

    net_savings = total_inflow - total_outflow
    savings_rate = round(float((net_savings / total_inflow) * 100), 1) if total_inflow > Decimal('0.00') else 0.0

    return {
        'net_worth': float(net_worth),
        'total_assets': float(total_assets),
        'total_liabilities': float(total_liabilities),
        'allocations': allocations,
        'category_breakdown': {k: {
            'title': v['title'],
            'total': float(v['total']),
            'count': len(v['accounts']),
            'accounts': v['accounts'],
            'icon': v['icon'],
            'color': v['color']
        } for k, v in category_map.items()},
        'cashflow': {
            'inflow_30d': float(total_inflow),
            'outflow_30d': float(total_outflow),
            'net_savings_30d': float(net_savings),
            'savings_rate_pct': savings_rate
        },
        'account_count': len(accounts)
    }

def get_user_accounts(user_id, category=None):
    """Retrieves all financial accounts for a user, optionally filtered by category."""
    query = db.select(FinancialAccount).where(FinancialAccount.user_id == user_id)
    if category:
        query = query.where(FinancialAccount.account_category == category)
    query = query.order_by(FinancialAccount.account_category.asc(), FinancialAccount.institution_name.asc())
    accounts = db.session.execute(query).scalars().all()
    return [acc.to_dict() for acc in accounts]

def get_account_by_id(user_id, account_id):
    """Retrieves a specific account ensuring ownership."""
    return db.session.execute(
        db.select(FinancialAccount).where(
            FinancialAccount.id == account_id,
            FinancialAccount.user_id == user_id
        )
    ).scalar_one_or_none()

def create_or_update_account(user_id, data, account_id=None):
    """Creates a new financial account or updates an existing one."""
    institution_name = (data.get('institution_name') or '').strip()
    account_category = (data.get('account_category') or 'bank_savings').strip()
    account_nickname = (data.get('account_nickname') or institution_name).strip()
    account_number_masked = (data.get('account_number_masked') or '').strip()
    currency = (data.get('currency') or 'MYR').strip().upper()

    try:
        current_balance = Decimal(str(data.get('current_balance', 0.0)))
    except Exception:
        current_balance = Decimal('0.00')

    valid_categories = {'ewallet', 'bank_savings', 'investment_unit_trust', 'investment_stocks', 'credit_debt'}
    if account_category not in valid_categories:
        account_category = 'bank_savings'

    if not institution_name:
        raise ValueError("Institution name is required.")
    if not account_nickname:
        account_nickname = institution_name

    if account_id:
        account = get_account_by_id(user_id, account_id)
        if not account:
            return None
        account.institution_name = institution_name
        account.account_category = account_category
        account.account_nickname = account_nickname
        if account_number_masked:
            account.account_number_masked = account_number_masked
        account.current_balance = current_balance
        account.currency = currency
        account.updated_at = datetime.now(timezone.utc)
    else:
        account = FinancialAccount(
            user_id=user_id,
            institution_name=institution_name,
            account_category=account_category,
            account_nickname=account_nickname,
            account_number_masked=account_number_masked or "••••",
            current_balance=current_balance,
            currency=currency,
            last_synced_at=datetime.now(timezone.utc)
        )
        db.session.add(account)

    db.session.commit()
    return account.to_dict()

def reconcile_account_balance(user_id, account_id, new_balance, note=None):
    """
    Reconciles an account balance directly against official statements or user confirmation.
    Logs an adjustment transaction for the difference.
    """
    account = get_account_by_id(user_id, account_id)
    if not account:
        return None

    try:
        new_balance_dec = Decimal(str(new_balance))
    except Exception:
        raise ValueError("Invalid balance amount format.")

    old_balance = Decimal(str(account.current_balance or 0.00))
    difference = new_balance_dec - old_balance

    # Update account balance and sync timestamp
    account.current_balance = new_balance_dec
    account.last_synced_at = datetime.now(timezone.utc)
    account.updated_at = datetime.now(timezone.utc)

    # If there is a non-zero difference, record a reconciliation audit transaction
    if abs(difference) > Decimal('0.001'):
        tx_type = 'income' if difference > 0 else 'expense'
        desc = note or f"Balance Reconciliation ({'+' if difference > 0 else ''}{float(difference):.2f})"
        audit_tx = FinancialTransaction(
            account_id=account.id,
            user_id=user_id,
            transaction_date=date.today(),
            description=desc,
            category='Reconciliation',
            amount=abs(difference),
            transaction_type=tx_type,
            merchant=account.institution_name,
            reference_id=f"REC-{int(datetime.now(timezone.utc).timestamp())}"
        )
        db.session.add(audit_tx)

    db.session.commit()
    return account.to_dict()

def delete_account(user_id, account_id):
    """Permanently deletes an account and cascade deletes all linked transactions."""
    account = get_account_by_id(user_id, account_id)
    if not account:
        return False
    db.session.delete(account)
    db.session.commit()
    return True

def get_transactions_ledger(user_id, account_id=None, category=None, tx_type=None, limit=100):
    """Fetches transaction ledger with optional filters."""
    query = db.select(FinancialTransaction).where(FinancialTransaction.user_id == user_id)
    if account_id:
        query = query.where(FinancialTransaction.account_id == account_id)
    if category:
        query = query.where(FinancialTransaction.category.ilike(f"%{category}%"))
    if tx_type:
        query = query.where(FinancialTransaction.transaction_type == tx_type)

    query = query.order_by(FinancialTransaction.transaction_date.desc(), FinancialTransaction.created_at.desc()).limit(limit)
    txs = db.session.execute(query).scalars().all()
    return [tx.to_dict() for tx in txs]

def create_manual_transaction(user_id, data):
    """Logs a single transaction into a specified financial account."""
    account_id = data.get('account_id')
    if not account_id:
        raise ValueError("Target account is required.")

    account = get_account_by_id(user_id, account_id)
    if not account:
        raise ValueError("Selected financial account does not exist or unauthorized.")

    try:
        amount = Decimal(str(data.get('amount', 0.0)))
        if amount <= Decimal('0.00'):
            raise ValueError("Amount must be greater than zero.")
    except Exception as e:
        raise ValueError(f"Invalid amount: {str(e)}")

    description = (data.get('description') or '').strip()
    if not description:
        raise ValueError("Description is required.")

    tx_type = (data.get('transaction_type') or 'expense').strip().lower()
    if tx_type not in {'expense', 'income', 'transfer'}:
        tx_type = 'expense'

    category = (data.get('category') or 'General').strip()
    merchant = (data.get('merchant') or '').strip() or None
    reference_id = (data.get('reference_id') or '').strip() or None

    tx_date = date.today()
    if data.get('transaction_date'):
        try:
            tx_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    tx = FinancialTransaction(
        account_id=account.id,
        user_id=user_id,
        transaction_date=tx_date,
        description=description,
        category=category,
        amount=amount,
        transaction_type=tx_type,
        merchant=merchant,
        reference_id=reference_id
    )

    # Update account balance accordingly
    if tx_type == 'income':
        account.current_balance = Decimal(str(account.current_balance or 0.00)) + amount
    elif tx_type == 'expense':
        account.current_balance = Decimal(str(account.current_balance or 0.00)) - amount
    account.last_synced_at = datetime.now(timezone.utc)

    db.session.add(tx)
    db.session.commit()
    return tx.to_dict()

def delete_financial_transaction(user_id, transaction_id):
    """Deletes a financial transaction and reverses its balance impact."""
    tx = db.session.execute(
        db.select(FinancialTransaction).where(
            FinancialTransaction.id == transaction_id,
            FinancialTransaction.user_id == user_id
        )
    ).scalar_one_or_none()

    if not tx:
        return False

    account = tx.account
    if account:
        amount = Decimal(str(tx.amount or 0.00))
        if tx.transaction_type == 'income':
            account.current_balance = Decimal(str(account.current_balance or 0.00)) - amount
        elif tx.transaction_type == 'expense':
            account.current_balance = Decimal(str(account.current_balance or 0.00)) + amount
        account.last_synced_at = datetime.now(timezone.utc)

    db.session.delete(tx)
    db.session.commit()
    return True

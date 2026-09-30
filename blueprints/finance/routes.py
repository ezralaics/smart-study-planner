import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from flask import render_template, request, jsonify, session, redirect, url_for
from extensions import db
from models.finance import BudgetGoal, Transaction
from models.financial_account import FinancialAccount, FinancialTransaction
from utils.auth import login_required
from blueprints.finance import finance_bp
from services.finance_service import (
    get_net_worth_overview,
    get_user_accounts,
    create_or_update_account,
    reconcile_account_balance,
    delete_account,
    get_transactions_ledger,
    create_manual_transaction,
    delete_financial_transaction
)
from services.statement_parser import (
    parse_statement_file,
    commit_statement_transactions
)

logger = logging.getLogger(__name__)

# ==============================================================================
# Presentation Tier: OmniFinance Views
# ==============================================================================

@finance_bp.route('/finance')
@finance_bp.route('/finance/dashboard')
@login_required
def finance_page():
    """OmniFinance Wealth Dashboard: Aggregated Net Worth, Asset Allocation & Inflow/Outflow."""
    session['active_workspace'] = 'finance'
    return render_template('finance/dashboard.html', active_page='finance_overview')

@finance_bp.route('/finance/accounts')
@login_required
def finance_accounts_page():
    """OmniFinance Linked Accounts Manager."""
    session['active_workspace'] = 'finance'
    return render_template('finance/accounts.html', active_page='finance_accounts')

@finance_bp.route('/finance/statements')
@login_required
def finance_statements_page():
    """OmniFinance Statement Ingestion & Dropzone Hub."""
    session['active_workspace'] = 'finance'
    return render_template('finance/statements.html', active_page='finance_statements')

@finance_bp.route('/finance/transactions')
@login_required
def finance_transactions_page():
    """OmniFinance Master Transaction Ledger."""
    session['active_workspace'] = 'finance'
    return render_template('finance/transactions.html', active_page='finance_transactions')

@finance_bp.route('/finance/budgets')
@finance_bp.route('/finance/budget')
def finance_budgets_page():
    """Student Budget & Monthly Savings Target Hub."""
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    session['active_workspace'] = 'finance'
    return render_template('finance/budgets.html', active_page='finance_budgets')


# ==============================================================================
# Controller Tier: OmniFinance RESTful APIs
# ==============================================================================

@finance_bp.route('/api/finance/net-worth', methods=['GET'])
@login_required
def api_get_net_worth():
    """Fetches real-time aggregated net worth, asset allocation, and cashflow velocity."""
    user_id = session['user_id']
    try:
        overview = get_net_worth_overview(user_id)
        return jsonify({
            'status': 'success',
            'data': overview
        }), 200
    except Exception as e:
        logger.error(f"Error computing net worth for user {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to compute net worth: {str(e)}'}), 500

@finance_bp.route('/api/finance/accounts', methods=['GET'])
@login_required
def api_get_accounts():
    """Lists all financial accounts linked by the user."""
    user_id = session['user_id']
    category = request.args.get('category')
    try:
        accounts = get_user_accounts(user_id, category=category)
        return jsonify({
            'status': 'success',
            'data': accounts,
            'count': len(accounts)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching accounts for user {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to retrieve accounts: {str(e)}'}), 500

@finance_bp.route('/api/finance/accounts', methods=['POST'])
@login_required
def api_create_account():
    """Creates a new financial account."""
    user_id = session['user_id']
    data = request.get_json() or {}
    try:
        acc = create_or_update_account(user_id, data)
        return jsonify({
            'status': 'success',
            'message': f"Account '{acc['institution_name']}' created successfully.",
            'data': acc
        }), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Error creating account for user {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to create account: {str(e)}'}), 500

@finance_bp.route('/api/finance/accounts/<string:account_id>', methods=['PUT'])
@login_required
def api_update_account(account_id):
    """Updates an existing financial account."""
    user_id = session['user_id']
    data = request.get_json() or {}
    try:
        acc = create_or_update_account(user_id, data, account_id=account_id)
        if not acc:
            return jsonify({'status': 'error', 'message': 'Account not found or access denied.'}), 404
        return jsonify({
            'status': 'success',
            'message': 'Account updated successfully.',
            'data': acc
        }), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to update account: {str(e)}'}), 500

@finance_bp.route('/api/finance/accounts/<string:account_id>', methods=['DELETE'])
@login_required
def api_delete_account(account_id):
    """Deletes an account and cascade deletes all linked transactions."""
    user_id = session['user_id']
    try:
        success = delete_account(user_id, account_id)
        if not success:
            return jsonify({'status': 'error', 'message': 'Account not found or access denied.'}), 404
        return jsonify({
            'status': 'success',
            'message': 'Account and associated transactions deleted successfully.'
        }), 200
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to delete account: {str(e)}'}), 500

@finance_bp.route('/api/finance/accounts/<string:account_id>/reconcile', methods=['POST'])
@login_required
def api_reconcile_account(account_id):
    """Reconciles account balance against official bank statement."""
    user_id = session['user_id']
    data = request.get_json() or {}
    new_balance = data.get('new_balance')
    note = data.get('note')

    if new_balance is None:
        return jsonify({'status': 'error', 'message': 'New balance is required.'}), 400

    try:
        result = reconcile_account_balance(user_id, account_id, new_balance, note=note)
        if not result:
            return jsonify({'status': 'error', 'message': 'Account not found or access denied.'}), 404
        return jsonify({
            'status': 'success',
            'message': f"Account balance reconciled to {result['currency']} {result['current_balance']:,.2f}.",
            'data': result
        }), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Error reconciling account {account_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to reconcile account: {str(e)}'}), 500

@finance_bp.route('/api/finance/transactions-ledger', methods=['GET'])
@login_required
def api_get_transactions_ledger():
    """Fetches itemized transactions from linked accounts."""
    user_id = session['user_id']
    account_id = request.args.get('account_id')
    category = request.args.get('category')
    tx_type = request.args.get('type')
    try:
        limit = min(int(request.args.get('limit', 100)), 500)
    except ValueError:
        limit = 100

    try:
        txs = get_transactions_ledger(user_id, account_id=account_id, category=category, tx_type=tx_type, limit=limit)
        return jsonify({
            'status': 'success',
            'data': txs,
            'count': len(txs)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching transaction ledger: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to fetch transactions: {str(e)}'}), 500

@finance_bp.route('/api/finance/transactions-ledger', methods=['POST'])
@login_required
def api_create_transactions_ledger():
    """Creates a manual transaction for a linked financial account."""
    user_id = session['user_id']
    data = request.get_json() or {}
    try:
        tx = create_manual_transaction(user_id, data)
        return jsonify({
            'status': 'success',
            'message': 'Transaction logged successfully.',
            'data': tx
        }), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Error recording transaction: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to record transaction: {str(e)}'}), 500

@finance_bp.route('/api/finance/transactions-ledger/<string:transaction_id>', methods=['DELETE'])
@login_required
def api_delete_transactions_ledger(transaction_id):
    """Deletes a transaction and adjusts the corresponding account balance."""
    user_id = session['user_id']
    try:
        success = delete_financial_transaction(user_id, transaction_id)
        if not success:
            return jsonify({'status': 'error', 'message': 'Transaction not found or unauthorized.'}), 404
        return jsonify({
            'status': 'success',
            'message': 'Transaction deleted and balance adjusted successfully.'
        }), 200
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to delete transaction: {str(e)}'}), 500

@finance_bp.route('/api/finance/parse-statement', methods=['POST'])
@login_required
def api_parse_statement():
    """Uploads and parses a financial statement (PDF, CSV, TXT) with AI & Regex."""
    user_id = session['user_id']
    file = request.files.get('file')
    if not file:
        return jsonify({'status': 'error', 'message': 'No statement file uploaded.'}), 400

    target_account_id = request.form.get('account_id')
    try:
        res = parse_statement_file(file, user_id, target_account_id=target_account_id)
        if res.get('status') == 'error':
            return jsonify(res), 400
        return jsonify(res), 200
    except Exception as e:
        logger.error(f"Error parsing statement: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Statement ingestion failed: {str(e)}'}), 500

@finance_bp.route('/api/finance/commit-statement', methods=['POST'])
@login_required
def api_commit_statement():
    """Commits reviewed statement transactions to the specified account."""
    user_id = session['user_id']
    data = request.get_json() or {}
    account_id = data.get('account_id')
    statement_data = data.get('statement_data') or {}

    if not account_id:
        return jsonify({'status': 'error', 'message': 'Target account ID is required.'}), 400

    try:
        res = commit_statement_transactions(user_id, account_id, statement_data)
        return jsonify(res), 200
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Error committing statement transactions: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to commit transactions: {str(e)}'}), 500


# ==============================================================================
# Legacy Endpoints (Preserved for 100% Backward Compatibility)
# ==============================================================================

@finance_bp.route('/api/finance/summary')
@login_required
def get_finance_summary():
    """Legacy budget goal summary endpoint."""
    user_id = session['user_id']
    current_month_str = date.today().strftime('%Y-%m')

    goal = db.session.execute(
        db.select(BudgetGoal).where(BudgetGoal.user_id == user_id, BudgetGoal.month_year == current_month_str)
    ).scalar_one_or_none()

    budget_limit = goal.monthly_budget_limit if goal else 1000.0
    savings_target = goal.savings_target if goal else 200.0
    currency = goal.currency_symbol if goal else '$'

    start_of_month = date(date.today().year, date.today().month, 1)
    transactions = db.session.execute(
        db.select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_of_month
        ).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
    ).scalars().all()

    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    remaining_budget = max(0.0, budget_limit - total_expense)
    budget_usage_pct = min(100.0, round((total_expense / budget_limit * 100.0), 1)) if budget_limit > 0 else 0.0

    cat_breakdown = {}
    for t in transactions:
        if t.type == 'expense':
            cat_breakdown[t.category] = cat_breakdown.get(t.category, 0.0) + t.amount

    return jsonify({
        'status': 'success',
        'month_year': current_month_str,
        'currency': currency,
        'budget_limit': round(budget_limit, 2),
        'savings_target': round(savings_target, 2),
        'total_expense': round(total_expense, 2),
        'total_income': round(total_income, 2),
        'remaining_budget': round(remaining_budget, 2),
        'budget_usage_pct': budget_usage_pct,
        'category_breakdown': {k: round(v, 2) for k, v in cat_breakdown.items()},
        'recent_transactions': [t.to_dict() for t in transactions[:10]]
    })

@finance_bp.route('/api/finance/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Legacy transaction list endpoint."""
    user_id = session['user_id']
    transactions = db.session.execute(
        db.select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
    ).scalars().all()

    return jsonify({
        'status': 'success',
        'data': [t.to_dict() for t in transactions]
    })

@finance_bp.route('/api/finance/transactions', methods=['POST'])
@login_required
def add_transaction():
    """Legacy transaction creation endpoint."""
    user_id = session['user_id']
    data = request.get_json() or {}

    amount_raw = data.get('amount')
    try:
        amount = float(amount_raw)
        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'Amount must be greater than zero.'}), 400
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Valid numeric amount is required.'}), 400

    description = (data.get('description') or '').strip()
    if not description:
        return jsonify({'status': 'error', 'message': 'Description is required.'}), 400

    tx_type = (data.get('type') or 'expense').strip().lower()
    if tx_type not in ['expense', 'income']:
        tx_type = 'expense'

    category = (data.get('category') or 'general').strip().lower()
    
    tx_date = date.today()
    if data.get('transaction_date'):
        try:
            tx_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    tx = Transaction(
        user_id=user_id,
        amount=amount,
        type=tx_type,
        category=category,
        description=description,
        transaction_date=tx_date,
        payment_method=(data.get('payment_method') or 'card').strip()
    )

    try:
        db.session.add(tx)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Transaction recorded successfully.',
            'data': tx.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to record transaction: {str(e)}'}), 500

@finance_bp.route('/api/finance/budget', methods=['POST'])
@login_required
def set_budget():
    """Legacy budget limit update endpoint."""
    user_id = session['user_id']
    data = request.get_json() or {}
    month_year = (data.get('month_year') or date.today().strftime('%Y-%m')).strip()

    try:
        budget_limit = float(data.get('monthly_budget_limit', 1000.0))
        savings_target = float(data.get('savings_target', 200.0))
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Budget and savings target must be valid numbers.'}), 400

    goal = db.session.execute(
        db.select(BudgetGoal).where(BudgetGoal.user_id == user_id, BudgetGoal.month_year == month_year)
    ).scalar_one_or_none()

    if goal:
        goal.monthly_budget_limit = budget_limit
        goal.savings_target = savings_target
        if data.get('currency_symbol'):
            goal.currency_symbol = data['currency_symbol'].strip()
    else:
        goal = BudgetGoal(
            user_id=user_id,
            month_year=month_year,
            monthly_budget_limit=budget_limit,
            savings_target=savings_target,
            currency_symbol=(data.get('currency_symbol') or '$').strip()
        )
        db.session.add(goal)

    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Budget settings updated successfully.',
            'data': goal.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to update budget: {str(e)}'}), 500

@finance_bp.route('/api/finance/transactions/<string:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """Legacy transaction delete endpoint."""
    user_id = session['user_id']
    tx = db.session.execute(
        db.select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user_id)
    ).scalar_one_or_none()

    if not tx:
        return jsonify({'status': 'error', 'message': 'Transaction not found.'}), 404

    try:
        db.session.delete(tx)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Transaction deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete transaction: {str(e)}'}), 500

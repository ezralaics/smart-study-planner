from datetime import date, datetime, timezone
from flask import render_template, request, jsonify, session
from extensions import db
from models.finance import BudgetGoal, Transaction
from utils.auth import login_required
from blueprints.finance import finance_bp

@finance_bp.route('/finance')
@login_required
def finance_page():
    session['active_workspace'] = 'finance'
    return render_template('finance/index.html', active_page='finance_budget')

@finance_bp.route('/api/finance/summary')
@login_required
def get_finance_summary():
    user_id = session['user_id']
    current_month_str = date.today().strftime('%Y-%m')

    # Fetch budget goal for current month
    goal = db.session.execute(
        db.select(BudgetGoal).where(BudgetGoal.user_id == user_id, BudgetGoal.month_year == current_month_str)
    ).scalar_one_or_none()

    budget_limit = goal.monthly_budget_limit if goal else 1000.0
    savings_target = goal.savings_target if goal else 200.0
    currency = goal.currency_symbol if goal else '$'

    # Fetch transactions for current month
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

    # Category breakdown for expenses
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

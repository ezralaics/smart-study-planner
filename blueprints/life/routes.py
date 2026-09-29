from datetime import date, datetime, timedelta, timezone
from flask import render_template, request, jsonify, session
from extensions import db
from models.habit import Habit, HabitLog
from utils.auth import login_required
from blueprints.life import life_bp

@life_bp.route('/life')
@login_required
def life_page():
    session['active_workspace'] = 'life'
    return render_template('life/index.html', active_page='life_habits')

@life_bp.route('/api/life/habits')
@login_required
def get_habits():
    user_id = session['user_id']
    habits = db.session.execute(
        db.select(Habit).where(Habit.user_id == user_id, Habit.is_archived.is_(False)).order_by(Habit.created_at.asc())
    ).scalars().all()

    today = date.today()
    # Fetch today's logs for this user
    today_logs = db.session.execute(
        db.select(HabitLog).where(HabitLog.user_id == user_id, HabitLog.log_date == today, HabitLog.is_completed.is_(True))
    ).scalars().all()
    completed_habit_ids = {str(log.habit_id) for log in today_logs}

    result = [h.to_dict(today_completed=(str(h.id) in completed_habit_ids)) for h in habits]
    return jsonify({
        'status': 'success',
        'data': result,
        'today': today.isoformat(),
        'completed_today_count': len(completed_habit_ids),
        'total_habits_count': len(habits)
    })

@life_bp.route('/api/life/habits', methods=['POST'])
@login_required
def create_habit():
    user_id = session['user_id']
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()

    if not title:
        return jsonify({'status': 'error', 'message': 'Habit title is required.'}), 400

    habit = Habit(
        user_id=user_id,
        title=title,
        description=(data.get('description') or '').strip() or None,
        category=(data.get('category') or 'general').strip().lower(),
        frequency=(data.get('frequency') or 'daily').strip().lower(),
        target_days_per_week=int(data.get('target_days_per_week', 7)),
        icon=(data.get('icon') or 'bi-check2-circle').strip(),
        color=(data.get('color') or '#198754').strip(),
        streak_count=0
    )

    try:
        db.session.add(habit)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Habit created successfully.',
            'data': habit.to_dict(today_completed=False)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to create habit: {str(e)}'}), 500

@life_bp.route('/api/life/habits/<string:habit_id>/toggle', methods=['POST'])
@login_required
def toggle_habit(habit_id):
    user_id = session['user_id']
    habit = db.session.execute(
        db.select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
    ).scalar_one_or_none()

    if not habit:
        return jsonify({'status': 'error', 'message': 'Habit not found.'}), 404

    today = date.today()
    log = db.session.execute(
        db.select(HabitLog).where(HabitLog.habit_id == habit.id, HabitLog.log_date == today)
    ).scalar_one_or_none()

    if log:
        log.is_completed = not log.is_completed
        if not log.is_completed and habit.streak_count > 0:
            habit.streak_count -= 1
        elif log.is_completed:
            habit.streak_count += 1
        status_now = log.is_completed
    else:
        log = HabitLog(
            habit_id=habit.id,
            user_id=user_id,
            log_date=today,
            is_completed=True
        )
        db.session.add(log)
        habit.streak_count += 1
        status_now = True

    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'is_completed': status_now,
            'streak_count': habit.streak_count,
            'habit': habit.to_dict(today_completed=status_now)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to toggle habit: {str(e)}'}), 500

@life_bp.route('/api/life/habits/<string:habit_id>', methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    user_id = session['user_id']
    habit = db.session.execute(
        db.select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
    ).scalar_one_or_none()

    if not habit:
        return jsonify({'status': 'error', 'message': 'Habit not found.'}), 404

    try:
        db.session.delete(habit)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Habit deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete habit: {str(e)}'}), 500

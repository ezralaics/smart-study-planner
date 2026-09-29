from datetime import date, datetime, timezone
from flask import render_template, request, jsonify, session
from extensions import db
from models.journal import JournalEntry
from utils.auth import login_required
from blueprints.journal import journal_bp

@journal_bp.route('/journal')
@login_required
def journal_page():
    session['active_workspace'] = 'journal'
    return render_template('journal/index.html', active_page='journal_diary')

@journal_bp.route('/api/journal/entries', methods=['GET'])
@login_required
def get_journal_entries():
    user_id = session['user_id']
    entries = db.session.execute(
        db.select(JournalEntry).where(JournalEntry.user_id == user_id).order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
    ).scalars().all()

    # Mood stats
    mood_counts = {}
    for e in entries:
        mood_counts[e.mood] = mood_counts.get(e.mood, 0) + 1

    return jsonify({
        'status': 'success',
        'data': [e.to_dict() for e in entries],
        'total_entries': len(entries),
        'mood_stats': mood_counts
    })

@journal_bp.route('/api/journal/entries', methods=['POST'])
@login_required
def add_journal_entry():
    user_id = session['user_id']
    data = request.get_json() or {}

    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()

    if not title or not content:
        return jsonify({'status': 'error', 'message': 'Both title and reflection content are required.'}), 400

    mood = (data.get('mood') or 'good').strip().lower()
    tags = (data.get('tags') or '').strip()
    is_pinned = bool(data.get('is_pinned', False))

    entry_date = date.today()
    if data.get('entry_date'):
        try:
            entry_date = datetime.strptime(data['entry_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    entry = JournalEntry(
        user_id=user_id,
        title=title,
        content=content,
        mood=mood,
        tags=tags or None,
        entry_date=entry_date,
        is_pinned=is_pinned
    )

    try:
        db.session.add(entry)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Journal entry saved successfully.',
            'data': entry.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to save journal entry: {str(e)}'}), 500

@journal_bp.route('/api/journal/entries/<string:entry_id>', methods=['DELETE'])
@login_required
def delete_journal_entry(entry_id):
    user_id = session['user_id']
    entry = db.session.execute(
        db.select(JournalEntry).where(JournalEntry.id == entry_id, JournalEntry.user_id == user_id)
    ).scalar_one_or_none()

    if not entry:
        return jsonify({'status': 'error', 'message': 'Journal entry not found.'}), 404

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Journal entry deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete journal entry: {str(e)}'}), 500

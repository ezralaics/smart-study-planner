import logging
from flask import render_template, request, jsonify, session
from utils.auth import login_required
from blueprints.study import study_bp
from blueprints.api import api_bp
from services.study_tip_service import (
    get_or_generate_daily_tip,
    toggle_reaction,
    toggle_bookmark,
    get_bookmarked_tips,
    get_tip_archive
)

logger = logging.getLogger(__name__)

# ==============================================================================
# Presentation Tier: Saved Tips Vault Web View
# ==============================================================================

@study_bp.route('/tips/saved')
@login_required
def saved_tips_page():
    """Web view displaying student's personal cognitive science study tip vault."""
    session['active_workspace'] = 'academics'
    user_id = session['user_id']
    category = request.args.get('category', 'all')
    saved_tips = get_bookmarked_tips(user_id, category=category)
    return render_template(
        'study/tips_archive.html',
        saved_tips=saved_tips,
        active_category=category,
        active_page='saved_study_tips'
    )

# ==============================================================================
# Controller Tier: RESTful Study Tips APIs
# ==============================================================================

@api_bp.route('/api/tips/today', methods=['GET'])
@study_bp.route('/api/tips/today', methods=['GET'])
@login_required
def api_get_today_tip():
    """Fetches today's personalized cognitive tip, bookmark state, and user reaction."""
    user_id = session.get('user_id')
    force = request.args.get('force', 'false').lower() == 'true'

    try:
        tip_data = get_or_generate_daily_tip(user_id, force_refresh=force)
        return jsonify({
            'status': 'success',
            'data': tip_data,
            'message': 'Today\'s cognitive study tip loaded.'
        }), 200
    except Exception as e:
        logger.error(f"Error fetching daily study tip: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve daily study tip.',
            'errors': [str(e)]
        }), 500

@api_bp.route('/api/tips/<string:tip_id>/react', methods=['POST'])
@study_bp.route('/api/tips/<string:tip_id>/react', methods=['POST'])
@login_required
def api_react_tip(tip_id):
    """Toggles reaction feedback ('helpful', 'unhelpful', 'neutral') on a study tip."""
    user_id = session.get('user_id')
    body = request.get_json(silent=True) or {}
    reaction = body.get('reaction', 'helpful')

    result = toggle_reaction(user_id, tip_id, reaction)
    if result.get('status') == 'success':
        return jsonify({
            'status': 'success',
            'data': result,
            'message': f"Reaction '{result.get('reaction')}' recorded."
        }), 200
    return jsonify({
        'status': 'error',
        'message': result.get('message', 'Failed to record feedback.')
    }), 400

@api_bp.route('/api/tips/<string:tip_id>/bookmark', methods=['POST'])
@study_bp.route('/api/tips/<string:tip_id>/bookmark', methods=['POST'])
@login_required
def api_bookmark_tip(tip_id):
    """Toggles bookmark status in student's personal tip vault."""
    user_id = session.get('user_id')
    result = toggle_bookmark(user_id, tip_id)
    if result.get('status') == 'success':
        action_str = "saved to" if result.get('is_bookmarked') else "removed from"
        return jsonify({
            'status': 'success',
            'data': result,
            'message': f"Tip {action_str} your vault."
        }), 200
    return jsonify({
        'status': 'error',
        'message': result.get('message', 'Failed to toggle bookmark.')
    }), 400

@api_bp.route('/api/tips/saved', methods=['GET'])
@study_bp.route('/api/tips/saved', methods=['GET'])
@login_required
def api_get_saved_tips():
    """Returns list of bookmarked tips for current user."""
    user_id = session.get('user_id')
    category = request.args.get('category', 'all')
    tips = get_bookmarked_tips(user_id, category=category)
    return jsonify({
        'status': 'success',
        'data': tips,
        'count': len(tips)
    }), 200

@api_bp.route('/api/tips/archive', methods=['GET'])
@study_bp.route('/api/tips/archive', methods=['GET'])
@login_required
def api_get_tip_archive():
    """Returns past study tips history for current user."""
    user_id = session.get('user_id')
    limit = int(request.args.get('limit', 15))
    archive = get_tip_archive(user_id, limit=limit)
    return jsonify({
        'status': 'success',
        'data': archive,
        'count': len(archive)
    }), 200

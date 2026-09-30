import logging
from datetime import date
from flask import render_template, request, jsonify, session, redirect, url_for
from utils.auth import login_required
from blueprints.reports import reports_bp
from services.digest_service import (
    get_or_create_daily_digest,
    synthesize_weekly_digest,
    send_digest_email,
    get_user_sources,
    create_user_source,
    update_user_source,
    delete_user_source,
    get_digest_history
)

logger = logging.getLogger(__name__)

# ==============================================================================
# Presentation Tier: OmniDigest Views
# ==============================================================================

@reports_bp.route('/reports')
@login_required
def reports_page():
    """OmniDigest: Today's Executive Intelligence Briefing & Archive."""
    session['active_workspace'] = 'reports'
    return render_template('reports/dashboard.html', active_page='reports_daily')

@reports_bp.route('/reports/weekly')
@login_required
def reports_weekly_page():
    """OmniDigest: Weekly Macro Intelligence & Topic Trends."""
    session['active_workspace'] = 'reports'
    return render_template('reports/weekly.html', active_page='reports_weekly')

@reports_bp.route('/reports/sources')
@login_required
def reports_sources_page():
    """OmniDigest: Curated News Sources & RSS Feed Manager."""
    session['active_workspace'] = 'reports'
    return render_template('reports/sources.html', active_page='reports_sources')


# ==============================================================================
# Controller Tier: OmniDigest RESTful APIs
# ==============================================================================

@reports_bp.route('/api/reports/today', methods=['GET'])
@login_required
def api_get_today_report():
    """Fetches or generates today's executive briefing (cost-cached)."""
    user_id = session['user_id']
    try:
        report = get_or_create_daily_digest(user_id, target_date=date.today(), force_refresh=False)
        return jsonify({
            'status': 'success',
            'data': report
        }), 200
    except Exception as e:
        logger.error(f"Error fetching daily report for {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to retrieve report: {str(e)}'}), 500

@reports_bp.route('/api/reports/refresh', methods=['POST'])
@login_required
def api_refresh_today_report():
    """Forces immediate re-synthesis of today's executive briefing."""
    user_id = session['user_id']
    try:
        report = get_or_create_daily_digest(user_id, target_date=date.today(), force_refresh=True)
        return jsonify({
            'status': 'success',
            'message': "Today's briefing re-synthesized with latest headlines.",
            'data': report
        }), 200
    except Exception as e:
        logger.error(f"Error refreshing daily report for {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to refresh report: {str(e)}'}), 500

@reports_bp.route('/api/reports/email-today', methods=['POST'])
@login_required
def api_email_today_report():
    """Dispatches today's executive briefing directly to the user's email."""
    user_id = session['user_id']
    try:
        # Ensure report exists
        report_dict = get_or_create_daily_digest(user_id, target_date=date.today(), force_refresh=False)
        report_id = report_dict['id']

        result = send_digest_email(user_id, report_id)
        status_code = 200 if result['status'] == 'success' else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error emailing report for {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to dispatch email: {str(e)}'}), 500

@reports_bp.route('/api/reports/weekly', methods=['GET'])
@login_required
def api_get_weekly_report():
    """Fetches or synthesizes the 7-day macro retrospective report."""
    user_id = session['user_id']
    force_refresh = request.args.get('refresh') == 'true'
    try:
        report = synthesize_weekly_digest(user_id, end_date=date.today(), force_refresh=force_refresh)
        return jsonify({
            'status': 'success',
            'data': report
        }), 200
    except Exception as e:
        logger.error(f"Error generating weekly report for {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to retrieve weekly report: {str(e)}'}), 500

@reports_bp.route('/api/reports/history', methods=['GET'])
@login_required
def api_get_report_history():
    """Lists previous digest reports for archive review."""
    user_id = session['user_id']
    report_type = request.args.get('type', 'daily')
    try:
        limit = min(int(request.args.get('limit', 30)), 100)
    except ValueError:
        limit = 30

    try:
        history = get_digest_history(user_id, report_type=report_type, limit=limit)
        return jsonify({
            'status': 'success',
            'data': history,
            'count': len(history)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching report history: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to fetch report history: {str(e)}'}), 500

# ==============================================================================
# Source Management APIs
# ==============================================================================

@reports_bp.route('/api/reports/sources', methods=['GET'])
@login_required
def api_get_sources():
    """Retrieves user's interest sources plus curated presets."""
    user_id = session['user_id']
    try:
        data = get_user_sources(user_id)
        return jsonify({
            'status': 'success',
            'data': data
        }), 200
    except Exception as e:
        logger.error(f"Error fetching sources for {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to fetch sources: {str(e)}'}), 500

@reports_bp.route('/api/reports/sources', methods=['POST'])
@login_required
def api_create_source():
    """Adds a new interest or RSS feed source."""
    user_id = session['user_id']
    data = request.get_json() or {}
    try:
        source = create_user_source(user_id, data)
        return jsonify({
            'status': 'success',
            'message': f"Source '{source['title']}' added successfully.",
            'data': source
        }), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Error creating source for {user_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to add source: {str(e)}'}), 500

@reports_bp.route('/api/reports/sources/<string:source_id>', methods=['PUT'])
@login_required
def api_update_source(source_id):
    """Updates or toggles an interest source."""
    user_id = session['user_id']
    data = request.get_json() or {}
    try:
        source = update_user_source(user_id, source_id, data)
        if not source:
            return jsonify({'status': 'error', 'message': 'Source not found.'}), 404
        return jsonify({
            'status': 'success',
            'message': 'Source updated successfully.',
            'data': source
        }), 200
    except Exception as e:
        logger.error(f"Error updating source {source_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to update source: {str(e)}'}), 500

@reports_bp.route('/api/reports/sources/<string:source_id>', methods=['DELETE'])
@login_required
def api_delete_source(source_id):
    """Deletes an interest source."""
    user_id = session['user_id']
    try:
        success = delete_user_source(user_id, source_id)
        if not success:
            return jsonify({'status': 'error', 'message': 'Source not found.'}), 404
        return jsonify({
            'status': 'success',
            'message': 'Source removed successfully.'
        }), 200
    except Exception as e:
        logger.error(f"Error deleting source {source_id}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Failed to delete source: {str(e)}'}), 500

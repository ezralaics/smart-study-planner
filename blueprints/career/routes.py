from datetime import date, datetime, timezone
from flask import render_template, request, jsonify, session
from extensions import db
from models.career import JobApplication
from utils.auth import login_required
from blueprints.career import career_bp

KANBAN_STAGES = ['wishlist', 'applied', 'interviewing', 'offer', 'rejected']

@career_bp.route('/career')
@login_required
def career_page():
    session['active_workspace'] = 'career'
    return render_template('career/index.html', active_page='career_kanban')

@career_bp.route('/api/career/applications', methods=['GET'])
@login_required
def get_applications():
    user_id = session['user_id']
    apps = db.session.execute(
        db.select(JobApplication).where(JobApplication.user_id == user_id).order_by(JobApplication.created_at.desc())
    ).scalars().all()

    grouped = {stage: [] for stage in KANBAN_STAGES}
    for app in apps:
        stage = app.status if app.status in grouped else 'wishlist'
        grouped[stage].append(app.to_dict())

    return jsonify({
        'status': 'success',
        'stages': KANBAN_STAGES,
        'grouped': grouped,
        'total_count': len(apps)
    })

@career_bp.route('/api/career/applications', methods=['POST'])
@login_required
def add_application():
    user_id = session['user_id']
    data = request.get_json() or {}

    company_name = (data.get('company_name') or '').strip()
    job_title = (data.get('job_title') or '').strip()

    if not company_name or not job_title:
        return jsonify({'status': 'error', 'message': 'Company name and job title are required.'}), 400

    status = (data.get('status') or 'wishlist').strip().lower()
    if status not in KANBAN_STAGES:
        status = 'wishlist'

    applied_date = None
    if data.get('applied_date'):
        try:
            applied_date = datetime.strptime(data['applied_date'], '%Y-%m-%d').date()
        except ValueError:
            pass
    elif status in ['applied', 'interviewing', 'offer']:
        applied_date = date.today()

    deadline_date = None
    if data.get('deadline_date'):
        try:
            deadline_date = datetime.strptime(data['deadline_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    app = JobApplication(
        user_id=user_id,
        company_name=company_name,
        job_title=job_title,
        status=status,
        location=(data.get('location') or '').strip() or None,
        workplace_type=(data.get('workplace_type') or 'hybrid').strip(),
        salary_range=(data.get('salary_range') or '').strip() or None,
        job_url=(data.get('job_url') or '').strip() or None,
        applied_date=applied_date,
        deadline_date=deadline_date,
        notes=(data.get('notes') or '').strip() or None,
        priority=(data.get('priority') or 'medium').strip().lower()
    )

    try:
        db.session.add(app)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Job application created successfully.',
            'data': app.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to create application: {str(e)}'}), 500

@career_bp.route('/api/career/applications/<string:app_id>/status', methods=['PATCH', 'POST'])
@login_required
def update_application_status(app_id):
    user_id = session['user_id']
    app = db.session.execute(
        db.select(JobApplication).where(JobApplication.id == app_id, JobApplication.user_id == user_id)
    ).scalar_one_or_none()

    if not app:
        return jsonify({'status': 'error', 'message': 'Job application not found.'}), 404

    data = request.get_json() or {}
    new_status = (data.get('status') or '').strip().lower()

    if new_status not in KANBAN_STAGES:
        return jsonify({'status': 'error', 'message': f'Invalid status. Allowed values: {", ".join(KANBAN_STAGES)}'}), 400

    app.status = new_status
    if new_status in ['applied', 'interviewing', 'offer'] and not app.applied_date:
        app.applied_date = date.today()

    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Status updated to {new_status}.',
            'data': app.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to update status: {str(e)}'}), 500

@career_bp.route('/api/career/applications/<string:app_id>', methods=['DELETE'])
@login_required
def delete_application(app_id):
    user_id = session['user_id']
    app = db.session.execute(
        db.select(JobApplication).where(JobApplication.id == app_id, JobApplication.user_id == user_id)
    ).scalar_one_or_none()

    if not app:
        return jsonify({'status': 'error', 'message': 'Job application not found.'}), 404

    try:
        db.session.delete(app)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Job application deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to delete application: {str(e)}'}), 500

import logging
from flask import render_template, session, jsonify, request
from extensions import db
from models.course import Course
from utils.auth import login_required
from blueprints.analytics import analytics_bp
from services.analytics_service import (
    calculate_what_if_grade,
    detect_burnout_and_deadline_clusters,
    calculate_study_velocity,
    get_analytics_dashboard_metrics,
    generate_study_flashcards_or_quiz
)

logger = logging.getLogger(__name__)

@analytics_bp.route('/analytics')
@login_required
def analytics_hub():
    """
    Renders the Academic Analytics & AI Insights Hub dashboard.
    """
    user_id = session.get('user_id')
    metrics = get_analytics_dashboard_metrics(user_id)

    courses = db.session.execute(
        db.select(Course)
        .where(Course.user_id == user_id, Course.is_completed == False)
        .order_by(Course.course_name.asc())
    ).scalars().all()

    # If no active courses, fetch any enrolled courses
    if not courses:
        courses = db.session.execute(
            db.select(Course)
            .where(Course.user_id == user_id)
            .order_by(Course.course_name.asc())
        ).scalars().all()

    return render_template(
        'analytics.html',
        metrics=metrics,
        courses=courses,
        active_page='analytics',
        active_workspace='study'
    )

@analytics_bp.route('/api/analytics/metrics', methods=['GET'])
@login_required
def get_metrics_api():
    """
    Returns visual telemetry data (Chart.js payloads and top-level KPIs).
    """
    user_id = session.get('user_id')
    metrics = get_analytics_dashboard_metrics(user_id)
    return jsonify({
        "status": "success",
        "data": metrics
    }), 200

@analytics_bp.route('/api/analytics/forecast', methods=['POST'])
@login_required
def forecast_grade_api():
    """
    Calculates What-If grade projection and required final exam mark.
    """
    data = request.get_json(silent=True) or {}
    course_id = data.get('course_id')
    target_grade = float(data.get('target_grade', 85.0))
    custom_marks = data.get('custom_marks', {})

    if not course_id:
        return jsonify({
            "status": "error",
            "message": "Course ID is required."
        }), 400

    forecast = calculate_what_if_grade(course_id, target_grade, custom_marks)
    return jsonify({
        "status": "success",
        "data": forecast
    }), 200

@analytics_bp.route('/api/analytics/burnout', methods=['GET'])
@login_required
def get_burnout_api():
    """
    Returns deadline cluster detection and workload risk diagnostics.
    """
    user_id = session.get('user_id')
    burnout = detect_burnout_and_deadline_clusters(user_id)
    return jsonify({
        "status": "success",
        "data": burnout
    }), 200

@analytics_bp.route('/api/analytics/velocity', methods=['GET'])
@login_required
def get_velocity_api():
    """
    Returns study velocity and on-time task delivery metrics.
    """
    user_id = session.get('user_id')
    velocity = calculate_study_velocity(user_id)
    return jsonify({
        "status": "success",
        "data": velocity
    }), 200

@analytics_bp.route('/api/analytics/generate-study-material', methods=['POST'])
@login_required
def generate_study_material_api():
    """
    AI Study Assistant flashcards & practice quiz generation grounded in course documents.
    """
    data = request.get_json(silent=True) or {}
    user_id = session.get('user_id')
    course_id = data.get('course_id')
    material_type = data.get('material_type', 'flashcards')

    result = generate_study_flashcards_or_quiz(user_id, course_id, material_type)
    return jsonify({
        "status": "success",
        "data": result
    }), 200

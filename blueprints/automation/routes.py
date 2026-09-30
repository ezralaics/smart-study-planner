import logging
from flask import request, jsonify, session
from utils.auth import login_required
from blueprints.automation import automation_bp
from services.automation_service import (
    parse_syllabus_document,
    batch_import_syllabus,
    rebalance_missed_schedule,
    decompose_task_with_ai,
    commit_subtasks_to_board
)

logger = logging.getLogger(__name__)

@automation_bp.route('/api/automation/parse-syllabus', methods=['POST'])
@login_required
def parse_syllabus():
    """
    Parses a syllabus PDF or document and returns structured course and task schema for preview.
    """
    if 'file' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No file uploaded. Please select a syllabus PDF or document."
        }), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({
            "status": "error",
            "message": "No file selected."
        }), 400

    user_id = session.get('user_id')
    try:
        result = parse_syllabus_document(file, user_id)
        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Syllabus parsing failed: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to parse syllabus: {str(e)}"
        }), 500

@automation_bp.route('/api/automation/import-syllabus', methods=['POST'])
@login_required
def import_syllabus():
    """
    Atomically persists reviewed course outline and extracted tasks to the database.
    """
    data = request.get_json(silent=True) or {}
    user_id = session.get('user_id')

    try:
        result = batch_import_syllabus(user_id, data)
        return jsonify(result), 201
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Syllabus import failed: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to import syllabus: {str(e)}"
        }), 500

@automation_bp.route('/api/automation/rebalance-schedule', methods=['POST'])
@login_required
def rebalance_schedule():
    """
    Self-Healing Schedule Optimizer: Shifts missed revision blocks forward into conflict-free slots.
    """
    user_id = session.get('user_id')
    try:
        result = rebalance_missed_schedule(user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Schedule rebalance error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to rebalance timetable: {str(e)}"
        }), 500

@automation_bp.route('/api/automation/decompose-task', methods=['POST'])
@login_required
def decompose_task():
    """
    Generates 3 to 5 actionable sub-tasks with estimated hours and milestone deadlines.
    """
    data = request.get_json(silent=True) or {}
    user_id = session.get('user_id')

    task_title = data.get('task_title')
    due_date = data.get('due_date')
    course_name = data.get('course_name')

    try:
        result = decompose_task_with_ai(user_id, task_title, due_date, course_name)
        return jsonify(result), 200
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Task decomposition error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to decompose task: {str(e)}"
        }), 500

@automation_bp.route('/api/automation/commit-subtasks', methods=['POST'])
@login_required
def commit_subtasks():
    """
    Batch inserts verified sub-tasks into the student's task manager.
    """
    data = request.get_json(silent=True) or {}
    user_id = session.get('user_id')
    parent_task_id = data.get('parent_task_id')
    subtasks = data.get('subtasks', [])

    try:
        result = commit_subtasks_to_board(user_id, parent_task_id, subtasks)
        return jsonify(result), 201
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Subtask commit error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to create subtasks: {str(e)}"
        }), 500

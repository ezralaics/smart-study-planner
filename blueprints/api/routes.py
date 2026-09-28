from datetime import datetime
from flask import request, jsonify, session
from extensions import db
from models.user import User
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from utils.auth import login_required
from blueprints.api import api_bp

# ==========================================
# Course Endpoints
# ==========================================

@api_bp.route('/api/save-course', methods=['POST'])
@login_required
def save_course():
    data = request.get_json()
    if not data or not data.get('course_name'):
        return jsonify({"status": "error", "message": "Course name is required"}), 400

    try:
        existing_course = Course.query.filter_by(
            user_id=session['user_id'],
            course_name=data['course_name']
        ).first()

        if existing_course:
            existing_course.credits = int(data.get('credits', 3))
            existing_course.target_grade = float(data.get('target_grade', 80))
            if 'semester' in data:
                existing_course.semester = data['semester']
            
            for task in existing_course.tasks:
                db.session.delete(task)
            course_target = existing_course
        else:
            course_target = Course(
                course_name=data['course_name'],
                credits=int(data.get('credits', 3)),
                target_grade=float(data.get('target_grade', 80)),
                user_id=session['user_id']
            )
            if 'semester' in data:
                course_target.semester = data['semester']
            db.session.add(course_target)
            
        db.session.flush() 

        for t in data.get('tasks', []):
            due_date_obj = datetime.strptime(t['due_date'], '%Y-%m-%d').date() if t.get('due_date') else None
            db.session.add(Task(
                course_id=course_target.id,
                user_id=session['user_id'],
                task_name=t['task_name'],
                weightage=float(t['weightage']),
                due_date=due_date_obj,
                category='Component' 
            ))

        db.session.commit()
        return jsonify({"status": "success", "message": "The course saved successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/api/generate_plan')
@login_required
def generate_plan():
    courses = Course.query.filter_by(user_id=session['user_id']).order_by(Course.id.desc()).all()
    output = [c.to_dict() for c in courses]
    return jsonify(output)

@api_bp.route('/api/delete_subject', methods=['POST'])
@login_required
def delete_subject():
    data = request.get_json() or {}
    course_name = data.get('name')
    course = Course.query.filter_by(user_id=session['user_id'], course_name=course_name).first()
    if course:
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"message": "Course not found"}), 404

@api_bp.route('/api/update-course-grade/<string:course_id>', methods=['POST'])
@login_required
def update_course_grade(course_id):
    course = db.session.get(Course, course_id)
    if course and str(course.user_id) == str(session['user_id']):
        data = request.get_json() or {}
        course.actual_grade = data.get('actual_grade')
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@api_bp.route('/api/toggle-course-completion/<string:course_id>', methods=['POST'])
@login_required
def toggle_course_completion(course_id):
    course = db.session.get(Course, course_id)
    if course and str(course.user_id) == str(session['user_id']):
        course.is_completed = not course.is_completed
        
        # Auto-complete or un-complete all tasks linked to this course
        for task in course.tasks:
            task.is_completed = course.is_completed
            
        db.session.commit()
        return jsonify({"status": "success", "is_completed": course.is_completed})
    return jsonify({"error": "Not found"}), 404

# ==========================================
# Task Endpoints
# ==========================================

@api_bp.route('/api/get-all-tasks')
@login_required
def get_all_tasks():
    courses = Course.query.filter_by(user_id=session['user_id']).all()
    course_ids = [c.id for c in courses]
    
    tasks = Task.query.filter((Task.user_id == session['user_id']) | (Task.course_id.in_(course_ids))).all()
    tasks_list = [t.to_dict() for t in tasks]
    tasks_list.sort(key=lambda x: x['due_date'] if x['due_date'] else "9999-99-99")
    return jsonify(tasks_list)

@api_bp.route('/api/update-grade/<string:task_id>', methods=['POST'])
@login_required
def update_grade(task_id):
    task = db.session.get(Task, task_id)
    if task and (str(task.user_id) == str(session['user_id']) or (task.course and str(task.course.user_id) == str(session['user_id']))):
        data = request.get_json() or {}
        try:
            val = data.get('marks_obtained')
            task.marks_obtained = float(val) if val is not None else None
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"error": "Task not found"}), 404

@api_bp.route('/api/add-task', methods=['POST'])
@login_required
def add_task():
    data = request.get_json() or {}
    try:
        due_date_obj = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None
        cat = data.get('category', 'Other Task')
        c_id = data.get('course_id') if cat == 'Academic Task' else None
        
        new_task = Task(
            user_id=session['user_id'],
            course_id=c_id,
            task_name=data['task_name'],
            category=cat,
            due_date=due_date_obj,
            weightage=0
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/api/update-task/<string:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if task and (str(task.user_id) == str(session['user_id']) or (task.course and str(task.course.user_id) == str(session['user_id']))):
        data = request.get_json() or {}
        task.task_name = data.get('task_name', task.task_name)
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None
        
        if not task.weightage or task.weightage == 0:
            task.category = data.get('category', task.category)
            c_id = data.get('course_id')
            task.course_id = c_id if c_id and task.category == 'Academic Task' else None
            
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@api_bp.route('/api/delete-task/<string:task_id>', methods=['POST'])
@login_required
def delete_task_route(task_id):
    task = db.session.get(Task, task_id)
    if task and (str(task.user_id) == str(session['user_id']) or (task.course and str(task.course.user_id) == str(session['user_id']))):
        db.session.delete(task)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@api_bp.route('/api/toggle-task/<string:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = db.session.get(Task, task_id)
    if task and (str(task.user_id) == str(session['user_id']) or (task.course and str(task.course.user_id) == str(session['user_id']))):
        task.is_completed = not task.is_completed  
        db.session.commit()
        return jsonify({"status": "success", "is_completed": task.is_completed})
    return jsonify({"status": "error", "message": "Task not found"}), 404

# ==========================================
# Schedule Endpoints
# ==========================================

@api_bp.route('/api/save-schedule', methods=['POST'])
@login_required
def save_schedule():
    data = request.get_json() or {}
    try:
        start_d = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None
        end_d = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None

        if data.get('id'): # Update existing
            sched = db.session.get(Schedule, data['id'])
            if sched and str(sched.user_id) == str(session['user_id']):
                sched.title = data['title']
                sched.activity_type = data['activity_type']
                sched.day_of_week = data['day']
                sched.start_time = data['start_time']
                sched.end_time = data['end_time']
                sched.venue = data.get('venue', '')
                sched.details = data.get('details', '')
                sched.start_date = start_d
                sched.end_date = end_d
        else: 
            new_schedule = Schedule(
                user_id=session['user_id'],
                title=data['title'],
                activity_type=data['activity_type'],
                day_of_week=data['day'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                venue=data.get('venue', ''),
                details=data.get('details', ''),
                start_date=start_d,
                end_date=end_d
            )
            db.session.add(new_schedule)
            
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/api/get-schedules')
@login_required
def get_schedules():
    schedules = Schedule.query.filter_by(user_id=session['user_id']).all()
    return jsonify([s.to_dict() for s in schedules])

@api_bp.route('/api/delete-schedule/<string:id>', methods=['POST'])
@login_required
def delete_schedule(id):
    sched = db.session.get(Schedule, id)
    if sched and str(sched.user_id) == str(session['user_id']):
        db.session.delete(sched)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

# ==========================================
# Algorithmic Auto-Scheduler Endpoints
# ==========================================

@api_bp.route('/api/auto-schedule/preview', methods=['POST'])
@login_required
def auto_schedule_preview():
    from services.scheduler import generate_study_schedule
    data = request.get_json() or {}
    daily_hours = int(data.get('daily_hours', 2))
    preferred_window = data.get('preferred_window', 'evening')
    horizon_days = int(data.get('horizon_days', 14))
    education_level = data.get('education_level')

    result = generate_study_schedule(
        user_id=session['user_id'],
        daily_hours=daily_hours,
        preferred_window=preferred_window,
        horizon_days=horizon_days,
        education_level=education_level
    )
    return jsonify(result)

@api_bp.route('/api/settings/education-level', methods=['POST'])
@login_required
def update_education_level():
    data = request.get_json() or {}
    level = data.get('education_level', '').strip().lower()
    from services.tier_service import VALID_TIERS, get_tier_config
    if level not in VALID_TIERS:
        return jsonify({
            "status": "error",
            "message": f"Invalid education level. Must be one of: {', '.join(VALID_TIERS)}"
        }), 400

    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user.education_level = level
    session['education_level'] = level
    try:
        db.session.commit()
        tier_info = get_tier_config(level)
        return jsonify({
            "status": "success",
            "message": f"Education tier updated to {tier_info['name']}",
            "data": {
                "education_level": level,
                "tier": tier_info
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route('/api/auto-schedule/apply', methods=['POST'])
@login_required
def auto_schedule_apply():
    from services.scheduler import apply_study_schedule
    data = request.get_json() or {}
    sessions = data.get('sessions', [])
    if not sessions:
        return jsonify({"status": "error", "message": "No sessions provided to apply."}), 400

    created_count = apply_study_schedule(session['user_id'], sessions)
    return jsonify({
        "status": "success",
        "count": created_count,
        "created_count": created_count,
        "message": f"Successfully synced {created_count} revision session(s) into your timetable and calendar!"
    })

# ==========================================
# Data Export & Management Endpoints
# ==========================================

@api_bp.route('/api/export-data')
@login_required
def export_data():
    from models.user import User
    from flask import Response
    import json
    from datetime import timezone

    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    courses = Course.query.filter_by(user_id=user.id).all()
    tasks = Task.query.filter_by(user_id=user.id).all()
    schedules = Schedule.query.filter_by(user_id=user.id).all()

    payload = {
        "export_metadata": {
            "system": "Smart Study Planner",
            "version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "user_profile": user.to_dict(),
        "courses": [c.to_dict() for c in courses],
        "tasks": [t.to_dict() for t in tasks],
        "schedules": [
            {
                "id": str(s.id),
                "title": s.title,
                "day_of_week": s.day_of_week,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "venue": s.venue,
                "activity_type": s.activity_type,
                "created_at": s.created_at.isoformat() if s.created_at else None
            } for s in schedules
        ]
    }

    json_str = json.dumps(payload, indent=2)
    filename = f"study_planner_backup_{user.username}.json"
    
    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@api_bp.route('/api/settings/clear-completed-tasks', methods=['POST'])
@login_required
def clear_completed_tasks():
    user_id = session['user_id']
    completed_tasks = Task.query.filter_by(user_id=user_id, is_completed=True).all()
    count = len(completed_tasks)
    for t in completed_tasks:
        db.session.delete(t)
    db.session.commit()
    return jsonify({
        "status": "success",
        "deleted_count": count,
        "message": f"Successfully cleared {count} completed task(s)."
    })

# ==========================================
# Direct Messages Endpoints
# ==========================================

@api_bp.route('/api/dm/unread-count')
@login_required
def dm_unread_count():
    from services.message_service import get_unread_message_count
    count = get_unread_message_count(session['user_id'])
    return jsonify({
        "status": "success",
        "unread_count": count
    })

@api_bp.route('/api/dm/conversations')
@login_required
def dm_conversations():
    from services.message_service import get_user_conversations
    conversations = get_user_conversations(session['user_id'])
    return jsonify({
        "status": "success",
        "data": conversations
    })

@api_bp.route('/api/dm/thread')
@login_required
def dm_thread():
    from services.message_service import get_conversation_thread
    target = request.args.get('email') or request.args.get('user_id')
    if not target:
        return jsonify({"status": "error", "message": "Email or user ID is required."}), 400

    data, err = get_conversation_thread(session['user_id'], target)
    if err:
        return jsonify({"status": "error", "message": err}), 404

    return jsonify({
        "status": "success",
        "data": data
    })

@api_bp.route('/api/dm/send', methods=['POST'])
@login_required
def dm_send():
    from services.message_service import send_direct_message
    payload = request.get_json() or {}
    recipient = payload.get('recipient_email') or payload.get('recipient_id')
    content = payload.get('content')

    if not recipient or not content:
        return jsonify({"status": "error", "message": "Recipient and message content are required."}), 400

    message, err = send_direct_message(session['user_id'], recipient, content)
    if err:
        return jsonify({"status": "error", "message": err}), 400

    return jsonify({
        "status": "success",
        "message": "Message sent successfully.",
        "data": message
    }), 201

@api_bp.route('/api/dm/search-classmates')
@login_required
def dm_search_classmates():
    from services.message_service import search_classmates
    q = request.args.get('q', '')
    users = search_classmates(session['user_id'], q)
    return jsonify({
        "status": "success",
        "data": users
    })



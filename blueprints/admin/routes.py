from flask import render_template, request, jsonify, session
from extensions import db
from models.user import User
from models.course import Course
from models.task import Task
from utils.auth import role_required
from blueprints.admin import admin_bp

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    total_users = User.query.count()
    student_count = User.query.filter_by(role='student').count()
    educator_count = User.query.filter_by(role='educator').count()
    admin_count = User.query.filter_by(role='admin').count()
    total_courses = Course.query.count()
    total_tasks = Task.query.count()

    recent_users = User.query.order_by(User.id.desc()).limit(8).all()

    return render_template(
        'admin/dashboard.html',
        active_page='admin_dashboard',
        total_users=total_users,
        student_count=student_count,
        educator_count=educator_count,
        admin_count=admin_count,
        total_courses=total_courses,
        total_tasks=total_tasks,
        recent_users=recent_users
    )

@admin_bp.route('/users')
@role_required('admin')
def users():
    users_list = User.query.order_by(User.id.desc()).all()
    return render_template(
        'admin/users.html',
        active_page='admin_users',
        users=users_list
    )

# ==========================================
# Admin API Endpoints
# ==========================================

@admin_bp.route('/api/users')
@role_required('admin')
def get_users_api():
    users_list = User.query.order_by(User.id.desc()).all()
    return jsonify([u.to_dict() for u in users_list])

@admin_bp.route('/api/update-role', methods=['POST'])
@role_required('admin')
def update_role():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    new_role = data.get('role', '').strip().lower()

    if new_role not in ['student', 'educator', 'admin']:
        return jsonify({"status": "error", "message": "Invalid role specified"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Prevent admin from accidentally demoting themselves
    if user.id == session['user_id'] and new_role != 'admin':
        return jsonify({"status": "error", "message": "You cannot demote your own admin account"}), 400

    user.role = new_role
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": f"Updated role for {user.username} to {new_role.capitalize()}."
    })

@admin_bp.route('/api/delete-user/<int:user_id>', methods=['POST'])
@role_required('admin')
def delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({"status": "error", "message": "You cannot delete your own account"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"status": "success", "message": f"User {user.username} deleted successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

from flask import render_template, session, redirect, url_for
from utils.auth import login_required
from blueprints.main import main_bp

@main_bp.route('/')
def home():
    if 'user_id' in session:
        role = session.get('role', 'student')
        if role == 'educator':
            return redirect(url_for('educator.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Smart router: routes educators & admins to dedicated portals, serves student dashboard directly."""
    role = session.get('role', 'student')
    if role == 'educator':
        return redirect(url_for('educator.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return render_template('index.html', active_page='student_dashboard')

# Backward-compatible aliases pointing to student module views
@main_bp.route('/calendar')
@login_required
def calendar_page():
    return render_template('calendar.html', active_page='student_calendar')

@main_bp.route('/study-planner')
@login_required
def study_planner():
    return render_template('study_planner.html', active_page='student_planner')

@main_bp.route('/classes')
@login_required
def classes_page():
    return render_template('classes.html', active_page='student_classes')

@main_bp.route('/tasks')
@login_required
def tasks_page():
    return render_template('tasks.html', active_page='student_tasks')

@main_bp.route('/grades')
@login_required
def grades_page():
    return render_template('grades.html', active_page='student_grades')


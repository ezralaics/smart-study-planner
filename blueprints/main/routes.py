from flask import render_template
from utils.auth import login_required
from blueprints.main import main_bp

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', active_page='dashboard')

@main_bp.route('/calendar')
@login_required
def calendar_page():
    return render_template('calendar.html', active_page='calendar')

@main_bp.route('/study-planner')
@login_required
def study_planner():
    return render_template('study_planner.html', active_page='study_planner')

@main_bp.route('/classes')
@login_required
def classes_page():
    return render_template('classes.html', active_page='classes')

@main_bp.route('/tasks')
@login_required
def tasks_page():
    return render_template('tasks.html', active_page='tasks')

@main_bp.route('/grades')
@login_required
def grades_page():
    return render_template('grades.html', active_page='grades')

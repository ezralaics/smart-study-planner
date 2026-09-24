from flask import render_template, session, redirect, url_for
from utils.auth import role_required
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from blueprints.student import student_bp

@student_bp.route('/dashboard')
@role_required('student', 'admin')
def dashboard():
    """Student Portal: Academic Dashboard & Workload Overview."""
    user_id = session['user_id']
    courses = Course.query.filter_by(user_id=user_id).all()
    tasks = Task.query.join(Course).filter(Course.user_id == user_id).all()
    schedules = Schedule.query.filter_by(user_id=user_id).all()

    return render_template(
        'index.html',
        active_page='student_dashboard',
        courses=courses,
        tasks=tasks,
        schedules=schedules
    )

@student_bp.route('/study-planner')
@role_required('student', 'admin')
def study_planner():
    """Student Portal: Course Registration & Intelligent Auto-Scheduler."""
    return render_template('study_planner.html', active_page='student_planner')

@student_bp.route('/calendar')
@role_required('student', 'admin')
def calendar_page():
    """Student Portal: Master Timetable & Revision Sessions."""
    return render_template('calendar.html', active_page='student_calendar')

@student_bp.route('/courses')
@student_bp.route('/classes')
@role_required('student', 'admin')
def courses_page():
    """Student Portal: Registered Academic Modules."""
    return render_template('classes.html', active_page='student_classes')

@student_bp.route('/tasks')
@role_required('student', 'admin')
def tasks_page():
    """Student Portal: Task, Assignment & Exam Management."""
    return render_template('tasks.html', active_page='student_tasks')

@student_bp.route('/grades')
@role_required('student', 'admin')
def grades_page():
    """Student Portal: Target Grade Simulator & GPA Tracker."""
    return render_template('grades.html', active_page='student_grades')

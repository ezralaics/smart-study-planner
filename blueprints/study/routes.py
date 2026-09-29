"""
OmniSuite Domain Blueprint: Study & Academics
Encapsulates Academic Course, Task, Schedule, and Planner endpoints.
"""
from flask import render_template, session, redirect, url_for
from utils.auth import login_required
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from blueprints.study import study_bp

@study_bp.route('')
@study_bp.route('/')
@login_required
def study_home():
    """Study Hub entry point: redirects to student academic dashboard."""
    session['active_workspace'] = 'academics'
    return redirect(url_for('student.dashboard'))

@study_bp.route('/planner')
@login_required
def study_planner_view():
    """Study Hub: Intelligent Course Registration & Revision Scheduler."""
    session['active_workspace'] = 'academics'
    return render_template('study_planner.html', active_page='student_planner')

@study_bp.route('/calendar')
@login_required
def calendar_view():
    """Study Hub: Master Timetable & Revision Sessions."""
    session['active_workspace'] = 'academics'
    return render_template('calendar.html', active_page='student_calendar')

@study_bp.route('/courses')
@login_required
def courses_view():
    """Study Hub: Registered Academic Modules."""
    session['active_workspace'] = 'academics'
    return render_template('classes.html', active_page='student_classes')

@study_bp.route('/tasks')
@login_required
def tasks_view():
    """Study Hub: Tasks, Deadlines & Assignment Tracker."""
    session['active_workspace'] = 'academics'
    return render_template('tasks.html', active_page='student_tasks')

@study_bp.route('/grades')
@login_required
def grades_view():
    """Study Hub: Target Grade Simulator & GPA Tracker."""
    session['active_workspace'] = 'academics'
    return render_template('grades.html', active_page='student_grades')

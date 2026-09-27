from flask import render_template, session, redirect, url_for, request, flash
from extensions import db
from models.user import User
from utils.auth import login_required
from blueprints.main import main_bp

@main_bp.route('/')
def home():
    if 'user_id' in session:
        if not session.get('is_profile_completed', False) and not session.get('skipped_onboarding'):
            return redirect(url_for('main.complete_profile'))
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
    if not session.get('is_profile_completed', False) and not session.get('skipped_onboarding'):
        return redirect(url_for('main.complete_profile'))
    role = session.get('role', 'student')
    if role == 'educator':
        return redirect(url_for('educator.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return render_template('index.html', active_page='student_dashboard')

# ==========================================
# Onboarding & Profile Management
# ==========================================

@main_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        user.phone_number = request.form.get('phone_number', '').strip() or None
        user.bio = request.form.get('bio', '').strip() or None

        if user.role == 'student':
            user.major_programme = request.form.get('major_programme', '').strip() or None
            user.academic_year = request.form.get('academic_year', '').strip() or None
            user.current_semester = request.form.get('current_semester', '').strip() or None
            cgpa_raw = request.form.get('target_cgpa', '').strip()
            if cgpa_raw:
                try:
                    cgpa = float(cgpa_raw)
                    if cgpa < 0.0 or cgpa > 4.0:
                        return "Target CGPA must be between 0.00 and 4.00", 400
                    user.target_cgpa = round(cgpa, 2)
                except ValueError:
                    return "Invalid Target CGPA format", 400
            else:
                user.target_cgpa = None

        elif user.role == 'educator':
            user.title_designation = request.form.get('title_designation', '').strip() or None
            user.faculty_department = request.form.get('faculty_department', '').strip() or None
            user.office_location = request.form.get('office_location', '').strip() or None

        elif user.role == 'admin':
            user.admin_department = request.form.get('admin_department', '').strip() or None
            user.staff_id = request.form.get('staff_id', '').strip() or None

        user.is_profile_completed = True
        session['is_profile_completed'] = True
        db.session.commit()

        flash("Profile completed successfully! Welcome to Smart Study Planner.", "success")
        if user.role == 'educator':
            return redirect(url_for('educator.dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    return render_template('onboarding.html', user=user)

@main_bp.route('/skip-onboarding')
@login_required
def skip_onboarding():
    session['skipped_onboarding'] = True
    role = session.get('role', 'student')
    if role == 'educator':
        return redirect(url_for('educator.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('student.dashboard'))

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        if fullname:
            user.fullname = fullname
            session['username'] = fullname

        avatar_url = request.form.get('avatar_url', '').strip()
        if avatar_url:
            user.avatar_url = avatar_url
            session['avatar_url'] = avatar_url

        user.phone_number = request.form.get('phone_number', '').strip() or None
        user.bio = request.form.get('bio', '').strip() or None

        if user.role == 'student':
            user.major_programme = request.form.get('major_programme', '').strip() or None
            user.academic_year = request.form.get('academic_year', '').strip() or None
            user.current_semester = request.form.get('current_semester', '').strip() or None
            cgpa_raw = request.form.get('target_cgpa', '').strip()
            if cgpa_raw:
                try:
                    cgpa = float(cgpa_raw)
                    if cgpa < 0.0 or cgpa > 4.0:
                        return render_template('profile.html', user=user, active_page='profile', error="Target CGPA must be between 0.00 and 4.00"), 400
                    user.target_cgpa = round(cgpa, 2)
                except ValueError:
                    return render_template('profile.html', user=user, active_page='profile', error="Invalid Target CGPA format"), 400
            else:
                user.target_cgpa = None

        elif user.role == 'educator':
            user.title_designation = request.form.get('title_designation', '').strip() or None
            user.faculty_department = request.form.get('faculty_department', '').strip() or None
            user.office_location = request.form.get('office_location', '').strip() or None

        elif user.role == 'admin':
            user.admin_department = request.form.get('admin_department', '').strip() or None
            user.staff_id = request.form.get('staff_id', '').strip() or None

        user.is_profile_completed = True
        session['is_profile_completed'] = True
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('main.profile_page'))

    return render_template('profile.html', user=user, active_page='profile')

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


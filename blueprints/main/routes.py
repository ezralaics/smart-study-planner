from flask import render_template, session, redirect, url_for, request, flash, send_from_directory, current_app
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
    """OmniLife OS: Today's Command Center aggregating Academics, Life, Finance, Journal & Career."""
    if not session.get('is_profile_completed', False) and not session.get('skipped_onboarding'):
        return redirect(url_for('main.complete_profile'))
    role = session.get('role', 'student')
    if role == 'educator':
        return redirect(url_for('educator.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return render_template('dashboard.html', active_page='command_center')

@main_bp.route('/workspace/<string:workspace_name>')
@login_required
def switch_workspace(workspace_name):
    """Workspace Switcher: updates active workspace in session and redirects to module overview."""
    from core.registry import get_module
    key = workspace_name.lower().strip()
    mod = get_module(key)
    if mod:
        session['active_workspace'] = key
        return redirect(mod.url)
    
    valid_workspaces = {
        'academics': '/student/dashboard',
        'life': '/life',
        'finance': '/finance',
        'reports': '/reports',
        'journal': '/journal',
        'career': '/career'
    }
    target = valid_workspaces.get(key)
    if target:
        session['active_workspace'] = key
        return redirect(target)
    return redirect(url_for('main.dashboard'))

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
            edu_lvl = request.form.get('education_level', '').strip().lower()
            if edu_lvl in ['primary', 'secondary', 'university', 'general']:
                user.education_level = edu_lvl
                session['education_level'] = edu_lvl
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
            edu_lvl = request.form.get('education_level', '').strip().lower()
            if edu_lvl in ['primary', 'secondary', 'university', 'general']:
                user.education_level = edu_lvl
                session['education_level'] = edu_lvl
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

# ==========================================
# Application Settings & Preferences
# ==========================================

@main_bp.route('/settings')
@login_required
def settings_page():
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('settings.html', user=user, active_page='settings')

@main_bp.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_password or not new_password or not confirm_password:
        flash("All password fields are required.", "danger")
        return render_template('settings.html', user=user, active_page='settings', password_error="All password fields are required."), 400

    if not user.check_password(current_password):
        flash("Current password does not match our records.", "danger")
        return render_template('settings.html', user=user, active_page='settings', password_error="Current password does not match our records."), 400

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return render_template('settings.html', user=user, active_page='settings', password_error="New passwords do not match."), 400

    if len(new_password) < 6:
        flash("Password must be at least 6 characters long.", "danger")
        return render_template('settings.html', user=user, active_page='settings', password_error="Password must be at least 6 characters long."), 400

    user.set_password(new_password)
    db.session.commit()

    flash("Your password has been updated successfully!", "success")
    return redirect(url_for('main.settings_page'))

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



@main_bp.route('/manifest.json')
def manifest():
    return send_from_directory(current_app.static_folder, 'manifest.json', mimetype='application/json')

@main_bp.route('/sw.js')
def service_worker():
    response = send_from_directory(current_app.static_folder, 'sw.js', mimetype='application/javascript')
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@main_bp.route('/offline')
def offline():
    return render_template('offline.html')

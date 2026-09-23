from flask import render_template, request, jsonify, redirect, url_for, session
from extensions import db
from models.user import User
from blueprints.auth import auth_bp
from services.demo_seeder import seed_demo_user

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        student_type = request.form.get('student_type', 'Other')
        role = request.form.get('role', 'student').strip().lower()
        if role not in ['student', 'educator']:
            role = 'student'
            
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password or not email or not fullname:
            return "Please fill in all required fields.", 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return "User already exists", 400

        try:
            new_user = User(
                fullname=fullname,
                email=email,
                username=username,
                student_type=student_type,
                role=role
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration Error: {e}")
            return "There was an error creating your account.", 500

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.fullname
            session['role'] = getattr(user, 'role', 'student')
            
            # Smart redirect based on user role
            if session['role'] == 'educator':
                return redirect(url_for('educator.dashboard'))
            elif session['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.dashboard'))
            
        return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Instant 1-click authentication for recruiters and evaluators."""
    if role not in ['student', 'educator', 'admin']:
        role = 'student'

    user = seed_demo_user(role)
    session.clear()
    session['user_id'] = user.id
    session['username'] = user.fullname
    session['role'] = user.role

    if user.role == 'educator':
        return redirect(url_for('educator.dashboard'))
    elif user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/current-user')
def current_user():
    if 'user_id' not in session:
        return jsonify({}), 401
    user = User.query.get(session['user_id'])
    if user:
        return jsonify({
            "name": user.fullname,
            "username": user.username,
            "student_type": user.student_type,
            "role": getattr(user, 'role', 'student')
        })
    return jsonify({}), 404

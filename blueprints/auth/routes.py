import os
import secrets
from urllib.parse import urlencode
import requests
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import render_template, request, jsonify, redirect, url_for, session, current_app
from extensions import db
from models.user import User
from blueprints.auth import auth_bp
from services.demo_seeder import seed_demo_user

def generate_oauth_state(secret_key):
    """Generates a cryptographically signed OAuth state token containing a random nonce."""
    s = URLSafeTimedSerializer(secret_key, salt='google-oauth-state')
    return s.dumps({'nonce': secrets.token_hex(16)})

def verify_oauth_state(state, secret_key, max_age=600):
    """Verifies a signed state token. Returns (is_valid, message)."""
    if not state:
        return False, "State parameter missing"
    s = URLSafeTimedSerializer(secret_key, salt='google-oauth-state')
    try:
        s.loads(state, max_age=max_age)
        return True, "Valid"
    except SignatureExpired:
        return False, "Google authorization session expired. Please try again."
    except BadSignature:
        return False, "Google authorization state signature mismatch or tampered."
    except Exception as e:
        return False, str(e)

def get_google_redirect_uri():
    """Gets the exact redirect URI to match Google Cloud Console configuration."""
    configured = current_app.config.get('GOOGLE_REDIRECT_URI')
    if configured and configured.strip():
        return configured.strip()
    return url_for('auth.google_callback', _external=True)


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

    client_id = current_app.config.get('GOOGLE_CLIENT_ID', '')
    return render_template('register.html', google_client_id=client_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID', '')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = str(user.id)
            session['username'] = user.fullname
            session['role'] = getattr(user, 'role', 'student')
            
            # Smart redirect based on user role
            if session['role'] == 'educator':
                return redirect(url_for('educator.dashboard'))
            elif session['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
            
        return render_template('login.html', error="Invalid Credentials", google_client_id=client_id)

    return render_template('login.html', google_client_id=client_id)

@auth_bp.route('/demo-login/<role>')
def demo_login(role):
    """Instant 1-click authentication for recruiters and evaluators."""
    if role not in ['student', 'educator', 'admin']:
        role = 'student'

    user = seed_demo_user(role)
    session.clear()
    session['user_id'] = str(user.id)
    session['username'] = user.fullname
    session['role'] = user.role

    if user.role == 'educator':
        return redirect(url_for('educator.dashboard'))
    elif user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('student.dashboard'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/current-user')
def current_user():
    if 'user_id' not in session:
        return jsonify({}), 401
    user = db.session.get(User, session['user_id'])
    if user:
        return jsonify({
            "name": user.fullname,
            "username": user.username,
            "student_type": user.student_type,
            "role": getattr(user, 'role', 'student')
        })
    return jsonify({}), 404

# ==========================================
# Google OAuth 2.0 Sign-In
# ==========================================

@auth_bp.route('/auth/google')
@auth_bp.route('/login/google')
def google_login():
    """Initiates Google OAuth 2.0 flow or Sandbox if not configured."""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    
    # If Google Client ID is not configured, redirect to Sandbox & Setup Guide
    if not client_id or client_id.strip() == '':
        return redirect(url_for('auth.google_sandbox'))
    
    secret_key = current_app.config.get('SECRET_KEY', 'fyp_secret_key_2026')
    state = generate_oauth_state(secret_key)
    session['oauth_state'] = state
    
    redirect_uri = get_google_redirect_uri()
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'online',
        'prompt': 'select_account'
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    resp = redirect(google_auth_url)
    resp.set_cookie('oauth_state', state, max_age=600, httponly=True, samesite='Lax')
    return resp

@auth_bp.route('/auth/google/callback')
@auth_bp.route('/login/google/callback')
def google_callback():
    """Handles OAuth 2.0 callback from Google."""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID', '')
    
    # Check if Google returned an error (e.g. user cancelled consent)
    oauth_error = request.args.get('error')
    if oauth_error:
        if oauth_error == 'access_denied':
            return render_template('login.html', error="Google Sign-In was cancelled.", google_client_id=client_id)
        return render_template('login.html', error=f"Google authorization failed: {oauth_error}", google_client_id=client_id)

    state = request.args.get('state')
    expected_session_state = session.get('oauth_state')
    expected_cookie_state = request.cookies.get('oauth_state')

    # Multi-layer CSRF validation:
    # 1. Matches session state (if session cookie was preserved)
    # 2. OR matches fallback cookie state (if session storage cycled)
    # 3. OR verified cryptographically by server's SECRET_KEY (immune to 127.0.0.1 vs localhost domain shifts)
    secret_key = current_app.config.get('SECRET_KEY', 'fyp_secret_key_2026')
    is_valid = False
    
    if (expected_session_state and state == expected_session_state) or \
       (expected_cookie_state and state == expected_cookie_state):
        is_valid = True
    else:
        sig_ok, reason = verify_oauth_state(state, secret_key)
        if sig_ok:
            is_valid = True
        else:
            return render_template('login.html', error=f"Google authentication failed: {reason}", google_client_id=client_id)

    code = request.args.get('code')
    if not code:
        return render_template('login.html', error="Google authorization code missing.", google_client_id=client_id)
    
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = get_google_redirect_uri()
    
    try:
        token_res = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            },
            timeout=10
        )
        token_data = token_res.json()
        access_token = token_data.get('access_token')
        if not access_token:
            return render_template('login.html', error=f"Google token exchange failed: {token_data.get('error_description', 'Invalid token response')}", google_client_id=client_id)
        
        userinfo_res = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        userinfo = userinfo_res.json()
        return process_google_user(userinfo)
    except Exception as e:
        return render_template('login.html', error=f"Error connecting to Google: {str(e)}", google_client_id=client_id)

def process_google_user(userinfo):
    """Processes verified Google user profile, creates account if needed, logs in."""
    google_id = userinfo.get('sub')
    email = userinfo.get('email')
    name = userinfo.get('name') or email.split('@')[0]
    picture = userinfo.get('picture')

    if not email:
        return render_template('login.html', error="Unable to obtain verified email from Google.")

    # Find existing user by google_id or email
    user = User.query.filter((User.google_id == google_id) | (User.email == email)).first()

    if not user:
        # Generate unique username
        base_username = email.split('@')[0].replace('.', '_')
        username = base_username
        suffix = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{suffix}"
            suffix += 1

        user = User(
            fullname=name,
            email=email,
            username=username,
            student_type='IT',
            role='student',
            google_id=google_id,
            avatar_url=picture
        )
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        db.session.commit()
    else:
        # Update existing user's Google ID & avatar if not set
        if not user.google_id:
            user.google_id = google_id
        if picture and not user.avatar_url:
            user.avatar_url = picture
        db.session.commit()

    # Establish session
    session.clear()
    session['user_id'] = str(user.id)
    session['username'] = user.fullname
    session['role'] = getattr(user, 'role', 'student')
    session['avatar_url'] = user.avatar_url

    if user.role == 'educator':
        return redirect(url_for('educator.dashboard'))
    elif user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('student.dashboard'))

@auth_bp.route('/auth/google/sandbox', methods=['GET', 'POST'])
def google_sandbox():
    """
    Simulated Google OAuth 2.0 Sandbox.
    Allows testing Google Sign-In immediately without configuring Google Cloud Console keys.
    """
    if request.method == 'POST':
        email = request.form.get('email', 'alex.student@gmail.com').strip()
        name = request.form.get('name', 'Alex Johnson').strip()
        role = request.form.get('role', 'student')
        
        simulated_userinfo = {
            'sub': f'google_sub_{abs(hash(email)) % 10000000}',
            'email': email,
            'name': name,
            'picture': 'https://lh3.googleusercontent.com/a/default-user=s96-c'
        }
        res = process_google_user(simulated_userinfo)
        if 'user_id' in session:
            user = db.session.get(User, session['user_id'])
            if user:
                user.role = role
                session['role'] = role
                db.session.commit()
                if role == 'educator':
                    return redirect(url_for('educator.dashboard'))
                elif role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('student.dashboard'))
        return res

    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    return render_template('auth/google_sandbox.html', client_id=client_id)

@auth_bp.route('/api/auth/google-verify-token', methods=['POST'])
def google_verify_token():
    """
    Verifies Google ID Token sent by Google Identity Services (GIS).
    Used by real websites with the Google One Tap / Sign In with Google button.
    """
    data = request.get_json() or {}
    token = data.get('credential')
    if not token:
        return jsonify({"status": "error", "message": "Missing credential token"}), 400

    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        # Verify with Google's public cryptographic certs
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id if client_id else None)
        
        userinfo = {
            'sub': idinfo.get('sub'),
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture')
        }
        process_google_user(userinfo)
        
        target_url = '/student/dashboard'
        if session.get('role') == 'educator':
            target_url = '/educator/dashboard'
        elif session.get('role') == 'admin':
            target_url = '/admin/dashboard'

        return jsonify({
            "status": "success",
            "message": "Authenticated with Google successfully.",
            "redirect_url": target_url
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Token verification failed: {str(e)}"}), 401



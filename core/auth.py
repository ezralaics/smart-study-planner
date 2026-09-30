"""Core Authentication & RBAC Authorization for Life Planner OS (OmniLife).
Provides uniform session guards and role decorators for all domain modules.
"""
from functools import wraps
from flask import session, redirect, url_for, jsonify, request, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "Unauthorized. Please login first."}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Restricts access to users with one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({"status": "error", "message": "Unauthorized. Please login first."}), 401
                return redirect(url_for('auth.login'))
            user_role = session.get('role', 'student')
            if user_role not in allowed_roles:
                if request.path.startswith('/api/'):
                    return jsonify({"status": "error", "message": "Forbidden. Insufficient permissions."}), 403
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

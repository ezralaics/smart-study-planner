import os
from flask import Flask
from config import Config
from extensions import db
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.api import api_bp
from blueprints.student import student_bp
from blueprints.educator import educator_bp
from blueprints.admin import admin_bp
from blueprints.ai import ai_bp
from blueprints.life import life_bp
from blueprints.finance import finance_bp
from blueprints.journal import journal_bp
from blueprints.career import career_bp
from blueprints.study import study_bp

# Import models so SQLAlchemy binds all tables during db.create_all()
import models  # noqa: F401

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(educator_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(life_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(study_bp)

    with app.app_context():
        try:
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            # Automatic Legacy Integer -> UUID Schema Migration:
            # If the database has legacy INTEGER primary keys on users, drop the legacy test tables
            # so db.create_all() initializes the complete, unified UUID enterprise schema without type conflicts.
            if 'users' in existing_tables:
                id_col = next((c for c in inspector.get_columns('users') if c['name'] == 'id'), None)
                if id_col and 'INT' in str(id_col.get('type', '')).upper():
                    app.logger.warning("Detected legacy INTEGER database schema. Upgrading database to production UUID schema...")
                    with db.engine.connect() as conn:
                        conn.execute(text("DROP TABLE IF EXISTS tasks, schedules, courses, users CASCADE;"))
                        conn.commit()

            # Initialize all tables with UUID primary and foreign keys
            db.create_all()

            # Safe incremental column additions for future schema evolutions
            inspector = inspect(db.engine)
            if 'users' in inspector.get_table_names():
                columns = [c['name'] for c in inspector.get_columns('users')]
                with db.engine.connect() as conn:
                    if 'role' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'student';"))
                    if 'google_id' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(100) UNIQUE;"))
                    if 'avatar_url' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(255);"))
                    if 'updated_at' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"))
                    if 'is_profile_completed' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_profile_completed BOOLEAN DEFAULT FALSE;"))
                    if 'phone_number' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(30);"))
                    if 'bio' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;"))
                    if 'major_programme' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS major_programme VARCHAR(100);"))
                    if 'academic_year' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS academic_year VARCHAR(20);"))
                    if 'current_semester' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS current_semester VARCHAR(20);"))
                    if 'target_cgpa' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS target_cgpa FLOAT;"))
                    if 'faculty_department' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS faculty_department VARCHAR(100);"))
                    if 'office_location' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS office_location VARCHAR(100);"))
                    if 'title_designation' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS title_designation VARCHAR(50);"))
                    if 'admin_department' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS admin_department VARCHAR(100);"))
                    if 'staff_id' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS staff_id VARCHAR(50);"))
                    if 'education_level' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS education_level VARCHAR(20) DEFAULT 'university';"))
                    conn.commit()
        except Exception as e:
            app.logger.error(f"Database connection or migration notice: {e}", exc_info=True)

    @app.context_processor
    def inject_tier_context():
        from flask import session, request
        from services.tier_service import get_tier_config, get_all_tiers
        level = session.get('education_level', 'university')

        # Derive active workspace from request path or session
        active_ws = session.get('active_workspace', 'academics')
        path = request.path
        if path.startswith('/life'):
            active_ws = 'life'
        elif path.startswith('/finance'):
            active_ws = 'finance'
        elif path.startswith('/journal'):
            active_ws = 'journal'
        elif path.startswith('/career'):
            active_ws = 'career'
        elif path in ['/student/dashboard', '/study-planner', '/calendar', '/courses', '/classes', '/tasks', '/grades', '/study-assistant']:
            active_ws = 'academics'

        workspaces_list = [
            {
                'key': 'academics',
                'name': 'Study & Academics',
                'short_name': 'Academics',
                'icon': 'bi-mortarboard-fill',
                'color': '#0d6efd',
                'url': '/student/dashboard',
                'badge': 'Academic Modules'
            },
            {
                'key': 'life',
                'name': 'Life & Daily Habits',
                'short_name': 'Habits',
                'icon': 'bi-flower1',
                'color': '#198754',
                'url': '/life',
                'badge': 'Habits & Wellness'
            },
            {
                'key': 'finance',
                'name': 'Financial Planner',
                'short_name': 'Finances',
                'icon': 'bi-wallet2',
                'color': '#0dcaf0',
                'url': '/finance',
                'badge': 'Budget & Expenses'
            },
            {
                'key': 'journal',
                'name': 'Journal & Reflection',
                'short_name': 'Journal',
                'icon': 'bi-journal-richtext',
                'color': '#6f42c1',
                'url': '/journal',
                'badge': 'Diary & Moods'
            },
            {
                'key': 'career',
                'name': 'Career & Job Tracker',
                'short_name': 'Career',
                'icon': 'bi-briefcase-fill',
                'color': '#fd7e14',
                'url': '/career',
                'badge': 'Applications Kanban'
            }
        ]

        current_ws = next((w for w in workspaces_list if w['key'] == active_ws), workspaces_list[0])

        return {
            'current_tier': get_tier_config(level),
            'education_tiers': get_all_tiers(),
            'active_workspace': active_ws,
            'current_workspace': current_ws,
            'workspaces_list': workspaces_list
        }

    @app.route('/api/debug-status')
    def debug_status():
        import traceback
        from flask import jsonify, request
        info = {}
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            info['tables'] = inspector.get_table_names()
            if 'users' in info['tables']:
                info['users_columns'] = [{'name': c['name'], 'type': str(c['type'])} for c in inspector.get_columns('users')]
                with db.engine.connect() as conn:
                    info['users_count'] = conn.execute(text("SELECT count(*) FROM users")).scalar()
                    row = conn.execute(text("SELECT id, username, role FROM users LIMIT 1")).fetchone()
                    info['first_user_raw'] = {'id': str(row[0]), 'username': row[1], 'role': row[2]} if row else None
            
            from models.user import User
            user = User.query.first()
            info['first_user_orm'] = {'id': str(user.id), 'username': user.username, 'role': user.role} if user else None
            return jsonify({'status': 'ok', 'info': info})
        except Exception as e:
            return jsonify({'status': 'error', 'error': str(e), 'traceback': traceback.format_exc(), 'info': info}), 500

    @app.errorhandler(500)
    def handle_500(e):
        import traceback
        from flask import request
        app.logger.error(f"500 Server Error: {e}\n{traceback.format_exc()}")
        if request.args.get('debug') == '1':
            return f"<pre style='color:red; background:#fee; padding:20px; font-size:14px;'>{traceback.format_exc()}</pre>", 500, {'Content-Type': 'text/html'}
        return render_template('login.html', error="An unexpected system error occurred. Please try again.")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



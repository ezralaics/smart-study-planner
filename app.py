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

    with app.app_context():
        try:
            db.create_all()
            # Auto-migrate schema: ensure columns added in updates exist in existing databases
            from sqlalchemy import text, inspect
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
                    conn.commit()
        except Exception as e:
            app.logger.warning(f"Database connection or migration notice: {e}")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
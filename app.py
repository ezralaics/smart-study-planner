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
        except Exception as e:
            app.logger.warning(f"Database connection notice on startup: {e}")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
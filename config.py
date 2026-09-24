import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fyp_secret_key_2026')
    
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:admin123@localhost:5432/study_planner_db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Cookie Security & OAuth Cross-Site Redirect Support
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to False for local HTTP development, True for production HTTPS
    SESSION_COOKIE_HTTPONLY = True

    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', '')



import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fyp_secret_key_2026')
    
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:admin123@localhost:5432/study_planner_db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

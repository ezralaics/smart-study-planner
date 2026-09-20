import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fyp_secret_key_2026')

db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:admin123@localhost:5432/study_planner_db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    student_type = db.Column(db.String(20), default='Other')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    courses = db.relationship('Course', backref='student', lazy=True, cascade="all, delete-orphan")
    schedules = db.relationship('Schedule', backref='student', lazy=True, cascade="all, delete-orphan")

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20)) 
    credits = db.Column(db.Integer, default=3)
    target_grade = db.Column(db.Float, default=80.0)
    actual_grade = db.Column(db.String(5), nullable=True) 
    is_completed = db.Column(db.Boolean, default=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='course', lazy=True, cascade="all, delete-orphan")

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    task_name = db.Column(db.String(100), nullable=False)
    weightage = db.Column(db.Numeric(5, 2), default=0)
    due_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), default='Academic Task') 
    marks_obtained = db.Column(db.Numeric(5, 2), nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), default='Class') 
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False, default="09:00")
    venue = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    details = db.Column(db.Text, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        student_type = request.form.get('student_type')
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return "User already exists", 400

        try:
            new_user = User(
                fullname=fullname, email=email, username=username,
                password=password, student_type=student_type
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration Error: {e}")
            return "There was an error creating your account.", 500

    return render_template('register.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form.get('username'),
            password=request.form.get('password')
        ).first()
        if user:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.fullname
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/current-user')
def current_user():
    if 'user_id' not in session:
        return jsonify({}), 401
    user = User.query.get(session['user_id'])
    if user:
        return jsonify({"name": user.fullname, "username": user.username, "student_type": user.student_type})
    return jsonify({}), 404

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/calendar')
def calendar_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('calendar.html')

@app.route('/study-planner')
def study_planner():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('study_planner.html')

@app.route('/classes')
def classes_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('classes.html')

@app.route('/tasks')
def tasks_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('tasks.html')

@app.route('/grades')
def grades_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('grades.html')



@app.route('/api/save-course', methods=['POST'])
def save_course():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Please login first"}), 401

    data = request.get_json()
    try:
        existing_course = Course.query.filter_by(user_id=session['user_id'], course_name=data['course_name']).first()

        if existing_course:
            
            existing_course.credits = int(data.get('credits', 3))
            existing_course.target_grade = float(data.get('target_grade', 80))
            if 'semester' in data and hasattr(existing_course, 'semester'):
                existing_course.semester = data['semester']
            
            for task in existing_course.tasks:
                db.session.delete(task)
            course_target = existing_course
        else:
            
            course_target = Course(
                course_name=data['course_name'], credits=int(data.get('credits', 3)),
                target_grade=float(data.get('target_grade', 80)), user_id=session['user_id']
            )
            if 'semester' in data and hasattr(course_target, 'semester'):
                course_target.semester = data['semester']
            db.session.add(course_target)
            
        db.session.flush() 

        for t in data.get('tasks', []):
            due_date_obj = datetime.strptime(t['due_date'], '%Y-%m-%d').date() if t.get('due_date') else None
            db.session.add(Task(
                course_id=course_target.id,
                user_id=session['user_id'],
                task_name=t['task_name'],
                weightage=float(t['weightage']),
                due_date=due_date_obj,
                category='Component' 
            ))

        db.session.commit()
        return jsonify({"status": "success", "message": "The course saved successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate_plan')
def generate_plan():
    if 'user_id' not in session: return jsonify([]), 401
    courses = Course.query.filter_by(user_id=session['user_id']).order_by(Course.id.desc()).all()
    output = []
    for c in courses:
        output.append({
            "id": c.id, "name": c.course_name, "semester": c.semester, 
            "credits": c.credits, "target_grade": c.target_grade,
            "actual_grade": c.actual_grade,
            "is_completed": c.is_completed, # <--- ADD THIS LINE
            "tasks": [{"name": t.task_name, "weight": float(t.weightage) if t.weightage else 0, "deadline": str(t.due_date) if t.due_date else None} for t in c.tasks]
        })
    return jsonify(output)

@app.route('/api/delete_subject', methods=['POST'])
def delete_subject():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
    course_name = request.get_json().get('name')
    course = Course.query.filter_by(user_id=session['user_id'], course_name=course_name).first()
    if course:
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"message": "Course not found"}), 404

@app.route('/api/update-course-grade/<int:course_id>', methods=['POST'])
def update_course_grade(course_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    course = Course.query.get(course_id)
    if course and course.user_id == session['user_id']:
        data = request.get_json()
        course.actual_grade = data.get('actual_grade')
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@app.route('/api/toggle-course-completion/<int:course_id>', methods=['POST'])
def toggle_course_completion(course_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    course = Course.query.get(course_id)
    if course and course.user_id == session['user_id']:
        course.is_completed = not course.is_completed
        
        # --- NEW: Auto-complete or un-complete all tasks linked to this course ---
        for task in course.tasks:
            task.is_completed = course.is_completed
            
        db.session.commit()
        return jsonify({"status": "success", "is_completed": course.is_completed})
    return jsonify({"error": "Not found"}), 404

@app.route('/api/get-all-tasks')
def get_all_tasks():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401

    courses = Course.query.filter_by(user_id=session['user_id']).all()
    course_ids = [c.id for c in courses]
    
    tasks = Task.query.filter((Task.user_id == session['user_id']) | (Task.course_id.in_(course_ids))).all()
    
    tasks_list = []
    for t in tasks:
        c_name = t.course.course_name.split('—')[0].strip() if t.course else "General"
        
        cat = "Other Task"
        if t.weightage and t.weightage > 0:
            cat = "Component"
        elif t.category == 'Academic Task' or t.course_id:
            cat = "Academic Task"
            
        if t.category == 'Other Task' and not t.course_id:
            cat = "Other Task"

        tasks_list.append({
            "id": t.id,
            "course_id": t.course_id,
            "course_name": c_name,
            "task_name": t.task_name,
            "weightage": float(t.weightage) if t.weightage else 0,
            "due_date": str(t.due_date) if t.due_date else "",
            "is_completed": t.is_completed,
            "category": cat,
            "marks_obtained": float(t.marks_obtained) if t.marks_obtained is not None else None,
            "course_is_completed": t.course.is_completed if t.course else False 
        })
        
    tasks_list.sort(key=lambda x: x['due_date'] if x['due_date'] else "9999-99-99")
    return jsonify(tasks_list)

@app.route('/api/update-grade/<int:task_id>', methods=['POST'])
def update_grade(task_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    task = Task.query.get(task_id)
    if task and (task.user_id == session['user_id'] or (task.course and task.course.user_id == session['user_id'])):
        data = request.get_json()
        try:
            val = data.get('marks_obtained')
            task.marks_obtained = float(val) if val is not None else None
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/add-task', methods=['POST'])
def add_task():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    try:
        due_date_obj = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None
        cat = data.get('category', 'Other Task')
        c_id = data.get('course_id') if cat == 'Academic Task' else None
        
        new_task = Task(
            user_id=session['user_id'], course_id=c_id, task_name=data['task_name'],
            category=cat, due_date=due_date_obj, weightage=0
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/update-task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    task = Task.query.get(task_id)
    if task and (task.user_id == session['user_id'] or (task.course and task.course.user_id == session['user_id'])):
        data = request.get_json()
        task.task_name = data.get('task_name', task.task_name)
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None
        
        if not task.weightage or task.weightage == 0:
            task.category = data.get('category', task.category)
            c_id = data.get('course_id')
            task.course_id = c_id if c_id and task.category == 'Academic Task' else None
            
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@app.route('/api/delete-task/<int:task_id>', methods=['POST'])
def delete_task_route(task_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    task = Task.query.get(task_id)
    if task and (task.user_id == session['user_id'] or (task.course and task.course.user_id == session['user_id'])):
        db.session.delete(task)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@app.route('/api/toggle-task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    if 'user_id' not in session: return jsonify({"status": "error", "message": "Unauthorized"}), 401
    task = Task.query.get(task_id)
    if task and (task.user_id == session['user_id'] or (task.course and task.course.user_id == session['user_id'])):
        task.is_completed = not task.is_completed  
        db.session.commit()
        return jsonify({"status": "success", "is_completed": task.is_completed})
    return jsonify({"status": "error", "message": "Task not found"}), 404



@app.route('/api/save-schedule', methods=['POST'])
def save_schedule():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    try:
        start_d = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None
        end_d = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None

        if data.get('id'): # Update existing
            sched = Schedule.query.get(data['id'])
            if sched and sched.user_id == session['user_id']:
                sched.title = data['title']
                sched.activity_type = data['activity_type']
                sched.day_of_week = data['day']
                sched.start_time = data['start_time']
                sched.end_time = data['end_time']
                sched.venue = data.get('venue', '')
                sched.details = data.get('details', '') # <--- ADD THIS LINE
                sched.start_date = start_d
                sched.end_date = end_d
        else: 
            new_schedule = Schedule(
                user_id=session['user_id'], title=data['title'], activity_type=data['activity_type'],
                day_of_week=data['day'], start_time=data['start_time'], end_time=data['end_time'],
                venue=data.get('venue', ''), details=data.get('details', ''), # <--- ADD THIS LINE
                start_date=start_d, end_date=end_d
            )
            db.session.add(new_schedule)
            
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-schedules')
def get_schedules():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    schedules = Schedule.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        "id": s.id, "title": s.title, "activity_type": s.activity_type,
        "day": s.day_of_week, "start_time": s.start_time, "end_time": s.end_time,
        "venue": s.venue, "details": s.details, # <--- ADD THIS LINE
        "start_date": str(s.start_date) if s.start_date else "", 
        "end_date": str(s.end_date) if s.end_date else ""
    } for s in schedules])

@app.route('/api/delete-schedule/<int:id>', methods=['POST'])
def delete_schedule(id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    sched = Schedule.query.get(id)
    if sched and sched.user_id == session['user_id']:
        db.session.delete(sched)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
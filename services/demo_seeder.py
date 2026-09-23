from datetime import date, timedelta
from extensions import db
from models.user import User
from models.course import Course
from models.task import Task
from models.schedule import Schedule

def seed_demo_user(role):
    """
    Ensures a rich, realistic demo user exists for the given role,
    with courses, schedules, and tasks pre-populated so recruiters
    experience a vibrant application immediately.
    """
    if role not in ['student', 'educator', 'admin']:
        role = 'student'

    username = f"demo_{role}"
    user = User.query.filter_by(username=username).first()

    if not user:
        role_titles = {
            'student': 'Alex Johnson (Student Demo)',
            'educator': 'Dr. Sarah Williams (Educator Demo)',
            'admin': 'Chief Administrator (Admin Demo)'
        }
        
        user = User(
            fullname=role_titles.get(role, f"Demo {role.capitalize()}"),
            username=username,
            email=f"{username}@demo.studyplanner.edu",
            student_type="IT" if role == 'student' else "Faculty",
            role=role
        )
        user.set_password("demo123")
        db.session.add(user)
        db.session.commit()

        # Seed data specifically tailored to the role
        if role == 'student':
            _seed_student_data(user)
        elif role == 'educator':
            _seed_educator_data(user)
        elif role == 'admin':
            _seed_admin_data(user)

    return user

def _seed_student_data(user):
    today = date.today()
    sem = "2026-09 (Active)"

    # Course 1: Java Programming 1
    c1 = Course(
        user_id=user.id,
        course_name="CD106 — Java Programming 1",
        semester=sem,
        credits=4,
        target_grade=85.0,
        actual_grade="A",
        is_completed=False
    )
    db.session.add(c1)
    db.session.flush()

    db.session.add(Task(
        course_id=c1.id, user_id=user.id, task_name="OOP Assignment 1: Polymorphism",
        weightage=20.0, due_date=today + timedelta(days=2), category="Component", is_completed=False
    ))
    db.session.add(Task(
        course_id=c1.id, user_id=user.id, task_name="Midterm Lab Exam",
        weightage=30.0, due_date=today + timedelta(days=14), category="Component", is_completed=False
    ))
    db.session.add(Task(
        course_id=c1.id, user_id=user.id, task_name="Final Capstone Project",
        weightage=50.0, due_date=today + timedelta(days=45), category="Component", is_completed=False
    ))

    # Course 2: Fundamental of Database Systems
    c2 = Course(
        user_id=user.id,
        course_name="CD103 — Fundamental of Database Systems",
        semester=sem,
        credits=4,
        target_grade=80.0,
        actual_grade="A-",
        is_completed=False
    )
    db.session.add(c2)
    db.session.flush()

    db.session.add(Task(
        course_id=c2.id, user_id=user.id, task_name="Database Normalization & ERD",
        weightage=30.0, due_date=today + timedelta(days=7), category="Component", is_completed=True, marks_obtained=88.0
    ))
    db.session.add(Task(
        course_id=c2.id, user_id=user.id, task_name="Complex SQL Queries Lab",
        weightage=30.0, due_date=today + timedelta(days=21), category="Component", is_completed=False
    ))
    db.session.add(Task(
        course_id=c2.id, user_id=user.id, task_name="Final Theory Exam",
        weightage=40.0, due_date=today + timedelta(days=50), category="Component", is_completed=False
    ))

    # Course 3: UI Design
    c3 = Course(
        user_id=user.id,
        course_name="CD204 — User Interface Design",
        semester=sem,
        credits=3,
        target_grade=90.0,
        actual_grade="A+",
        is_completed=False
    )
    db.session.add(c3)
    db.session.flush()

    db.session.add(Task(
        course_id=c3.id, user_id=user.id, task_name="Figma High-Fidelity Prototype",
        weightage=40.0, due_date=today + timedelta(days=1), category="Component", is_completed=False
    ))
    db.session.add(Task(
        course_id=c3.id, user_id=user.id, task_name="Design Critique & User Testing",
        weightage=30.0, due_date=today + timedelta(days=18), category="Component", is_completed=False
    ))
    db.session.add(Task(
        course_id=c3.id, user_id=user.id, task_name="Interactive Design Portfolio",
        weightage=30.0, due_date=today + timedelta(days=40), category="Component", is_completed=False
    ))

    # Personal Task
    db.session.add(Task(
        course_id=None, user_id=user.id, task_name="LeetCode Practice: Arrays & HashMaps",
        weightage=0, due_date=today + timedelta(days=3), category="Other Task", is_completed=False
    ))

    # Timetable Schedules
    db.session.add(Schedule(
        user_id=user.id, title="CD106 — Java Programming 1", activity_type="Class",
        day_of_week="Monday", start_time="09:00", end_time="11:00", venue="Lab 3 - Block G",
        details="Practical coding session"
    ))
    db.session.add(Schedule(
        user_id=user.id, title="CD103 — Fundamental of Database Systems", activity_type="Class",
        day_of_week="Tuesday", start_time="14:00", end_time="16:00", venue="Lecture Hall B",
        details="PostgreSQL queries and schema design"
    ))
    db.session.add(Schedule(
        user_id=user.id, title="CD204 — User Interface Design", activity_type="Class",
        day_of_week="Wednesday", start_time="10:00", end_time="12:00", venue="Studio 2",
        details="Wireframing and Figma feedback"
    ))
    db.session.add(Schedule(
        user_id=user.id, title="Algorithmic Study & Revision", activity_type="Revision",
        day_of_week="Thursday", start_time="16:00", end_time="18:00", venue="Library Level 3",
        details="Review week's coding exercises"
    ))

    db.session.commit()

def _seed_educator_data(user):
    sem = "2026-09 (Active)"
    
    # Educator creates 2 courses that they teach
    c1 = Course(
        user_id=user.id,
        course_name="CD106 — Java Programming 1",
        semester=sem,
        credits=4,
        target_grade=80.0,
        actual_grade=None
    )
    c2 = Course(
        user_id=user.id,
        course_name="CD103 — Fundamental of Database Systems",
        semester=sem,
        credits=4,
        target_grade=80.0,
        actual_grade=None
    )
    db.session.add_all([c1, c2])
    db.session.flush()

    # Educator teaching schedule
    db.session.add(Schedule(
        user_id=user.id, title="Lecture: Java OOP Concepts", activity_type="Class",
        day_of_week="Monday", start_time="09:00", end_time="11:00", venue="Lab 3 - Block G",
        details="Module CD106 Cohort A"
    ))
    db.session.add(Schedule(
        user_id=user.id, title="Lecture: SQL Joins & Indexing", activity_type="Class",
        day_of_week="Tuesday", start_time="14:00", end_time="16:00", venue="Lecture Hall B",
        details="Module CD103 Cohort B"
    ))
    db.session.add(Schedule(
        user_id=user.id, title="Student Consultation Hours", activity_type="Revision",
        day_of_week="Friday", start_time="14:00", end_time="16:00", venue="Staff Office 4B",
        details="Open office hours for assignment queries"
    ))

    db.session.commit()

def _seed_admin_data(user):
    # Ensure a few sample student and educator accounts exist for the admin user directory
    sample_users = [
        {"fullname": "Emily Watson", "username": "emily_w", "email": "emily@university.edu", "role": "student"},
        {"fullname": "Marcus Chen", "username": "marcus_c", "email": "marcus@university.edu", "role": "student"},
        {"fullname": "Chloe Bennett", "username": "chloe_b", "email": "chloe@university.edu", "role": "student"},
        {"fullname": "Prof. Alan Turing", "username": "alan_t", "email": "alan@faculty.edu", "role": "educator"},
        {"fullname": "Dr. Ada Lovelace", "username": "ada_l", "email": "ada@faculty.edu", "role": "educator"}
    ]

    for su in sample_users:
        if not User.query.filter_by(username=su['username']).first():
            u = User(
                fullname=su['fullname'],
                username=su['username'],
                email=su['email'],
                student_type="IT" if su['role'] == 'student' else "Faculty",
                role=su['role']
            )
            u.set_password("pass123")
            db.session.add(u)

    db.session.commit()

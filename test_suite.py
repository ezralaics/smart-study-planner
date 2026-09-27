import os
import sys
import unittest
import uuid
import sqlite3
from datetime import datetime, date, timedelta, timezone

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from sqlalchemy import event, Engine
from app import create_app
from extensions import db
from models.user import User
from models.course import Course
from models.task import Task
from models.schedule import Schedule

# Enable foreign keys for SQLite test runs
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

class TestAppConfig:
    TESTING = True
    SECRET_KEY = 'test_secret_key_uuid'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class SmartStudyPlannerUUIDTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestAppConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            
            # Create a test student
            student = User(
                fullname="Ezra Student",
                username="student_user",
                email="student@test.com",
                student_type="IT",
                role="student"
            )
            student.set_password("pass123")
            db.session.add(student)

            # Create a test educator
            educator = User(
                fullname="Prof. Smart",
                username="educator_user",
                email="educator@test.com",
                student_type="Faculty",
                role="educator"
            )
            educator.set_password("pass123")
            db.session.add(educator)

            # Create a test admin
            admin = User(
                fullname="Master Admin",
                username="admin_user",
                email="admin@test.com",
                student_type="Faculty",
                role="admin"
            )
            admin.set_password("pass123")
            db.session.add(admin)

            # Create a legacy user with plaintext password
            legacy = User(
                fullname="Legacy User",
                username="legacyuser",
                email="legacy@test.com",
                password="plaintext_password",
                student_type="Other",
                role="student"
            )
            db.session.add(legacy)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_routes_exist(self):
        """Verify public pages load properly."""
        routes = ['/', '/login', '/register']
        for r in routes:
            res = self.client.get(r)
            self.assertIn(res.status_code, [200, 302])

    def test_uuid_generation_and_serialization(self):
        """Verify all models generate valid UUIDv4 primary keys and serialize to strings."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            self.assertIsNotNone(student.id)
            # Must be a valid UUIDv4
            parsed_user_uuid = uuid.UUID(str(student.id))
            self.assertEqual(parsed_user_uuid.version, 4)

            # Test Course UUID
            course = Course(
                user_id=student.id,
                course_name="Software Architecture",
                credits=3,
                target_grade=90.0
            )
            db.session.add(course)
            db.session.commit()

            parsed_course_uuid = uuid.UUID(str(course.id))
            self.assertEqual(parsed_course_uuid.version, 4)

            # Test Task UUID
            task = Task(
                user_id=student.id,
                course_id=course.id,
                task_name="Distributed Systems Milestone",
                due_date=date.today() + timedelta(days=5),
                weightage=25.0
            )
            db.session.add(task)
            db.session.commit()

            parsed_task_uuid = uuid.UUID(str(task.id))
            self.assertEqual(parsed_task_uuid.version, 4)

            # Test Schedule UUID
            sched = Schedule(
                user_id=student.id,
                title="Systems Lab",
                activity_type="Class",
                day_of_week="Thursday",
                start_time="10:00",
                end_time="12:00"
            )
            db.session.add(sched)
            db.session.commit()

            parsed_sched_uuid = uuid.UUID(str(sched.id))
            self.assertEqual(parsed_sched_uuid.version, 4)

            # Verify dictionary serialization outputs string UUIDs
            u_dict = student.to_dict()
            c_dict = course.to_dict()
            t_dict = task.to_dict()
            s_dict = sched.to_dict()

            self.assertIsInstance(u_dict['id'], str)
            self.assertEqual(len(u_dict['id']), 36)
            self.assertIsInstance(c_dict['id'], str)
            self.assertIsInstance(t_dict['id'], str)
            self.assertIsInstance(s_dict['id'], str)

            # Verify timestamps exist
            self.assertIn('created_at', u_dict)
            self.assertIn('updated_at', u_dict)

    def test_cascade_deletion(self):
        """Verify ondelete='CASCADE' cleans up child records when a parent user is deleted."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            course = Course(user_id=student.id, course_name="Cloud Security", credits=3)
            db.session.add(course)
            db.session.flush()

            task = Task(user_id=student.id, course_id=course.id, task_name="Threat Analysis", due_date=date.today())
            sched = Schedule(user_id=student.id, title="Security Seminar", day_of_week="Friday", start_time="09:00", end_time="10:00")
            db.session.add_all([task, sched])
            db.session.commit()

            course_id = course.id
            task_id = task.id
            sched_id = sched.id

            # Access relationships to populate session identity map
            _ = student.courses
            _ = student.tasks
            _ = student.schedules

            # Delete the parent user
            db.session.delete(student)
            db.session.commit()

            # Courses, Tasks, and Schedules must be deleted
            self.assertIsNone(db.session.get(Course, course_id))
            self.assertIsNone(db.session.get(Task, task_id))
            self.assertIsNone(db.session.get(Schedule, sched_id))

    def test_demo_login_student(self):
        """Test 1-click recruiter demo access for Student."""
        res = self.client.get('/demo-login/student', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/dashboard', res.headers.get('Location', ''))
        
        # Follow to dashboard
        dash = self.client.get('/dashboard')
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b"Smart Study Planner", dash.data)

    def test_demo_login_educator(self):
        """Test 1-click recruiter demo access for Educator."""
        res = self.client.get('/demo-login/educator', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/educator/dashboard', res.headers.get('Location', ''))

        dash = self.client.get('/educator/dashboard')
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b"Faculty Portal", dash.data)

    def test_demo_login_admin(self):
        """Test 1-click recruiter demo access for Admin."""
        res = self.client.get('/demo-login/admin', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/dashboard', res.headers.get('Location', ''))

        dash = self.client.get('/admin/dashboard')
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b"System Administration", dash.data)

    def test_password_hash_migration(self):
        """Verify plaintext legacy password upgrades to Werkzeug hash on first login."""
        res = self.client.post('/login', data={'username': 'legacyuser', 'password': 'plaintext_password'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            user = User.query.filter_by(username='legacyuser').first()
            self.assertFalse(user.password == 'plaintext_password')
            self.assertTrue(user.check_password('plaintext_password'))

    def test_academic_planner_uuid_endpoints(self):
        """Verify course addition, task creation, toggle, and grading with UUID parameters."""
        self.client.post('/login', data={'username': 'student_user', 'password': 'pass123'})

        # Add course via save-course
        res = self.client.post('/api/save-course', json={
            'course_name': 'Cloud Computing CS301',
            'semester': '2026-09 (Active)',
            'credits': 4,
            'target_grade': 85.0
        })
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            student = User.query.filter_by(username='student_user').first()
            course = Course.query.filter_by(user_id=student.id, course_name='Cloud Computing CS301').first()
            self.assertIsNotNone(course)
            course_id_str = str(course.id)

        # Update course grade with string UUID
        grade_res = self.client.post(f'/api/update-course-grade/{course_id_str}', json={'actual_grade': 'A'})
        self.assertEqual(grade_res.status_code, 200)
        self.assertEqual(grade_res.get_json()['status'], 'success')

        # Add task with UUID course_id
        task_res = self.client.post('/api/add-task', json={
            'course_id': course_id_str,
            'task_name': 'Terraform Infrastructure Setup',
            'category': 'Academic Task',
            'due_date': '2026-10-15'
        })
        self.assertEqual(task_res.status_code, 200)

        with self.app.app_context():
            task = Task.query.filter_by(task_name='Terraform Infrastructure Setup').first()
            self.assertIsNotNone(task)
            task_id_str = str(task.id)

        # Toggle task with string UUID
        toggle_res = self.client.post(f'/api/toggle-task/{task_id_str}')
        self.assertEqual(toggle_res.status_code, 200)
        self.assertTrue(toggle_res.get_json()['is_completed'])

        # Delete task with string UUID
        del_task_res = self.client.post(f'/api/delete-task/{task_id_str}')
        self.assertEqual(del_task_res.status_code, 200)
        self.assertEqual(del_task_res.get_json()['status'], 'success')

    def test_admin_user_management(self):
        """Verify admin can view users and update roles using string UUIDs."""
        self.client.post('/login', data={'username': 'admin_user', 'password': 'pass123'})

        users_page = self.client.get('/admin/users')
        self.assertEqual(users_page.status_code, 200)
        self.assertIn(b"User Directory", users_page.data)

        with self.app.app_context():
            student = User.query.filter_by(username='student_user').first()
            student_id_str = str(student.id)

        update_res = self.client.post('/admin/api/update-role', json={
            'user_id': student_id_str,
            'role': 'educator'
        })
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()['status'], 'success')

        with self.app.app_context():
            updated = db.session.get(User, student_id_str)
            self.assertEqual(updated.role, 'educator')

    def test_auto_scheduler_preview_and_apply(self):
        """Verify intelligent auto-scheduler works seamlessly with UUID entities."""
        self.client.post('/login', data={'username': 'student_user', 'password': 'pass123'})

        with self.app.app_context():
            student = User.query.filter_by(username='student_user').first()
            course = Course(
                user_id=student.id,
                course_name="Data Structures & Algorithms",
                semester="2026-09 (Active)",
                credits=4,
                target_grade=85.0
            )
            db.session.add(course)
            db.session.commit()

            due_soon = date.today() + timedelta(days=3)
            t1 = Task(
                course_id=course.id,
                task_name="Binary Trees Implementation",
                weightage=30.0,
                due_date=due_soon
            )
            due_later = date.today() + timedelta(days=10)
            t2 = Task(
                course_id=course.id,
                task_name="Graph Theory Quiz",
                weightage=15.0,
                due_date=due_later
            )
            db.session.add_all([t1, t2])

            existing_class = Schedule(
                user_id=student.id,
                title="Data Structures Lecture",
                day_of_week="Monday",
                start_time="18:00",
                end_time="20:00",
                venue="Auditorium A",
                activity_type="Class"
            )
            db.session.add(existing_class)
            db.session.commit()

        preview_res = self.client.post('/api/auto-schedule/preview', json={
            'daily_hours': 2,
            'preferred_window': 'evening',
            'days_ahead': 7
        })
        self.assertEqual(preview_res.status_code, 200)
        data = preview_res.get_json()
        self.assertIn('sessions', data)
        self.assertGreater(len(data['sessions']), 0)
        self.assertEqual(data['tasks_considered'], 2)

        # Apply sessions
        apply_res = self.client.post('/api/auto-schedule/apply', json={'sessions': data['sessions']})
        self.assertEqual(apply_res.status_code, 200)
        self.assertEqual(apply_res.get_json()['status'], 'success')

    def test_new_user_profile_flag_and_login_redirect(self):
        """Verify new users default to is_profile_completed=False and are prompted to complete profile."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            self.assertFalse(student.is_profile_completed)

        # Login as student_user
        res = self.client.post('/login', data={
            'username': 'student_user',
            'password': 'pass123'
        }, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/complete-profile', res.headers['Location'])

    def test_complete_profile_student(self):
        """Submit student onboarding form and verify profile marked as completed."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.post('/complete-profile', data={
            'phone_number': '+60123456789',
            'bio': 'Passionate AI & Data Science scholar.',
            'major_programme': 'BSc Computer Science',
            'academic_year': 'Year 3',
            'current_semester': 'Semester 1',
            'target_cgpa': '3.85'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            self.assertTrue(student.is_profile_completed)
            self.assertEqual(student.major_programme, 'BSc Computer Science')
            self.assertEqual(student.academic_year, 'Year 3')
            self.assertEqual(student.current_semester, 'Semester 1')
            self.assertEqual(student.target_cgpa, 3.85)
            self.assertEqual(student.phone_number, '+60123456789')
            self.assertEqual(student.bio, 'Passionate AI & Data Science scholar.')

    def test_complete_profile_educator(self):
        """Submit educator onboarding form and verify educator-specific metadata saved."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                educator = User.query.filter_by(username="educator_user").first()
                sess['user_id'] = str(educator.id)
                sess['username'] = educator.fullname
                sess['role'] = 'educator'

        res = self.client.post('/complete-profile', data={
            'title_designation': 'Prof.',
            'faculty_department': 'Department of Computing',
            'office_location': 'Block B, Room 301',
            'phone_number': '+601122334455',
            'bio': 'Dean of AI & Machine Learning Research.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            educator = User.query.filter_by(username="educator_user").first()
            self.assertTrue(educator.is_profile_completed)
            self.assertEqual(educator.title_designation, 'Prof.')
            self.assertEqual(educator.faculty_department, 'Department of Computing')
            self.assertEqual(educator.office_location, 'Block B, Room 301')

    def test_complete_profile_admin(self):
        """Submit admin onboarding form and verify admin-specific metadata saved."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                admin = User.query.filter_by(username="admin_user").first()
                sess['user_id'] = str(admin.id)
                sess['username'] = admin.fullname
                sess['role'] = 'admin'

        res = self.client.post('/complete-profile', data={
            'staff_id': 'ADM-9901',
            'admin_department': 'Office of Academic Affairs',
            'phone_number': '+60199998888',
            'bio': 'System Administrator and Compliance Lead.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            admin = User.query.filter_by(username="admin_user").first()
            self.assertTrue(admin.is_profile_completed)
            self.assertEqual(admin.staff_id, 'ADM-9901')
            self.assertEqual(admin.admin_department, 'Office of Academic Affairs')

    def test_complete_profile_validation(self):
        """Verify target_cgpa boundaries reject values > 4.0 or < 0.0 with HTTP 400."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        # Reject CGPA > 4.0
        res_high = self.client.post('/complete-profile', data={
            'major_programme': 'BSc Computer Science',
            'target_cgpa': '5.0'
        })
        self.assertEqual(res_high.status_code, 400)

        # Reject negative CGPA
        res_low = self.client.post('/complete-profile', data={
            'major_programme': 'BSc Computer Science',
            'target_cgpa': '-1.0'
        })
        self.assertEqual(res_low.status_code, 400)

    def test_skip_onboarding(self):
        """Verify skip-onboarding sets session flag and routes to student dashboard."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.get('/skip-onboarding', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/student/dashboard', res.headers['Location'])

        with self.client.session_transaction() as sess:
            self.assertTrue(sess.get('skipped_onboarding'))

    def test_profile_update(self):
        """Verify editing bio, phone, and role attributes via /profile persists to DB."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.post('/profile', data={
            'fullname': 'Ezra Lai Kwang Zhe',
            'phone_number': '+60198887777',
            'bio': 'Updated software engineer bio.',
            'major_programme': 'Software Engineering',
            'academic_year': 'Year 4',
            'current_semester': 'Semester 2',
            'target_cgpa': '3.92'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            self.assertEqual(student.fullname, 'Ezra Lai Kwang Zhe')
            self.assertEqual(student.phone_number, '+60198887777')
            self.assertEqual(student.bio, 'Updated software engineer bio.')
            self.assertEqual(student.major_programme, 'Software Engineering')
            self.assertEqual(student.target_cgpa, 3.92)

if __name__ == '__main__':
    unittest.main()

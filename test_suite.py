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
from models.message import DirectMessage
from models.habit import Habit, HabitLog
from models.finance import BudgetGoal, Transaction, FinancialAccount, FinancialTransaction
from models.journal import JournalEntry
from models.career import JobApplication
from models.report import UserInterestSource, DigestReport

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

    def test_settings_requires_auth(self):
        """Verify /settings redirects unauthenticated visitors to login."""
        res = self.client.get('/settings', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers['Location'])

    def test_settings_page_authenticated(self):
        """Verify /settings loads cleanly for authenticated users."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.get('/settings')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Settings &amp; Preferences', res.data)

    def test_change_password_success(self):
        """Verify changing password updates hash in DB and allows subsequent authentication."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.post('/settings/change-password', data={
            'current_password': 'pass123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/settings', res.headers['Location'])

        # Verify new password works in User model
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            self.assertTrue(student.check_password('newpassword456'))
            self.assertFalse(student.check_password('pass123'))

    def test_change_password_wrong_current(self):
        """Verify wrong current password is rejected with HTTP 400."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.post('/settings/change-password', data={
            'current_password': 'wrong_password_here',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'Current password does not match', res.data)

    def test_change_password_mismatch(self):
        """Verify mismatched new password and confirm password is rejected with HTTP 400."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.post('/settings/change-password', data={
            'current_password': 'pass123',
            'new_password': 'newpassword456',
            'confirm_password': 'differentsomething'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn(b'New passwords do not match', res.data)

    def test_export_data_endpoint(self):
        """Verify /api/export-data returns structured JSON with courses, tasks, and schedules."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            c = Course(course_name="Data Structures", credits=4, user_id=student.id)
            db.session.add(c)
            db.session.flush()
            t = Task(course_id=c.id, user_id=student.id, task_name="Assignment 1", weightage=20.0)
            s = Schedule(user_id=student.id, title="Lecture A", day_of_week="Tuesday", start_time="10:00", end_time="12:00")
            db.session.add_all([t, s])
            db.session.commit()

        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.get('/api/export-data')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'application/json')
        self.assertIn('attachment', res.headers.get('Content-Disposition', ''))
        
        data = res.get_json()
        self.assertIn('export_metadata', data)
        self.assertIn('user_profile', data)
        self.assertIn('courses', data)
        self.assertIn('tasks', data)
        self.assertIn('schedules', data)
        self.assertGreaterEqual(len(data['courses']), 1)
        self.assertGreaterEqual(len(data['tasks']), 1)
        self.assertGreaterEqual(len(data['schedules']), 1)

    def test_clear_completed_tasks_api(self):
        """Verify /api/settings/clear-completed-tasks deletes finished tasks and keeps pending ones."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            c = Course(course_name="Algorithms", credits=3, user_id=student.id)
            db.session.add(c)
            db.session.flush()
            t_done = Task(course_id=c.id, user_id=student.id, task_name="Completed Quiz", weightage=10.0, is_completed=True)
            t_pending = Task(course_id=c.id, user_id=student.id, task_name="Pending Project", weightage=30.0, is_completed=False)
            db.session.add_all([t_done, t_pending])
            db.session.commit()

        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.post('/api/settings/clear-completed-tasks')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(data['deleted_count'], 1)

        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            remaining_tasks = Task.query.filter_by(user_id=student.id).all()
            task_names = [t.task_name for t in remaining_tasks]
            self.assertNotIn("Completed Quiz", task_names)
            self.assertIn("Pending Project", task_names)

    def test_ai_key_encryption_roundtrip(self):
        """Verify Fernet symmetric encryption and decryption reproduces exact API keys."""
        from models.user_ai_config import encrypt_value, decrypt_value
        secret = "super_test_secret_key_12345"
        raw_key = "AIzaSyD-sample-google-gemini-key-998877"
        encrypted = encrypt_value(raw_key, secret)
        self.assertNotEqual(encrypted, raw_key)
        self.assertTrue(len(encrypted) > 20)
        decrypted = decrypt_value(encrypted, secret)
        self.assertEqual(decrypted, raw_key)

    def test_ai_masked_keys(self):
        """Verify mask_value redacts the middle portion of secrets."""
        from models.user_ai_config import mask_value
        self.assertEqual(mask_value(""), "")
        self.assertEqual(mask_value("short"), "••••••••")
        masked = mask_value("sk-or-v1-abcdef1234567890xyz")
        self.assertTrue(masked.startswith("sk-o"))
        self.assertTrue(masked.endswith("0xyz"))
        self.assertIn("••••••••", masked)

    def test_document_parser_txt(self):
        """Verify document_parser extracts text and generates snippet from text files."""
        import tempfile
        from services.document_parser import extract_text_from_file, generate_snippet
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Artificial Intelligence in Computer Science involves search algorithms and heuristics.")
            tmp_path = f.name
        try:
            extracted = extract_text_from_file(tmp_path, 'txt')
            self.assertIn("Artificial Intelligence", extracted)
            snippet = generate_snippet(extracted, max_chars=30)
            self.assertTrue(len(snippet) <= 35)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_document_parser_pdf(self):
        """Verify pypdf extracts text from a PDF document buffer."""
        import pypdf
        import tempfile
        from services.document_parser import extract_text_from_file
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=100, height=100)
        with tempfile.NamedTemporaryFile('wb', delete=False, suffix='.pdf') as f:
            writer.write(f)
            tmp_path = f.name
        try:
            extracted = extract_text_from_file(tmp_path, 'pdf')
            self.assertIsInstance(extracted, str)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_document_upload_and_delete_api(self):
        """Verify /api/ai/upload-document stores note and /api/ai/documents/<id> deletes it."""
        import io
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        # Upload a sample lecture note
        sample_file = (io.BytesIO(b"Data Structures: Binary Search Trees have O(log n) average lookup time."), "lecture1.txt")
        res = self.client.post('/api/ai/upload-document', data={'file': sample_file}, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        doc_id = data['document']['id']
        self.assertIn("lecture1.txt", data['document']['filename'])

        # Preview document
        preview_res = self.client.get(f'/api/ai/documents/{doc_id}/preview')
        self.assertEqual(preview_res.status_code, 200)
        preview_data = preview_res.get_json()
        self.assertIn("Binary Search Trees", preview_data['document']['extracted_text'])

        # Delete document
        del_res = self.client.delete(f'/api/ai/documents/{doc_id}')
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.get_json()['status'], 'success')

    def test_ai_config_api(self):
        """Verify /api/ai/config persists and returns masked keys."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        res = self.client.post('/api/ai/config', json={
            'google_api_key': 'AIzaSyFakeGoogleKeyForTesting12345',
            'openrouter_api_key': 'sk-or-v1-fakeOpenRouterKey67890',
            'default_provider': 'google',
            'default_model': 'gemini-2.0-flash'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['config']['has_google_key'])
        self.assertIn('••••', data['config']['google_key_masked'])

        # GET config returns masked keys
        get_res = self.client.get('/api/ai/config')
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.get_json()
        self.assertTrue(get_data['has_google_key'])
        self.assertTrue(get_data['has_openrouter_key'])

    def test_ai_chat_missing_keys_handled(self):
        """Verify /api/ai/chat returns friendly error when keys are missing."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                # Test with educator who has no keys configured
                educator = User.query.filter_by(username="educator_user").first()
                sess['user_id'] = str(educator.id)
                sess['username'] = educator.fullname
                sess['role'] = 'educator'

        # Ensure no system env keys interfere with test
        old_g = os.environ.pop('GOOGLE_API_KEY', None)
        old_gem = os.environ.pop('GEMINI_API_KEY', None)
        try:
            res = self.client.post('/api/ai/chat', json={
                'prompt': 'Can you explain dynamic programming?',
                'provider': 'google'
            })
            self.assertEqual(res.status_code, 400)
            data = res.get_json()
            self.assertIn("key is missing", data['message'])
        finally:
            if old_g: os.environ['GOOGLE_API_KEY'] = old_g
            if old_gem: os.environ['GEMINI_API_KEY'] = old_gem

    def test_registration_with_all_education_levels(self):
        """Verify new users can register with each of the 4 education levels."""
        levels = ['primary', 'secondary', 'university', 'general']
        for lvl in levels:
            username = f"user_{lvl}_{uuid.uuid4().hex[:6]}"
            email = f"{username}@test.edu"
            res = self.client.post('/register', data={
                'fullname': f'Student {lvl.capitalize()}',
                'username': username,
                'email': email,
                'password': 'Password123!',
                'role': 'student',
                'student_type': 'IT',
                'education_level': lvl
            }, follow_redirects=False)
            self.assertEqual(res.status_code, 302, f"Failed registration for tier {lvl}")

            with self.app.app_context():
                user = User.query.filter_by(username=username).first()
                self.assertIsNotNone(user, f"User was not persisted for {lvl}")
                self.assertEqual(user.education_level, lvl, f"Education level mismatch for {lvl}")
                self.assertEqual(user.to_dict()['education_level'], lvl)

    def test_adaptive_scheduler_chunk_durations(self):
        """Verify scheduler returns 15-minute chunks for primary and 45-minute chunks for university."""
        from services.scheduler import generate_study_schedule

        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            # Ensure student has a course and an upcoming task
            course = Course(user_id=student.id, course_name="Mathematics", semester="Term 1", target_grade=85.0)
            db.session.add(course)
            db.session.commit()

            task = Task(
                user_id=student.id,
                course_id=course.id,
                task_name="Algebra Revision Sheet",
                weightage=30.0,
                due_date=date.today() + timedelta(days=5),
                is_completed=False
            )
            db.session.add(task)
            db.session.commit()

            # 1. Test Primary: 15-minute chunks
            primary_sched = generate_study_schedule(student.id, daily_hours=2, education_level='primary')
            self.assertEqual(primary_sched['status'], 'success')
            self.assertEqual(primary_sched['chunk_minutes'], 15)
            self.assertTrue(len(primary_sched['sessions']) > 0)
            for s in primary_sched['sessions']:
                self.assertEqual(s['duration_minutes'], 15, "Primary sessions must be 15-minute chunks")
                self.assertEqual(s['break_minutes'], 5)

            # 2. Test University: 45-minute chunks
            uni_sched = generate_study_schedule(student.id, daily_hours=2, education_level='university')
            self.assertEqual(uni_sched['status'], 'success')
            self.assertEqual(uni_sched['chunk_minutes'], 45)
            self.assertTrue(len(uni_sched['sessions']) > 0)
            for s in uni_sched['sessions']:
                self.assertEqual(s['duration_minutes'], 45, "University sessions must be 45-minute chunks")
                self.assertEqual(s['break_minutes'], 15)

            # 3. Test Secondary: 30-minute chunks
            sec_sched = generate_study_schedule(student.id, daily_hours=2, education_level='secondary')
            self.assertEqual(sec_sched['status'], 'success')
            self.assertEqual(sec_sched['chunk_minutes'], 30)
            for s in sec_sched['sessions']:
                self.assertEqual(s['duration_minutes'], 30, "Secondary sessions must be 30-minute chunks")

    def test_update_education_level_api(self):
        """Verify /api/settings/education-level updates user tier and handles invalid inputs."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.fullname
                sess['role'] = 'student'

        # Test valid update
        res = self.client.post('/api/settings/education-level', json={'education_level': 'secondary'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['education_level'], 'secondary')

        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            self.assertEqual(student.education_level, 'secondary')

        # Test invalid update
        bad_res = self.client.post('/api/settings/education-level', json={'education_level': 'kindergarten_phd'})
        self.assertEqual(bad_res.status_code, 400)
        bad_data = bad_res.get_json()
        self.assertEqual(bad_data['status'], 'error')

    def test_backward_compatibility_university_defaults(self):
        """Verify legacy accounts default to university and courses remain functional."""
        with self.app.app_context():
            # Create a user with default education_level
            legacy_user = User(
                fullname="Legacy Learner",
                username=f"legacy_{uuid.uuid4().hex[:6]}",
                email=f"legacy_{uuid.uuid4().hex[:6]}@test.edu",
                password="pass",
                role="student"
            )
            db.session.add(legacy_user)
            db.session.commit()

            self.assertEqual(legacy_user.education_level, 'university')
            self.assertEqual(legacy_user.to_dict()['education_level'], 'university')

    def test_dm_send_and_unread_count(self):
        """Verify sending a direct message creates record and updates unread badge count."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            educator = User.query.filter_by(username="educator_user").first()
            student_id = str(student.id)
            educator_id = str(educator.id)
            educator_email = educator.email

        # 1. Login as student and send message to educator
        with self.client.session_transaction() as sess:
            sess['user_id'] = student_id
            sess['username'] = "Ezra Student"
            sess['role'] = 'student'

        send_res = self.client.post('/api/dm/send', json={
            'recipient_email': educator_email,
            'content': 'Hello Professor, do we have consultation hours tomorrow?'
        })
        self.assertEqual(send_res.status_code, 201)
        send_data = send_res.get_json()
        self.assertEqual(send_data['status'], 'success')
        self.assertEqual(send_data['data']['content'], 'Hello Professor, do we have consultation hours tomorrow?')
        self.assertFalse(send_data['data']['is_read'])

        # 2. Login as educator and check unread count
        with self.client.session_transaction() as sess:
            sess['user_id'] = educator_id
            sess['username'] = "Prof. Smart"
            sess['role'] = 'educator'

        count_res = self.client.get('/api/dm/unread-count')
        self.assertEqual(count_res.status_code, 200)
        self.assertEqual(count_res.get_json()['unread_count'], 1)

        # Check conversations list
        conv_res = self.client.get('/api/dm/conversations')
        self.assertEqual(conv_res.status_code, 200)
        convs = conv_res.get_json()['data']
        self.assertEqual(len(convs), 1)
        self.assertEqual(convs[0]['peer']['email'], 'student@test.com')
        self.assertEqual(convs[0]['unread_count'], 1)

    def test_dm_thread_and_read_receipt(self):
        """Verify opening a thread retrieves messages and marks unread messages as read."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            educator = User.query.filter_by(username="educator_user").first()
            student_id = str(student.id)
            educator_id = str(educator.id)
            student_email = student.email

        # Send a direct message from student to educator
        with self.client.session_transaction() as sess:
            sess['user_id'] = student_id
            sess['username'] = "Ezra Student"
            sess['role'] = 'student'
        self.client.post('/api/dm/send', json={
            'recipient_email': educator.email,
            'content': 'Thread test message'
        })

        # Switch to educator session and fetch thread
        with self.client.session_transaction() as sess:
            sess['user_id'] = educator_id
            sess['username'] = "Prof. Smart"
            sess['role'] = 'educator'

        thread_res = self.client.get(f'/api/dm/thread?email={student_email}')
        self.assertEqual(thread_res.status_code, 200)
        thread_data = thread_res.get_json()['data']
        self.assertEqual(thread_data['peer']['email'], student_email)
        self.assertEqual(len(thread_data['messages']), 1)
        self.assertEqual(thread_data['messages'][0]['is_mine'], False)
        self.assertEqual(thread_data['messages'][0]['content'], 'Thread test message')

        # Check unread count is now 0 because viewing thread marks them read
        count_res = self.client.get('/api/dm/unread-count')
        self.assertEqual(count_res.status_code, 200)
        self.assertEqual(count_res.get_json()['unread_count'], 0)

    def test_dm_authorization_and_validation(self):
        """Verify strict authorization, validation constraints, and classmate search."""
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            educator = User.query.filter_by(username="educator_user").first()
            student_id = str(student.id)
            student_email = student.email
            educator_id = str(educator.id)

        # 1. Self-messaging rejected
        with self.client.session_transaction() as sess:
            sess['user_id'] = student_id
            sess['username'] = "Ezra Student"
            sess['role'] = 'student'

        self_res = self.client.post('/api/dm/send', json={
            'recipient_email': student_email,
            'content': 'Messaging myself is disallowed'
        })
        self.assertEqual(self_res.status_code, 400)
        self.assertIn("cannot send messages to yourself", self_res.get_json()['message'].lower())

        # 2. Empty content or recipient rejected
        empty_res = self.client.post('/api/dm/send', json={
            'recipient_email': '',
            'content': ''
        })
        self.assertEqual(empty_res.status_code, 400)

        # 3. Classmate search finds peer by name/email but excludes self
        search_res = self.client.get('/api/dm/search-classmates?q=prof')
        self.assertEqual(search_res.status_code, 200)
        peers = search_res.get_json()['data']
        self.assertEqual(len(peers), 1)
        self.assertEqual(peers[0]['email'], 'educator@test.com')

        # Search for self should return empty
        self_search = self.client.get('/api/dm/search-classmates?q=Ezra')
        self.assertEqual(self_search.status_code, 200)
        self.assertEqual(len(self_search.get_json()['data']), 0)

    def test_workspace_switcher_route_and_session(self):
        """Verify workspace switcher updates active_workspace in session and redirects correctly."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = "Ezra Student"
                sess['role'] = 'student'
                sess['is_profile_completed'] = True

        # 1. Switch to life workspace
        res_life = self.client.get('/workspace/life')
        self.assertEqual(res_life.status_code, 302)
        self.assertIn('/life', res_life.headers['Location'])
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('active_workspace'), 'life')

        # 2. Switch to finance workspace
        res_fin = self.client.get('/workspace/finance')
        self.assertEqual(res_fin.status_code, 302)
        self.assertIn('/finance', res_fin.headers['Location'])

        # 3. Switch to journal workspace
        res_jrn = self.client.get('/workspace/journal')
        self.assertEqual(res_jrn.status_code, 302)
        self.assertIn('/journal', res_jrn.headers['Location'])

        # 4. Switch to career workspace
        res_car = self.client.get('/workspace/career')
        self.assertEqual(res_car.status_code, 302)
        self.assertIn('/career', res_car.headers['Location'])

        # 5. Switch back to academics workspace
        res_acad = self.client.get('/workspace/academics')
        self.assertEqual(res_acad.status_code, 302)
        self.assertIn('/student/dashboard', res_acad.headers['Location'])

        # 6. Today's Command Center renders 200
        cmd_res = self.client.get('/dashboard')
        self.assertEqual(cmd_res.status_code, 200)

    def test_life_habits_create_and_toggle(self):
        """Verify Habit creation, log persistence, streak calculation, and toggle behavior."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = "Ezra Student"
                sess['role'] = 'student'

        # 1. Create a habit
        create_res = self.client.post('/api/life/habits', json={
            'title': 'Read 20 Pages',
            'category': 'learning',
            'frequency': 'daily',
            'target_days_per_week': 7
        })
        self.assertEqual(create_res.status_code, 201)
        habit_data = create_res.get_json()['data']
        habit_id = habit_data['id']
        self.assertEqual(habit_data['title'], 'Read 20 Pages')
        self.assertEqual(habit_data['streak_count'], 0)

        # 2. Fetch habits
        fetch_res = self.client.get('/api/life/habits')
        self.assertEqual(fetch_res.status_code, 200)
        habits = fetch_res.get_json()['data']
        self.assertEqual(len(habits), 1)
        self.assertFalse(habits[0]['today_completed'])

        # 3. Toggle habit to complete
        toggle_res = self.client.post(f'/api/life/habits/{habit_id}/toggle')
        self.assertEqual(toggle_res.status_code, 200)
        toggle_data = toggle_res.get_json()
        self.assertTrue(toggle_data['is_completed'])
        self.assertEqual(toggle_data['streak_count'], 1)

        # 4. Verify fetch reflects completion
        fetch2 = self.client.get('/api/life/habits')
        self.assertEqual(fetch2.get_json()['completed_today_count'], 1)

    def test_finance_transactions_and_summary(self):
        """Verify Budget goal setting, expense/income transactions, and remaining budget calculation."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = "Ezra Student"
                sess['role'] = 'student'

        # 1. Set budget
        budget_res = self.client.post('/api/finance/budget', json={
            'monthly_budget_limit': 1500.0,
            'savings_target': 300.0,
            'currency_symbol': '$'
        })
        self.assertEqual(budget_res.status_code, 200)

        # 2. Log expense
        exp_res = self.client.post('/api/finance/transactions', json={
            'type': 'expense',
            'amount': 50.0,
            'description': 'Algorithms Textbook',
            'category': 'books',
            'payment_method': 'card'
        })
        self.assertEqual(exp_res.status_code, 201)

        # 3. Log income
        inc_res = self.client.post('/api/finance/transactions', json={
            'type': 'income',
            'amount': 200.0,
            'description': 'Peer Tutoring Stipend',
            'category': 'income'
        })
        self.assertEqual(inc_res.status_code, 201)

        # 4. Fetch summary
        sum_res = self.client.get('/api/finance/summary')
        self.assertEqual(sum_res.status_code, 200)
        sum_data = sum_res.get_json()
        self.assertEqual(sum_data['budget_limit'], 1500.0)
        self.assertEqual(sum_data['total_expense'], 50.0)
        self.assertEqual(sum_data['total_income'], 200.0)
        self.assertEqual(sum_data['remaining_budget'], 1450.0)
        self.assertIn('books', sum_data['category_breakdown'])

    def test_journal_entry_create_and_fetch(self):
        """Verify Journal diary reflection logging and mood stats."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = "Ezra Student"
                sess['role'] = 'student'

        # 1. Write journal entry
        post_res = self.client.post('/api/journal/entries', json={
            'title': 'Midterm Reflection',
            'content': 'Focused heavily on dynamic programming today and solved 3 hard problems.',
            'mood': 'great',
            'tags': 'academics,goals'
        })
        self.assertEqual(post_res.status_code, 201)

        # 2. Fetch journal entries
        get_res = self.client.get('/api/journal/entries')
        self.assertEqual(get_res.status_code, 200)
        data = get_res.get_json()
        self.assertEqual(data['total_entries'], 1)
        self.assertEqual(data['data'][0]['mood'], 'great')
        self.assertEqual(data['mood_stats']['great'], 1)

    def test_career_application_status_update(self):
        """Verify Career application tracking and Kanban stage transition."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = "Ezra Student"
                sess['role'] = 'student'

        # 1. Add application
        add_res = self.client.post('/api/career/applications', json={
            'company_name': 'DeepMind',
            'job_title': 'AI Research Engineer Intern',
            'status': 'wishlist',
            'location': 'London / Hybrid',
            'salary_range': '$5,000/mo'
        })
        self.assertEqual(add_res.status_code, 201)
        app_id = add_res.get_json()['data']['id']

        # 2. Move stage to applied
        move_res = self.client.patch(f'/api/career/applications/{app_id}/status', json={
            'status': 'applied'
        })
        self.assertEqual(move_res.status_code, 200)
        self.assertEqual(move_res.get_json()['data']['status'], 'applied')

        # 3. Fetch applications
        apps_res = self.client.get('/api/career/applications')
        self.assertEqual(apps_res.status_code, 200)
        grouped = apps_res.get_json()['grouped']
        self.assertEqual(len(grouped['applied']), 1)
        self.assertEqual(grouped['applied'][0]['company_name'], 'DeepMind')

    def test_study_hub_modular_routes_and_aliases(self):
        """Verify blueprints/study domain routes and backward-compatible aliases."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = "Ezra Student"
                sess['role'] = 'student'
                sess['is_profile_completed'] = True

        # 1. Test /study root redirects to student dashboard
        res_study = self.client.get('/study')
        self.assertEqual(res_study.status_code, 302)
        self.assertIn('/student/dashboard', res_study.headers['Location'])

        # 2. Test /study/planner, /study/calendar, /study/courses, /study/tasks, /study/grades
        res_planner = self.client.get('/study/planner')
        self.assertEqual(res_planner.status_code, 200)

        res_calendar = self.client.get('/study/calendar')
        self.assertEqual(res_calendar.status_code, 200)

        res_courses = self.client.get('/study/courses')
        self.assertEqual(res_courses.status_code, 200)

        res_tasks = self.client.get('/study/tasks')
        self.assertEqual(res_tasks.status_code, 200)

        res_grades = self.client.get('/study/grades')
        self.assertEqual(res_grades.status_code, 200)

        # 3. Test backward-compatible aliases
        res_alias_planner = self.client.get('/study-planner')
        self.assertEqual(res_alias_planner.status_code, 200)

        res_alias_cal = self.client.get('/calendar')
        self.assertEqual(res_alias_cal.status_code, 200)

    def test_models_study_facade(self):
        """Verify models/study.py exports Course, Task, and Schedule properly."""
        from models.study import Course as StudyCourse, Task as StudyTask, Schedule as StudySchedule
        self.assertIs(StudyCourse, Course)
        self.assertIs(StudyTask, Task)
        self.assertIs(StudySchedule, Schedule)

    def test_whatif_grade_calculator_accuracy(self):
        """Verify What-If grade forecasting engine: edge cases, zero weights, impossible and secured targets."""
        from services.analytics_service import calculate_what_if_grade
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            course = Course(
                user_id=student.id,
                course_name="Algorithms & Complexity",
                credits=4,
                target_grade=85.0
            )
            db.session.add(course)
            db.session.commit()

            # Case 1: Course with zero tasks (100% pending weight)
            calc_empty = calculate_what_if_grade(str(course.id), target_grade=85.0)
            self.assertEqual(calc_empty["status"], "achievable")
            self.assertEqual(calc_empty["required_pending_pct"], 85.0)

            # Case 2: Add completed task: Midterm weight 40%, score 90% (earned = 36%)
            midterm = Task(
                course_id=course.id,
                user_id=student.id,
                task_name="Midterm Examination",
                weightage=40.0,
                marks_obtained=90.0,
                is_completed=True
            )
            # Pending Final Exam weight 60%
            final_exam = Task(
                course_id=course.id,
                user_id=student.id,
                task_name="Final Examination",
                weightage=60.0,
                is_completed=False
            )
            db.session.add_all([midterm, final_exam])
            db.session.commit()

            # Target 85%: Current earned = 36%, needed = 49% across 60% pending -> 49/60 * 100 = 81.67 -> 81.7%
            calc_normal = calculate_what_if_grade(str(course.id), target_grade=85.0)
            self.assertEqual(calc_normal["status"], "achievable")
            self.assertAlmostEqual(calc_normal["required_pending_pct"], 81.7, places=1)

            # Case 3: Impossible target (e.g. 98% target -> needed 62% on 60% pending -> >100%)
            calc_impossible = calculate_what_if_grade(str(course.id), target_grade=98.0)
            self.assertEqual(calc_impossible["status"], "impossible")
            self.assertGreater(calc_impossible["required_pending_pct"], 100.0)

            # Case 4: Already secured target (e.g. target 30% -> needed <= 0%)
            calc_secured = calculate_what_if_grade(str(course.id), target_grade=30.0)
            self.assertEqual(calc_secured["status"], "secured")
            self.assertEqual(calc_secured["required_pending_pct"], 0.0)

    def test_deadline_clustering_and_burnout_risk(self):
        """Verify rolling 72-hour deadline cluster detection and burnout severity calculation."""
        from services.analytics_service import detect_burnout_and_deadline_clusters
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            today = date.today()

            # Create 3 tasks coinciding within 48 hours (within 72-hour rolling window)
            t1 = Task(user_id=student.id, task_name="Sprint 1 Milestone", due_date=today + timedelta(days=5), is_completed=False)
            t2 = Task(user_id=student.id, task_name="Calculus Problem Set", due_date=today + timedelta(days=6), is_completed=False)
            t3 = Task(user_id=student.id, task_name="Software Architecture Doc", due_date=today + timedelta(days=7), is_completed=False)
            db.session.add_all([t1, t2, t3])
            db.session.commit()

            burnout_high = detect_burnout_and_deadline_clusters(str(student.id))
            self.assertEqual(burnout_high["risk_level"], "high")
            self.assertEqual(burnout_high["risk_title"], "High Workload Alert")
            self.assertGreaterEqual(burnout_high["cluster_count"], 1)

            # Complete the tasks and verify risk drops to low
            t1.is_completed = True
            t2.is_completed = True
            t3.is_completed = True
            db.session.commit()

            burnout_low = detect_burnout_and_deadline_clusters(str(student.id))
            self.assertEqual(burnout_low["risk_level"], "low")
            self.assertEqual(burnout_low["risk_title"], "Healthy Study Rhythm")

    def test_analytics_routes_and_apis(self):
        """Verify /analytics requires auth and returns 200 with chart metrics payload and forecast APIs."""
        # 1. Unauthenticated request redirects to /login
        res_unauth = self.client.get('/analytics', follow_redirects=False)
        self.assertEqual(res_unauth.status_code, 302)
        self.assertIn('/login', res_unauth.headers['Location'])

        # 2. Authenticated user access
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = "Ezra Student"
                sess['role'] = 'student'
                sess['is_profile_completed'] = True

        res_auth = self.client.get('/analytics')
        self.assertEqual(res_auth.status_code, 200)
        self.assertIn(b'Academic Analytics &amp; AI Insights Hub', res_auth.data)

        # 3. Test GET /api/analytics/metrics
        res_metrics = self.client.get('/api/analytics/metrics')
        self.assertEqual(res_metrics.status_code, 200)
        m_json = res_metrics.get_json()
        self.assertEqual(m_json["status"], "success")
        self.assertIn("charts", m_json["data"])
        self.assertIn("doughnut", m_json["data"]["charts"])
        self.assertIn("line", m_json["data"]["charts"])
        self.assertIn("heatmap", m_json["data"]["charts"])
        self.assertIn("radar", m_json["data"]["charts"])

        # 4. Test POST /api/analytics/forecast
        with self.app.app_context():
            course = Course.query.filter_by(course_name="Algorithms & Complexity").first()
            if not course:
                student = User.query.filter_by(username="student_user").first()
                course = Course(user_id=student.id, course_name="Testing Analytics Course", target_grade=80.0)
                db.session.add(course)
                db.session.commit()
            course_id = str(course.id)

        res_forecast = self.client.post('/api/analytics/forecast', json={
            "course_id": course_id,
            "target_grade": 85.0
        })
        self.assertEqual(res_forecast.status_code, 200)
        f_json = res_forecast.get_json()
        self.assertEqual(f_json["status"], "success")
        self.assertIn("required_pending_pct", f_json["data"])

        # 5. Test POST /api/analytics/generate-study-material
        res_ai = self.client.post('/api/analytics/generate-study-material', json={
            "course_id": course_id,
            "material_type": "flashcards"
        })
        self.assertEqual(res_ai.status_code, 200)
        ai_json = res_ai.get_json()
        self.assertEqual(ai_json["status"], "success")
        self.assertEqual(len(ai_json["data"]["items"]), 5)

    def test_syllabus_parser_and_fallback(self):
        """Verify syllabus text parser correctly extracts course details or gracefully degrades."""
        from services.automation_service import _heuristic_syllabus_parser
        text = """
        CS301 - Cloud Architecture and Scalable Systems
        Credit Hours: 4 Units
        Grading Components:
        - Lab 1 Docker: 15%
        - Midterm Examination: 35%
        - Final Project and Presentation: 50%
        """
        parsed = _heuristic_syllabus_parser(text, "CS301_Syllabus.pdf")
        self.assertEqual(parsed["credits"], 4)
        self.assertIn("CS301", parsed["course_name"])
        self.assertTrue(len(parsed["tasks"]) >= 3)
        weights = [t["weightage"] for t in parsed["tasks"]]
        self.assertIn(15.0, weights)
        self.assertIn(35.0, weights)
        self.assertIn(50.0, weights)

        # Malformed text test
        malformed = "Welcome to university. Attendance is expected."
        fallback = _heuristic_syllabus_parser(malformed, "notes.pdf")
        self.assertTrue(len(fallback["tasks"]) >= 1)

    def test_syllabus_batch_import_atomicity(self):
        """Verify batch importing syllabus atomically creates Course and Task records with relational integrity."""
        from services.automation_service import batch_import_syllabus
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            payload = {
                "course_name": "CS402 — Distributed Computing Systems",
                "semester": "Semester 1",
                "credits": 4,
                "target_grade": 88.0,
                "tasks": [
                    {"task_name": "Milestone 1: Raft Consensus", "weightage": 25.0, "due_date": "2026-10-20"},
                    {"task_name": "Milestone 2: MapReduce Engine", "weightage": 35.0, "due_date": "2026-11-15"},
                    {"task_name": "Final Defense", "weightage": 40.0, "due_date": "2026-12-05"}
                ]
            }
            res = batch_import_syllabus(student.id, payload)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["tasks_count"], 3)

            # Assert database state
            course = Course.query.filter_by(course_name="CS402 — Distributed Computing Systems").first()
            self.assertIsNotNone(course)
            self.assertEqual(course.credits, 4)
            self.assertEqual(len(course.tasks), 3)
            for t in course.tasks:
                self.assertEqual(t.course_id, course.id)
                self.assertEqual(t.user_id, student.id)
                self.assertGreater(t.weightage, 0)

    def test_schedule_rebalancer_avoids_class_collisions(self):
        """Verify self-healing schedule rebalancer cleans missed sessions and shifts revisions forward without class collisions."""
        from services.automation_service import rebalance_missed_schedule
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            today = date.today()

            # 1. Add fixed recurring Class on Monday 09:00 - 10:00
            class_sched = Schedule(
                user_id=student.id,
                title="CS402 Lecture",
                activity_type="Class",
                day_of_week="Monday",
                start_time="09:00",
                end_time="10:00",
                start_date=today,
                end_date=today + timedelta(days=30)
            )
            # 2. Add past missed revision session
            missed_sched = Schedule(
                user_id=student.id,
                title="Revision: Old Topic",
                activity_type="Revision",
                day_of_week="Sunday",
                start_time="14:00",
                end_time="15:00",
                start_date=today - timedelta(days=2),
                end_date=today - timedelta(days=2)
            )
            # 3. Add upcoming task
            task = Task(
                user_id=student.id,
                task_name="Distributed Consensus Lab",
                due_date=today + timedelta(days=7),
                is_completed=False
            )
            db.session.add_all([class_sched, missed_sched, task])
            db.session.commit()

            rebalance_res = rebalance_missed_schedule(student.id)
            self.assertEqual(rebalance_res["status"], "success")
            self.assertGreaterEqual(rebalance_res["rebalanced_count"], 1)

            # Assert old missed revision was purged
            old_check = Schedule.query.filter_by(title="Revision: Old Topic").first()
            self.assertIsNone(old_check)

            # Assert new revision sessions do not overlap with Monday 09:00 - 10:00
            monday_revisions = Schedule.query.filter_by(
                user_id=student.id,
                day_of_week="Monday",
                activity_type="Revision"
            ).all()
            for r in monday_revisions:
                # Interval overlap: max(start1, start2) < min(end1, end2)
                overlap = max("09:00", r.start_time) < min("10:00", r.end_time)
                self.assertFalse(overlap, f"Collision detected with Monday Class: {r.start_time} - {r.end_time}")

    def test_task_decomposition_and_subtasks_commit(self):
        """Verify task decomposer generates milestone sub-tasks and commits them to the task board."""
        from services.automation_service import decompose_task_with_ai, commit_subtasks_to_board
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            decomp = decompose_task_with_ai(
                student.id,
                task_title="Machine Learning Term Paper",
                due_date="2026-11-20",
                course_name="CS501 AI"
            )
            self.assertEqual(decomp["status"], "success")
            self.assertTrue(len(decomp["subtasks"]) >= 3)

            # Test committing subtasks
            commit_res = commit_subtasks_to_board(student.id, parent_task_id=None, subtasks=decomp["subtasks"][:2])
            self.assertEqual(commit_res["status"], "success")
            self.assertEqual(commit_res["created_count"], 2)

    def test_omnifinance_strict_decoupling(self):
        """Verify OmniFinance models are strictly decoupled with zero references to Course, Task, or Schedule."""
        from sqlalchemy import inspect
        with self.app.app_context():
            inspector = inspect(db.engine)
            for table_name in ['financial_accounts', 'financial_transactions']:
                fks = inspector.get_foreign_keys(table_name)
                referred_tables = {fk['referred_table'] for fk in fks}
                self.assertNotIn('courses', referred_tables)
                self.assertNotIn('tasks', referred_tables)
                self.assertNotIn('schedules', referred_tables)
                if table_name == 'financial_accounts':
                    self.assertEqual(referred_tables, {'users'})
                elif table_name == 'financial_transactions':
                    self.assertEqual(referred_tables, {'users', 'financial_accounts'})

    def test_omnifinance_net_worth_and_asset_allocation(self):
        """Verify aggregated net worth calculation: Total Assets - Liabilities across Malaysian platforms."""
        from services.finance_service import get_net_worth_overview, create_or_update_account
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()

            # 1. Create accounts across 5 categories
            create_or_update_account(student.id, {
                'institution_name': "Touch 'n Go eWallet",
                'account_category': 'ewallet',
                'current_balance': 350.00
            })
            create_or_update_account(student.id, {
                'institution_name': "Maybank",
                'account_category': 'bank_savings',
                'current_balance': 4500.00
            })
            create_or_update_account(student.id, {
                'institution_name': "myASNB",
                'account_category': 'investment_unit_trust',
                'current_balance': 8000.00
            })
            create_or_update_account(student.id, {
                'institution_name': "Moomoo Malaysia",
                'account_category': 'investment_stocks',
                'current_balance': 2000.00
            })
            create_or_update_account(student.id, {
                'institution_name': "PTPTN Education Loan",
                'account_category': 'credit_debt',
                'current_balance': 1500.00
            })

            overview = get_net_worth_overview(student.id)
            # Assets = 350 + 4500 + 8000 + 2000 = 14850.00
            self.assertEqual(overview['total_assets'], 14850.00)
            # Liabilities = 1500.00
            self.assertEqual(overview['total_liabilities'], 1500.00)
            # Net Worth = 14850 - 1500 = 13350.00
            self.assertEqual(overview['net_worth'], 13350.00)
            self.assertEqual(overview['account_count'], 5)

            # Check allocation percentage for ASNB (8000 / 14850 * 100 = 53.9%)
            asnb_alloc = overview['allocations']['investment_unit_trust']
            self.assertAlmostEqual(asnb_alloc['percentage'], 53.9, delta=0.5)

    def test_omnifinance_account_crud_and_cascade_delete(self):
        """Verify account creation, manual transaction logging, and cascade deletion."""
        from services.finance_service import (
            create_or_update_account, 
            create_manual_transaction, 
            delete_account,
            get_account_by_id
        )
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            acc_dict = create_or_update_account(student.id, {
                'institution_name': "CIMB Bank",
                'account_category': 'bank_savings',
                'account_nickname': "Savings",
                'current_balance': 1000.00
            })
            acc_id = acc_dict['id']

            # Add transaction
            tx_dict = create_manual_transaction(student.id, {
                'account_id': acc_id,
                'description': "Tealive Boba",
                'amount': 12.50,
                'transaction_type': 'expense'
            })
            tx_id = tx_dict['id']

            # Verify transaction exists in db
            tx = db.session.get(FinancialTransaction, uuid.UUID(tx_id))
            self.assertIsNotNone(tx)

            # Cascade delete account
            deleted = delete_account(student.id, acc_id)
            self.assertTrue(deleted)

            # Verify account and transaction were deleted
            self.assertIsNone(get_account_by_id(student.id, acc_id))
            self.assertIsNone(db.session.get(FinancialTransaction, uuid.UUID(tx_id)))

    def test_omnifinance_balance_reconcile(self):
        """Verify balance reconciliation updates balance and logs an audit adjustment transaction."""
        from services.finance_service import create_or_update_account, reconcile_account_balance
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            acc_dict = create_or_update_account(student.id, {
                'institution_name': "Boost eWallet",
                'account_category': 'ewallet',
                'current_balance': 100.00
            })
            acc_id = acc_dict['id']

            # Reconcile from 100.00 to 145.50 (+45.50)
            res = reconcile_account_balance(student.id, acc_id, 145.50, note="Monthly Statement Audit")
            self.assertEqual(res['current_balance'], 145.50)

            # Check audit transaction created
            adj_tx = FinancialTransaction.query.filter_by(account_id=acc_id).first()
            self.assertIsNotNone(adj_tx)
            self.assertEqual(adj_tx.transaction_type, 'income')
            self.assertAlmostEqual(float(adj_tx.amount), 45.50, delta=0.01)

    def test_omnifinance_statement_commit_and_balance_update(self):
        """Verify committing parsed statement transactions correctly updates account balance."""
        from services.finance_service import create_or_update_account
        from services.statement_parser import commit_statement_transactions
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            acc = create_or_update_account(student.id, {
                'institution_name': "RHB Bank",
                'account_category': 'bank_savings',
                'current_balance': 500.00
            })
            acc_id = acc['id']

            payload = {
                'transactions': [
                    {'transaction_date': '2026-09-15', 'description': 'Salary Credit', 'amount': 1200.00, 'transaction_type': 'income'},
                    {'transaction_date': '2026-09-16', 'description': 'Jaya Grocer', 'amount': 150.00, 'transaction_type': 'expense'}
                ]
            }

            res = commit_statement_transactions(student.id, acc_id, payload)
            self.assertEqual(res['status'], 'success')
            self.assertEqual(res['committed_count'], 2)
            # New balance = 500 + 1200 - 150 = 1550.00
            self.assertEqual(res['new_balance'], 1550.00)

    def test_omnifinance_api_endpoints(self):
        """Verify OmniFinance RESTful endpoints operate properly under authenticated session."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.username
                sess['role'] = student.role

        # 1. Net worth endpoint
        res = self.client.get('/api/finance/net-worth')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('net_worth', json_data['data'])

        # 2. Create account endpoint
        create_res = self.client.post('/api/finance/accounts', json={
            'institution_name': "Public Bank",
            'account_category': 'bank_savings',
            'account_nickname': "Fixed Deposit",
            'current_balance': 5000.00
        })
        self.assertEqual(create_res.status_code, 201)
        created_acc = create_res.get_json()['data']

        # 3. Reconcile endpoint
        rec_res = self.client.post(f"/api/finance/accounts/{created_acc['id']}/reconcile", json={
            'new_balance': 5200.00
        })
        self.assertEqual(rec_res.status_code, 200)
        self.assertEqual(rec_res.get_json()['data']['current_balance'], 5200.00)

        # 4. View routes
        dash_res = self.client.get('/finance')
        self.assertEqual(dash_res.status_code, 200)
        acc_page_res = self.client.get('/finance/accounts')
        self.assertEqual(acc_page_res.status_code, 200)
        stmt_page_res = self.client.get('/finance/statements')
        self.assertEqual(stmt_page_res.status_code, 200)
        tx_page_res = self.client.get('/finance/transactions')
        self.assertEqual(tx_page_res.status_code, 200)
        budget_page_res = self.client.get('/finance/budgets')
        self.assertEqual(budget_page_res.status_code, 200)

    def test_omnidigest_strict_decoupling(self):
        """Verify OmniDigest models are strictly decoupled with zero references to academic or financial tables."""
        from sqlalchemy import inspect
        with self.app.app_context():
            inspector = inspect(db.engine)
            for table_name in ['user_interest_sources', 'digest_reports']:
                fks = inspector.get_foreign_keys(table_name)
                referred_tables = {fk['referred_table'] for fk in fks}
                self.assertNotIn('courses', referred_tables)
                self.assertNotIn('tasks', referred_tables)
                self.assertNotIn('schedules', referred_tables)
                self.assertNotIn('financial_accounts', referred_tables)
                self.assertEqual(referred_tables, {'users'})

    def test_omnidigest_caching_and_idempotency(self):
        """Verify daily digest caching: consecutive calls for the same day return cached report without duplicate DB entries."""
        from services.digest_service import get_or_create_daily_digest
        with self.app.app_context():
            student = User.query.filter_by(username="student_user").first()
            today_val = date.today()

            # First generation
            report1 = get_or_create_daily_digest(student.id, target_date=today_val, force_refresh=False)
            self.assertIsNotNone(report1)
            self.assertIn('title', report1)
            self.assertIn('Top 3 Must-Know Headlines', report1['summary_content'])

            # Second call should fetch cached report with same ID
            report2 = get_or_create_daily_digest(student.id, target_date=today_val, force_refresh=False)
            self.assertEqual(report1['id'], report2['id'])

            # Verify only 1 record exists in DB for this date
            reports_in_db = DigestReport.query.filter_by(user_id=student.id, report_type='daily', report_date=today_val).all()
            self.assertEqual(len(reports_in_db), 1)

    def test_omnidigest_cascade_delete(self):
        """Verify deleting a user cascades to all their interest sources and digest reports."""
        with self.app.app_context():
            temp_user = User(
                fullname="Temp Digest User",
                username="temp_digest_user",
                email="tempdigest@test.com",
                student_type="IT",
                role="student"
            )
            temp_user.set_password("pass123")
            db.session.add(temp_user)
            db.session.commit()

            # Add source and report
            src = UserInterestSource(
                user_id=temp_user.id,
                title="The Edge Malaysia",
                source_url="https://theedgemalaysia.com/rss",
                category="finance"
            )
            rep = DigestReport(
                user_id=temp_user.id,
                report_type="daily",
                report_date=date.today(),
                title="Temp Briefing",
                summary_content="Sample summary",
                reading_time_mins=3
            )
            db.session.add_all([src, rep])
            db.session.commit()

            src_id = src.id
            rep_id = rep.id

            # Delete user
            db.session.delete(temp_user)
            db.session.commit()

            # Verify cascade deletion
            self.assertIsNone(db.session.get(UserInterestSource, src_id))
            self.assertIsNone(db.session.get(DigestReport, rep_id))

    def test_omnidigest_rss_feed_fault_tolerance(self):
        """Verify feed ingestion handles unreachable or malformed URLs gracefully without crashing."""
        from services.digest_service import fetch_source_headlines
        # 1. Non-existent domain
        res1 = fetch_source_headlines("http://invalid-non-existent-feed-domain-12345.com/rss")
        self.assertEqual(res1, [])

        # 2. Malformed URL
        res2 = fetch_source_headlines("not-even-a-url")
        self.assertEqual(res2, [])

    def test_omnidigest_api_endpoints(self):
        """Verify OmniDigest REST endpoints under an authenticated session."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.username
                sess['role'] = student.role

        # 1. GET /api/reports/today
        res = self.client.get('/api/reports/today')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('summary_content', data['data'])

        # 2. POST /api/reports/sources
        create_src = self.client.post('/api/reports/sources', json={
            'title': 'Hacker News RSS',
            'source_url': 'https://news.ycombinator.com/rss',
            'category': 'technology'
        })
        self.assertEqual(create_src.status_code, 201)
        src_id = create_src.get_json()['data']['id']

        # 3. GET /api/reports/sources
        get_srcs = self.client.get('/api/reports/sources')
        self.assertEqual(get_srcs.status_code, 200)
        self.assertGreaterEqual(len(get_srcs.get_json()['data']['sources']), 1)

        # 4. PUT /api/reports/sources/<id>
        put_src = self.client.put(f'/api/reports/sources/{src_id}', json={'is_active': False})
        self.assertEqual(put_src.status_code, 200)
        self.assertFalse(put_src.get_json()['data']['is_active'])

        # 5. DELETE /api/reports/sources/<id>
        del_src = self.client.delete(f'/api/reports/sources/{src_id}')
        self.assertEqual(del_src.status_code, 200)

        # 6. Page views
        p1 = self.client.get('/reports')
        self.assertEqual(p1.status_code, 200)
        p2 = self.client.get('/reports/weekly')
        self.assertEqual(p2.status_code, 200)
        p3 = self.client.get('/reports/sources')
        self.assertEqual(p3.status_code, 200)

    # =========================================================================
    # Life Planner OS (OmniLife) Enterprise Modular Monolith Test Cases
    # =========================================================================

    def test_core_package_exports_and_backward_compatibility(self):
        """Verify core package exports and backward compatibility via extensions and utils/auth."""
        import core
        self.assertIsNotNone(core.db)
        self.assertIsNotNone(core.GUID)
        self.assertIsNotNone(core.login_required)
        self.assertIsNotNone(core.role_required)
        self.assertIsNotNone(core.registry)
        self.assertIsNotNone(core.LifePlannerModule)

        # Backward compatibility aliases
        import extensions
        self.assertIs(extensions.db, core.db)
        self.assertIs(extensions.GUID, core.GUID)

        import utils.auth
        self.assertIs(utils.auth.login_required, core.login_required)
        self.assertIs(utils.auth.role_required, core.role_required)

    def test_pluggable_module_registry(self):
        """Verify the 6 foundational Life Planner OS domain modules are registered."""
        from core.registry import get_registered_modules, get_workspaces_list, get_module

        modules = get_registered_modules()
        self.assertGreaterEqual(len(modules), 6)

        keys = [m.key for m in modules]
        expected_keys = ['academics', 'finance', 'life', 'reports', 'journal', 'career']
        for k in expected_keys:
            self.assertIn(k, keys)
            mod = get_module(k)
            self.assertIsNotNone(mod)
            self.assertTrue(mod.name)
            self.assertTrue(mod.url)
            self.assertTrue(mod.icon)

        ws_list = get_workspaces_list()
        self.assertGreaterEqual(len(ws_list), 6)
        ws_keys = [w['key'] for w in ws_list]
        for k in expected_keys:
            self.assertIn(k, ws_keys)

    def test_pluggable_registry_extension(self):
        """Verify registering a new future domain module works cleanly without modifying core infrastructure."""
        from core.registry import LifePlannerModule, registry, get_module

        fitness_mod = LifePlannerModule(
            key='fitness',
            name='Health & Fitness',
            short_name='Fitness',
            icon='bi-heart-pulse-fill',
            color='#e11d48',
            url='/fitness',
            badge='Workouts & Health',
            description='Daily workout logging, cardio tracker and nutrition ledger'
        )
        registry.register(fitness_mod)

        retrieved = get_module('fitness')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'Health & Fitness')
        self.assertEqual(retrieved.color, '#e11d48')
        self.assertEqual(retrieved.to_dict()['badge'], 'Workouts & Health')

    def test_workspace_switcher_all_six_domains(self):
        """Verify /workspace/<name> seamlessly updates session and redirects for all 6 life domains."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.username
                sess['role'] = student.role

        domain_targets = {
            'academics': '/student/dashboard',
            'finance': '/finance',
            'life': '/life',
            'reports': '/reports',
            'journal': '/journal',
            'career': '/career'
        }

        for domain, expected_url in domain_targets.items():
            res = self.client.get(f'/workspace/{domain}')
            self.assertEqual(res.status_code, 302, f"Failed for domain {domain}")
            self.assertIn(expected_url, res.headers['Location'])

    def test_route_aliases_preserved(self):
        """Verify legacy bookmark route aliases continue functioning seamlessly."""
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                student = User.query.filter_by(username="student_user").first()
                sess['user_id'] = str(student.id)
                sess['username'] = student.username
                sess['role'] = student.role

        aliases = [
            '/dashboard',
            '/study-planner',
            '/calendar',
            '/grades',
            '/study-assistant',
            '/analytics',
            '/finance',
            '/life',
            '/reports',
            '/journal',
            '/career'
        ]

        for route in aliases:
            res = self.client.get(route)
            self.assertIn(res.status_code, [200, 302], f"Route alias {route} failed with status {res.status_code}")

if __name__ == '__main__':
    unittest.main()



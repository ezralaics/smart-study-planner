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

if __name__ == '__main__':
    unittest.main()


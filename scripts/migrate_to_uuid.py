"""
PostgreSQL Schema Migration: Integer IDs -> UUIDv4 Primary & Foreign Keys
Safely migrates users, courses, tasks, and schedules while preserving all existing data and relationships.
"""
import uuid
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text, inspect
from app import create_app
from extensions import db

def run_migration():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        if 'users' not in inspector.get_table_names():
            print("[NOTICE] Table 'users' not found. Creating all tables from current models...")
            db.create_all()
            print("[SUCCESS] Database tables created with UUIDv4 schema.")
            return

        users_id_col = next((c for c in inspector.get_columns('users') if c['name'] == 'id'), None)
        if not users_id_col:
            print("[ERROR] 'id' column not found in 'users' table.")
            return

        col_type_str = str(users_id_col['type']).upper()
        if 'UUID' in col_type_str:
            print("[OK] Database is already running on native UUID columns. Checking indexes & updated_at...")
            ensure_timestamps_and_indexes()
            return

        print(f"[INFO] Current users.id type: {col_type_str}. Beginning safe UUIDv4 migration...")

        with db.engine.connect() as conn:
            # Begin explicit transaction
            trans = conn.begin()
            try:
                # Enable pgcrypto if possible for default gen_random_uuid
                try:
                    conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
                except Exception as e:
                    print("Notice: pgcrypto extension not enabled, Python will generate UUIDs directly.", e)

                # 1. Generate UUID mappings for all existing tables in memory
                print("Step 1: Reading existing records and generating UUIDv4 mappings...")
                user_rows = conn.execute(text("SELECT id FROM users")).fetchall()
                user_map = {row[0]: str(uuid.uuid4()) for row in user_rows}

                course_rows = conn.execute(text("SELECT id, user_id FROM courses")).fetchall()
                course_map = {row[0]: str(uuid.uuid4()) for row in course_rows}

                task_rows = conn.execute(text("SELECT id, course_id, user_id FROM tasks")).fetchall()
                task_map = {row[0]: str(uuid.uuid4()) for row in task_rows}

                schedule_rows = conn.execute(text("SELECT id, user_id FROM schedules")).fetchall()
                schedule_map = {row[0]: str(uuid.uuid4()) for row in schedule_rows}

                print(f"Mapped {len(user_map)} users, {len(course_map)} courses, {len(task_map)} tasks, {len(schedule_map)} schedules.")

                # 2. Add temporary UUID columns
                print("Step 2: Adding temporary UUID columns...")
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS uuid_id UUID;"))
                conn.execute(text("ALTER TABLE courses ADD COLUMN IF NOT EXISTS uuid_id UUID, ADD COLUMN IF NOT EXISTS user_uuid UUID;"))
                conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS uuid_id UUID, ADD COLUMN IF NOT EXISTS course_uuid UUID, ADD COLUMN IF NOT EXISTS user_uuid UUID;"))
                conn.execute(text("ALTER TABLE schedules ADD COLUMN IF NOT EXISTS uuid_id UUID, ADD COLUMN IF NOT EXISTS user_uuid UUID;"))

                # 3. Populate temporary UUID columns with the mappings
                print("Step 3: Populating UUID values across all tables...")
                for old_id, new_uuid in user_map.items():
                    conn.execute(text("UPDATE users SET uuid_id = :uuid WHERE id = :old_id"), {"uuid": new_uuid, "old_id": old_id})

                for old_id, new_uuid in course_map.items():
                    conn.execute(text("UPDATE courses SET uuid_id = :uuid WHERE id = :old_id"), {"uuid": new_uuid, "old_id": old_id})
                for old_c_id, old_u_id in course_rows:
                    if old_u_id in user_map:
                        conn.execute(text("UPDATE courses SET user_uuid = :u_uuid WHERE id = :old_id"), {"u_uuid": user_map[old_u_id], "old_id": old_c_id})

                for old_id, new_uuid in task_map.items():
                    conn.execute(text("UPDATE tasks SET uuid_id = :uuid WHERE id = :old_id"), {"uuid": new_uuid, "old_id": old_id})
                for old_t_id, old_c_id, old_u_id in task_rows:
                    params = {"old_id": old_t_id}
                    updates = []
                    if old_c_id and old_c_id in course_map:
                        updates.append("course_uuid = :c_uuid")
                        params["c_uuid"] = course_map[old_c_id]
                    if old_u_id and old_u_id in user_map:
                        updates.append("user_uuid = :u_uuid")
                        params["u_uuid"] = user_map[old_u_id]
                    if updates:
                        conn.execute(text(f"UPDATE tasks SET {', '.join(updates)} WHERE id = :old_id"), params)

                for old_id, new_uuid in schedule_map.items():
                    conn.execute(text("UPDATE schedules SET uuid_id = :uuid WHERE id = :old_id"), {"uuid": new_uuid, "old_id": old_id})
                for old_s_id, old_u_id in schedule_rows:
                    if old_u_id in user_map:
                        conn.execute(text("UPDATE schedules SET user_uuid = :u_uuid WHERE id = :old_id"), {"u_uuid": user_map[old_u_id], "old_id": old_s_id})

                # 4. Drop old foreign key constraints
                print("Step 4: Dropping legacy foreign key constraints...")
                # Find and drop constraints referencing users and courses
                fk_query = text("""
                    SELECT conrelid::regclass AS table_name, conname AS fk_name
                    FROM pg_constraint
                    WHERE contype = 'f' AND confrelid::regclass IN ('users'::regclass, 'courses'::regclass);
                """)
                for fk in conn.execute(fk_query).fetchall():
                    conn.execute(text(f"ALTER TABLE {fk[0]} DROP CONSTRAINT IF EXISTS {fk[1]};"))

                # 5. Drop old primary keys & columns, rename UUID columns to standard names
                print("Step 5: Swapping integer primary and foreign keys with UUIDv4...")
                for tbl in ['schedules', 'tasks', 'courses', 'users']:
                    # Drop existing PK constraint
                    pk_name = conn.execute(text(f"""
                        SELECT conname FROM pg_constraint
                        WHERE contype = 'p' AND conrelid = '{tbl}'::regclass;
                    """)).scalar()
                    if pk_name:
                        conn.execute(text(f"ALTER TABLE {tbl} DROP CONSTRAINT {pk_name};"))

                # Drop old integer ID and rename uuid_id to id
                conn.execute(text("ALTER TABLE users DROP COLUMN id;"))
                conn.execute(text("ALTER TABLE users RENAME COLUMN uuid_id TO id;"))
                conn.execute(text("ALTER TABLE users ALTER COLUMN id SET NOT NULL;"))
                conn.execute(text("ALTER TABLE users ADD PRIMARY KEY (id);"))

                conn.execute(text("ALTER TABLE courses DROP COLUMN id;"))
                conn.execute(text("ALTER TABLE courses RENAME COLUMN uuid_id TO id;"))
                conn.execute(text("ALTER TABLE courses ALTER COLUMN id SET NOT NULL;"))
                conn.execute(text("ALTER TABLE courses ADD PRIMARY KEY (id);"))
                conn.execute(text("ALTER TABLE courses DROP COLUMN user_id;"))
                conn.execute(text("ALTER TABLE courses RENAME COLUMN user_uuid TO user_id;"))
                conn.execute(text("ALTER TABLE courses ALTER COLUMN user_id SET NOT NULL;"))

                conn.execute(text("ALTER TABLE tasks DROP COLUMN id;"))
                conn.execute(text("ALTER TABLE tasks RENAME COLUMN uuid_id TO id;"))
                conn.execute(text("ALTER TABLE tasks ALTER COLUMN id SET NOT NULL;"))
                conn.execute(text("ALTER TABLE tasks ADD PRIMARY KEY (id);"))
                conn.execute(text("ALTER TABLE tasks DROP COLUMN user_id;"))
                conn.execute(text("ALTER TABLE tasks RENAME COLUMN user_uuid TO user_id;"))
                conn.execute(text("ALTER TABLE tasks DROP COLUMN course_id;"))
                conn.execute(text("ALTER TABLE tasks RENAME COLUMN course_uuid TO course_id;"))

                conn.execute(text("ALTER TABLE schedules DROP COLUMN id;"))
                conn.execute(text("ALTER TABLE schedules RENAME COLUMN uuid_id TO id;"))
                conn.execute(text("ALTER TABLE schedules ALTER COLUMN id SET NOT NULL;"))
                conn.execute(text("ALTER TABLE schedules ADD PRIMARY KEY (id);"))
                conn.execute(text("ALTER TABLE schedules DROP COLUMN user_id;"))
                conn.execute(text("ALTER TABLE schedules RENAME COLUMN user_uuid TO user_id;"))
                conn.execute(text("ALTER TABLE schedules ALTER COLUMN user_id SET NOT NULL;"))

                # 6. Re-create foreign keys with ON DELETE CASCADE
                print("Step 6: Creating foreign keys with ON DELETE CASCADE...")
                conn.execute(text("ALTER TABLE courses ADD CONSTRAINT fk_courses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;"))
                conn.execute(text("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;"))
                conn.execute(text("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE;"))
                conn.execute(text("ALTER TABLE schedules ADD CONSTRAINT fk_schedules_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;"))

                # 7. Add updated_at and production composite indexes
                print("Step 7: Adding updated_at timestamps and composite indexes...")
                for tbl in ['users', 'courses', 'tasks', 'schedules']:
                    conn.execute(text(f"ALTER TABLE {tbl} ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"))

                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_courses_user_completed ON courses(user_id, is_completed);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_user_due_completed ON tasks(user_id, due_date, is_completed);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_course_due ON tasks(course_id, due_date);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_schedules_user_day ON schedules(user_id, day_of_week);"))

                # Commit transaction
                trans.commit()
                print("[SUCCESS] MIGRATION COMPLETE! All 4 tables successfully refactored to UUIDv4.")

            except Exception as e:
                trans.rollback()
                print(f"[ERROR] Migration failed and was rolled back safely: {e}")
                raise e

def ensure_timestamps_and_indexes():
    """Ensures indexes and updated_at exist even if schema was already UUID."""
    with db.engine.connect() as conn:
        with conn.begin():
            for tbl in ['users', 'courses', 'tasks', 'schedules']:
                conn.execute(text(f"ALTER TABLE {tbl} ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_courses_user_completed ON courses(user_id, is_completed);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_user_due_completed ON tasks(user_id, due_date, is_completed);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_course_due ON tasks(course_id, due_date);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_schedules_user_day ON schedules(user_id, day_of_week);"))
    print("[SUCCESS] Indexes and updated_at columns verified.")

if __name__ == '__main__':
    run_migration()

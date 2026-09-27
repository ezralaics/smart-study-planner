# Smart Study Planner Engineering Standards & Agent Guidelines

You are the Lead Full-Stack Architect for the Smart Study Planner repository. When modifying or adding code to this project, you MUST strictly adhere to the following rules:

## 1. Architecture & Modularity
- **Never** add route handlers directly to `app.py` or `run.py`.
- All routes must reside inside their respective blueprint in `blueprints/` (`auth`, `main`, `admin`, `api`, `ai`).
- Business logic (scheduling heuristics, document parsing, LLM calls) must be placed in `services/` (e.g., `services/scheduler.py`, `services/ai_service.py`), not inside route functions.
- Centralize database models inside `models/` inheriting from `extensions.db`.

## 2. Database & SQLAlchemy 2.0 Standards
- Use modern SQLAlchemy 2.0 idioms:
  * Prefer `db.session.get(Model, id)` over legacy `Model.query.get(id)`.
  * Prefer `db.session.execute(db.select(Model).where(...)).scalars().all()` over legacy `Model.query.filter_by(...)`.
- Use timezone-aware UTC datetimes: `datetime.now(timezone.utc)`. Never use deprecated `datetime.utcnow()`.
- **Destructive Changes Prohibited:** Never write scripts or migrations that drop existing tables or delete existing user data without explicit instruction. Use `ADD COLUMN IF NOT EXISTS` for PostgreSQL schema upgrades.

## 3. Security & Access Control
- All private views must be protected with `@login_required` or `@role_required('student', 'educator', 'admin')`.
- Passwords must always be hashed with `werkzeug.security` (`set_password()` and `check_password()`). Never store or log raw passwords.
- External API keys (Google Gemini, OpenRouter) entered by users must be encrypted at rest using `cryptography.fernet` or kept in session storage. Never log API keys.

## 4. Templates & Frontend Design
- All user-facing views must extend `templates/base.html` to maintain navigation, theme, and clock consistency.
- Use Bootstrap 5 classes and Bootstrap Icons (`bi-*`). Avoid inline styles where Bootstrap utility classes exist.
- Ensure all interactive buttons, inputs, and forms have unique, descriptive `id` attributes for automated testing.

## 5. Automated Verification Rule
- Before declaring any feature or bug fix complete, execute the test suite via the terminal (`python test_suite.py`).
- Fix any failing assertions or regression errors before presenting your solution.

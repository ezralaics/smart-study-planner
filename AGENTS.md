# Smart Study Planner Enterprise Engineering Standards & AI Guidelines

You are the Lead Full-Stack Architect for the Smart Study Planner repository. When modifying or adding code to this project, you MUST strictly adhere to these industry-standard requirements:

## 1. System Architecture & System Design
- **Layered Clean Architecture:** Strictly separate concerns into distinct tiers:
  * **Presentation Tier:** Templates (`templates/*.html`, Jinja2 layouts) & assets (`static/`).
  * **Controller Tier:** Blueprint route handlers (`blueprints/<module>/routes.py`). Must only handle request validation, authorization checks, and HTTP responses. Keep route functions concise (<50 lines).
  * **Domain/Service Tier:** Core business logic, scheduling heuristics, document parsing, and LLM integrations must reside in `services/`.
  * **Persistence Tier:** Database models in `models/` inheriting from `extensions.db`.
- **Application Factory Pattern:** Never initialize `SQLAlchemy()` or attach routes directly to `app.py`. All extensions are registered in `create_app()`.
- **RESTful API Contracts:** All `/api/*` endpoints must follow standard REST conventions with uniform JSON response envelopes:
  * Success: `{ "status": "success", "data": { ... }, "message": "..." }` (HTTP 200/201)
  * Error: `{ "status": "error", "message": "...", "errors": [ ... ] }` (HTTP 400/401/403/404/500)
- **Centralized Error Handling & Logging:** Use Python's built-in `logging` module. Never use raw `print()` statements for debugging or production logging.

## 2. Database Standards & Relational Integrity
- **ORM Standards:** Use modern SQLAlchemy 2.0 syntax:
  * Prefer `db.session.get(Model, id)` over legacy `Model.query.get(id)`.
  * Prefer `db.session.execute(db.select(Model).where(...)).scalars().all()` over legacy `Model.query.filter_by(...)`.
- **Relational Integrity & Cascade Rules:** Explicitly declare foreign key delete behaviors (`ondelete='CASCADE'` or `ondelete='SET NULL'`).
- **Indexing Strategy:** Foreign key columns (`user_id`, `course_id`) and high-frequency search fields (`due_date`, `is_completed`) must have database indexes.
- **Auditability & Timezones:** Every model must track `created_at` and `updated_at` using timezone-aware UTC (`datetime.now(timezone.utc)`). Never use deprecated `datetime.utcnow()`.
- **Transaction Atomicity:** Always encapsulate database commits in `try...except` blocks with explicit `db.session.rollback()` on exception.
- **Non-Destructive Evolution:** Never drop tables or existing columns. Use safe migration techniques (`ADD COLUMN IF NOT EXISTS`).

## 3. UI / UX Design & Accessibility Standards (WCAG 2.1 AA)
- **Master Layout Consistency:** All views must extend `templates/base.html` to preserve global navigation, live clock, offcanvas sidebar, and theme tokens.
- **Visual Design System:** Use the `Inter` font, standardized 12px-16px card radii, and consistent color palette (`#0d6efd` primary, `#198754` success, `#dc3545` urgent).
- **Asynchronous Feedback:**
  * Disable buttons and show loading spinners on async fetch/submit operations.
  * Use non-blocking Bootstrap toast notifications for user alerts instead of native browser `alert()`.
- **Empty States:** When a dataset contains 0 items, display a clean empty-state card with an icon, explanatory guidance, and a prominent Action button.
- **Accessibility:** Form controls must have descriptive `<label for="...">` associations, minimum 44x44px touch targets, and semantic HTML elements (`<main>`, `<nav>`, `<section>`).

## 4. Security & Production Hardening
- **Access Control:** Guard every private route with `@login_required` or `@role_required(...)`.
- **Password Security:** Always hash passwords with `werkzeug.security` (`set_password()` and `check_password()`).
- **Secrets & BYOK Management:** External API keys (Google Gemini, OpenRouter) entered by users must be encrypted at rest using `cryptography.fernet` or preserved in session/client state. Never log or leak keys.
- **Input Sanitization:** Validate and sanitize all user input; rely on SQLAlchemy parameterized queries to prevent SQL injection.

## 5. Automated Verification Rule
- Before completing any task, run the test suite: `python test_suite.py`.
- Fix any failing assertions or regressions before delivering your changes.

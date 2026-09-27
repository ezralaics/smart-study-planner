---
name: system-architecture-audit
description: Use this skill when reviewing, refactoring, or auditing the codebase against industry-standard software engineering benchmarks (Clean Architecture, RESTful API contracts, database normalization, indexing, and error handling).
---

# System Architecture & Design Audit Skill

This skill guides the evaluation and enhancement of the system architecture to meet enterprise software engineering benchmarks.

## 1. Clean Layered Architecture (Separation of Concerns)
Every component must belong to its strict architectural tier:

```
[Presentation Tier]   templates/ (*.html, Jinja2 layouts) + static/ (CSS, JS)
       │
[Controller Tier]     blueprints/<module>/routes.py (Input validation, auth guards, HTTP responses)
       │
[Domain/Service Tier] services/*.py (Business logic, scheduling, LLM orchestration, parsers)
       │
[Persistence Tier]    models/*.py + extensions.db (SQLAlchemy ORM, database entities)
```

- **Rule:** Controllers (`routes.py`) MUST NOT contain raw algorithmic logic or complex database transformations. Delegate to `services/`.
- **Rule:** Never instantiate `SQLAlchemy()` multiple times; always import `db` from `extensions.py`.

## 2. RESTful API Contract Standards
All `/api/*` endpoints must follow strict REST conventions:

| Action | HTTP Method | Route Example | Success Status | Error Status |
| :--- | :--- | :--- | :--- | :--- |
| Read Resource | `GET` | `/api/courses` | `200 OK` | `401`, `404` |
| Create Resource | `POST` | `/api/courses` | `201 Created` | `400 Bad Request` |
| Update Resource | `PUT` / `PATCH` | `/api/courses/<id>` | `200 OK` | `400`, `404` |
| Delete Resource | `DELETE` | `/api/courses/<id>` | `200 OK` | `404 Not Found` |

### Uniform JSON Response Envelope
All API endpoints must return a predictable JSON payload:
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```
Error responses:
```json
{
  "status": "error",
  "message": "Descriptive error message",
  "errors": [ ... ]
}
```

## 3. Database Standards & Integrity
1. **Primary & Foreign Keys:**
   - Use UUIDv4 or indexed BigInteger for high-cardinality tables.
   - Enforce `ondelete='CASCADE'` on child records (e.g., tasks belonging to a deleted course).
2. **Indexing:**
   - Always index foreign key columns (`user_id`, `course_id`).
   - Add composite indexes on common query filters: `(user_id, is_completed)` and `(user_id, due_date)`.
3. **Auditability:**
   - Every model must track `created_at` and `updated_at` with timezone-aware UTC (`datetime.now(timezone.utc)`).
4. **Transaction Safety:**
   - Wrap state modifications in `try...except` blocks with explicit `db.session.rollback()` on failure.

## 4. Audit Checklist
Before committing major changes:
- [ ] Are route functions under 50 lines of code?
- [ ] Are database queries using modern SQLAlchemy 2.0 (`db.session.get`, `db.select`)?
- [ ] Are all database updates wrapped with `rollback()` handlers?
- [ ] Is input sanitized and validated before database ingestion?

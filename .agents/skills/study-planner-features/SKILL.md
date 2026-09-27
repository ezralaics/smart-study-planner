---
name: study-planner-features
description: Use this skill when creating a new page, blueprint, or database model for the Smart Study Planner (e.g., settings, grades, calendar, educator portal).
---

# Smart Study Planner Feature Workflow

Follow this 4-step sequence when adding any new feature to the codebase:

## Step 1: Model & Migration
1. Define the model in `models/<entity>.py`.
2. Export the model in `models/__init__.py`.
3. Add a non-destructive column/table check in `app.py` `create_app()` hook.

## Step 2: Blueprint Route Implementation
1. Create or open `blueprints/<module>/routes.py`.
2. Apply appropriate decorators:
   ```python
   @bp.route('/my-endpoint')
   @login_required
   @role_required('student', 'educator')
   def my_view(): ...
   ```
3. Always return JSON for `/api/*` routes and `render_template` for view routes.

## Step 3: Template Integration
1. Extend `base.html`:
   ```jinja2
   {% extends "base.html" %}
   {% block title %}Feature Title | Smart Study Planner{% endblock %}
   {% block content %} ... {% endblock %}
   ```
2. Update the navigation link in `templates/base.html` so users can access the new page.

## Step 4: Verification
Add a test in `test_suite.py` asserting:
- Unauthenticated access redirects to `/login`.
- Authenticated user receives status 200.

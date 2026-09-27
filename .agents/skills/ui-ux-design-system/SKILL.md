---
name: ui-ux-design-system
description: Use this skill when designing, reviewing, or styling frontend interfaces, templates, modals, forms, or animations in the Smart Study Planner to adhere to modern UI/UX and WCAG accessibility standards.
---

# UI/UX Design System & Accessibility Skill

This skill enforces modern, professional design aesthetics and user experience patterns across all templates.

## 1. Visual Design Tokens & Hierarchy
All page views must strictly follow the core design system defined in `templates/base.html` and `static/style.css`:

- **Typography:** Use the `Inter` font family with clear weight hierarchy:
  * Page Title: `fw-bold fs-3` (700/800 weight)
  * Section Headers: `fw-semibold fs-5` (600 weight)
  * Body Text: `text-main` (400 weight, 1.5 line-height)
  * Subtitles & Meta: `text-muted small`
- **Color Palette & Contrast:**
  * Primary Accent: `#0d6efd` (Bootstrap Blue)
  * Secondary / Deep Accent: `#0a4da2`
  * Neutral Background: `#f4f7f6` (Light mode) / `#121212` (Dark mode)
  * Card Surfaces: White `#ffffff` with subtle elevation: `box-shadow: 0 4px 12px rgba(0,0,0,0.05)`
  * Semantic Accents: Green `#198754` (Complete/Success), Amber `#ffc107` (Warning), Red `#dc3545` (Urgent/Danger)
- **Border Radii:** Standardize on modern rounded corners: `border-radius: 12px` to `16px` for cards and modals, `8px` for buttons and input fields.

## 2. Interaction Design & Feedback Loops
Never leave the user wondering if an action succeeded or failed:

1. **Async Button States:**
   - On clicking submit or fetch buttons (e.g., Save Course, Generate Plan), immediately disable the button and show a spinner:
     ```html
     <button class="btn btn-primary" id="saveBtn" disabled>
       <span class="spinner-border spinner-border-sm me-2" role="status"></span>Saving...
     </button>
     ```
2. **Toast Notifications:**
   - Display non-intrusive Bootstrap toast notifications in the top-right corner for success/failure feedback instead of blocking browser `alert()`.
3. **Empty States with Clear CTAs:**
   - When lists are empty (e.g. 0 courses or 0 tasks), display a clean empty state card with an icon, explanatory text, and a prominent Action button:
     ```html
     <div class="text-center py-5">
       <i class="bi bi-journal-plus fs-1 text-muted"></i>
       <h5 class="fw-bold mt-3">No Courses Added Yet</h5>
       <p class="text-muted small">Add your first semester course to start generating study schedules.</p>
       <button class="btn btn-primary mt-2" data-bs-toggle="modal" data-bs-target="#addCourseModal">Add Course</button>
     </div>
     ```
4. **Destructive Action Confirmation:**
   - Deleting a course, task, or schedule must trigger a confirmation modal (never rely solely on native `confirm()`).

## 3. Accessibility Standards (WCAG 2.1 AA)
- **Tap Targets:** Interactive elements must have a minimum clickable area of 44x44px for touch usability.
- **Form Inputs:** Every `<input>`, `<select>`, and `<textarea>` must have an associated `<label>` with a matching `for="<id>"` attribute.
- **Semantic HTML:** Use `<header>`, `<nav>`, `<main>`, `<section>`, and `<footer>` elements rather than generic nested `<div>` blocks.
- **Keyboard Navigation:** Ensure modal dialogues manage focus properly and can be closed with the <kbd>Esc</kbd> key.

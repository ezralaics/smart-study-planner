import json
import logging
import re
from datetime import datetime, date, timedelta, time, timezone
from extensions import db
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from models.user import User
from services.ai_service import resolve_api_keys, query_google_gemini, query_openrouter
from services.document_parser import extract_text_from_file, allowed_file, MAX_FILE_SIZE
from services.tier_service import get_tier_config
import os
import uuid
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

SYLLABUS_EXTRACTION_PROMPT = """You are an expert academic curriculum parser and university registrar assistant.
Analyze the following course syllabus document and extract the core course details and graded assessment components.

Return ONLY a valid JSON object with NO markdown backticks, matching this exact schema:
{
  "course_name": "Course Title or Code (e.g. CS301 - Cloud Architecture)",
  "semester": "Semester 1",
  "credits": 3,
  "target_grade": 80.0,
  "tasks": [
    {
      "task_name": "Name of assignment, quiz, lab, midterm, or final exam",
      "weightage": 20.0,
      "due_date": "YYYY-MM-DD"
    }
  ]
}

Guidelines:
1. Ensure the sum of weightages does not exceed 100%. If weights are missing, estimate reasonable percentages (e.g. 20% assignments, 30% midterm, 50% final exam).
2. For due dates, format as YYYY-MM-DD if explicitly stated. If only a week is mentioned (e.g., Week 6), project a realistic future date within the active academic term. If completely absent, leave due_date as an empty string "".
3. Keep task names descriptive (e.g. "Lab 1: Docker Containers", "Midterm Examination", "Final Project Milestone").

SYLLABUS DOCUMENT TEXT:
"""

TASK_DECOMPOSITION_PROMPT = """You are an agile academic project coach and study strategist.
A student needs to break down the following major academic task or project into 3 to 5 clear, actionable sub-task milestones:

Task Title: "{task_title}"
Course Subject: "{course_name}"
Final Due Date: "{due_date}"

Return ONLY a valid JSON object with NO markdown backticks, matching this exact schema:
{
  "subtasks": [
    {
      "title": "Clear action-oriented sub-task name (e.g. Literature Review & Requirement Gathering)",
      "estimated_hours": 3.5,
      "recommended_due_date": "YYYY-MM-DD",
      "phase": "Research / Draft / Implementation / Review"
    }
  ]
}

Guidelines:
1. Ensure recommended due dates are chronologically ordered and strictly spaced prior to the final deadline ({due_date}).
2. Break large ambiguous deliverables into concrete steps.
"""

def parse_syllabus_document(file_storage, user_id: str, upload_root: str = 'uploads/syllabi') -> dict:
    """
    Extracts course details and assessment components from an uploaded syllabus PDF or image.
    Uses LLM (Gemini / OpenRouter) with robust fallback heuristics.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided for syllabus ingestion.")

    filename = file_storage.filename
    if not allowed_file(filename):
        raise ValueError("Unsupported file format. Please upload a PDF, TXT, or Image file.")

    ext = filename.rsplit('.', 1)[1].lower()
    safe_name = secure_filename(filename) or f"syllabus_{uuid.uuid4().hex[:6]}.{ext}"

    user_dir = os.path.join(upload_root, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    temp_path = os.path.join(user_dir, f"{uuid.uuid4().hex[:8]}_{safe_name}")

    try:
        file_storage.save(temp_path)
        file_size = os.path.getsize(temp_path)
        if file_size > MAX_FILE_SIZE:
            raise ValueError("File exceeds maximum allowed size of 15MB.")

        extracted_text = extract_text_from_file(temp_path, ext)
    finally:
        # Clean up temporary upload
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

    if not extracted_text or len(extracted_text.strip()) < 10:
        raise ValueError("Could not extract readable text from the syllabus document. Please ensure it is not an unsearchable scanned image.")

    # Call AI Service
    api_config = resolve_api_keys(user_id)
    provider = api_config.get("default_provider", "google")
    model = api_config.get("default_model", "gemini-2.0-flash")

    prompt = SYLLABUS_EXTRACTION_PROMPT + extracted_text[:12000]
    raw_ai_response = ""

    try:
        if provider == "google" and api_config.get("google_key"):
            raw_ai_response = query_google_gemini(api_config["google_key"], model, prompt)
        elif provider == "openrouter" and api_config.get("openrouter_key"):
            raw_ai_response = query_openrouter(api_config["openrouter_key"], model, prompt)
    except Exception as e:
        logger.warning(f"AI syllabus parsing API error: {e}. Falling back to heuristic parsing.")

    parsed_data = None
    if raw_ai_response:
        parsed_data = _clean_and_parse_json(raw_ai_response)

    # If AI parsing succeeded and extracted tasks
    if parsed_data and isinstance(parsed_data, dict) and parsed_data.get("tasks"):
        return {
            "status": "success",
            "source": "ai_model",
            "data": _normalize_syllabus_data(parsed_data)
        }

    # Fallback: Heuristic regex and structured syllabus extractor
    logger.info("Employing heuristic pattern extraction for syllabus.")
    fallback_data = _heuristic_syllabus_parser(extracted_text, filename)
    return {
        "status": "success",
        "source": "heuristic_fallback",
        "data": fallback_data
    }

def _clean_and_parse_json(text: str):
    """Strips markdown code fences and returns parsed JSON object."""
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        # Search for first { and last }
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return None

def _normalize_syllabus_data(data: dict) -> dict:
    """Sanitizes and normalizes extracted syllabus data."""
    course_name = str(data.get("course_name") or "New Course").strip()
    semester = str(data.get("semester") or "Semester 1").strip()
    
    try:
        credits = int(data.get("credits", 3))
    except (ValueError, TypeError):
        credits = 3

    try:
        target_grade = float(data.get("target_grade", 80.0))
    except (ValueError, TypeError):
        target_grade = 80.0

    raw_tasks = data.get("tasks") or []
    normalized_tasks = []
    total_w = 0.0

    for t in raw_tasks:
        tname = str(t.get("task_name") or t.get("name") or "Assessment").strip()
        try:
            w = float(t.get("weightage") or t.get("weight") or 0.0)
        except (ValueError, TypeError):
            w = 0.0
        
        due = str(t.get("due_date") or "").strip()
        if due:
            try:
                # Validate date format YYYY-MM-DD
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                due = ""

        total_w += w
        normalized_tasks.append({
            "task_name": tname,
            "weightage": round(w, 2),
            "due_date": due
        })

    # If tasks total weight is 0 or empty, populate standard baseline components
    if not normalized_tasks:
        normalized_tasks = [
            {"task_name": "Assignments & Problem Sets", "weightage": 20.0, "due_date": ""},
            {"task_name": "Midterm Examination", "weightage": 30.0, "due_date": ""},
            {"task_name": "Final Project / Examination", "weightage": 50.0, "due_date": ""}
        ]

    return {
        "course_name": course_name,
        "semester": semester,
        "credits": max(1, min(credits, 8)),
        "target_grade": max(40.0, min(target_grade, 100.0)),
        "tasks": normalized_tasks
    }

def _heuristic_syllabus_parser(text: str, filename: str) -> dict:
    """
    Deterministic rule-based pattern extractor for course syllabus documents.
    Extracts course code, title, credits, assignments, and percentages.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Extract Course Title / Code
    course_name = ""
    code_match = re.search(r'\b([A-Z]{2,4}\s?[0-9]{3,4}[A-Z]?)\b[:\s—\-]+([A-Za-z0-9\s,&]{4,60})', text)
    if code_match:
        course_name = f"{code_match.group(1).strip()} — {code_match.group(2).strip()}"
    else:
        # Fallback to first non-empty header line or filename
        for line in lines[:5]:
            if len(line) > 5 and len(line) < 60 and not line.startswith("---"):
                course_name = line
                break
        if not course_name:
            clean_base = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
            course_name = f"{clean_base} Course"

    # Extract Credits
    credits = 3
    cred_match = re.search(r'(\d+)\s*(?:credit|credits|unit|units|cr)\b', text, re.IGNORECASE)
    if cred_match:
        try:
            credits = int(cred_match.group(1))
        except (ValueError, TypeError):
            credits = 3

    # Extract Assessment Tasks
    tasks = []
    # Match patterns like: "Midterm Exam: 30%", "Assignment 1 (15%)", "Final Project - 40%"
    assessment_patterns = [
        r'(?:^|\n)[-•*]?\s*([A-Za-z0-9\s/]{3,40})\s*[:\-\(]\s*(\d{1,2}(?:\.\d)?)\s*%',
        r'\b(Assignment\s*\d*|Quiz\s*\d*|Lab\s*\d*|Midterm|Final Exam|Project|Milestone\s*\d*)[^0-9\n]{1,25}(\d{1,2})\s*%'
    ]

    seen_names = set()
    for pat in assessment_patterns:
        matches = re.finditer(pat, text, re.IGNORECASE)
        for m in matches:
            tname = m.group(1).strip()
            # Clean unwanted tokens
            tname = re.sub(r'^(and|or|the)\s+', '', tname, flags=re.IGNORECASE)
            try:
                weight = float(m.group(2))
            except ValueError:
                weight = 10.0

            if 1.0 <= weight <= 70.0 and tname.lower() not in seen_names:
                seen_names.add(tname.lower())
                tasks.append({
                    "task_name": tname.title(),
                    "weightage": weight,
                    "due_date": ""
                })

    if not tasks:
        tasks = [
            {"task_name": "Coursework Assignments", "weightage": 25.0, "due_date": ""},
            {"task_name": "Midterm Examination", "weightage": 30.0, "due_date": ""},
            {"task_name": "Final Assessment", "weightage": 45.0, "due_date": ""}
        ]

    return {
        "course_name": course_name,
        "semester": "Semester 1",
        "credits": max(1, min(credits, 6)),
        "target_grade": 80.0,
        "tasks": tasks
    }

def batch_import_syllabus(user_id: str, syllabus_data: dict) -> dict:
    """
    Atomically creates a Course and all associated Tasks in a single database transaction.
    """
    if not syllabus_data:
        raise ValueError("No syllabus data provided for batch import.")

    course_name = syllabus_data.get("course_name", "").strip()
    if not course_name:
        raise ValueError("Course title is required.")

    semester = syllabus_data.get("semester", "Semester 1").strip()
    credits = int(syllabus_data.get("credits", 3))
    target_grade = float(syllabus_data.get("target_grade", 80.0))
    raw_tasks = syllabus_data.get("tasks", [])

    try:
        with db.session.begin_nested():
            # 1. Create Course
            new_course = Course(
                user_id=user_id,
                course_name=course_name,
                semester=semester,
                credits=credits,
                target_grade=target_grade,
                is_completed=False
            )
            db.session.add(new_course)
            db.session.flush() # Flush to get new_course.id for foreign keys

            created_tasks = []
            for t in raw_tasks:
                tname = t.get("task_name", "").strip()
                if not tname:
                    continue

                w = float(t.get("weightage", 0.0))
                due_str = t.get("due_date", "").strip()
                due_val = None
                if due_str:
                    try:
                        due_val = datetime.strptime(due_str, "%Y-%m-%d").date()
                    except ValueError:
                        due_val = None

                new_task = Task(
                    course_id=new_course.id,
                    user_id=user_id,
                    task_name=tname,
                    weightage=w,
                    due_date=due_val,
                    category="Component" if w > 0 else "Academic Task",
                    is_completed=False
                )
                db.session.add(new_task)
                created_tasks.append(new_task)

        db.session.commit()
        return {
            "status": "success",
            "course": new_course.to_dict(),
            "tasks_count": len(created_tasks),
            "message": f"Successfully imported '{course_name}' with {len(created_tasks)} assessments!"
        }
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during batch syllabus import: {e}")
        raise ValueError(f"Failed to import syllabus components: {str(e)}")

def rebalance_missed_schedule(user_id: str) -> dict:
    """
    Self-Healing Schedule Optimizer:
    1. Identifies past uncompleted study sessions (activity_type == 'Revision' and end_time < now).
    2. Identifies pending high-priority tasks due in the next 14 days.
    3. Finds empty time windows without collisions with 'Class' slots and outside rest hours (08:00 - 22:00).
    4. Automatically shifts needed study hours forward.
    5. Returns an AI-powered conversational explanation of the rebalanced slots.
    """
    now = datetime.now()
    today = date.today()
    current_time_str = now.strftime('%H:%M')

    user = db.session.get(User, user_id)
    edu_level = getattr(user, 'education_level', 'university') if user else 'university'
    tier_cfg = get_tier_config(edu_level)
    chunk_minutes = tier_cfg.get('chunk_minutes', 45)

    # 1. Find missed revision sessions
    all_schedules = Schedule.query.filter_by(user_id=user_id).all()
    missed_sessions = []
    active_commitments = []

    for s in all_schedules:
        s_date = s.start_date or today
        is_past = (s_date < today) or (s_date == today and s.end_time < current_time_str)

        if s.activity_type == 'Revision' and is_past:
            missed_sessions.append(s)
        else:
            active_commitments.append(s)

    # 2. Find pending tasks due in the next 14 days
    future_horizon = today + timedelta(days=14)
    tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.is_completed == False,
        Task.due_date >= today,
        Task.due_date <= future_horizon
    ).order_by(Task.due_date.asc()).all()

    if not tasks and not missed_sessions:
        return {
            "status": "up_to_date",
            "rebalanced_count": 0,
            "message": "Your timetable is perfectly on track! No overdue revision blocks or upcoming deadline crunches detected."
        }

    # 3. Conflict detection helper
    def has_time_conflict(target_date, cand_start, cand_end):
        target_day = target_date.strftime('%A')
        for act in active_commitments:
            # Recurring class on matching day of week, or specific dated event on target_date
            is_matching_day = (act.activity_type == 'Class' and act.day_of_week.lower() == target_day.lower())
            is_matching_date = (act.start_date == target_date)
            
            if is_matching_day or is_matching_date:
                if max(act.start_time, cand_start) < min(act.end_time, cand_end):
                    return True
        return False

    # Candidate slot pool: Allowed hours 08:00 to 22:00
    candidate_hours = [
        ("09:00", "09:45"), ("10:00", "10:45"), ("11:00", "11:45"),
        ("14:00", "14:45"), ("15:00", "15:45"), ("16:00", "16:45"),
        ("17:00", "17:45"), ("19:00", "19:45"), ("20:00", "20:45"),
        ("21:00", "21:45")
    ]

    reallocated_sessions = []
    sessions_to_shift = len(missed_sessions) if missed_sessions else min(3, len(tasks))
    sessions_to_shift = max(1, min(sessions_to_shift, 6))

    # Priority task queue
    task_queue = tasks if tasks else [Task(task_name="General Review", due_date=today + timedelta(days=7))]

    # Shift forward across the next 7 days
    day_offset = 1 # Start tomorrow to give student immediate breathing room
    allocated_count = 0

    while day_offset <= 10 and allocated_count < sessions_to_shift:
        cand_date = today + timedelta(days=day_offset)
        assigned_task = task_queue[allocated_count % len(task_queue)]

        # Cannot schedule revision after task due date
        if assigned_task.due_date and cand_date >= assigned_task.due_date:
            day_offset += 1
            continue

        for cand_start, cand_end in candidate_hours:
            if not has_time_conflict(cand_date, cand_start, cand_end):
                # Valid conflict-free slot found
                new_title = f"Revision: {assigned_task.task_name}"
                course_label = assigned_task.course.course_name if assigned_task.course else "General Study"
                
                new_sched = Schedule(
                    user_id=user_id,
                    title=new_title,
                    activity_type="Revision",
                    day_of_week=cand_date.strftime('%A'),
                    start_time=cand_start,
                    end_time=cand_end,
                    venue="Study Space / Library",
                    details=f"Self-Healed: Re-allocated from past missed revision slot ({course_label}).",
                    start_date=cand_date,
                    end_date=cand_date
                )
                db.session.add(new_sched)
                active_commitments.append(new_sched)

                reallocated_sessions.append({
                    "task_name": assigned_task.task_name,
                    "date": cand_date.isoformat(),
                    "day": cand_date.strftime('%A'),
                    "time": f"{cand_start} – {cand_end}"
                })
                allocated_count += 1
                break

        day_offset += 1

    # Remove past missed revision sessions to clean up schedule
    for old_s in missed_sessions:
        db.session.delete(old_s)

    db.session.commit()

    # Generate conversational AI summary
    if reallocated_sessions:
        details_list = [f"{s['task_name']} to {s['day']} ({s['date']}) at {s['time']}" for s in reallocated_sessions[:3]]
        summary_msg = f"Self-Healing Optimizer rebalanced {len(reallocated_sessions)} study sessions! Shifted: {'; '.join(details_list)} without class collisions."
    else:
        summary_msg = "Timetable scanned. No additional slots required."

    return {
        "status": "success",
        "rebalanced_count": len(reallocated_sessions),
        "cleaned_missed_count": len(missed_sessions),
        "reallocated_sessions": reallocated_sessions,
        "message": summary_msg
    }

def decompose_task_with_ai(user_id: str, task_title: str, due_date: str = None, course_name: str = None) -> dict:
    """
    Smart Task Decomposer:
    Breaks down a major academic task or project into 3 to 5 milestone sub-tasks with estimated hours
    and recommended interim deadlines spaced evenly prior to the final due date.
    """
    if not task_title or not task_title.strip():
        raise ValueError("Task title is required for decomposition.")

    task_title = task_title.strip()
    course_name = course_name or "Academic Subject"
    due_date_str = due_date or (date.today() + timedelta(days=14)).isoformat()

    api_config = resolve_api_keys(user_id)
    provider = api_config.get("default_provider", "google")
    model = api_config.get("default_model", "gemini-2.0-flash")

    prompt = (
        TASK_DECOMPOSITION_PROMPT
        .replace("{task_title}", task_title)
        .replace("{course_name}", course_name)
        .replace("{due_date}", due_date_str)
    )

    raw_ai_response = ""
    try:
        if provider == "google" and api_config.get("google_key"):
            raw_ai_response = query_google_gemini(api_config["google_key"], model, prompt)
        elif provider == "openrouter" and api_config.get("openrouter_key"):
            raw_ai_response = query_openrouter(api_config["openrouter_key"], model, prompt)
    except Exception as e:
        logger.warning(f"AI task decomposition call failed: {e}. Using intelligent fallback decomposition.")

    parsed = _clean_and_parse_json(raw_ai_response)
    if parsed and isinstance(parsed, dict) and parsed.get("subtasks"):
        subtasks = parsed["subtasks"]
        # Normalize items
        normalized = []
        for s in subtasks:
            normalized.append({
                "title": s.get("title", "Sub-task milestone"),
                "estimated_hours": float(s.get("estimated_hours", 2.0)),
                "recommended_due_date": s.get("recommended_due_date", due_date_str),
                "phase": s.get("phase", "Implementation")
            })
        return {
            "status": "success",
            "source": "ai_model",
            "parent_task": task_title,
            "final_due_date": due_date_str,
            "subtasks": normalized
        }

    # Deterministic fallback milestone generator
    logger.info("Generating fallback project decomposition milestones.")
    fallback_subtasks = _fallback_task_milestones(task_title, due_date_str)
    return {
        "status": "success",
        "source": "heuristic_fallback",
        "parent_task": task_title,
        "final_due_date": due_date_str,
        "subtasks": fallback_subtasks
    }

def _fallback_task_milestones(task_title: str, final_due_date_str: str) -> list:
    """Computes chronologically-spaced milestones backward from the deadline."""
    try:
        deadline = datetime.strptime(final_due_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        deadline = date.today() + timedelta(days=14)

    today = date.today()
    total_days = max(4, (deadline - today).days)

    d1 = today + timedelta(days=max(1, int(total_days * 0.25)))
    d2 = today + timedelta(days=max(2, int(total_days * 0.55)))
    d3 = today + timedelta(days=max(3, int(total_days * 0.85)))
    d4 = deadline

    return [
        {
            "title": f"Phase 1: Research, Outline & Architecture ({task_title[:25]})",
            "estimated_hours": 2.5,
            "recommended_due_date": d1.isoformat(),
            "phase": "Research"
        },
        {
            "title": f"Phase 2: Core Drafting & Primary Implementation",
            "estimated_hours": 5.0,
            "recommended_due_date": d2.isoformat(),
            "phase": "Implementation"
        },
        {
            "title": f"Phase 3: Verification, Testing & Peer Review",
            "estimated_hours": 3.0,
            "recommended_due_date": d3.isoformat(),
            "phase": "Review"
        },
        {
            "title": f"Phase 4: Final Polishing, Formatting & Submission",
            "estimated_hours": 1.5,
            "recommended_due_date": d4.isoformat(),
            "phase": "Submission"
        }
    ]

def commit_subtasks_to_board(user_id: str, parent_task_id: str, subtasks: list) -> dict:
    """
    Persists selected subtasks into the Task manager under the same course or user scope.
    """
    if not subtasks:
        raise ValueError("No sub-tasks selected to commit.")

    parent_task = None
    course_id = None
    if parent_task_id:
        parent_task = db.session.get(Task, parent_task_id)
        if parent_task:
            course_id = parent_task.course_id

    created_tasks = []
    try:
        with db.session.begin_nested():
            for s in subtasks:
                title = s.get("title", "").strip()
                if not title:
                    continue

                due_str = s.get("recommended_due_date", "")
                due_val = None
                if due_str:
                    try:
                        due_val = datetime.strptime(due_str, "%Y-%m-%d").date()
                    except ValueError:
                        due_val = None

                new_sub = Task(
                    user_id=user_id,
                    course_id=course_id,
                    task_name=title,
                    due_date=due_val,
                    weightage=0.0,
                    category="Academic Task",
                    is_completed=False
                )
                db.session.add(new_sub)
                created_tasks.append(new_sub)

        db.session.commit()
        return {
            "status": "success",
            "created_count": len(created_tasks),
            "message": f"Successfully created {len(created_tasks)} sub-task milestones!"
        }
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Failed to commit subtasks: {str(e)}")

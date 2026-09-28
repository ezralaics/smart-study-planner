from datetime import date, timedelta
from extensions import db
from models.course import Course
from models.task import Task
from models.schedule import Schedule
from models.user import User
from services.tier_service import get_tier_config

def generate_study_schedule(user_id, daily_hours=2, preferred_window='evening', horizon_days=14, education_level=None):
    """
    Intelligent heuristic constraint satisfaction scheduler with Adaptive Multi-Tier heuristics:
    1. Adjusts session chunk durations based on education_level (Primary: 15m, Secondary: 30m, University/General: 45m).
    2. Scores tasks based on deadline urgency, component weightage, and target grade.
    3. Gathers busy time intervals from student's existing Schedule.
    4. Allocates revision sessions backward from deadlines into non-conflicting time slots.
    """
    today = date.today()
    daily_hours = max(1, min(int(daily_hours), 4))

    # Determine education level
    if not education_level:
        user = db.session.get(User, user_id)
        education_level = getattr(user, 'education_level', 'university') if user else 'university'
    education_level = (education_level or 'university').lower()

    tier_config = get_tier_config(education_level)
    chunk_minutes = tier_config.get('chunk_minutes', 45)
    break_minutes = tier_config.get('break_minutes', 15)

    # 1. Fetch user's courses and build lookup map
    courses = Course.query.filter_by(user_id=user_id).all()
    course_map = {c.id: c for c in courses}
    course_ids = [c.id for c in courses]

    # 2. Fetch all incomplete tasks with upcoming due dates
    tasks = Task.query.filter(
        ((Task.user_id == user_id) | (Task.course_id.in_(course_ids))),
        Task.is_completed == False,
        Task.due_date != None
    ).all()

    valid_tasks = []
    for t in tasks:
        if t.due_date and t.due_date >= today:
            valid_tasks.append(t)

    if not valid_tasks:
        return {
            "status": "empty",
            "education_level": education_level,
            "chunk_minutes": chunk_minutes,
            "message": "No upcoming tasks found. Add tasks with due dates in the Study Planner to generate a schedule.",
            "sessions": []
        }

    # 3. Calculate priority scores for each task
    scored_tasks = []
    for t in valid_tasks:
        course = course_map.get(t.course_id)
        c_name = course.course_name.split('—')[0].strip() if course else "General"
        target_grade = float(course.target_grade) if course and course.target_grade else 80.0
        weight = float(t.weightage) if t.weightage and t.weightage > 0 else 15.0

        days_remaining = (t.due_date - today).days

        # Algorithmic priority score:
        # High weightage + close deadline + ambitious target grade = top priority
        urgency_factor = 1.0 / max(1, days_remaining)
        weight_factor = weight / 100.0
        target_factor = target_grade / 100.0

        # Score on a scale from 0 to 100
        score = round(((urgency_factor * 0.5) + (weight_factor * 0.3) + (target_factor * 0.2)) * 100, 1)

        urgency_label = "Critical" if days_remaining <= 2 else ("High" if days_remaining <= 5 else ("Medium" if days_remaining <= 10 else "Normal"))

        scored_tasks.append({
            "task": t,
            "course_name": c_name,
            "weight": weight,
            "days_remaining": days_remaining,
            "priority_score": score,
            "urgency_label": urgency_label,
            "needed_sessions": min(6, max(1, int(round(weight / 15.0)))) # Heuristic: heavier tasks get more sessions
        })

    # Sort tasks by priority score descending
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)

    # 4. Fetch existing schedule commitments to prevent collisions
    schedules = Schedule.query.filter_by(user_id=user_id).all()

    def has_time_conflict(day_name, cand_start, cand_end):
        """Checks if a proposed revision slot overlaps with any existing schedule for that day."""
        for s in schedules:
            if s.day_of_week.lower() == day_name.lower():
                # Interval overlap: max(start1, start2) < min(end1, end2)
                if max(s.start_time, cand_start) < min(s.end_time, cand_end):
                    return True
        return False

    # 5. Dynamically generate candidate time slots based on chunk_minutes and break_minutes
    window_boundaries = {
        'morning': (8 * 60, 12 * 60),      # 08:00 – 12:00
        'afternoon': (13 * 60, 17 * 60),  # 13:00 – 17:00
        'evening': (18 * 60, 22 * 60)     # 18:00 – 22:00
    }
    w_start, w_end = window_boundaries.get(preferred_window.lower(), window_boundaries['evening'])
    
    slots_pool = []
    curr_time = w_start
    step = chunk_minutes + break_minutes
    while curr_time + chunk_minutes <= w_end:
        start_str = f"{curr_time // 60:02d}:{curr_time % 60:02d}"
        end_val = curr_time + chunk_minutes
        end_str = f"{end_val // 60:02d}:{end_val % 60:02d}"
        slots_pool.append((start_str, end_str))
        curr_time += step

    if not slots_pool:
        slots_pool = [("19:00", f"19:{chunk_minutes:02d}")]

    # 6. Allocate slots across the lookahead horizon
    daily_budget_minutes = daily_hours * 60
    proposed_sessions = []
    daily_allocated_minutes = {} # date_key -> minutes allocated

    for item in scored_tasks:
        task = item['task']
        due_date = task.due_date
        sessions_needed = item['needed_sessions']
        sessions_assigned = 0

        # Try to schedule days prior to due date (backward distribution)
        current_day_offset = 0
        while current_day_offset < horizon_days and sessions_assigned < sessions_needed:
            session_date = today + timedelta(days=current_day_offset)
            
            # Cannot schedule on or after due date
            if session_date >= due_date:
                break

            day_name = session_date.strftime('%A')
            date_key = str(session_date)

            if daily_allocated_minutes.get(date_key, 0) + chunk_minutes <= daily_budget_minutes:
                # Find an open slot without timetable collision
                for slot in slots_pool:
                    cand_start, cand_end = slot
                    
                    # Check existing class collision AND already booked revision session collision
                    already_booked = any(
                        s['date'] == date_key and max(s['start_time'], cand_start) < min(s['end_time'], cand_end)
                        for s in proposed_sessions
                    )
                    
                    if not already_booked and not has_time_conflict(day_name, cand_start, cand_end):
                        proposed_sessions.append({
                            "task_id": task.id,
                            "task_name": task.task_name,
                            "course_name": item['course_name'],
                            "date": date_key,
                            "day_of_week": day_name,
                            "start_time": cand_start,
                            "end_time": cand_end,
                            "duration_minutes": chunk_minutes,
                            "duration_hours": round(chunk_minutes / 60.0, 2),
                            "break_minutes": break_minutes,
                            "priority_score": item['priority_score'],
                            "urgency": item['urgency_label'],
                            "reason": f"{item['weight']}% weight · {item['days_remaining']}d left · {chunk_minutes}m focus chunk"
                        })
                        daily_allocated_minutes[date_key] = daily_allocated_minutes.get(date_key, 0) + chunk_minutes
                        sessions_assigned += 1
                        break

            current_day_offset += 1

    # Sort final schedule chronologically
    proposed_sessions.sort(key=lambda x: (x['date'], x['start_time']))

    total_study_minutes = sum(s['duration_minutes'] for s in proposed_sessions)
    return {
        "status": "success",
        "education_level": education_level,
        "tasks_considered": len(scored_tasks),
        "total_sessions": len(proposed_sessions),
        "total_study_hours": round(total_study_minutes / 60.0, 2),
        "total_study_minutes": total_study_minutes,
        "chunk_minutes": chunk_minutes,
        "break_minutes": break_minutes,
        "daily_hours_budget": daily_hours,
        "preferred_window": preferred_window.capitalize(),
        "sessions": proposed_sessions
    }


def apply_study_schedule(user_id, sessions):
    """
    Commits approved revision sessions into the user's Schedule table
    with activity_type='Revision'.
    """
    created_count = 0
    for s in sessions:
        sched_date = date.fromisoformat(s['date']) if isinstance(s['date'], str) else s['date']
        
        # Check if already exists to avoid duplicates
        existing = Schedule.query.filter_by(
            user_id=user_id,
            title=f"Revision: {s['task_name']}",
            start_date=sched_date,
            start_time=s['start_time']
        ).first()

        if not existing:
            new_sched = Schedule(
                user_id=user_id,
                title=f"Revision: {s['task_name']}",
                activity_type="Revision",
                day_of_week=s['day_of_week'],
                start_time=s['start_time'],
                end_time=s['end_time'],
                venue="Study Space / Library",
                details=f"Target: {s['course_name']} ({s.get('reason', '')})",
                start_date=sched_date,
                end_date=sched_date
            )
            db.session.add(new_sched)
            created_count += 1

    db.session.commit()
    return created_count

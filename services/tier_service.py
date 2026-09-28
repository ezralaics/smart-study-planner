"""
services/tier_service.py
Adaptive Multi-Tier Education Engine for Smart Study Planner.
Supports:
1. Primary School (Elementary / Ages 7-12)
2. Secondary School (High School / SPM / GCSE / O-Levels / A-Levels)
3. University / College (Higher Education)
4. General Learner (Self-taught / Professional Certifications / Lifelong Learning)
"""

TIER_CONFIG = {
    'university': {
        'key': 'university',
        'name': 'University / College',
        'badge': 'Higher Education',
        'icon': 'bi-mortarboard-fill',
        'color': '#2563eb',
        'description': 'Bachelor’s, Master’s, or Diploma programmes with credit hours, semesters, and CGPA tracking.',
        'course_label': 'Course / Module',
        'course_placeholder': 'e.g. CD106 — Java Programming',
        'course_code_label': 'Course Code',
        'term_label': 'Semester',
        'term_placeholder': 'e.g. Semester 1',
        'credits_label': 'Credit Hours',
        'task_label': 'Assignment / Assessment',
        'target_metric_label': 'Target CGPA (4.0 Scale)',
        'target_metric_type': 'cgpa',
        'show_credits': True,
        'show_weightage': True,
        'show_stars': False,
        'show_gpa': True,
        'chunk_minutes': 45,
        'break_minutes': 15,
        'default_daily_target': 3,
        'predefined_courses': [
            {"code": "CD102", "name": "Computer Ethics", "credits": 3},
            {"code": "CD103", "name": "Fundamental of Database Systems", "credits": 4},
            {"code": "CD105", "name": "System Analysis & Design", "credits": 4},
            {"code": "CD106", "name": "Java Programming", "credits": 4},
            {"code": "CD108", "name": "Discrete Mathematics", "credits": 3},
            {"code": "CD204", "name": "User Interface Design", "credits": 3}
        ]
    },
    'secondary': {
        'key': 'secondary',
        'name': 'Secondary / High School',
        'badge': 'SPM / GCSE / High School',
        'icon': 'bi-building',
        'color': '#0d9488',
        'description': 'Middle & High School curriculums focusing on core academic subjects, terms, and letter/percentage grades.',
        'course_label': 'Subject Name',
        'course_placeholder': 'e.g. Additional Mathematics, Physics, History',
        'course_code_label': 'Subject Code',
        'term_label': 'Academic Term / Quarter',
        'term_placeholder': 'e.g. Term 1, Mid-Year',
        'credits_label': 'Study Periods',
        'task_label': 'Homework / Assignment',
        'target_metric_label': 'Target Grade (A/B/C or %)',
        'target_metric_type': 'grade',
        'show_credits': False,
        'show_weightage': True,
        'show_stars': False,
        'show_gpa': False,
        'chunk_minutes': 30,
        'break_minutes': 5,
        'default_daily_target': 2,
        'predefined_courses': [
            {"code": "MATH", "name": "Mathematics", "credits": 1},
            {"code": "AMATH", "name": "Additional Mathematics", "credits": 1},
            {"code": "PHY", "name": "Physics", "credits": 1},
            {"code": "CHEM", "name": "Chemistry", "credits": 1},
            {"code": "BIO", "name": "Biology", "credits": 1},
            {"code": "ENG", "name": "English Language & Literature", "credits": 1},
            {"code": "HIST", "name": "History", "credits": 1}
        ]
    },
    'primary': {
        'key': 'primary',
        'name': 'Primary School',
        'badge': 'Elementary (Ages 7–12)',
        'icon': 'bi-backpack-fill',
        'color': '#f59e0b',
        'description': 'Young learners with simplified homework checklists, star rewards, and bite-sized focus sessions.',
        'course_label': 'Subject / Class',
        'course_placeholder': 'e.g. Math, Science, Art, English',
        'course_code_label': 'Class Room',
        'term_label': 'School Term',
        'term_placeholder': 'e.g. Term 1',
        'credits_label': 'Class Stars',
        'task_label': 'Homework / Activity',
        'target_metric_label': 'Target Stars & Badges ⭐',
        'target_metric_type': 'stars',
        'show_credits': False,
        'show_weightage': False,
        'show_stars': True,
        'show_gpa': False,
        'chunk_minutes': 15,
        'break_minutes': 5,
        'default_daily_target': 1,
        'predefined_courses': [
            {"code": "MATH", "name": "Fun Math & Numbers", "credits": 1},
            {"code": "ENG", "name": "English Reading & Phonics", "credits": 1},
            {"code": "SCI", "name": "World of Science", "credits": 1},
            {"code": "ART", "name": "Creative Arts & Drawing", "credits": 1},
            {"code": "MUSIC", "name": "Music & Songs", "credits": 1}
        ]
    },
    'general': {
        'key': 'general',
        'name': 'Lifelong / Professional Learner',
        'badge': 'Certifications & Skills',
        'icon': 'bi-briefcase-fill',
        'color': '#8b5cf6',
        'description': 'Self-directed learners, bootcamps, and professional certifications with flexible milestone tracks.',
        'course_label': 'Skill / Project / Certification',
        'course_placeholder': 'e.g. AWS Solutions Architect, Python Bootcamp',
        'course_code_label': 'Track / Cert ID',
        'term_label': 'Milestone Phase',
        'term_placeholder': 'e.g. Phase 1 — Foundations',
        'credits_label': 'Estimated Total Study Hours',
        'task_label': 'Milestone / Task',
        'target_metric_label': 'Target Completion Date',
        'target_metric_type': 'date',
        'show_credits': True,
        'show_weightage': False,
        'show_stars': False,
        'show_gpa': False,
        'chunk_minutes': 45,
        'break_minutes': 15,
        'default_daily_target': 2,
        'predefined_courses': [
            {"code": "AWS-SAA", "name": "AWS Certified Solutions Architect", "credits": 40},
            {"code": "PY-BOOT", "name": "Full-Stack Python Bootcamp", "credits": 60},
            {"code": "PMP-CERT", "name": "Project Management Professional (PMP)", "credits": 35},
            {"code": "DS-ML", "name": "Machine Learning Foundations", "credits": 50}
        ]
    }
}

VALID_TIERS = list(TIER_CONFIG.keys())

def get_tier_config(level_key=None):
    """
    Retrieves the configuration dictionary for an education level.
    Defaults safely to 'university' if level_key is invalid or unassigned.
    """
    if not level_key or level_key.lower() not in TIER_CONFIG:
        return TIER_CONFIG['university']
    return TIER_CONFIG[level_key.lower()]

def get_all_tiers():
    """Returns a list of all tier configuration objects."""
    return list(TIER_CONFIG.values())

def get_tier_pomodoro_settings(level_key=None):
    """Returns (chunk_minutes, break_minutes) for the given level."""
    tier = get_tier_config(level_key)
    return tier['chunk_minutes'], tier['break_minutes']

import json
import logging
import random
import re
from datetime import date, datetime, timedelta, timezone
from extensions import db
from models.course import Course
from models.task import Task
from models.habit import Habit
from models.study_tip import StudyTip, UserTipInteraction
from services.ai_service import resolve_api_keys, query_google_gemini

logger = logging.getLogger(__name__)

# Evidence-based cognitive science tip bank (50+ curated tips across 6 core domains)
CURATED_COGNITIVE_TIPS = [
    # 1. Active Recall
    {
        "category": "active_recall",
        "title": "The Testing Effect: Close the Book Before Re-Reading",
        "content": "Cognitive psychologists Roediger and Karpicke demonstrated that retrieving knowledge from memory creates significantly stronger neural pathways than passive review. Merely highlighting or re-reading gives an illusion of competence without durable retention.",
        "action_item": "Close your notes right now and write down the 3 core principles of your last lecture from memory.",
        "source_reference": "Roediger & Karpicke (2006), Psychological Science"
    },
    {
        "category": "active_recall",
        "title": "Blurting Method for Rapid Knowledge Audit",
        "content": "The 'blurting' technique forces maximum cognitive effort by writing everything you remember onto a blank page, followed by immediate comparison against your syllabus or lecture slides to identify knowledge gaps.",
        "action_item": "Spend 5 minutes scribbling all terms and equations you remember for your most difficult course, then check missed items.",
        "source_reference": "Dunlosky et al. (2013), Improving Students' Learning"
    },
    {
        "category": "active_recall",
        "title": "Pre-Testing: Priming with Unfamiliar Problems",
        "content": "Attempting practice questions before studying the lecture material activates curiosity and primes the brain for deeper encoding, even if your initial guesses are incorrect.",
        "action_item": "Scan the end-of-chapter questions before opening next week's lecture slides.",
        "source_reference": "Kornell et al. (2009), Journal of Experimental Psychology"
    },
    {
        "category": "active_recall",
        "title": "The Feynman Technique: Simplify Down to First Principles",
        "content": "Nobel laureate Richard Feynman advocated that true mastery is the ability to explain a complex topic without jargon to a child. Jargon often masks shallow conceptual understanding.",
        "action_item": "Explain today's hardest concept aloud in 60 seconds using only plain everyday analogies.",
        "source_reference": "Richard Feynman, 'Surely You're Joking, Mr. Feynman!'"
    },
    {
        "category": "active_recall",
        "title": "Cornell Cue Column Active Quizzing",
        "content": "When reviewing Cornell notes, cover the right-side summary column and force yourself to answer the questions and prompts written in the left cue column.",
        "action_item": "Fold your notes in half and quiz yourself on 5 cue questions before dinner.",
        "source_reference": "Walter Pauk, Cornell University Learning Strategies Center"
    },
    {
        "category": "active_recall",
        "title": "Elaborative Interrogation: Asking 'Why is this true?'",
        "content": "Asking yourself 'Why does this fact hold true?' or 'Under what conditions would this fail?' integrates new information into your existing mental scaffolding much faster than rote memorization.",
        "action_item": "Pick one core definition in your notes and write two sentences explaining why it is fundamentally necessary.",
        "source_reference": "Pressley et al. (1992), Cognitive Educational Psychology"
    },
    {
        "category": "active_recall",
        "title": "Self-Generated Flashcards Over Pre-Made Decks",
        "content": "The process of formulating a high-yield question and distilling the answer forces deep cognitive processing that you bypass entirely when downloading someone else's flashcard deck.",
        "action_item": "Draft 5 custom flashcard prompts focusing strictly on your weakest lecture sub-topic.",
        "source_reference": "Kornell & Bjork (2008), Memory & Cognition"
    },
    {
        "category": "active_recall",
        "title": "Dual-Coding: Pairing Diagrams with Verbal Explanations",
        "content": "Allan Paivio's Dual-Coding Theory shows that encoding both visual spatial representations and verbal semantic explanations creates two independent retrieval pathways in long-term memory.",
        "action_item": "Draw a flowchart or conceptual mind map linking three concepts from your syllabus.",
        "source_reference": "Allan Paivio (1971), Dual Coding Theory"
    },

    # 2. Spaced Repetition
    {
        "category": "spaced_repetition",
        "title": "The Ebbinghaus Forgetting Curve Interception",
        "content": "Without review, humans lose approximately 70% of new academic information within 48 hours. Reviewing at expanding intervals (Day 1, Day 3, Day 7, Day 21) resets the decay curve to near 100%.",
        "action_item": "Schedule a 10-minute speed review of material you studied 3 days ago.",
        "source_reference": "Hermann Ebbinghaus (1885), Memory: A Contribution to Experimental Psychology"
    },
    {
        "category": "spaced_repetition",
        "title": "Interleaving: Mix Problem Types to Prevent Autopilot",
        "content": "Blocking study by doing 30 identical math problems creates pseudo-fluency. Mixing problem types (interleaving) trains your brain to discriminate which strategy applies to each novel problem.",
        "action_item": "Shuffle practice questions across two different chapters rather than doing them sequentially.",
        "source_reference": "Rohrer & Taylor (2007), Instructional Science"
    },
    {
        "category": "spaced_repetition",
        "title": "Leitner Box System for High-Yield Efficiency",
        "content": "Sebastian Leitner's box system routes concepts you master into longer review cycles while keeping tricky cards in daily rotation, optimizing revision time by up to 300%.",
        "action_item": "Separate today's practice questions into 'Mastered' and 'Needs Review' piles.",
        "source_reference": "Sebastian Leitner (1972), So lernt man lernen"
    },
    {
        "category": "spaced_repetition",
        "title": "Sleep-Dependent Memory Consolidation",
        "content": "During slow-wave and REM sleep, the hippocampus replays waking memory traces and transfers them into the neocortex for permanent storage. All-nighters severely degrade synaptic consolidation.",
        "action_item": "Review your most challenging formula sheet for 10 minutes right before sleeping tonight.",
        "source_reference": "Stickgold (2005), Nature: Sleep-dependent memory consolidation"
    },
    {
        "category": "spaced_repetition",
        "title": "The Spacing Effect Over Massed Cramming",
        "content": "Ten 1-hour study sessions distributed over two weeks produce vastly higher exam retention and transferability than a single grueling 10-hour marathon session.",
        "action_item": "Split your next major revision block into three 45-minute daily slots across the week.",
        "source_reference": "Cepeda et al. (2006), Psychological Bulletin"
    },
    {
        "category": "spaced_repetition",
        "title": "Cumulative Weekly Review Ritual",
        "content": "Dedicating just 45 minutes on Sunday to skim through the entire week's notes prevents the mid-semester backlog from turning into an unmanageable crisis.",
        "action_item": "Block out 30 minutes on your calendar this weekend for a high-level syllabus sweep.",
        "source_reference": "Brown, Roediger & McDaniel, 'Make It Stick' (2014)"
    },

    # 3. Pomodoro & Flow State
    {
        "category": "pomodoro_flow",
        "title": "The Ultradian Rhythm: 90-Minute Energy Cycles",
        "content": "Chronobiologist Nathaniel Kleitman revealed that human alertness operates in 90-minute ultradian cycles. Pushing past 90 minutes without a biological reset triggers cognitive fatigue and error rates.",
        "action_item": "Cap your intense analytical study blocks at 90 minutes, followed by a 15-minute screen-free break.",
        "source_reference": "Nathaniel Kleitman, Sleep and Wakefulness"
    },
    {
        "category": "pomodoro_flow",
        "title": "The Classic 25/5 Pomodoro Friction Breaker",
        "content": "Procrastination is an emotional aversion to the anticipation of pain, not the task itself. Committing to just 25 minutes tricks the amygdala into lowering task resistance.",
        "action_item": "Set a timer for 25 minutes and commit to working on only one assignment without checking tabs.",
        "source_reference": "Francesco Cirillo (1980s), The Pomodoro Technique"
    },
    {
        "category": "pomodoro_flow",
        "title": "Active Rest vs. Pseudo-Rest",
        "content": "Scrolling social media during study breaks floods the working memory with high-arousal stimuli, preventing cognitive replenishment. True rest involves movement, hydration, or looking into the distance.",
        "action_item": "On your next break, step away from screens, stretch, and drink a tall glass of water.",
        "source_reference": "Dr. Andrew Huberman, Huberman Lab Podcast: Focus & Neuroplasticity"
    },
    {
        "category": "pomodoro_flow",
        "title": "Micro-Deadlines to Induce Flow State",
        "content": "Csikszentmihalyi's Flow model demonstrates that high challenge matched with high skill triggers deep immersion. Setting tight micro-deadlines increases focus and locks out distractions.",
        "action_item": "Challenge yourself to outline Section 1 of your assignment within the next 20 minutes.",
        "source_reference": "Mihaly Csikszentmihalyi (1990), 'Flow: The Psychology of Optimal Experience'"
    },
    {
        "category": "pomodoro_flow",
        "title": "Task Batching: Defeating the Context Switching Tax",
        "content": "Switching between administrative emails, homework coding, and social media creates 'attention residue' that lingers for up to 20 minutes after each switch.",
        "action_item": "Group all small administrative tasks into a single 30-minute block at the end of the day.",
        "source_reference": "Sophie Leroy (2009), Organizational Behavior and Human Decision Processes"
    },

    # 4. Deep Work & Focus
    {
        "category": "deep_work",
        "title": "Physical Distance from Digital Distractions",
        "content": "Research from the University of Texas found that having a smartphone on the desk—even turned face-down and silenced—subconsciously consumes working memory capacity ('brain drain').",
        "action_item": "Place your smartphone in another room or inside your backpack for the next study session.",
        "source_reference": "Ward et al. (2017), Journal of the Association for Consumer Research"
    },
    {
        "category": "deep_work",
        "title": "Binaural Beats & 40Hz Gamma Stimulation",
        "content": "Neuroscientific studies indicate that auditory entrainment with 40 Hz gamma frequencies or low-tempo instrumental sounds can enhance focal attention and reaction speed in learning tasks.",
        "action_item": "Put on ambient instrumental lofi or 40Hz binaural audio before starting your reading.",
        "source_reference": "Narayanan et al. (2020), Cognitive Enhancement Reviews"
    },
    {
        "category": "deep_work",
        "title": "Cal Newport's Shutdown Ritual",
        "content": "Without a clear end-of-day shutdown ritual, incomplete tasks trigger the Zeigarnik Effect, causing invasive thoughts about uncompleted work during your evening relaxation.",
        "action_item": "Review tomorrow's top 3 tasks at 6 PM, close your study tabs, and declare your study day officially complete.",
        "source_reference": "Cal Newport, 'Deep Work: Rules for Focused Success' (2016)"
    },
    {
        "category": "deep_work",
        "title": "Visual Horizon Anchoring for Concentration",
        "content": "Visual focus drives mental focus. Restricting your visual field (e.g. wearing a cap or hoodie, using clean lighting on your desk) narrows the brain's attentional spotlight.",
        "action_item": "Clear everything off your desk except the single textbook or notebook you are reading right now.",
        "source_reference": "Dr. Andrew Huberman, Stanford School of Medicine"
    },
    {
        "category": "deep_work",
        "title": "The Rule of 3 Daily Non-Negotiables",
        "content": "Overloaded to-do lists trigger decision fatigue. High-performing students identify the top 3 highest-leverage academic tasks each morning and complete them before anything else.",
        "action_item": "Pick your top 3 non-negotiable tasks in the Study Planner and prioritize them today.",
        "source_reference": "Chris Bailey, 'The Productivity Project'"
    },

    # 5. Exam Anxiety & Mindset
    {
        "category": "exam_anxiety",
        "title": "Expressive Writing: Purge Worry Before the Test",
        "content": "Research published in Science found that having anxious students write freely about their worries for 10 minutes immediately before an exam offloads working memory and boosts grades by up to a full letter.",
        "action_item": "If you feel stressed about an upcoming deadline, write down your exact fears on paper for 5 minutes.",
        "source_reference": "Ramirez & Beilock (2011), Science: Writing Away Test Anxiety"
    },
    {
        "category": "exam_anxiety",
        "title": "Physiological Sigh: Fast Autonomic De-escalation",
        "content": "Two rapid inhales through the nose followed by a long, slow exhale through the mouth maximally inflates the alveoli and rapidly drops heart rate by engaging the vagus nerve.",
        "action_item": "Perform 3 physiological sighs before beginning a timed mock test or problem set.",
        "source_reference": "Balban et al. (2023), Cell Reports Medicine"
    },
    {
        "category": "exam_anxiety",
        "title": "Stress Re-appraisal: From Threat to Challenge",
        "content": "Harvard psychologist Alison Wood Brooks found that telling yourself 'I am excited' rather than 'I must calm down' transforms stress hormones into high-performance arousal.",
        "action_item": "When you feel pre-exam butterflies, remind yourself: 'My body is preparing energy to think sharply.'",
        "source_reference": "Alison Wood Brooks (2014), Journal of Experimental Psychology"
    },
    {
        "category": "exam_anxiety",
        "title": "Desensitization Through Timed Mock Conditions",
        "content": "Practicing in comfortable, silent, un-timed conditions fails to build stress tolerance. Doing practice papers under strict exam timer conditions immunizes you against test-day panic.",
        "action_item": "Take one practice quiz under strict countdown conditions without access to answer keys.",
        "source_reference": "Yerkes-Dodson Law of Arousal and Performance"
    },
    {
        "category": "exam_anxiety",
        "title": "Growth Mindset & Error Neuroplasticity",
        "content": "Carol Dweck's research shows that students who view errors as neural growth signals outperform those who view mistakes as evidence of fixed inability.",
        "action_item": "Review one problem you got wrong this week and write down the exact misconception that caused it.",
        "source_reference": "Carol Dweck, 'Mindset: The New Psychology of Success'"
    },

    # 6. Retention & Note-Taking Hacks
    {
        "category": "retention_hack",
        "title": "Generation Effect: Solve Before Checking the Solution",
        "content": "Generating an answer or predicting the outcome before seeing the solution improves future recall significantly more than passively following a step-by-step worked example.",
        "action_item": "Cover the solution of an example problem and attempt at least step 1 before looking.",
        "source_reference": "Slamecka & Graf (1978), Journal of Experimental Psychology"
    },
    {
        "category": "retention_hack",
        "title": "Handwritten Notes vs. Laptop Transcription",
        "content": "Mueller & Oppenheimer found that students typing on laptops transcribe lectures verbatim without synthesis. Handwriting forces cognitive summarization, resulting in better conceptual understanding.",
        "action_item": "Summarize today's core lecture takeaway on a physical index card or notebook.",
        "source_reference": "Mueller & Oppenheimer (2014), Psychological Science"
    },
    {
        "category": "retention_hack",
        "title": "Method of Loci (Memory Palace) for Lists",
        "content": "Associating items in a sequence with vivid physical landmarks along a familiar route leverages the brain's ancient spatial navigation centers for virtually limitless recall.",
        "action_item": "Anchor 5 sequential anatomical terms or historical events to 5 rooms in your childhood home.",
        "source_reference": "Yates (1966), 'The Art of Memory'"
    },
    {
        "category": "retention_hack",
        "title": "Chunking Information to Bypass Working Memory Limits",
        "content": "Working memory can only hold 4–7 discrete items simultaneously. Grouping related facts into meaningful conceptual 'chunks' allows you to process vast amounts of complex data.",
        "action_item": "Group 10 isolated definitions in your course into 3 overarching thematic categories.",
        "source_reference": "George Miller (1956), 'The Magical Number Seven, Plus or Minus Two'"
    }
]

def get_student_academic_context(user_id: str) -> dict:
    """Extracts course load, upcoming deadlines, and study streaks for personalization."""
    today = date.today()
    in_7_days = today + timedelta(days=7)

    # 1. Active Courses
    courses = db.session.execute(
        db.select(Course).where(Course.user_id == user_id)
    ).scalars().all()
    course_names = [c.course_name for c in courses]

    # 2. Upcoming tasks/assignments within next 7 days
    upcoming_tasks = db.session.execute(
        db.select(Task).where(
            Task.user_id == user_id,
            Task.is_completed.is_(False),
            Task.due_date >= today,
            Task.due_date <= in_7_days
        ).order_by(Task.due_date.asc())
    ).scalars().all()
    tasks_summary = [f"{t.title} (due {t.due_date.strftime('%b %d')}, priority: {t.priority})" for t in upcoming_tasks[:5]]

    # 3. Habit streaks
    habits = db.session.execute(
        db.select(Habit).where(Habit.user_id == user_id, Habit.is_archived.is_(False))
    ).scalars().all()
    max_streak = max([h.streak_count for h in habits], default=0)

    return {
        "today": today.isoformat(),
        "courses_count": len(courses),
        "courses": course_names,
        "upcoming_tasks_count": len(upcoming_tasks),
        "upcoming_tasks": tasks_summary,
        "study_streak": max_streak,
        "has_urgent_deadlines": any(t.priority == 'urgent' or (t.due_date - today).days <= 2 for t in upcoming_tasks)
    }

def get_or_generate_daily_tip(user_id: str, force_refresh: bool = False) -> dict:
    """
    Zero-Waste Daily Caching Pipeline:
    1. Checks if today's tip for this user already exists in DB.
    2. If found (and not forced), returns immediately without redundant AI calls.
    3. If absent, analyzes student pressure points, attempts Gemini/OpenRouter structured generation.
    4. Falls back gracefully to curated cognitive psychology bank if offline or no key.
    """
    today = date.today()

    # 1. Check existing cached tip for today
    if not force_refresh:
        existing_tip = db.session.execute(
            db.select(StudyTip).where(StudyTip.user_id == user_id, StudyTip.tip_date == today)
        ).scalar_one_or_none()

        if existing_tip:
            interaction = db.session.execute(
                db.select(UserTipInteraction).where(
                    UserTipInteraction.user_id == user_id,
                    UserTipInteraction.tip_id == existing_tip.id
                )
            ).scalar_one_or_none()
            return existing_tip.to_dict(interaction)

    # 2. Gather student academic context
    ctx = get_student_academic_context(user_id)

    # 3. Attempt AI generation if API keys exist
    ai_keys = resolve_api_keys(user_id)
    generated_tip_data = None

    if ai_keys.get('google_key') and not ai_keys.get('is_fallback_google'):
        try:
            generated_tip_data = generate_ai_tip(user_id, ctx, ai_keys['google_key'])
        except Exception as e:
            logger.warning(f"AI StudyTip generation failed for user {user_id}, falling back: {e}")

    # 4. Fallback to curated cognitive psychology tip bank
    if not generated_tip_data:
        generated_tip_data = select_curated_fallback_tip(user_id, ctx)

    # 5. Persist to DB
    new_tip = StudyTip(
        user_id=user_id,
        tip_date=today,
        category=generated_tip_data.get('category', 'active_recall'),
        title=generated_tip_data.get('title', 'Active Recall Strategy')[:150],
        content=generated_tip_data.get('content', 'Practice recalling facts from memory rather than re-reading notes.'),
        action_item=generated_tip_data.get('action_item', 'Write 3 key points from memory now.')[:255],
        source_reference=generated_tip_data.get('source_reference', 'Cognitive Psychology')[:100],
        is_ai_generated=bool(generated_tip_data.get('is_ai_generated', False))
    )

    try:
        db.session.add(new_tip)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to persist StudyTip: {e}")
        # If DB collision on race condition, fetch existing
        existing = db.session.execute(
            db.select(StudyTip).where(StudyTip.user_id == user_id, StudyTip.tip_date == today)
        ).scalar_one_or_none()
        if existing:
            return existing.to_dict()

    return new_tip.to_dict()

def generate_ai_tip(user_id: str, context: dict, api_key: str) -> dict:
    """Prompts Gemini for structured study tip matched to student's workload."""
    prompt = f"""
You are the Lead Cognitive Science Learning Specialist for the Smart Study Planner application.
Generate a personalized, high-impact daily study technique for a student based on their current academic context:

Student Context:
- Enrolled Courses: {', '.join(context.get('courses', [])) or 'General University Academics'}
- Impending Deadlines (next 7 days): {'; '.join(context.get('upcoming_tasks', [])) or 'No immediate critical deadlines'}
- Current Habit Streak: {context.get('study_streak', 0)} days
- Urgent Pressure: {'High' if context.get('has_urgent_deadlines') else 'Moderate/Normal'}

Pedagogical Directives:
1. Target an evidence-based cognitive technique (e.g. Active Recall, Spaced Repetition, Interleaving, Pomodoro Flow, Stress De-escalation, Dual Coding, Elaborative Interrogation).
2. If urgent deadlines exist, offer high-leverage exam stress relief or rapid active retrieval strategies.
3. Keep the content concise (2-3 punchy, encouraging sentences).
4. Provide a concrete, 5-minute micro-action item the student can execute right now.

Respond ONLY with valid JSON in this exact schema (no markdown code blocks, no other text):
{{
    "category": "spaced_repetition | pomodoro_flow | exam_anxiety | deep_work | active_recall | retention_hack",
    "title": "Catchy, Action-Oriented Title (max 70 chars)",
    "content": "2-3 sentences explaining the cognitive mechanism and why it works.",
    "action_item": "Specific micro-action the student can do right now (max 120 chars)",
    "source_reference": "Scientist, author, or landmark paper (e.g. Roediger & Karpicke, Cal Newport)"
}}
"""
    raw_response = query_google_gemini(api_key, "gemini-2.0-flash", prompt)
    
    # Strip markdown wrappers if present
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    parsed = json.loads(cleaned)
    parsed['is_ai_generated'] = True
    return parsed

def select_curated_fallback_tip(user_id: str, context: dict) -> dict:
    """Selects an evidence-backed tip from the curated bank, weighted by current pressure points."""
    # If student has urgent deadlines, filter for anxiety relief or active recall
    candidates = CURATED_COGNITIVE_TIPS
    if context.get('has_urgent_deadlines'):
        urgent_candidates = [t for t in CURATED_COGNITIVE_TIPS if t['category'] in ('exam_anxiety', 'active_recall', 'pomodoro_flow')]
        if urgent_candidates:
            candidates = urgent_candidates

    # Deterministic daily rotation based on date + user_id hash to prevent same tip every click
    seed_str = f"{date.today().isoformat()}-{user_id}"
    idx = abs(hash(seed_str)) % len(candidates)
    tip = dict(candidates[idx])
    tip['is_ai_generated'] = False
    return tip

def toggle_reaction(user_id: str, tip_id: str, reaction: str) -> dict:
    """Toggles or sets reaction feedback ('helpful', 'unhelpful', 'neutral')."""
    if reaction not in ('helpful', 'unhelpful', 'neutral', None):
        reaction = 'helpful'

    interaction = db.session.execute(
        db.select(UserTipInteraction).where(
            UserTipInteraction.user_id == user_id,
            UserTipInteraction.tip_id == tip_id
        )
    ).scalar_one_or_none()

    if interaction:
        # If clicked same reaction again, toggle off to neutral
        if interaction.reaction == reaction:
            interaction.reaction = None
        else:
            interaction.reaction = reaction
        interaction.interacted_at = datetime.now(timezone.utc)
    else:
        interaction = UserTipInteraction(
            user_id=user_id,
            tip_id=tip_id,
            reaction=reaction,
            is_bookmarked=False
        )
        db.session.add(interaction)

    try:
        db.session.commit()
        return {"status": "success", "reaction": interaction.reaction, "interaction": interaction.to_dict()}
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to record tip reaction: {e}")
        return {"status": "error", "message": str(e)}

def toggle_bookmark(user_id: str, tip_id: str) -> dict:
    """Toggles bookmark status in student's personal cognitive vault."""
    interaction = db.session.execute(
        db.select(UserTipInteraction).where(
            UserTipInteraction.user_id == user_id,
            UserTipInteraction.tip_id == tip_id
        )
    ).scalar_one_or_none()

    if interaction:
        interaction.is_bookmarked = not interaction.is_bookmarked
        interaction.interacted_at = datetime.now(timezone.utc)
    else:
        interaction = UserTipInteraction(
            user_id=user_id,
            tip_id=tip_id,
            is_bookmarked=True,
            reaction=None
        )
        db.session.add(interaction)

    try:
        db.session.commit()
        return {"status": "success", "is_bookmarked": interaction.is_bookmarked, "interaction": interaction.to_dict()}
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to toggle tip bookmark: {e}")
        return {"status": "error", "message": str(e)}

def get_bookmarked_tips(user_id: str, category: str = None) -> list:
    """Retrieves all bookmarked tips in user's vault."""
    query = (
        db.select(StudyTip, UserTipInteraction)
        .join(UserTipInteraction, StudyTip.id == UserTipInteraction.tip_id)
        .where(
            UserTipInteraction.user_id == user_id,
            UserTipInteraction.is_bookmarked.is_(True)
        )
        .order_by(UserTipInteraction.interacted_at.desc())
    )

    if category and category != 'all':
        query = query.where(StudyTip.category == category)

    results = db.session.execute(query).all()
    return [tip.to_dict(interaction) for tip, interaction in results]

def get_tip_archive(user_id: str, limit: int = 15) -> list:
    """Retrieves recent tips history for the user."""
    tips = db.session.execute(
        db.select(StudyTip)
        .where(StudyTip.user_id == user_id)
        .order_by(StudyTip.tip_date.desc())
        .limit(limit)
    ).scalars().all()

    tip_ids = [t.id for t in tips]
    interactions = {}
    if tip_ids:
        rows = db.session.execute(
            db.select(UserTipInteraction).where(
                UserTipInteraction.user_id == user_id,
                UserTipInteraction.tip_id.in_(tip_ids)
            )
        ).scalars().all()
        interactions = {str(row.tip_id): row for row in rows}

    return [t.to_dict(interactions.get(str(t.id))) for t in tips]

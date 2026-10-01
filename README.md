# 🎓 Smart Study Planner &bull; OmniLife OS

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/Flask-3.1.0-emerald?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/PostgreSQL%20%2F%20SQLite-Ready-blue?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/AI-Google%20Gemini%202.0-8A2BE2?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

> **OmniLife OS** is an enterprise-grade modular life operating system and intelligent academic study planner. Engineered with clean layered architecture, it unifies academic syllabus automation, multi-account wealth aggregation, atomic habit tracking, AI executive briefings, reflection journaling, and career progression under a unified 9-Dot App Switcher.

---

## 🌟 Key Workspaces (The OmniSuite Ecosystem)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OMNILIFE OS COMMAND CENTER                         │
│                    Unified 9-Dot Global Application Switcher                │
└──────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────┘
       │              │              │              │              │
       ▼              ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  🎓 ACADEMIC ││   🌿 LIFE    ││  💰 WEALTH   ││  📰 DIGEST   ││  🚀 CAREER   │
│   STUDY HUB  ││  & HABITS    ││  & FINANCE   ││  & REPORTS   ││  & INTERNS   │
│              ││              ││              ││              ││              │
│ • Syllabus AI││ • Routine Check│ • Multi-Bank ││ • RSS Feeds  ││ • Kanban App │
│ • Auto-Sched ││ • Streak Fire│ • TNG / Maybank│ • AI Briefing││ • Milestones │
│ • StudyTip AI││ • Opt. Toggle│ • Cash Flow   ││ • Market News││ • Interview  │
│ • GPA Sim    ││ • Categories ││ • PDF Parser ││ • Audio/Email││ • Offer Eval │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

### 1. 🎓 Academic & Study Hub (`/study` & `/student`)
- **Self-Healing AI Scheduler:** Automatically detects missed study sessions or overdue assignments and redistributes revisions forward into open timetable gaps without schedule collisions.
- **Automated Syllabus Ingestion:** Upload an academic syllabus PDF $\rightarrow$ Gemini extracts course titles, credits, assignment weightages, and deadlines with 1-click batch database insertion.
- **StudyTip AI (Cognitive Techniques Engine):** Delivers context-aware, evidence-based cognitive strategies (Active Recall, Spaced Repetition, Pomodoro Flow, Deep Work, Exam Anxiety Relief) tailored to upcoming deadlines. Features zero-waste daily caching and a personal **Cognitive Vault** (`/study/tips/saved`).
- **Target Grade Simulator & GPA Analytics:** Visual grade trajectory, credit distribution doughnut charts, and What-If forecasting.
- **AI Academic Tutor & Document Grounding:** Interactive study assistant grounded strictly in student-uploaded lecture slides and notes with LaTeX mathematical formula rendering.

### 2. 🌿 Life & Daily Habits (`/life`)
- **Atomic Habit Streaks:** Track daily routines, morning mindfulness, and study rituals with celebratory streak animations.
- **Optimistic UI Engine:** Instant local feedback on habit checks with automatic background REST synchronization and failure rollback.
- **Category Segmentation:** Filter by Learning, Health, Fitness, Mindfulness, or General growth.

### 3. 💰 OmniFinance Wealth Aggregator (`/finance`)
- **Decoupled Standalone Domain:** Independent financial module aggregating Malaysian e-wallets (Touch 'n Go, Boost, GrabPay), commercial banks (Maybank, CIMB, Public Bank, RHB), unit trusts (myASNB, Public Mutual), and stock brokerages (Moomoo, Rakuten Trade).
- **Cash Flow Analytics & Budget Gauges:** Track monthly income vs. expenses, net worth trajectories, and account balance reconciliation.
- **Financial Statement Parser:** Automated PDF/CSV bank statement ingestion.

### 4. 📰 OmniDigest Executive Intelligence (`/reports`)
- **Automated Feed Aggregator:** Ingests RSS feeds across Technology, Business/Finance, Science, and World News.
- **AI Morning Briefing:** Daily 3-minute executive synthesis of top industry trends.
- **Weekly Trend Review:** Multi-day thematic summaries and trend extraction.

### 5. 📔 Reflection & Journal (`/journal`)
- **Daily Mood Tracking:** Sentiment tracking with visual calendar heatmaps.
- **Long-Form Markdown Journal:** Distraction-free journaling with privacy and security protections.

### 6. 🚀 Career & Internship Hub (`/career`)
- **Kanban Application Pipeline:** Drag-and-drop job application tracker (Wishlist, Applied, Interviewing, Offer, Rejected).
- **Milestone Tracker:** Track interview rounds, technical assessment deadlines, and compensation offers.

---

## 🏗️ Architecture & Engineering Standards

The codebase strictly adheres to enterprise-grade software engineering patterns:

```mermaid
graph TD
    subgraph Presentation Tier
        Views["Jinja2 Templates (templates/*.html)"]
        Assets["Static Assets & CSS (static/style.css)"]
    end

    subgraph Controller Tier
        Blueprints["Blueprint Controllers (blueprints/*)"]
        AuthGuards["Auth Guards (@login_required, @role_required)"]
    end

    subgraph Domain & Service Tier
        AIService["AI & BYOK Encryption (services/ai_service.py)"]
        Scheduler["Schedule Optimizer (services/scheduler.py)"]
        TipService["StudyTip Engine (services/study_tip_service.py)"]
        FinanceService["Finance Aggregator (services/finance_service.py)"]
        DigestService["Digest Intelligence (services/digest_service.py)"]
    end

    subgraph Persistence Tier
        ORM["SQLAlchemy 2.0 ORM Models (models/*)"]
        DB[(PostgreSQL / SQLite with UUIDv4 PKs)]
    end

    Presentation Tier --> Controller Tier
    Controller Tier --> Domain & Service Tier
    Domain & Service Tier --> Persistence Tier
```

- **Application Factory Pattern:** Extensions (`db`) are initialized separately in `extensions.py` and bound inside `create_app()` in `app.py`.
- **Database Normalization & UUIDv4:** All tables utilize non-sequential UUID primary keys, explicit foreign key cascade behaviors (`CASCADE`), and indexed search columns (`user_id`, `due_date`, `is_completed`).
- **RESTful API Envelopes:** All endpoints under `/api/*` follow standardized envelopes:
  - Success: `{ "status": "success", "data": { ... }, "message": "..." }`
  - Error: `{ "status": "error", "message": "...", "errors": [ ... ] }`
- **BYOK (Bring Your Own Key) Security:** User-provided Google Gemini or OpenRouter API keys are encrypted at rest using AES-based `cryptography.fernet`.
- **Design System:** Bespoke dark/light mode with curated HSL slate tokens, glassmorphic sheen (`backdrop-filter: blur(16px)`), spring physics micro-interactions (`cubic-bezier(0.34, 1.56, 0.64, 1)`), and WCAG 2.1 AA accessibility compliance.

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git
- (Optional) PostgreSQL database (defaults to SQLite if unconfigured)

### 1. Clone the Repository
```bash
git clone https://github.com/ezralaics/smart-study-planner.git
cd smart-study-planner
```

### 2. Set Up Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your settings:
```ini
# Flask Secret Key
SECRET_KEY=fyp_study_planner_production_secret_key_2026

# Database Connection (Leave empty or use sqlite for local SQLite)
DATABASE_URL=sqlite:///instance/study_planner.db

# Optional AI API Key (Or enter via the in-app AI Settings modal)
GEMINI_API_KEY=your_gemini_api_key_here

# Server Port
PORT=5000
```

### 5. Launch the Application
```bash
python run.py
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

---

## 🧪 Automated Testing Suite

The repository includes a comprehensive, regression-proof test suite covering database models, foreign key cascades, authentication, API contracts, scheduling heuristics, financial aggregation, and AI tip caching.

Run all tests:
```bash
python test_suite.py
```

Expected output:
```
Ran 72 tests in ~85s
OK
```

---

## 📁 Repository Structure

```
smart-study-planner/
├── app.py                      # Application Factory (create_app)
├── run.py                      # Development server runner
├── config.py                   # Environment & runtime configurations
├── extensions.py               # Shared extensions (SQLAlchemy db, GUID)
├── requirements.txt            # Production & testing dependencies
├── test_suite.py               # Automated 72-test validation suite
├── blueprints/                 # Domain Controllers
│   ├── auth/                   # User authentication & session management
│   ├── main/                   # Public landing, onboarding, workspace routing
│   ├── student/                # Academic dashboard & timetable
│   ├── study/                  # Study Hub, course planner, StudyTip AI routes
│   ├── life/                   # Habit tracking & routine routes
│   ├── finance/                # Wealth aggregator, accounts & transactions
│   ├── reports/                # RSS feed curation & AI digest briefings
│   ├── journal/                # Mood tracking & reflection entries
│   ├── career/                 # Kanban application tracker
│   ├── analytics/              # GPA simulation & study velocity metrics
│   ├── automation/             # Syllabus parser & schedule rebalancer
│   └── api/                    # Core REST API endpoints
├── models/                     # SQLAlchemy 2.0 Persistence Layer
│   ├── user.py                 # User authentication & profile model
│   ├── course.py               # Academic courses & credit hours
│   ├── task.py                 # Assignments, exams & priority tasks
│   ├── schedule.py             # Timetable revision blocks & lectures
│   ├── study_tip.py            # Cognitive tips & bookmark interactions
│   ├── habit.py                # Habits, categories & streak logs
│   ├── financial_account.py    # Bank accounts, e-wallets & ledgers
│   ├── report.py               # RSS feeds & AI digests
│   ├── journal.py              # Journal entries & sentiment tracking
│   └── career.py               # Job application milestones
├── services/                   # Domain Logic & Business Rules
│   ├── ai_service.py           # Gemini/OpenRouter integration & BYOK encryption
│   ├── scheduler.py            # Heuristic study session generator
│   ├── automation_service.py   # Syllabus PDF extraction & schedule healer
│   ├── study_tip_service.py    # Zero-waste caching & 50+ cognitive tip bank
│   ├── finance_service.py      # Net worth calculation & cashflow metrics
│   ├── digest_service.py       # RSS parser & briefing generator
│   └── statement_parser.py     # PDF bank statement extractor
├── static/                     # Global CSS tokens, PWA manifests, icons
└── templates/                  # Jinja2 presentation templates
    ├── base.html               # Master layout with 9-dot launcher & toasts
    ├── home.html               # Public landing page with 3D perspective mockup
    ├── dashboard.html          # Unified Command Center
    ├── study_planner.html      # Course planner with StudyTip AI banner
    ├── study/                  # Saved StudyTip vault & archive
    ├── life/                   # Habit tracking dashboard
    ├── finance/                # Multi-account wealth dashboard
    └── reports/                # Digest intelligence hub
```

---

## 🔒 Security & Privacy

- **Password Hashing:** Passwords encrypted using Werkzeug PBKDF2/SHA256 with automatic salt generation.
- **BYOK Encryption:** User API keys encrypted via `cryptography.fernet` using the application's master secret key.
- **SQL Injection Prevention:** 100% parameterized queries via SQLAlchemy 2.0.
- **XSS Protection:** Context-aware auto-escaping enabled by default across all Jinja2 templates.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

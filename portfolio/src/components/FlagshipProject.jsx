import React, { useState } from 'react';
import { 
  Sparkles, 
  Layers, 
  Cpu, 
  ShieldCheck, 
  ExternalLink, 
  Database,
  Smartphone,
  Bot,
  KeyRound,
  CheckCircle2,
  Workflow,
  ArrowRight,
  Server,
  Terminal,
  Play
} from 'lucide-react';
import { GithubIcon } from './Icons';

export default function FlagshipProject() {
  const [activeTab, setActiveTab] = useState('pillars');
  const [activePillar, setActivePillar] = useState('rbac');
  const [selectedFlowStep, setSelectedFlowStep] = useState(0);

  const pillars = [
    {
      id: 'rbac',
      name: 'Modular Monolith & RBAC',
      badge: 'Architecture & Security',
      icon: <Layers size={18} color="#6366f1" />,
      color: '#6366f1',
      title: 'Multi-Tenant Institutional RBAC & Flask Blueprints',
      description: 'Refactored from a script into an enterprise Flask Application Factory pattern with 6 decoupled domain Blueprints. Strict separation of concerns eliminates circular imports and enforces institutional role security.',
      points: [
        'Dedicated isolated portals: Student (Academic hub), Educator (Cohort gradebook matrix), Admin (System telemetry & role upgrades)',
        'Custom `@role_required(*allowed_roles)` security decorators enforcing HTTP 403 Forbidden on unauthorized elevation attempts',
        'Built-in 1-Click Recruiter sandbox authenticators allowing instant exploration of Student, Educator, or Admin roles without credentials',
        'Stateful sessions protected with HttpOnly, SameSite=Lax flags, and cryptographically signed session cookies'
      ],
      codeSnippet: `@student_bp.route('/planner')
@login_required
@role_required('student')
def planner_view():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('student/planner.html', tasks=tasks)`
    },
    {
      id: 'db',
      name: 'Production Database',
      badge: 'Database & Scale',
      icon: <Database size={18} color="#06b6d4" />,
      color: '#06b6d4',
      title: 'PostgreSQL UUID Architecture & Automated Migrations',
      description: 'Production-hardened relational persistence with UUID v4 primary keys across all tables, preventing sequential ID harvesting and enabling seamless distributed scaling.',
      points: [
        'UUID v4 primary keys (`uuid_generate_v4()`) on users, courses, tasks, and schedules to guarantee collision-free global IDs',
        'Automated zero-downtime schema migrations inspecting database state and applying non-destructive column synchronizations at startup',
        'Indexed foreign key relationships with strict cascade rules preventing orphan records during course or user deletions',
        'Dual-compatibility driver support: psycopg2 for PostgreSQL in cloud production with seamless fallback for local environments'
      ],
      codeSnippet: `class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), default='student', nullable=False)`
    },
    {
      id: 'ai',
      name: 'AI Knowledge Base & BYOK',
      badge: 'Multi-LLM Systems',
      icon: <Bot size={18} color="#a855f7" />,
      color: '#a855f7',
      title: 'Multi-Provider BYOK AI & Contextual Knowledge Base',
      description: 'Dual-provider LLM gateway supporting Google Gemini and OpenRouter (Anthropic/OpenAI/Meta). Features client Bring-Your-Own-Key (BYOK) with cryptographic encryption.',
      points: [
        'Client-owned Bring-Your-Own-Key (BYOK) architecture: user keys are encrypted in-flight and stored with AES encryption, never logged or leaked',
        'Context-aware academic prompting: automatically binds course syllabi, assignment due dates, and grading weights into LLM context',
        'Intelligent heuristic fallback: seamless fallback mechanisms ensure core study scheduling continues even during LLM API outages',
        'Direct study assistance: converts unstructured syllabus text and lecture notes into structured calendar study milestones'
      ],
      codeSnippet: `def generate_study_insights(user_key, course_context, query):
    client = initialize_llm_provider(user_key, provider='gemini')
    system_prompt = build_academic_context(course_context)
    return client.generate_content(prompt=system_prompt + query)`
    },
    {
      id: 'pwa',
      name: 'Mobile & Reliability',
      badge: 'PWA & 45+ Tests',
      icon: <Smartphone size={18} color="#10b981" />,
      color: '#10b981',
      title: 'Native Installable PWA & 45+ Automated Unit Tests',
      description: 'Engineered as a Progressive Web App (PWA) with offline timetable caching, backed by a rigorous 45-test automated unit suite verifying 100% of critical paths.',
      points: [
        'Native PWA manifest & Service Worker: installable on iOS, Android, and macOS/Windows with standalone app appearance',
        '45 comprehensive automated unit tests covering authentication, RBAC boundaries, gradebook persistence, and interval collisions',
        '100% test pass rate executed in under 12 seconds via automated test runner (`test_suite.py`)',
        'Mathematical interval collision algorithm: `max(s1, s2) < min(e1, e2)` ensures study blocks never clash with existing classes'
      ],
      codeSnippet: `Ran 45 tests in 10.842s
OK (Authentication: 12/12, RBAC: 10/10, Schedulers: 15/15, DB: 8/8)
Status: 100% Passing - Zero Regressions`
    }
  ];

  const flowSteps = [
    {
      step: '01',
      title: 'Client Tier & Native PWA',
      role: 'Frontend Presentation',
      desc: 'Users access the responsive interface via browser or installed PWA. Supports offline timetable inspection via Service Worker caching.',
      tag: 'React / Jinja2 / PWA'
    },
    {
      step: '02',
      title: 'Security & RBAC Middleware',
      role: 'Authentication & Guard',
      desc: 'Requests pass through secure session cookies and `@role_required` decorators, validating Student, Educator, or Admin credentials.',
      tag: 'Session / Werkzeug / RBAC'
    },
    {
      step: '03',
      title: 'Modular Blueprints & Factory',
      role: 'Application Core',
      desc: 'Application Factory routes requests across 6 domain Blueprints (`auth`, `student`, `educator`, `admin`, `api`, `main`).',
      tag: 'Flask 3.x / Blueprints'
    },
    {
      step: '04',
      title: 'Heuristic Scheduler & AI Gateway',
      role: 'Computation Engine',
      desc: 'Constraint engine calculates urgency heuristic scores while BYOK LLM gateway (Gemini/OpenRouter) powers contextual study insights.',
      tag: 'Interval Algorithms & Gemini'
    },
    {
      step: '05',
      title: 'PostgreSQL Relational Storage',
      role: 'Persistence Layer',
      desc: 'Data persists in PostgreSQL using UUID v4 keys, ACID transactions, foreign key cascades, and automated schema migration on boot.',
      tag: 'PostgreSQL / SQLAlchemy'
    }
  ];

  return (
    <section className="section" id="flagship">
      <div className="content-wrapper">
        {/* Section Header */}
        <div className="section-header">
          <div className="status-pill" style={{ marginBottom: '14px' }}>
            <Sparkles size={14} className="text-accent" />
            <span>Flagship Engineering Showcase</span>
          </div>
          <h2 className="section-title">
            NextOmni <span className="gradient-text">OS</span>
          </h2>
          <p className="section-subtitle">
            An institutional multi-tenant academic management platform and constraint-satisfaction scheduling system, engineered for production cloud deployment.
          </p>
        </div>

        {/* Hero Flagship Banner Card */}
        <div className="flagship-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
            <div>
              <span className="project-category" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
                ⭐ Flagship Production Application
              </span>
              <h3 className="flagship-title" style={{ marginTop: '10px' }}>
                NextOmni OS &bull; Academic & Life Operating System
              </h3>
              <p className="flagship-tagline">
                Automating academic workload balancing, cohort gradebooks, and conflict-free study timetable generation with production-grade security.
              </p>
            </div>

            {/* Direct Deployment Status */}
            <div className="status-badge-live">
              <span className="pulse-dot"></span>
              <span>Live on Render Cloud</span>
            </div>
          </div>

          {/* Quick Stats Grid */}
          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-number">45+ Tests</div>
              <div className="stat-label">100% Pass Rate Automated Suite</div>
            </div>
            <div className="stat-box">
              <div className="stat-number">3 Tier RBAC</div>
              <div className="stat-label">Student, Educator & Admin Portals</div>
            </div>
            <div className="stat-box">
              <div className="stat-number">PostgreSQL UUID</div>
              <div className="stat-label">Zero-Downtime Schema Migrations</div>
            </div>
            <div className="stat-box">
              <div className="stat-number">Multi-LLM BYOK</div>
              <div className="stat-label">Google Gemini & OpenRouter</div>
            </div>
          </div>

          {/* High-Impact Recruiter Action Buttons */}
          <div className="flagship-action-bar">
            <a 
              href="https://smart-study-planner-1-vozm.onrender.com" 
              target="_blank" 
              rel="noreferrer" 
              className="btn btn-primary"
              id="flagship-launch-app-btn"
            >
              <Play size={16} fill="currentColor" /> Launch Live App <ExternalLink size={14} />
            </a>

            <a 
              href="https://smart-study-planner-1-vozm.onrender.com/demo-login/student" 
              target="_blank" 
              rel="noreferrer" 
              className="btn btn-accent-demo"
              id="flagship-recruiter-demo-btn"
            >
              <KeyRound size={16} /> 1-Click Recruiter Demo <ExternalLink size={14} />
            </a>

            <a 
              href="https://github.com/ezralaics/smart-study-planner" 
              target="_blank" 
              rel="noreferrer" 
              className="btn btn-secondary"
              id="flagship-github-btn"
            >
              <GithubIcon size={16} /> GitHub Repository <ExternalLink size={14} />
            </a>
          </div>

          {/* Tech Stack Pills */}
          <div className="tech-tags" style={{ marginTop: '24px' }}>
            <span className="tag">Python 3.12</span>
            <span className="tag">Flask Application Factory</span>
            <span className="tag">6 Domain Blueprints</span>
            <span className="tag">PostgreSQL UUID v4</span>
            <span className="tag">SQLAlchemy ORM</span>
            <span className="tag">RBAC Security Decorators</span>
            <span className="tag">Google Gemini 2.5 API</span>
            <span className="tag">OpenRouter Gateway</span>
            <span className="tag">Native PWA</span>
            <span className="tag">Automated Unit Tests</span>
          </div>

          {/* Main Showcase Navigation Tabs */}
          <div className="showcase-tabs" style={{ marginTop: '32px' }}>
            <button 
              className={`tab-btn ${activeTab === 'pillars' ? 'active' : ''}`}
              onClick={() => setActiveTab('pillars')}
              id="tab-btn-pillars"
            >
              <Layers size={16} style={{ verticalAlign: 'text-bottom', marginRight: '6px' }} />
              The 4 Engineering Pillars
            </button>
            <button 
              className={`tab-btn ${activeTab === 'architecture' ? 'active' : ''}`}
              onClick={() => setActiveTab('architecture')}
              id="tab-btn-architecture"
            >
              <Workflow size={16} style={{ verticalAlign: 'text-bottom', marginRight: '6px' }} />
              Interactive System Flow & Architecture
            </button>
            <button 
              className={`tab-btn ${activeTab === 'algorithm' ? 'active' : ''}`}
              onClick={() => setActiveTab('algorithm')}
              id="tab-btn-algorithm"
            >
              <Cpu size={16} style={{ verticalAlign: 'text-bottom', marginRight: '6px' }} />
              Heuristic Scheduling Engine
            </button>
          </div>

          {/* Tab Content Panes */}
          {activeTab === 'pillars' && (
            <div className="tab-pane">
              {/* Pillar Selector Pills */}
              <div className="pillar-selector-bar">
                {pillars.map(p => (
                  <button
                    key={p.id}
                    className={`pillar-pill-btn ${activePillar === p.id ? 'active' : ''}`}
                    onClick={() => setActivePillar(p.id)}
                    style={{
                      borderColor: activePillar === p.id ? p.color : 'transparent'
                    }}
                  >
                    {p.icon}
                    <span>{p.name}</span>
                  </button>
                ))}
              </div>

              {/* Active Pillar Details Card */}
              {pillars.map(p => p.id === activePillar && (
                <div key={p.id} className="pillar-detail-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
                    <h4 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                      {p.title}
                    </h4>
                    <span className="badge-pill" style={{ background: `${p.color}22`, color: p.color, border: `1px solid ${p.color}44` }}>
                      {p.badge}
                    </span>
                  </div>

                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.96rem', lineHeight: '1.6', marginBottom: '20px' }}>
                    {p.description}
                  </p>

                  <div className="pillar-points-grid">
                    {p.points.map((point, idx) => (
                      <div className="pillar-point-item" key={idx}>
                        <CheckCircle2 size={16} color={p.color} style={{ flexShrink: 0, marginTop: '3px' }} />
                        <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: '1.5' }}>
                          {point}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="code-preview-box" style={{ marginTop: '20px' }}>
                    <div className="code-header">
                      <span>Production Implementation Snippet</span>
                      <Terminal size={14} color="#94a3b8" />
                    </div>
                    <pre style={{ margin: 0, padding: '14px', fontFamily: 'var(--font-code)', fontSize: '0.84rem', color: '#cbd5e1', overflowX: 'auto' }}>
                      {p.codeSnippet}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'architecture' && (
            <div className="tab-pane">
              <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                End-to-End System Flow Breakdown
              </h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '24px' }}>
                Follow how incoming user requests traverse from the Progressive Web App client through the security boundaries, factory blueprints, heuristic engines, and PostgreSQL database:
              </p>

              {/* Interactive Step Navigator */}
              <div className="flow-steps-grid">
                {flowSteps.map((step, idx) => (
                  <div 
                    key={idx}
                    className={`flow-step-card ${selectedFlowStep === idx ? 'active' : ''}`}
                    onClick={() => setSelectedFlowStep(idx)}
                  >
                    <div className="flow-step-number">{step.step}</div>
                    <div className="flow-step-content">
                      <div className="flow-step-title">{step.title}</div>
                      <div className="flow-step-role">{step.role}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Detailed Explanation of Selected Step */}
              <div className="flow-detail-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--accent-cyan)', fontSize: '0.9rem' }}>
                    Step {flowSteps[selectedFlowStep].step} Deep Dive: {flowSteps[selectedFlowStep].title}
                  </span>
                  <span className="tag" style={{ margin: 0 }}>
                    {flowSteps[selectedFlowStep].tag}
                  </span>
                </div>
                <p style={{ color: 'var(--text-primary)', fontSize: '0.94rem', margin: 0, lineHeight: '1.6' }}>
                  {flowSteps[selectedFlowStep].desc}
                </p>
              </div>

              {/* Visual System Diagram */}
              <div className="system-diagram-visual">
                <div className="diagram-node node-client">
                  <Smartphone size={20} color="#38bdf8" />
                  <strong>Client Tier</strong>
                  <span>PWA & Desktop</span>
                </div>
                <div className="diagram-arrow"><ArrowRight size={18} /></div>
                <div className="diagram-node node-security">
                  <ShieldCheck size={20} color="#10b981" />
                  <strong>RBAC Guard</strong>
                  <span>Session & Cookies</span>
                </div>
                <div className="diagram-arrow"><ArrowRight size={18} /></div>
                <div className="diagram-node node-app">
                  <Server size={20} color="#6366f1" />
                  <strong>Flask Factory</strong>
                  <span>6 Blueprints</span>
                </div>
                <div className="diagram-arrow"><ArrowRight size={18} /></div>
                <div className="diagram-node node-engine">
                  <Cpu size={20} color="#f59e0b" />
                  <strong>Scheduler / AI</strong>
                  <span>Gemini & Overlaps</span>
                </div>
                <div className="diagram-arrow"><ArrowRight size={18} /></div>
                <div className="diagram-node node-db">
                  <Database size={20} color="#a855f7" />
                  <strong>PostgreSQL</strong>
                  <span>UUID v4 Primary Keys</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'algorithm' && (
            <div className="tab-pane">
              <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                Multi-Factor Heuristic Scheduling Engine
              </h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '18px' }}>
                Traditional calendars require students to manually coordinate study times. The Smart Study Planner evaluates pending assignments and exams, calculates an urgency score, and schedules non-colliding study sessions automatically.
              </p>

              <div className="formula-box">
                <strong>Priority Score Optimization Formula:</strong><br />
                <code>Priority_Score = round(((Urgency_Factor x 0.5) + (Weight_Factor x 0.3) + (Target_Grade_Factor x 0.2)) x 100, 1)</code>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginTop: '18px' }}>
                <div className="feature-highlight-card">
                  <div style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.92rem', marginBottom: '6px' }}>
                    1. Exponential Urgency (50%)
                  </div>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', margin: 0 }}>
                    Formulated as <code>1.0 / max(1, days_remaining)</code>. Components due in under 72 hours are automatically scheduled first.
                  </p>
                </div>

                <div className="feature-highlight-card">
                  <div style={{ color: 'var(--accent-primary)', fontWeight: 700, fontSize: '0.92rem', marginBottom: '6px' }}>
                    2. Weight & Grade Target (50%)
                  </div>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', margin: 0 }}>
                    Major coursework (e.g. 40% Final Exam) allocates multiple 1-hour sessions, adjusted for the student's target letter grade.
                  </p>
                </div>

                <div className="feature-highlight-card">
                  <div style={{ color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.92rem', marginBottom: '6px' }}>
                    3. Zero-Collision Interval Constraint
                  </div>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', margin: 0 }}>
                    Evaluates mathematical interval overlaps: <code>max(s1, s2) &lt; min(e1, e2)</code>. Sessions never overlap with class timetables.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Bottom Action Footer */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '32px', paddingTop: '20px', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '16px' }}>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              Ready to see the system live? Click below to try the 1-Click Recruiter Demo.
            </div>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <a 
                href="https://smart-study-planner-1-vozm.onrender.com/demo-login/student" 
                target="_blank" 
                rel="noreferrer" 
                className="btn btn-primary btn-sm"
              >
                <KeyRound size={14} /> Instant Recruiter Demo <ExternalLink size={12} />
              </a>
              <a 
                href="https://github.com/ezralaics/smart-study-planner" 
                target="_blank" 
                rel="noreferrer" 
                className="btn btn-secondary btn-sm"
              >
                <GithubIcon size={14} /> View Code on GitHub <ExternalLink size={12} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

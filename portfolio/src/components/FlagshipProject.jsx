import React, { useState } from 'react';
import { 
  Sparkles, 
  Layers, 
  Cpu, 
  ShieldCheck, 
  CheckCircle, 
  ExternalLink, 
  Clock, 
  Code2, 
  Database,
  CalendarCheck
} from 'lucide-react';
import { GithubIcon } from './Icons';

export default function FlagshipProject() {
  const [activeTab, setActiveTab] = useState('algorithm');

  return (
    <section className="section" id="flagship">
      <div className="content-wrapper">
        <div className="section-header">
          <span className="section-tag">// Flagship Engineering Case Study</span>
          <h2 className="section-title">Smart Study Planner — Enterprise Edition</h2>
          <p className="section-subtitle">
            An institutional academic management and heuristic scheduling platform built with Flask, SQLAlchemy, and algorithmic constraint satisfaction.
          </p>
        </div>

        <div className="flagship-card">
          <div className="flagship-badge">
            <Sparkles size={14} /> Flagship Software Project
          </div>

          <h3 className="flagship-title">Smart Study Planner</h3>
          <p className="flagship-tagline">
            Automating course workload balancing, deadline management, and institutional cohort grading with zero-collision study session generation.
          </p>

          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-number">6 Blueprints</div>
              <div className="stat-label">Modular Application Factory Pattern</div>
            </div>
            <div className="stat-box">
              <div className="stat-number">3 Dedicated Modules</div>
              <div className="stat-label">Student, Educator & Admin Portals</div>
            </div>
            <div className="stat-box">
              <div className="stat-number">100% Conflict-Free</div>
              <div className="stat-label">Interval Overlap Timetable Checker</div>
            </div>
            <div className="stat-box">
              <div className="stat-number">9/9 Passed</div>
              <div className="stat-label">Comprehensive Automated Test Suite</div>
            </div>
          </div>

          <div className="tech-tags">
            <span className="tag">Python 3.12+</span>
            <span className="tag">Flask Factory Pattern</span>
            <span className="tag">SQLAlchemy ORM</span>
            <span className="tag">RBAC Security</span>
            <span className="tag">Werkzeug Crypto</span>
            <span className="tag">Constraint Scheduling Algorithm</span>
            <span className="tag">Bootstrap 5 + Jinja2</span>
            <span className="tag">SQLite / PostgreSQL Ready</span>
          </div>

          {/* Interactive Case Study Tabs */}
          <div className="showcase-tabs">
            <button 
              className={`tab-btn ${activeTab === 'algorithm' ? 'active' : ''}`}
              onClick={() => setActiveTab('algorithm')}
            >
              <Cpu size={15} style={{ verticalAlign: 'text-bottom', marginRight: '6px' }} />
              Auto-Scheduler Algorithm
            </button>
            <button 
              className={`tab-btn ${activeTab === 'architecture' ? 'active' : ''}`}
              onClick={() => setActiveTab('architecture')}
            >
              <Layers size={15} style={{ verticalAlign: 'text-bottom', marginRight: '6px' }} />
              System Architecture
            </button>
            <button 
              className={`tab-btn ${activeTab === 'rbac' ? 'active' : ''}`}
              onClick={() => setActiveTab('rbac')}
            >
              <ShieldCheck size={15} style={{ verticalAlign: 'text-bottom', marginRight: '6px' }} />
              Institutional RBAC & 1-Click Demos
            </button>
            <button 
              className={`tab-btn ${activeTab === 'tests' ? 'active' : ''}`}
              onClick={() => setActiveTab('tests')}
            >
              <CheckCircle size={15} style={{ verticalAlign: 'text-bottom', marginRight: '6px' }} />
              Testing & Verification
            </button>
          </div>

          {/* Tab Content Panes */}
          <div className="tab-pane">
            {activeTab === 'algorithm' && (
              <div>
                <h4 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  Intelligent Study Session Auto-Scheduler
                </h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '16px' }}>
                  Traditional study planners require students to manually pick study times. The Smart Study Planner evaluates pending assignments and exams, scores urgency, and generates conflict-free study blocks automatically.
                </p>

                <div className="formula-box">
                  <strong>Priority Score Formula:</strong><br />
                  Score = round(((Urgency_Factor × 0.5) + (Weight_Factor × 0.3) + (Target_Grade_Factor × 0.2)) × 100, 1)
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginTop: '16px' }}>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.88rem' }}>1. Urgency Heuristic (50% weight)</div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      Calculated as <code>1.0 / max(1, days_remaining)</code>. Prioritizes components due in under 72 hours exponentially.
                    </p>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ color: 'var(--accent-primary)', fontWeight: 700, fontSize: '0.88rem' }}>2. Weightage & Target (50% weight)</div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      Heavier components (e.g. 30% Final Project) receive more dedicated 1-hour sessions than lightweight 5% quizzes.
                    </p>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.88rem' }}>3. Interval Conflict Avoidance</div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      Mathematical interval collision: <code>max(s1, s2) &lt; min(e1, e2)</code>. Sessions never clash with existing lectures or classes.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'architecture' && (
              <div>
                <h4 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  Enterprise Modular Architecture
                </h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '16px' }}>
                  Refactored from a monolithic script into an industry-standard Flask Application Factory pattern with decoupled extensions and Blueprints.
                </p>

                <div style={{ background: '#090e1a', padding: '16px', borderRadius: '8px', fontFamily: 'var(--font-code)', fontSize: '0.85rem', lineHeight: '1.7', color: '#94a3b8' }}>
                  <span style={{ color: '#38bdf8' }}>frontend folder/</span><br />
                  &nbsp;&nbsp;├── <span style={{ color: '#f59e0b' }}>app.py</span> (create_app factory & environment config)<br />
                  &nbsp;&nbsp;├── <span style={{ color: '#f59e0b' }}>extensions.py</span> (decoupled db = SQLAlchemy() to prevent circular imports)<br />
                  &nbsp;&nbsp;├── <span style={{ color: '#a5b4fc' }}>blueprints/</span><br />
                  &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── <span style={{ color: '#34d399' }}>auth/</span> (/login, /register, /demo-login/&lt;role&gt;)<br />
                  &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── <span style={{ color: '#34d399' }}>student/</span> (/student/dashboard, planner, calendar, courses, tasks)<br />
                  &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── <span style={{ color: '#34d399' }}>educator/</span> (Faculty dashboard, gradebook, courses, notices)<br />
                  &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── <span style={{ color: '#34d399' }}>admin/</span> (System health telemetry, users, catalog, audit)<br />
                  &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── <span style={{ color: '#34d399' }}>api/</span> (Courses, Tasks, Schedules, and Auto-Scheduler)<br />
                  &nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── <span style={{ color: '#34d399' }}>main/</span> (Smart portal routing & backward-compatible aliases)<br />
                  &nbsp;&nbsp;└── <span style={{ color: '#a5b4fc' }}>services/</span><br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <span style={{ color: '#f43f5e' }}>scheduler.py</span> (Heuristic scheduling engine)<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── <span style={{ color: '#f43f5e' }}>demo_seeder.py</span> (Multi-role demo data seeder)
                </div>
              </div>
            )}

            {activeTab === 'rbac' && (
              <div>
                <h4 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  Institutional Multi-Role RBAC & Recruiter Demos
                </h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '16px' }}>
                  The application distinguishes between 3 institutional tiers, secured with custom <code>@role_required(*allowed_roles)</code> decorators:
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: '8px' }}>
                    <div style={{ fontWeight: 700, color: 'var(--accent-primary)', marginBottom: '4px' }}>🎓 Student Module</div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      Enrolled in diploma/degree modules, tracks grades against targets, views master calendar, and runs the AI auto-scheduler.
                    </p>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: '8px' }}>
                    <div style={{ fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '4px' }}>👨‍🏫 Educator Module</div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      Accesses the Faculty Gradebook matrix, inputs component scores, manages syllabi, and broadcasts notices.
                    </p>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: '8px' }}>
                    <div style={{ fontWeight: 700, color: 'var(--accent-amber)', marginBottom: '4px' }}>⚙️ Administrator Module</div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      Platform overview, user directory with instant role promotions, master course catalog, and system telemetry.
                    </p>
                  </div>
                </div>

                <div style={{ marginTop: '16px', padding: '12px 16px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px' }}>
                  <strong style={{ color: 'var(--accent-emerald)', fontSize: '0.9rem' }}>Recruiter 1-Click Demo Buttons:</strong>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                    Built right onto the login screen so recruiters and hiring managers can explore each role instantly without needing to register or fill out credentials.
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'tests' && (
              <div>
                <h4 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  Automated Verification & Security
                </h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '16px' }}>
                  Every endpoint, authorization rule, and algorithm component is validated with a dedicated automated test suite:
                </p>

                <div style={{ background: '#090e1a', padding: '16px', borderRadius: '8px', fontFamily: 'var(--font-code)', fontSize: '0.85rem', lineHeight: '1.8' }}>
                  <div style={{ color: '#10b981' }}>✔ test_routes_exist (Public pages render properly)</div>
                  <div style={{ color: '#10b981' }}>✔ test_demo_login_student (1-Click Student authentication)</div>
                  <div style={{ color: '#10b981' }}>✔ test_demo_login_educator (1-Click Educator authentication)</div>
                  <div style={{ color: '#10b981' }}>✔ test_demo_login_admin (1-Click Admin authentication)</div>
                  <div style={{ color: '#10b981' }}>✔ test_rbac_access_restrictions (HTTP 403 Forbidden on unauthorized roles)</div>
                  <div style={{ color: '#10b981' }}>✔ test_educator_gradebook_and_api (Cohort marks matrix persistence)</div>
                  <div style={{ color: '#10b981' }}>✔ test_admin_user_management (Real-time role upgrade API)</div>
                  <div style={{ color: '#10b981' }}>✔ test_auto_scheduler_preview_and_apply (Urgency scoring, collision check, calendar sync)</div>
                  <div style={{ color: '#10b981' }}>✔ test_separated_user_modules (Dedicated Student, Educator & Admin portals verified)</div>
                  <div style={{ color: '#38bdf8', marginTop: '8px', fontWeight: 700 }}>Ran 9 tests in 11.4s — OK (All passing)</div>
                </div>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '14px', marginTop: '28px', flexWrap: 'wrap' }}>
            <a 
              href="https://github.com/ezralaics/smart-study-planner" 
              target="_blank" 
              rel="noreferrer" 
              className="btn btn-primary"
            >
              <GithubIcon size={16} /> View GitHub Repository <ExternalLink size={14} />
            </a>
            <a 
              href="#contact" 
              className="btn btn-secondary"
            >
              Discuss System Architecture <ExternalLink size={14} />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

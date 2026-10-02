import React, { useState } from 'react';
import { 
  ArrowRight, 
  Mail, 
  Terminal, 
  ShieldCheck, 
  Server, 
  Database,
  Download
} from 'lucide-react';
import { GithubIcon } from './Icons';

export default function Hero() {
  const [activeTab, setActiveTab] = useState('profile');

  const terminalOutputs = {
    profile: `const softwareEngineer = {
  name: "Ezra Lai Kwang Zhe",
  title: "Full-Stack Software Engineer & Systems Builder",
  domain: "laikwangzhe.com",
  status: "🟢 Available for Engineering Roles (Full-Stack / Backend)",
  coreStack: ["Python / Flask", "React 19 / Vite", "PostgreSQL", "JavaScript (ES6+)"],
  engineeringFocus: [
    "Modular Monoliths & Clean Architecture",
    "PostgreSQL UUID Schemas & Migrations",
    "Algorithmic Constraint Schedulers",
    "Multi-LLM BYOK Gateways (Gemini / OpenRouter)",
    "Comprehensive Automated Test Suites"
  ]
};`,
    architecture: `// Production Engineering Principles Applied:
- Flask Application Factory Pattern & 6 Decoupled Domain Blueprints
- Zero-Downtime PostgreSQL Migrations & UUID v4 Primary Keys
- Strict RBAC Guarding via Custom @role_required Decorators
- Interval Overlap Constraint Scheduling: max(s1, s2) < min(e1, e2)
- Client Bring-Your-Own-Key (BYOK) AES Encrypted AI Pipelines
- Offline-First PWA Manifest & Service Worker Cache Synchronization`,
    metrics: `// Verified Cloud Production Telemetry:
- Flagship App: NextOmni OS (Smart Study Planner & Life Platform)
- Automated Suite: 72 / 72 Tests Passing (100% Pass Rate)
- Production DB: PostgreSQL on Cloud Infrastructure
- Cloud Deployment: Live on Render (Backend) & Vercel (Frontend)
- Institutional Roles: Student, Educator, Admin Isolation Verified`
  };

  return (
    <section className="section hero-section" id="about">
      <div className="content-wrapper">
        <div className="hero-grid">
          <div>
            {/* Top Status Pill */}
            <div className="status-pill" style={{ marginBottom: '18px' }}>
              <span className="pulse-dot"></span>
              <span>Available for Full-Stack & Software Engineering Roles</span>
            </div>

            {/* Main Headline */}
            <h1 className="hero-title">
              Ezra Lai Kwang Zhe — <span className="gradient-text">Full-Stack Software Engineer</span> & Systems Builder.
            </h1>

            {/* Subtitle Description */}
            <p className="hero-desc">
              I architect and build production-grade web platforms with a focus on modular backend systems, PostgreSQL UUID architectures, multi-tenant RBAC security, and algorithmic constraint schedulers.
            </p>

            {/* 3 Quick Stat Badges */}
            <div className="hero-stat-badges">
              <div className="stat-badge-item">
                <ShieldCheck size={16} color="#10b981" />
                <span><strong>45+</strong> Automated Unit Tests (100% Pass)</span>
              </div>
              <div className="stat-badge-item">
                <Server size={16} color="#6366f1" />
                <span><strong>Full-Stack</strong> Python & React 19</span>
              </div>
              <div className="stat-badge-item">
                <Database size={16} color="#06b6d4" />
                <span><strong>Production</strong> PostgreSQL Cloud Deployment</span>
              </div>
            </div>

            {/* Primary Hero Actions */}
            <div className="hero-actions" style={{ marginTop: '28px' }}>
              <a href="#flagship" className="btn btn-primary" id="hero-flagship-btn">
                Explore Flagship Project <ArrowRight size={16} />
              </a>

              <a 
                href="/resume.pdf" 
                download="Ezra_Lai_Kwang_Zhe_Resume.pdf"
                className="btn btn-accent-demo" 
                id="hero-resume-btn"
                title="Download PDF Resume"
              >
                <Download size={16} /> Download Resume / CV
              </a>

              <a 
                href="https://github.com/ezralaics" 
                target="_blank" 
                rel="noreferrer" 
                className="btn btn-secondary"
                id="hero-github-btn"
              >
                <GithubIcon size={16} /> GitHub Profile
              </a>

              <a href="#contact" className="btn btn-secondary" id="hero-contact-btn">
                <Mail size={16} /> Get In Touch
              </a>
            </div>
          </div>

          {/* Interactive Developer Terminal */}
          <div>
            <div className="terminal-card">
              <div className="terminal-header">
                <div className="terminal-dots">
                  <span className="t-dot t-red"></span>
                  <span className="t-dot t-yellow"></span>
                  <span className="t-dot t-green"></span>
                </div>
                <div className="terminal-title">ezra@laikwangzhe: ~ /production</div>
                <Terminal size={14} className="text-muted" />
              </div>

              {/* Terminal Navigation Tabs */}
              <div style={{ background: '#0e172a', padding: '8px 16px', display: 'flex', gap: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)', overflowX: 'auto' }}>
                <button 
                  onClick={() => setActiveTab('profile')}
                  style={{
                    background: activeTab === 'profile' ? '#1e293b' : 'transparent',
                    border: 'none',
                    color: activeTab === 'profile' ? '#38bdf8' : '#94a3b8',
                    padding: '4px 10px',
                    borderRadius: '4px',
                    fontSize: '0.78rem',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-code)',
                    whiteSpace: 'nowrap'
                  }}
                  id="term-tab-profile"
                >
                  ezra.profile()
                </button>
                <button 
                  onClick={() => setActiveTab('architecture')}
                  style={{
                    background: activeTab === 'architecture' ? '#1e293b' : 'transparent',
                    border: 'none',
                    color: activeTab === 'architecture' ? '#38bdf8' : '#94a3b8',
                    padding: '4px 10px',
                    borderRadius: '4px',
                    fontSize: '0.78rem',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-code)',
                    whiteSpace: 'nowrap'
                  }}
                  id="term-tab-architecture"
                >
                  ezra.architecture()
                </button>
                <button 
                  onClick={() => setActiveTab('metrics')}
                  style={{
                    background: activeTab === 'metrics' ? '#1e293b' : 'transparent',
                    border: 'none',
                    color: activeTab === 'metrics' ? '#38bdf8' : '#94a3b8',
                    padding: '4px 10px',
                    borderRadius: '4px',
                    fontSize: '0.78rem',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-code)',
                    whiteSpace: 'nowrap'
                  }}
                  id="term-tab-metrics"
                >
                  ezra.metrics()
                </button>
              </div>

              {/* Terminal Screen Body */}
              <div className="terminal-body">
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: '#cbd5e1', lineHeight: '1.6' }}>
                  {terminalOutputs[activeTab]}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

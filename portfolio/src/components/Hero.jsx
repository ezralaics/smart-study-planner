import React, { useState } from 'react';
import { ArrowRight, Mail, FileText, Terminal, CheckCircle2, Sparkles } from 'lucide-react';
import { GithubIcon } from './Icons';

export default function Hero() {
  const [activeTab, setActiveTab] = useState('profile');

  const terminalOutputs = {
    profile: `const developer = {
  name: "Ezra Lai (Lai Kwang Zhe)",
  targetRole: "Software Engineer / Full-Stack Developer",
  education: "Bachelor / Diploma in Information Technology",
  domain: "laikwangzhe.com",
  status: "🟢 Actively seeking Software Engineering opportunities",
  focus: ["Clean Architecture", "Algorithmic Schedulers", "RBAC Systems"]
};`,
    architecture: `// Engineering Principles Applied:
- Flask Application Factory & Decoupled Extensions
- Cryptographic Password Hashing (Backward-Compatible)
- Heuristic Constraint Scheduling (Zero Collisions)
- Strict RBAC Decorators (@role_required)
- Unified Jinja2 & Modern React UIs`,
    metrics: `// Project Portfolio Metrics:
- Flagship: Smart Study Planner (Enterprise Edition)
- Test Coverage: 8/8 Automated Suite Passing
- Users Handled: Students, Faculty Educators, Admins
- Algorithm: Multi-Factor Priority Heuristic Score (0-100)`
  };

  return (
    <section className="section hero-section" id="about">
      <div className="content-wrapper">
        <div className="hero-grid">
          <div>
            <div className="status-pill" style={{ marginBottom: '18px' }}>
              <span className="pulse-dot"></span>
              <span>Software Engineer & Full-Stack Developer</span>
            </div>

            <h1 className="hero-title">
              Engineering <span className="gradient-text">scalable web platforms</span> & intelligent algorithms.
            </h1>

            <p className="hero-desc">
              Hi, I’m <strong>Ezra Lai (Lai Kwang Zhe)</strong>. I design and build production-grade web systems with a focus on modular backend architectures, heuristic constraint-satisfaction algorithms, and high-performance user interfaces.
            </p>

            <div className="hero-actions">
              <a href="#flagship" className="btn btn-primary" id="hero-flagship-btn">
                Explore Flagship Project <ArrowRight size={16} />
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

          <div>
            <div className="terminal-card">
              <div className="terminal-header">
                <div className="terminal-dots">
                  <span className="t-dot t-red"></span>
                  <span className="t-dot t-yellow"></span>
                  <span className="t-dot t-green"></span>
                </div>
                <div className="terminal-title">ezra@laikwangzhe ~ zsh</div>
                <Terminal size={14} className="text-muted" />
              </div>

              <div style={{ background: '#0e172a', padding: '8px 16px', display: 'flex', gap: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
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
                    fontFamily: 'var(--font-code)'
                  }}
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
                    fontFamily: 'var(--font-code)'
                  }}
                >
                  ezra.principles()
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
                    fontFamily: 'var(--font-code)'
                  }}
                >
                  ezra.metrics()
                </button>
              </div>

              <div className="terminal-body">
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: '#cbd5e1' }}>
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

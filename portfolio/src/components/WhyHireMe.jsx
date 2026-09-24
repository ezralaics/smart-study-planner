import React from 'react';
import { Layers, ShieldCheck, Cpu, Rocket, CheckCircle2 } from 'lucide-react';

export default function WhyHireMe() {
  const pitchPoints = [
    {
      icon: <Layers size={28} color="#6366f1" />,
      title: 'Architectural Rigor Over Quick Hacks',
      description: 'I design software with modularity in mind. Instead of sprawling monolithic files, I leverage the Application Factory pattern, decoupled extensions, and domain Blueprints to ensure maintainability and testability.'
    },
    {
      icon: <Cpu size={28} color="#06b6d4" />,
      title: 'Algorithmic & Heuristic Problem Solving',
      description: 'I enjoy tackling complex computational challenges, such as multi-variable constraint satisfaction scheduling, priority scoring models, and mathematical interval overlap algorithms.'
    },
    {
      icon: <ShieldCheck size={28} color="#10b981" />,
      title: 'Security & Production-First Mindset',
      description: 'I treat security as a first-class citizen: implementing cryptographic Werkzeug password hashing with transparent backward-compatible auto-upgrades, strict role-based access decorators, and parameterized SQL queries.'
    },
    {
      icon: <Rocket size={28} color="#f59e0b" />,
      title: 'Full-Stack Ownership & Velocity',
      description: 'From relational database schema design (SQLAlchemy) to interactive frontends (React & Jinja2), I deliver end-to-end features with high velocity and comprehensive unit testing.'
    }
  ];

  return (
    <section className="section" id="why-me">
      <div className="content-wrapper">
        <div className="pitch-card">
          <span className="section-tag">// Recruiter & Engineering Lead Overview</span>
          <h2 className="section-title">Why Bring Ezra Onto Your Engineering Team?</h2>
          <p className="section-subtitle">
            A developer who bridges solid computer science fundamentals with modern full-stack development best practices.
          </p>

          <div className="pitch-grid">
            {pitchPoints.map((item, index) => (
              <div className="pitch-item" key={index}>
                <div className="pitch-icon">{item.icon}</div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-primary)' }}>
                  {item.title}
                </h3>
                <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

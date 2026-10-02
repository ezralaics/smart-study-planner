import React from 'react';
import { Layers, ShieldCheck, Database, Bot } from 'lucide-react';

export default function WhyHireMe() {
  const pitchPoints = [
    {
      icon: <Layers size={26} color="#6366f1" />,
      title: 'Architectural Modularity Over Quick Hacks',
      description: 'I design software with scalable boundaries. Rather than sprawling spaghetti scripts, I structure applications using the Application Factory pattern, decoupled extensions, and domain Blueprints that remain testable as codebases expand.'
    },
    {
      icon: <Database size={26} color="#06b6d4" />,
      title: 'Production Database & Zero-Downtime Migrations',
      description: 'I build persistence layers ready for enterprise workloads: PostgreSQL with UUID v4 primary keys, automated startup schema migrations, relational indexing, and ACID transaction safety.'
    },
    {
      icon: <Bot size={26} color="#a855f7" />,
      title: 'Modern AI Systems with Security by Design',
      description: 'I orchestrate multi-provider LLMs (Google Gemini & OpenRouter) using Bring-Your-Own-Key (BYOK) architectures with encrypted key handling and intelligent heuristic fallbacks that maintain system continuity.'
    },
    {
      icon: <ShieldCheck size={26} color="#10b981" />,
      title: '45+ Unit Tests & Production-First Verification',
      description: 'I treat automated verification as non-negotiable: every authentication path, role-based boundary, and scheduling algorithm is verified with a comprehensive unit test suite achieving a 100% pass rate.'
    }
  ];

  return (
    <section className="section" id="why-me">
      <div className="content-wrapper">
        <div className="pitch-card">
          <span className="section-tag">// Engineering Leadership Overview</span>
          <h2 className="section-title">Why Bring Ezra Onto Your Engineering Team?</h2>
          <p className="section-subtitle">
            A software engineer who bridges deep computer science fundamentals with modern production-grade full-stack delivery.
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

import React from 'react';
import { 
  Code, 
  Server, 
  Database, 
  ShieldCheck, 
  Bot,
  Smartphone,
  CheckCircle2 
} from 'lucide-react';

export default function Skills() {
  const skillCategories = [
    {
      title: 'Programming Languages',
      icon: <Code size={20} color="#6366f1" />,
      skills: ['Python 3.12+', 'JavaScript (ES6+)', 'SQL (PostgreSQL/SQLite)', 'Java (Core / OOP)', 'HTML5 / Modern CSS3']
    },
    {
      title: 'Backend & Systems Architecture',
      icon: <Server size={20} color="#06b6d4" />,
      skills: [
        'Flask Application Factory & Blueprints',
        'Role-Based Access Control (RBAC)',
        'Heuristic Constraint Scheduling',
        'RESTful API Gateway Design',
        'Asynchronous Worker Architecture',
        'Microservice Modular Monoliths'
      ]
    },
    {
      title: 'Database & Relational Modeling',
      icon: <Database size={20} color="#a855f7" />,
      skills: [
        'PostgreSQL UUID v4 Architecture',
        'Automated Zero-Downtime Schema Migrations',
        'SQLAlchemy ORM 2.0',
        'Relational Normalization & Cascades',
        'Connection Pooling & Index Tuning',
        'ACID Transactions & Data Integrity'
      ]
    },
    {
      title: 'AI & Multi-LLM Orchestration',
      icon: <Bot size={20} color="#f59e0b" />,
      skills: [
        'Google Gemini 2.5 API Integration',
        'OpenRouter Multi-LLM Gateway',
        'Encrypted Bring-Your-Own-Key (BYOK)',
        'Context Window & Prompt Engineering',
        'Vector Embeddings & Semantic Search',
        'Heuristic Graceful AI Fallbacks'
      ]
    },
    {
      title: 'Frontend & Mobile Engineering',
      icon: <Smartphone size={20} color="#10b981" />,
      skills: [
        'React 19 & Vite Tooling',
        'Progressive Web Apps (Native PWA)',
        'Service Worker Offline Timetable Caching',
        'Modern Responsive CSS & Glassmorphism',
        'Jinja2 Master Layout Inheritance',
        'Cross-Browser & Mobile Optimization'
      ]
    },
    {
      title: 'DevOps, Security & Verification',
      icon: <ShieldCheck size={20} color="#f43f5e" />,
      skills: [
        '45+ Automated Unit Tests (100% Pass Rate)',
        'Werkzeug Cryptographic Password Hashing',
        'Session Security (HttpOnly / SameSite)',
        'Render Cloud Deployment & PostgreSQL',
        'Vercel & Cloudflare Edge Hosting',
        'Git CI/CD Automated Pipelines'
      ]
    }
  ];

  return (
    <section className="section" id="skills">
      <div className="content-wrapper">
        <div className="section-header">
          <span className="section-tag">// Technical Competencies</span>
          <h2 className="section-title">Skills & Production Engineering Stack</h2>
          <p className="section-subtitle">
            Tools, technologies, and system design paradigms applied across enterprise full-stack deployments and cloud architectures.
          </p>
        </div>

        <div className="skills-container">
          {skillCategories.map((cat, idx) => (
            <div className="skill-category-card" key={idx}>
              <h3 className="skill-cat-title">
                {cat.icon} {cat.title}
              </h3>

              <div className="skill-chips">
                {cat.skills.map((skill, sIdx) => (
                  <span className="skill-chip" key={sIdx}>
                    <CheckCircle2 size={13} color="#10b981" /> {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

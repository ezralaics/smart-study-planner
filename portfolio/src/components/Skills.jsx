import React from 'react';
import { 
  Code, 
  Server, 
  Layout, 
  Database, 
  Terminal, 
  ShieldCheck, 
  GitBranch, 
  CheckCircle2 
} from 'lucide-react';

export default function Skills() {
  const skillCategories = [
    {
      title: 'Programming Languages',
      icon: <Code size={20} color="#6366f1" />,
      skills: ['Python 3.x', 'JavaScript (ES6+)', 'SQL', 'Java (Core / OOP)', 'C++', 'HTML5 / CSS3']
    },
    {
      title: 'Backend & Systems Architecture',
      icon: <Server size={20} color="#06b6d4" />,
      skills: [
        'Flask (Application Factory & Blueprints)',
        'RESTful API Design & OpenAPI',
        'SQLAlchemy ORM',
        'Role-Based Access Control (RBAC)',
        'Constraint Satisfaction Schedulers',
        'Node.js / Express'
      ]
    },
    {
      title: 'Frontend & UI Engineering',
      icon: <Layout size={20} color="#10b981" />,
      skills: [
        'React (Hooks, Context, State)',
        'Vite Tooling',
        'Modern Responsive CSS (Flexbox/Grid)',
        'Glassmorphism & Micro-animations',
        'Bootstrap 5',
        'Jinja2 Template Inheritance'
      ]
    },
    {
      title: 'Database & Data Modeling',
      icon: <Database size={20} color="#f59e0b" />,
      skills: [
        'SQLite & Query Optimization',
        'PostgreSQL',
        'Relational Database Normalization',
        'Foreign Key Cascades',
        'Index Tuning & Query Plans'
      ]
    },
    {
      title: 'DevOps, Tooling & Testing',
      icon: <Terminal size={20} color="#a855f7" />,
      skills: [
        'Git & GitHub Version Control',
        'Python Unittest & Pytest Suites',
        'Linux / Bash Shell Scripting',
        'Postman API Testing',
        'CI/CD Workflows',
        'Vercel Deployment'
      ]
    },
    {
      title: 'Software Security & Principles',
      icon: <ShieldCheck size={20} color="#f43f5e" />,
      skills: [
        'Werkzeug Password Hashing',
        'SQL Injection Defense (Parameterized ORM)',
        'Session Security & Cookies',
        'DRY & SOLID Principles',
        'Separation of Concerns',
        'Graceful Degradation'
      ]
    }
  ];

  return (
    <section className="section" id="skills">
      <div className="content-wrapper">
        <div className="section-header">
          <span className="section-tag">// Technical Competencies</span>
          <h2 className="section-title">Skills & Engineering Stack</h2>
          <p className="section-subtitle">
            Tools, technologies, and system design paradigms applied across enterprise and personal projects.
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

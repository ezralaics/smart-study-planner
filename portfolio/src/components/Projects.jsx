import React, { useState } from 'react';
import { 
  ExternalLink, 
  Terminal, 
  Database, 
  Network, 
  Cpu, 
  Bot, 
  Smartphone, 
  Sparkles, 
  KeyRound, 
  Play
} from 'lucide-react';
import { GithubIcon } from './Icons';
import { projectsData, projectCategories } from '../data/projects';

export default function Projects() {
  const [filter, setFilter] = useState('all');

  const getIcon = (iconName) => {
    switch (iconName) {
      case 'Sparkles':
        return <Sparkles size={22} color="#6366f1" />;
      case 'Network':
        return <Network size={22} color="#06b6d4" />;
      case 'Bot':
        return <Bot size={22} color="#a855f7" />;
      case 'Smartphone':
        return <Smartphone size={22} color="#10b981" />;
      case 'Cpu':
        return <Cpu size={22} color="#f59e0b" />;
      case 'Database':
        return <Database size={22} color="#38bdf8" />;
      default:
        return <Terminal size={22} color="#6366f1" />;
    }
  };

  const filteredProjects = filter === 'all' 
    ? projectsData 
    : projectsData.filter(p => p.category === filter);

  return (
    <section className="section" id="projects">
      <div className="content-wrapper">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-tag">// Engineering Portfolio</span>
          <h2 className="section-title">Technical Projects & System Architectures</h2>
          <p className="section-subtitle">
            A modular registry of full-stack platforms, distributed systems, algorithmic tools, and offline-first mobile web applications.
          </p>
        </div>

        {/* Category Filter Tabs */}
        <div className="showcase-tabs" style={{ marginBottom: '32px' }}>
          {projectCategories.map(cat => {
            const count = cat.id === 'all' 
              ? projectsData.length 
              : projectsData.filter(p => p.category === cat.id).length;

            return (
              <button 
                key={cat.id}
                className={`tab-btn ${filter === cat.id ? 'active' : ''}`}
                onClick={() => setFilter(cat.id)}
                id={`filter-btn-${cat.id}`}
              >
                {cat.label} ({count})
              </button>
            );
          })}
        </div>

        {/* Projects Grid */}
        <div className="projects-grid">
          {filteredProjects.map(proj => {
            const isInDev = proj.status === 'in-development';

            return (
              <div 
                className={`project-card ${isInDev ? 'project-card-dev' : ''}`} 
                key={proj.id}
                id={`project-card-${proj.id}`}
              >
                <div>
                  {/* Card Header & Status */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ padding: '8px', background: 'var(--bg-tertiary)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {getIcon(proj.iconName)}
                    </div>

                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <span className={`badge-pill ${isInDev ? 'badge-pill-dev' : 'badge-pill-live'}`}>
                        {proj.statusLabel}
                      </span>
                      <span className="project-category">{proj.categoryLabel}</span>
                    </div>
                  </div>

                  <h3 className="project-title">{proj.title}</h3>
                  <div style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: '8px' }}>
                    {proj.tagline}
                  </div>
                  <p className="project-desc">{proj.description}</p>

                  {/* Highlights Bullet Points */}
                  {proj.highlights && (
                    <ul className="project-highlights-list">
                      {proj.highlights.slice(0, 2).map((h, i) => (
                        <li key={i}>{h}</li>
                      ))}
                    </ul>
                  )}
                </div>

                <div>
                  {/* Metrics Badge */}
                  <div className="project-metrics-bar">
                    <code>{proj.metrics}</code>
                  </div>

                  {/* Tech Tags */}
                  <div className="tech-tags">
                    {proj.tags.map((t, idx) => (
                      <span className="tag" key={idx}>{t}</span>
                    ))}
                  </div>

                  {/* Action Buttons */}
                  <div className="project-card-actions">
                    {proj.liveUrl && (
                      <a 
                        href={proj.liveUrl} 
                        target="_blank" 
                        rel="noreferrer" 
                        className="btn btn-primary btn-sm"
                        style={{ flex: '1 1 auto' }}
                      >
                        <Play size={13} fill="currentColor" /> Live App <ExternalLink size={12} />
                      </a>
                    )}

                    {proj.demoUrl && (
                      <a 
                        href={proj.demoUrl} 
                        target="_blank" 
                        rel="noreferrer" 
                        className="btn btn-accent-demo btn-sm"
                        style={{ flex: '1 1 auto' }}
                      >
                        <KeyRound size={13} /> Demo <ExternalLink size={12} />
                      </a>
                    )}

                    <a 
                      href={proj.github} 
                      target="_blank" 
                      rel="noreferrer" 
                      className="btn btn-secondary btn-sm"
                      style={{ flex: '1 1 auto' }}
                    >
                      <GithubIcon size={14} /> GitHub <ExternalLink size={12} />
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

import React, { useState } from 'react';
import { ExternalLink, Terminal, Database, Network, Cpu } from 'lucide-react';
import { GithubIcon } from './Icons';

export default function Projects() {
  const [filter, setFilter] = useState('all');

  const projectsData = [
    {
      id: 'task-engine',
      title: 'Distributed Background Job & Queue Engine',
      category: 'systems',
      categoryLabel: 'Distributed Systems',
      description: 'A resilient asynchronous task processing worker built in Python with Redis-backed queueing, retry backoffs, and heartbeat health monitoring.',
      tags: ['Python', 'Redis', 'Concurrency', 'System Design', 'Docker'],
      github: 'https://github.com/ezralaics',
      icon: <Network size={22} color="#06b6d4" />
    },
    {
      id: 'graph-algo',
      title: 'Algorithmic Pathfinding & Network Visualizer',
      category: 'algorithms',
      categoryLabel: 'Algorithms & Data Structures',
      description: 'Interactive graph pathfinding platform demonstrating Dijkstra, A*, Breadth-First, and Depth-First algorithms with heuristic tuning and obstacle mazes.',
      tags: ['JavaScript (ES6+)', 'Graph Theory', 'A* Heuristics', 'Canvas API'],
      github: 'https://github.com/ezralaics',
      icon: <Cpu size={22} color="#6366f1" />
    },
    {
      id: 'enterprise-api',
      title: 'High-Throughput Enterprise REST API Gateway',
      category: 'backend',
      categoryLabel: 'Backend Engineering',
      description: 'Secure API service featuring JWT authentication, rate limiting, role authorization middleware, structured SQL logging, and Swagger OpenAPI documentation.',
      tags: ['Flask / Express', 'JWT Auth', 'PostgreSQL', 'Rate Limiting', 'OpenAPI'],
      github: 'https://github.com/ezralaics',
      icon: <Database size={22} color="#10b981" />
    }
  ];

  const filteredProjects = filter === 'all' 
    ? projectsData 
    : projectsData.filter(p => p.category === filter);

  return (
    <section className="section" id="projects">
      <div className="content-wrapper">
        <div className="section-header">
          <span className="section-tag">// Engineering Portfolio</span>
          <h2 className="section-title">Additional Technical Projects</h2>
          <p className="section-subtitle">
            A selection of software engineering projects exploring system design, concurrency, graph algorithms, and cloud APIs.
          </p>
        </div>

        {/* Category Filters */}
        <div className="showcase-tabs" style={{ marginBottom: '32px' }}>
          <button 
            className={`tab-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Work ({projectsData.length})
          </button>
          <button 
            className={`tab-btn ${filter === 'systems' ? 'active' : ''}`}
            onClick={() => setFilter('systems')}
          >
            Distributed Systems
          </button>
          <button 
            className={`tab-btn ${filter === 'algorithms' ? 'active' : ''}`}
            onClick={() => setFilter('algorithms')}
          >
            Algorithms
          </button>
          <button 
            className={`tab-btn ${filter === 'backend' ? 'active' : ''}`}
            onClick={() => setFilter('backend')}
          >
            Backend & APIs
          </button>
        </div>

        <div className="projects-grid">
          {filteredProjects.map(proj => (
            <div className="project-card" key={proj.id}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <div style={{ padding: '8px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                    {proj.icon}
                  </div>
                  <span className="project-category">{proj.categoryLabel}</span>
                </div>

                <h3 className="project-title">{proj.title}</h3>
                <p className="project-desc">{proj.description}</p>
              </div>

              <div>
                <div className="tech-tags">
                  {proj.tags.map((t, idx) => (
                    <span className="tag" key={idx}>{t}</span>
                  ))}
                </div>

                <a 
                  href={proj.github} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="btn btn-secondary btn-sm"
                  style={{ width: '100%' }}
                >
                  <GithubIcon size={14} /> View Code on GitHub <ExternalLink size={12} />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

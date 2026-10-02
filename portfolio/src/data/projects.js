export const projectsData = [
  {
    id: 'smart-study-planner',
    title: 'NextOmni OS (Smart Study Planner & Life Platform)',
    tagline: 'Multi-Tenant Institutional Academic Platform & Algorithmic Scheduler',
    category: 'full-stack',
    categoryLabel: 'Full-Stack & Cloud',
    status: 'featured',
    statusLabel: '🚀 Live on Render',
    description: 'NextOmni is an enterprise modular academic & life management platform featuring 3 institutional roles (Student, Educator, Admin), heuristic constraint-satisfaction scheduling, and BYOK AI knowledge base.',
    highlights: [
      'Flask Application Factory & 6 modular domain Blueprints',
      'PostgreSQL with UUID primary keys & automated schema migrations',
      'Google Gemini & OpenRouter AI integrations with encrypted client keys',
      'Native installable PWA with 72 automated unit tests (100% pass rate)'
    ],
    tags: ['Python 3.12', 'Flask Blueprints', 'PostgreSQL UUID', 'Google Gemini AI', 'PWA', '72 Unit Tests'],
    metrics: '72 Tests Passing | 3 Tier RBAC | <50ms API Latency',
    github: 'https://github.com/ezralaics/smart-study-planner',
    liveUrl: 'https://smart-study-planner-1-vozm.onrender.com',
    demoUrl: 'https://smart-study-planner-1-vozm.onrender.com/demo-login/student',
    iconName: 'Sparkles'
  },
  {
    id: 'task-engine',
    title: 'Distributed Background Job & Queue Engine',
    tagline: 'Fault-Tolerant Asynchronous Worker Architecture',
    category: 'systems-ai',
    categoryLabel: 'AI & Systems',
    status: 'production',
    statusLabel: 'Production Architecture',
    description: 'A resilient asynchronous task processing worker built in Python with Redis-backed queueing, dead-letter retries with exponential backoffs, and heartbeat health monitoring telemetry.',
    highlights: [
      'Reliable task persistence across unexpected worker restarts',
      'Dynamic concurrency worker pools with priority scheduling',
      'Prometheus-compatible health probe endpoints and system metrics'
    ],
    tags: ['Python', 'Redis', 'Concurrency', 'System Design', 'Docker'],
    metrics: 'Sub-millisecond Enqueue | Zero Task Loss',
    github: 'https://github.com/ezralaics',
    iconName: 'Network'
  },
  {
    id: 'omnilife-os',
    title: 'OmniLife Personal Intelligence OS',
    tagline: 'Multi-Modal Cognitive & Habit Intelligence Core',
    category: 'systems-ai',
    categoryLabel: 'AI & Systems',
    status: 'in-development',
    statusLabel: '⚡ In Development',
    description: 'Next-generation personal productivity core combining local-first vector memory, contextual habit tracking, and proactive daily briefing agents powered by LLMs.',
    highlights: [
      'Multi-agent orchestration for habit synthesis and cognitive reflection',
      'Local vector store for privacy-first semantic document retrieval',
      'Offline-capable event stream synchronizing with cloud endpoints'
    ],
    tags: ['Python / FastAPI', 'Vector Embeddings', 'Multi-Agent LLMs', 'Event Sourcing'],
    metrics: 'Active Engineering Phase',
    github: 'https://github.com/ezralaics',
    iconName: 'Bot'
  },
  {
    id: 'pwa-companion',
    title: 'Cross-Platform Native PWA Companion',
    tagline: 'Offline-First Academic Timetable & Push Alerts',
    category: 'mobile-pwa',
    categoryLabel: 'Mobile / PWA',
    status: 'in-development',
    statusLabel: '⚡ In Development',
    description: 'Progressive Web App client delivering installable desktop & mobile experiences, offline cache synchronization via IndexedDB, and automated class reminder Web Push alerts.',
    highlights: [
      'Service Worker lifecycle management with Cache-First strategy',
      'Instant timetable access even in zero-connectivity lecture halls',
      'Native Web Push notifications for impending assignment deadlines'
    ],
    tags: ['PWA', 'Service Workers', 'IndexedDB', 'Web Push API', 'React 19'],
    metrics: 'Lighthouse 100 PWA Score Target',
    github: 'https://github.com/ezralaics',
    iconName: 'Smartphone'
  },
  {
    id: 'graph-algo',
    title: 'Algorithmic Pathfinding & Network Visualizer',
    tagline: 'Interactive Heuristic Graph Theory Simulator',
    category: 'systems-ai',
    categoryLabel: 'AI & Systems',
    status: 'production',
    statusLabel: 'Interactive App',
    description: 'Interactive graph pathfinding platform demonstrating Dijkstra, A*, Breadth-First, and Depth-First algorithms with dynamic heuristic tuning, weighted terrains, and obstacle mazes.',
    highlights: [
      'Custom Manhattan and Euclidean heuristic weighting engines',
      'Real-time HTML5 Canvas render loop with 60 FPS animation control',
      'Randomized Prim and recursive division maze generation algorithms'
    ],
    tags: ['JavaScript (ES6+)', 'Graph Theory', 'A* Heuristics', 'Canvas API'],
    metrics: '60 FPS Canvas Rendering | 4 Pathfinding Algorithms',
    github: 'https://github.com/ezralaics',
    iconName: 'Cpu'
  },
  {
    id: 'enterprise-api',
    title: 'High-Throughput Enterprise REST API Gateway',
    tagline: 'Secure Microservice Gateway & Auth Layer',
    category: 'full-stack',
    categoryLabel: 'Full-Stack & Cloud',
    status: 'production',
    statusLabel: 'Production Architecture',
    description: 'Secure API service featuring cryptographic JWT authentication, sliding token refresh, token bucket rate limiting, role authorization middleware, and OpenAPI documentation.',
    highlights: [
      'Token bucket algorithm mitigating DDoS and noisy neighbors',
      'Parameterized query ORM layer eliminating SQL injection vectors',
      'Automated OpenAPI Swagger interactive test harness'
    ],
    tags: ['Python / Flask', 'JWT Auth', 'PostgreSQL', 'Rate Limiting', 'OpenAPI'],
    metrics: '99.9% Uptime Target | Zero Vulnerabilities',
    github: 'https://github.com/ezralaics',
    iconName: 'Database'
  }
];

export const projectCategories = [
  { id: 'all', label: 'All Projects' },
  { id: 'full-stack', label: 'Full-Stack' },
  { id: 'systems-ai', label: 'AI / Systems' },
  { id: 'mobile-pwa', label: 'Mobile / PWA' }
];

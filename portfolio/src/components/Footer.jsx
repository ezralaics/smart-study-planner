import React from 'react';
import { ArrowUp, Mail, Heart } from 'lucide-react';
import { GithubIcon } from './Icons';

export default function Footer() {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="site-footer">
      <div className="content-wrapper">
        <div className="footer-inner">
          <div>
            <div style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
              Ezra Lai <span style={{ color: 'var(--accent-cyan)' }}>•</span> laikwangzhe.com
            </div>
            <div className="footer-text" style={{ marginTop: '4px' }}>
              Software Engineer & Full-Stack Developer • Building scalable platforms & intelligent systems.
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <a 
              href="https://github.com/ezralaics" 
              target="_blank" 
              rel="noreferrer" 
              className="theme-toggle-btn"
              title="GitHub Profile"
            >
              <GithubIcon size={18} />
            </a>
            <a 
              href="mailto:kwangzhe.lai@gmail.com" 
              className="theme-toggle-btn"
              title="Email Ezra"
            >
              <Mail size={18} />
            </a>
            <button 
              onClick={scrollToTop} 
              className="theme-toggle-btn" 
              title="Scroll to Top"
              id="back-to-top-btn"
            >
              <ArrowUp size={18} />
            </button>
          </div>
        </div>

        <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          © {new Date().getFullYear()} Ezra Lai (Lai Kwang Zhe). All rights reserved. Designed & engineered for production.
        </div>
      </div>
    </footer>
  );
}

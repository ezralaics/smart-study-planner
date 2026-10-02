import React from 'react';
import { Sun, Moon, ArrowUpRight } from 'lucide-react';

export default function Navbar({ theme, toggleTheme }) {
  return (
    <header className="site-nav">
      <div className="content-wrapper">
        <div className="nav-inner">
          <a href="#" className="brand-logo" id="nav-brand-logo">
            <span className="brand-dot"></span>
            Ezra Lai
            <span className="brand-domain">laikwangzhe.com</span>
          </a>

          <ul className="nav-links">
            <li><a href="#about">About</a></li>
            <li><a href="#flagship">Flagship Project</a></li>
            <li><a href="#projects">Projects</a></li>
            <li><a href="#skills">Skills</a></li>
            <li><a href="#why-me">Why Me</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>

          <div className="nav-actions">
            <div className="status-pill d-none-sm">
              <span className="pulse-dot"></span>
              <span>Available for Hire</span>
            </div>

            <button 
              className="theme-toggle-btn" 
              onClick={toggleTheme} 
              aria-label="Toggle Dark/Light Mode"
              id="theme-toggle-btn"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <a href="#contact" className="btn btn-primary btn-sm" id="nav-hire-btn">
              Let's Talk <ArrowUpRight size={15} />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}

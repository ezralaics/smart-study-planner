import React, { useState } from 'react';
import { Mail, Globe, Send, Check, Copy } from 'lucide-react';
import { GithubIcon } from './Icons';

export default function Contact() {
  const [copied, setCopied] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });

  const contactEmail = 'kwangzhe.lai@gmail.com';

  const copyEmail = () => {
    navigator.clipboard.writeText(contactEmail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.message) return;
    setSubmitted(true);
    // Opens default mail client as reliable fallback
    window.location.href = `mailto:${contactEmail}?subject=Contact from ${encodeURIComponent(formData.name)}&body=${encodeURIComponent(formData.message + '\n\nFrom: ' + formData.email)}`;
  };

  return (
    <section className="section" id="contact">
      <div className="content-wrapper">
        <div className="section-header">
          <span className="section-tag">// Get In Touch</span>
          <h2 className="section-title">Let's Build Something Great Together</h2>
          <p className="section-subtitle">
            Whether you have an engineering role opening, a project opportunity, or want to discuss system architecture, my inbox is always open.
          </p>
        </div>

        <div className="contact-grid">
          {/* Contact Details Card */}
          <div className="contact-info-card">
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '12px' }}>
              Direct Channels
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '24px' }}>
              Feel free to reach out via email or connect with me on GitHub. I typically respond within 24 hours.
            </p>

            <div className="contact-links">
              <div className="contact-item" style={{ cursor: 'pointer' }} onClick={copyEmail}>
                <div style={{ padding: '8px', background: 'rgba(99, 102, 241, 0.15)', borderRadius: '8px' }}>
                  <Mail size={20} color="#6366f1" />
                </div>
                <div style={{ flexGrow: 1 }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Email Address</div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{contactEmail}</div>
                </div>
                <button 
                  type="button"
                  style={{ background: 'transparent', border: 'none', color: copied ? '#10b981' : 'var(--text-secondary)', cursor: 'pointer', padding: '6px' }}
                  title="Copy email to clipboard"
                >
                  {copied ? <Check size={18} /> : <Copy size={18} />}
                </button>
              </div>

              <a 
                href="https://github.com/ezralaics" 
                target="_blank" 
                rel="noreferrer" 
                className="contact-item"
              >
                <div style={{ padding: '8px', background: 'rgba(6, 182, 212, 0.15)', borderRadius: '8px' }}>
                  <GithubIcon size={20} color="#06b6d4" />
                </div>
                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>GitHub Profile</div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>github.com/ezralaics</div>
                </div>
              </a>

              <a 
                href="https://laikwangzhe.com" 
                target="_blank" 
                rel="noreferrer" 
                className="contact-item"
              >
                <div style={{ padding: '8px', background: 'rgba(16, 185, 129, 0.15)', borderRadius: '8px' }}>
                  <Globe size={20} color="#10b981" />
                </div>
                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Portfolio Domain</div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>laikwangzhe.com</div>
                </div>
              </a>
            </div>

            <div style={{ marginTop: '32px', padding: '16px', background: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981', fontWeight: 600, fontSize: '0.88rem' }}>
                <span className="pulse-dot"></span>
                <span>Active Availability: Immediately available</span>
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px', marginBottom: 0 }}>
                Open to Full-Stack Developer, Backend Engineer, and Software Engineering positions.
              </p>
            </div>
          </div>

          {/* Interactive Message Form */}
          <form className="contact-form" onSubmit={handleSubmit} id="contact-form">
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '20px' }}>
              Send a Direct Message
            </h3>

            {submitted ? (
              <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
                <Check size={32} color="#10b981" style={{ margin: '0 auto 10px' }} />
                <h4 style={{ color: '#10b981', fontWeight: 700 }}>Thank you for reaching out!</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '6px 0 0' }}>
                  Your email client has been prepared. I will review your message promptly.
                </p>
              </div>
            ) : (
              <>
                <div className="form-group">
                  <label className="form-label" htmlFor="contact-name">YOUR NAME / COMPANY</label>
                  <input 
                    type="text" 
                    id="contact-name" 
                    className="form-control" 
                    placeholder="e.g. Alex (Engineering Manager at TechCorp)" 
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required 
                  />
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="contact-email">YOUR EMAIL</label>
                  <input 
                    type="email" 
                    id="contact-email" 
                    className="form-control" 
                    placeholder="e.g. alex@company.com" 
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required 
                  />
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="contact-message">MESSAGE</label>
                  <textarea 
                    id="contact-message" 
                    rows={4} 
                    className="form-control" 
                    placeholder="Hi Ezra, I reviewed your Smart Study Planner architecture and would like to discuss an opportunity..."
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    required
                  ></textarea>
                </div>

                <button type="submit" className="btn btn-primary" style={{ width: '100%' }} id="contact-submit-btn">
                  <Send size={16} /> Send Message via Email
                </button>
              </>
            )}
          </form>
        </div>
      </div>
    </section>
  );
}

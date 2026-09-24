import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import FlagshipProject from './components/FlagshipProject';
import Projects from './components/Projects';
import Skills from './components/Skills';
import WhyHireMe from './components/WhyHireMe';
import Contact from './components/Contact';
import Footer from './components/Footer';

export default function App() {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="app-container">
      {/* Dynamic Ambient Glow & Grid Layer */}
      <div className="bg-ambient-layer">
        <div className="ambient-orb orb-1"></div>
        <div className="ambient-orb orb-2"></div>
      </div>
      <div className="bg-grid-pattern"></div>

      {/* Main Content */}
      <Navbar theme={theme} toggleTheme={toggleTheme} />
      <main>
        <Hero />
        <FlagshipProject />
        <Projects />
        <Skills />
        <WhyHireMe />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}

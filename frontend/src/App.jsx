// src/App.jsx
import React, { useState } from 'react';
import Header from './components/layout/Header';
import Hero from './components/sections/Hero';
import About from './components/sections/About';
import Features from './components/sections/Features';
import HowItWorks from './components/sections/HowItWorks';
import TechStack from './components/sections/TechStack';
import WhyChoose from './components/sections/WhyChoose';
import Demo from './components/sections/Demo';
import Contact from './components/sections/Contact';
import Footer from './components/layout/Footer';

function App() {
  // Shared reportId for Hero + Demo
  const [reportId, setReportId] = useState(null);

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        {/* Hero uploads and calls setReportId when done */}
        <Hero onReportProcessed={setReportId} />

        <About />
        <Features />
        <Demo reportId={reportId} onReportProcessed={setReportId} />
        <HowItWorks />
        <TechStack />
        <WhyChoose />

        {/* Demo uses same reportId and can also upload */}
        

        <Contact />
      </main>
      <Footer />
    </div>
  );
}

export default App;

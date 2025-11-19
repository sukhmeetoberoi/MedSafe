import React from 'react';
import Header from './components/layout/Header';
import Hero from './components/sections/Hero';
import About from './components/sections/About';
import Features from './components/sections/Features';
import HowItWorks from './components/sections/HowItWorks';
import TechStack from './components/sections/TechStack';
import WhyChoose from './components/sections/WhyChoose';
import InteractiveDemo from './components/sections/InteractiveDemo';
import Contact from './components/sections/Contact';
import Footer from './components/layout/Footer';

function App() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <Hero />
        <About />
        <Features />
        <HowItWorks />
        <TechStack />
        <WhyChoose />
        <Demo />
        <InteractiveDemo />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}

export default App;
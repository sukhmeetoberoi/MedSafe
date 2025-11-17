import React from 'react';
import { motion } from 'framer-motion';
import { Brain, FileText, Users, Eye, Zap, Shield } from 'lucide-react';

const About = () => {
  const technologies = [
    {
      icon: FileText,
      title: 'OCR Technology',
      description: 'Extract text from medical reports, scans, and PDFs with 99% accuracy',
      color: 'text-blue-600'
    },
    {
      icon: Brain,
      title: 'Natural Language Processing',
      description: 'Understand medical terminology and extract key clinical information',
      color: 'text-purple-600'
    },
    {
      icon: Zap,
      title: 'Large Language Models',
      description: 'Powered by Google Gemini Pro and GPT for intelligent summarization',
      color: 'text-yellow-600'
    }
  ];

  const summaryTypes = [
    {
      icon: Users,
      title: 'Clinician-Oriented Summary',
      description: 'Detailed, technical summaries with medical terminology, ICD codes, and clinical insights for healthcare professionals.',
      features: ['Medical terminology', 'Drug interactions', 'Lab results analysis', 'Clinical recommendations']
    },
    {
      icon: Eye,
      title: 'Patient-Friendly Summary',
      description: 'Simple, easy-to-understand summaries in plain language that patients can comprehend without medical knowledge.',
      features: ['Plain language', 'Action items', 'Next steps', 'Warning signs']
    }
  ];

  return (
    <section id="about" className="py-20 bg-light-gradient-bg">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <motion.h2
            className="text-4xl md:text-5xl font-bold text-dark-blue-gray mb-6"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            viewport={{ once: true }}
          >
            About MedSummarize
          </motion.h2>
          <motion.p
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            Transforming complex medical reports into clear, actionable insights using cutting-edge AI technology.
            Our platform bridges the gap between medical documentation and human understanding.
          </motion.p>
        </motion.div>

        {/* Technology Pipeline */}
        <motion.div
          className="mb-20"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-3xl font-bold text-center text-dark-blue-gray mb-12">
            Our Technology Pipeline
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {technologies.map((tech, index) => (
              <motion.div
                key={tech.title}
                className="card text-center group"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                viewport={{ once: true }}
                whileHover={{ y: -10 }}
              >
                <motion.div
                  className={`w-20 h-20 mx-auto mb-6 bg-white rounded-full flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300`}
                  whileHover={{ scale: 1.1 }}
                >
                  <tech.icon className={`w-10 h-10 ${tech.color}`} />
                </motion.div>
                <h4 className="text-xl font-semibold text-dark-blue-gray mb-4">
                  {tech.title}
                </h4>
                <p className="text-gray-600 leading-relaxed">
                  {tech.description}
                </p>
              </motion.div>
            ))}
          </div>

          {/* Process Flow */}
          <motion.div
            className="mt-16 relative"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            <div className="hidden md:block absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-medical-blue via-teal-accent to-medical-blue transform -translate-y-1/2"></div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {['Upload Report', 'OCR Processing', 'AI Analysis', 'Dual Summaries'].map((step, index) => (
                <motion.div
                  key={step}
                  className="relative z-10"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                >
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-4 bg-white rounded-full flex items-center justify-center shadow-lg border-4 border-medical-blue">
                      <span className="text-xl font-bold text-medical-blue">{index + 1}</span>
                    </div>
                    <h5 className="font-semibold text-dark-blue-gray">{step}</h5>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>

        {/* Dual Summary Types */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-12"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="col-span-full text-3xl font-bold text-center text-dark-blue-gray mb-8">
            Two Types of Smart Summaries
          </h3>

          {summaryTypes.map((summary, index) => (
            <motion.div
              key={summary.title}
              className={`card ${index === 0 ? 'border-l-4 border-medical-blue' : 'border-l-4 border-teal-accent'}`}
              initial={{ opacity: 0, x: index === 0 ? -50 : 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.1 * index }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-full ${index === 0 ? 'bg-blue-100' : 'bg-teal-100'}`}>
                  <summary.icon className={`w-6 h-6 ${index === 0 ? 'text-blue-600' : 'text-teal-600'}`} />
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-dark-blue-gray mb-4">
                    {summary.title}
                  </h4>
                  <p className="text-gray-600 mb-6 leading-relaxed">
                    {summary.description}
                  </p>
                  <div className="space-y-3">
                    {summary.features.map((feature) => (
                      <div key={feature} className="flex items-center space-x-2">
                        <Shield className="w-4 h-4 text-green-500 flex-shrink-0" />
                        <span className="text-sm text-gray-700">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
            <h4 className="text-2xl font-semibold text-dark-blue-gray mb-6">
              Trusted by Healthcare Professionals
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {[
                ['HIPAA', 'Compliant'],
                ['99%', 'Accuracy'],
                ['2M+', 'Reports'],
                ['24/7', 'Available']
              ].map(([value, label], index) => (
                <motion.div
                  key={value}
                  className="text-center"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                >
                  <div className="text-3xl font-bold text-medical-blue mb-2">{value}</div>
                  <div className="text-sm text-gray-600">{label}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default About;
import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Shield, Languages, MessageSquare, FileText, Zap } from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Summaries',
      description: 'Advanced extractive and abstractive summarization using state-of-the-art language models',
      color: 'bg-blue-100 text-blue-600',
      features: ['Extract key information', 'Generate human-readable summaries', 'Maintain medical accuracy', 'Context-aware processing']
    },
    {
      icon: Shield,
      title: 'PHI Redaction',
      description: 'HIPAA and GDPR compliant privacy protection with automatic PHI detection and removal',
      color: 'bg-green-100 text-green-600',
      features: ['Automated PHI detection', 'HIPAA compliant', 'GDPR ready', 'Audit logging']
    },
    {
      icon: Languages,
      title: 'Multilingual Support',
      description: 'Summarize medical reports in multiple languages for diverse patient populations',
      color: 'bg-purple-100 text-purple-600',
      features: ['50+ languages', 'Cultural sensitivity', 'Accurate medical translation', 'Localization support']
    },
    {
      icon: MessageSquare,
      title: 'Interactive Q&A',
      description: 'Ask questions about your medical reports and get instant AI-powered answers',
      color: 'bg-yellow-100 text-yellow-600',
      features: ['Natural language queries', 'Context-aware answers', 'Medical validation', 'Real-time responses']
    },
    {
      icon: FileText,
      title: 'Multiple File Formats',
      description: 'Upload PDFs, scanned documents, images, and digital medical records seamlessly',
      color: 'bg-red-100 text-red-600',
      features: ['PDF processing', 'Image OCR', 'Handwriting recognition', 'Batch uploads']
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Get comprehensive summaries in seconds, not hours or days',
      color: 'bg-indigo-100 text-indigo-600',
      features: ['2-minute processing', 'Real-time updates', 'Queue management', 'Priority processing']
    }
  ];

  return (
    <section id="features" className="py-20 bg-white">
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
            Key Features
          </motion.h2>
          <motion.p
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            Discover the powerful features that make MedSummarize the leading choice for medical report analysis and summarization.
          </motion.p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="group"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              viewport={{ once: true }}
              whileHover={{ y: -10 }}
            >
              <div className="card h-full border-0 hover:shadow-2xl transition-all duration-300">
                {/* Icon */}
                <motion.div
                  className={`w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center ${feature.color} group-hover:scale-110 transition-transform duration-300`}
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  <feature.icon className="w-10 h-10" />
                </motion.div>

                {/* Content */}
                <div className="text-center">
                  <h3 className="text-xl font-semibold text-dark-blue-gray mb-4 group-hover:text-medical-blue transition-colors duration-300">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-6 leading-relaxed">
                    {feature.description}
                  </p>

                  {/* Feature List */}
                  <div className="space-y-2">
                    {feature.features.map((item, itemIndex) => (
                      <motion.div
                        key={item}
                        className="flex items-center justify-center space-x-2 text-sm text-gray-500"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: 0.1 * itemIndex }}
                        viewport={{ once: true }}
                      >
                        <div className="w-1 h-1 bg-teal-accent rounded-full"></div>
                        <span>{item}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Hover Effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-medical-blue/5 to-teal-accent/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom Stats */}
        <motion.div
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          {[
            ['50+', 'Languages Supported'],
            ['99.9%', 'Uptime SLA'],
            ['<2min', 'Processing Time'],
            ['24/7', 'Support Available']
          ].map(([value, label], index) => (
            <motion.div
              key={value}
              className="text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.1 }}
            >
              <div className="text-4xl font-bold text-medical-blue mb-2">{value}</div>
              <div className="text-sm text-gray-600 font-medium">{label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Call to Action */}
        <motion.div
          className="mt-16 text-center bg-gradient-to-r from-medical-blue to-teal-accent rounded-2xl p-8 text-white"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-2xl font-bold mb-4">
            Ready to Experience the Power of AI?
          </h3>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Join thousands of healthcare professionals who are already saving time and improving patient care with MedSummarize.
          </p>
          <motion.button
            className="bg-white text-medical-blue font-semibold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors duration-300"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Start Free Trial
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
};

export default Features;
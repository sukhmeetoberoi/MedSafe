import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Scan, Shield, Brain, FileCheck, MessageSquare, ChevronRight, ChevronLeft } from 'lucide-react';

const HowItWorks = () => {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      id: 1,
      icon: Upload,
      title: 'Upload Report',
      description: 'Upload your medical report in any format - PDF, image, or scanned document.',
      details: [
        'Drag and drop or click to upload',
        'Supports PDF, JPG, PNG, TIFF formats',
        'Secure encrypted transmission',
        'Files processed immediately'
      ],
      color: 'bg-blue-500'
    },
    {
      id: 2,
      icon: Scan,
      title: 'OCR Processing',
      description: 'Our advanced OCR technology extracts and digitizes text from your documents.',
      details: [
        '99%+ accuracy for printed text',
        'Handwriting recognition support',
        'Multi-language text extraction',
        'Preserves document structure'
      ],
      color: 'bg-purple-500'
    },
    {
      id: 3,
      icon: Shield,
      title: 'PHI Redaction',
      description: 'Automatically detect and redact Protected Health Information for privacy compliance.',
      details: [
        'HIPAA compliant redaction',
        'Removes names, addresses, IDs',
        'Maintains medical context',
        'Audit trail for compliance'
      ],
      color: 'bg-green-500'
    },
    {
      id: 4,
      icon: Brain,
      title: 'Information Extraction',
      description: 'AI-powered analysis identifies key medical information and clinical data.',
      details: [
        'Medical entity recognition',
        'Drug interaction analysis',
        'Lab result interpretation',
        'Clinical timeline creation'
      ],
      color: 'bg-yellow-500'
    },
    {
      id: 5,
      icon: FileCheck,
      title: 'AI Summary',
      description: 'Generate comprehensive summaries in both clinical and patient-friendly formats.',
      details: [
        'Clinician-oriented summary',
        'Patient-friendly explanation',
        'Key findings highlight',
        'Actionable recommendations'
      ],
      color: 'bg-red-500'
    },
    {
      id: 6,
      icon: MessageSquare,
      title: 'Interactive Q&A',
      description: 'Ask questions about your report and get instant AI-powered answers.',
      details: [
        'Natural language queries',
        'Context-aware responses',
        'Medical accuracy validation',
        'Unlimited follow-up questions'
      ],
      color: 'bg-indigo-500'
    }
  ];

  const nextStep = () => {
    setActiveStep((prev) => (prev + 1) % steps.length);
  };

  const prevStep = () => {
    setActiveStep((prev) => (prev - 1 + steps.length) % steps.length);
  };

  return (
    <section id="how-it-works" className="py-20 bg-light-gradient-bg">
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
            How It Works
          </motion.h2>
          <motion.p
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            From document upload to AI-powered insights, our streamlined process transforms complex medical reports into clear, actionable information in just minutes.
          </motion.p>
        </motion.div>

        {/* Desktop View - Horizontal Flow */}
        <div className="hidden lg:block">
          {/* Progress Line */}
          <div className="relative mb-12">
            <div className="absolute top-8 left-0 right-0 h-1 bg-gray-300 rounded-full"></div>
            <motion.div
              className="absolute top-8 left-0 h-1 bg-gradient-to-r from-medical-blue to-teal-accent rounded-full"
              initial={{ width: '0%' }}
              whileInView={{ width: `${((activeStep + 1) / steps.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            ></motion.div>

            {/* Step Indicators */}
            <div className="relative flex justify-between">
              {steps.map((step, index) => (
                <motion.button
                  key={step.id}
                  className="relative z-10"
                  onClick={() => setActiveStep(index)}
                  initial={{ scale: 0.8, opacity: 0 }}
                  whileInView={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                  whileHover={{ scale: 1.2 }}
                >
                  <div className={`w-16 h-16 rounded-full ${step.color} text-white flex items-center justify-center font-bold text-lg shadow-lg ${
                    index === activeStep ? 'ring-4 ring-white ring-offset-4 ring-offset-gray-100' : ''
                  }`}>
                    {step.id}
                  </div>
                  <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap text-sm font-medium text-dark-blue-gray">
                    {step.title}
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Active Step Details */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeStep}
              className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mt-20"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.5 }}
            >
              {/* Left - Icon and Title */}
              <div className="text-center lg:text-left">
                <motion.div
                  className={`w-32 h-32 mx-auto lg:mx-0 rounded-full ${steps[activeStep].color} text-white flex items-center justify-center mb-6 shadow-xl`}
                  initial={{ scale: 0.8, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ duration: 0.6 }}
                >
                  <steps[activeStep].icon className="w-16 h-16" />
                </motion.div>
                <h3 className="text-3xl font-bold text-dark-blue-gray mb-4">
                  {steps[activeStep].title}
                </h3>
                <p className="text-xl text-gray-600 leading-relaxed">
                  {steps[activeStep].description}
                </p>
              </div>

              {/* Right - Details List */}
              <div className="bg-white rounded-2xl p-8 shadow-lg">
                <h4 className="font-semibold text-dark-blue-gray mb-4">Key Features:</h4>
                <div className="space-y-3">
                  {steps[activeStep].details.map((detail, index) => (
                    <motion.div
                      key={detail}
                      className="flex items-center space-x-3"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4, delay: 0.1 * index }}
                    >
                      <div className="w-2 h-2 bg-teal-accent rounded-full flex-shrink-0"></div>
                      <span className="text-gray-700">{detail}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex justify-center space-x-4 mt-12">
            <button
              onClick={prevStep}
              className="flex items-center space-x-2 px-6 py-3 bg-white text-medical-blue rounded-lg shadow-md hover:shadow-lg transition-all duration-300"
            >
              <ChevronLeft className="w-5 h-5" />
              <span>Previous</span>
            </button>
            <button
              onClick={nextStep}
              className="flex items-center space-x-2 px-6 py-3 bg-medical-blue text-white rounded-lg shadow-md hover:shadow-lg transition-all duration-300"
            >
              <span>Next</span>
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Mobile View - Vertical Cards */}
        <div className="lg:hidden">
          <div className="space-y-8">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                className={`card border-l-4 ${index === activeStep ? 'border-medical-blue' : 'border-gray-300'}`}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                viewport={{ once: true }}
                onClick={() => setActiveStep(index)}
              >
                <div className="flex items-start space-x-4">
                  <div className={`w-12 h-12 rounded-full ${step.color} text-white flex items-center justify-center flex-shrink-0`}>
                    <step.icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-dark-blue-gray mb-2">
                      {step.id}. {step.title}
                    </h3>
                    <p className="text-gray-600 mb-4">{step.description}</p>
                    <div className="space-y-2">
                      {step.details.map((detail) => (
                        <div key={detail} className="flex items-center space-x-2 text-sm text-gray-500">
                          <div className="w-1 h-1 bg-teal-accent rounded-full"></div>
                          <span>{detail}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Process Summary */}
        <motion.div
          className="mt-20 text-center"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
            <h3 className="text-2xl font-semibold text-dark-blue-gray mb-4">
              Complete Processing in Under 2 Minutes
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              From the moment you upload your medical report to receiving comprehensive AI-powered summaries,
              our streamlined process ensures you get the insights you need quickly and securely.
            </p>
            <div className="mt-6 flex justify-center items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-green-500" />
                <span className="text-sm text-gray-600">100% Secure</span>
              </div>
              <div className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-blue-500" />
                <span className="text-sm text-gray-600">AI-Powered</span>
              </div>
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-5 h-5 text-purple-500" />
                <span className="text-sm text-gray-600">Interactive</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks;
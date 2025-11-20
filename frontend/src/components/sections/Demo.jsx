import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Download, Eye, EyeOff, Play, Pause, RotateCcw, ChevronRight } from 'lucide-react';

const Demo = () => {
  const [activeView, setActiveView] = useState('clinician');
  const [isPlaying, setIsPlaying] = useState(false);

  const sampleReports = [
    {
      id: 1,
      title: 'Cardiology Consultation Report',
      type: 'PDF',
      pages: 4,
      size: '2.3 MB',
      date: '2024-01-15'
    },
    {
      id: 2,
      title: 'Blood Test Results',
      type: 'PDF',
      pages: 2,
      size: '856 KB',
      date: '2024-01-10'
    },
    {
      id: 3,
      title: 'Radiology MRI Scan',
      type: 'Image',
      pages: 1,
      size: '4.1 MB',
      date: '2024-01-08'
    }
  ];

  const summaries = {
    clinician: {
      title: 'Clinician-Oriented Summary',
      content: `
        <div class="space-y-4">
          <div>
            <h4 class="font-bold text-blue-600 mb-2">PATIENT INFORMATION</h4>
            <p>58-year-old male, hypertension (controlled), type 2 diabetes mellitus</p>
          </div>

          <div>
            <h4 class="font-bold text-blue-600 mb-2">KEY FINDINGS</h4>
            <ul class="list-disc list-inside space-y-1">
              <li>Echocardiogram: LVEF 45% (mildly reduced)</li>
              <li>Laboratory: HbA1c 8.2% (elevated), Creatinine 1.4 mg/dL</li>
              <li>ECG: Sinus rhythm, occasional PVCs</li>
              <li>Blood Pressure: 142/88 mmHg (elevated)</li>
            </ul>
          </div>

          <div>
            <h4 class="font-bold text-blue-600 mb-2">RECOMMENDATIONS</h4>
            <ul class="list-disc list-inside space-y-1">
              <li>Optimize antihypertensive regimen</li>
              <li>Intensify diabetes management</li>
              <li>Cardiology follow-up in 3 months</li>
              <li>Consider cardiac MRI for further evaluation</li>
            </ul>
          </div>

          <div>
            <h4 class="font-bold text-blue-600 mb-2">MEDICATIONS</h4>
            <p>Lisinopril 10mg daily, Metformin 500mg BID, Atorvastatin 20mg daily</p>
          </div>
        </div>
      `
    },
    patient: {
      title: 'Patient-Friendly Summary',
      content: `
        <div class="space-y-4">
          <div>
            <h4 class="font-bold text-green-600 mb-2">What We Found</h4>
            <p>Your heart is working, but not as strongly as it should. Your blood sugar and blood pressure are higher than we'd like to see.</p>
          </div>

          <div>
            <h4 class="font-bold text-green-600 mb-2">What This Means</h4>
            <p>These results are manageable with the right treatment plan. Your doctor wants to keep a close eye on your heart health and help you better control your diabetes.</p>
          </div>

          <div>
            <h4 class="font-bold text-green-600 mb-2">Next Steps</h4>
            <ul class="list-disc list-inside space-y-1">
              <li>Continue taking your medications as prescribed</li>
              <li>Follow a heart-healthy diet low in salt</li>
              <li>Exercise for 30 minutes, 5 days a week</li>
              <li>Check your blood sugar regularly</li>
              <li>See your heart doctor again in 3 months</li>
            </ul>
          </div>

          <div>
            <h4 class="font-bold text-green-600 mb-2">When to Call Your Doctor</h4>
            <p>Call right away if you have chest pain, shortness of breath, or feel faint. Call your regular doctor if your blood sugar readings are consistently high.</p>
          </div>
        </div>
      `
    }
  };

  const features = [
    {
      icon: Eye,
      title: 'Before & After View',
      description: 'See the original report side-by-side with the AI summary'
    },
    {
      icon: Download,
      title: 'Download Options',
      description: 'Export summaries as PDF, Word, or share via secure link'
    },
    {
      icon: RotateCcw,
      title: 'Multiple Formats',
      description: 'Clinician and patient-friendly versions of the same report'
    }
  ];

  const toggleDemo = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <section id="demo" className="py-20 bg-white">
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
            See MedSummarize in Action
          </motion.h2>
          <motion.p
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            Experience the power of AI-driven medical report analysis. Upload a report, watch it process in real-time, and see comprehensive summaries generated instantly.
          </motion.p>
        </motion.div>

        {/* Interactive Demo Area */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          {/* Upload Area */}
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-dark-blue-gray mb-6">Upload Your Report</h3>

            {/* Upload Interface */}
            <motion.div
              className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-medical-blue transition-colors duration-300 bg-light-blue-bg/50"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Upload className="w-16 h-16 text-medical-blue mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-dark-blue-gray mb-2">
                Drop files here or click to upload
              </h4>
              <p className="text-gray-600 mb-4">
                Supports PDF, JPG, PNG, TIFF up to 10MB
              </p>
              <button className="btn-secondary">
                Choose Files
              </button>
            </motion.div>

            {/* Sample Reports */}
            <div>
              <h4 className="font-semibold text-dark-blue-gray mb-3">Sample Reports:</h4>
              <div className="space-y-2">
                {sampleReports.map((report) => (
                  <motion.div
                    key={report.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200 cursor-pointer"
                    whileHover={{ x: 5 }}
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="w-5 h-5 text-medical-blue" />
                      <div>
                        <div className="font-medium text-dark-blue-gray">{report.title}</div>
                        <div className="text-sm text-gray-500">
                          {report.type} • {report.pages} pages • {report.size}
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Processing Status */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-3 mb-3">
                <motion.div
                  className="w-4 h-4 bg-blue-500 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                ></motion.div>
                <span className="text-blue-800 font-semibold">Processing Report...</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <motion.div
                  className="bg-blue-500 h-2 rounded-full"
                  initial={{ width: '0%' }}
                  animate={{ width: '75%' }}
                  transition={{ duration: 2 }}
                ></motion.div>
              </div>
              <div className="mt-2 text-sm text-blue-700">
                OCR → PHI Redaction → Analysis → Summary Generation
              </div>
            </div>
          </div>

          {/* Summary Display */}
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-dark-blue-gray mb-6">Generated Summary</h3>

            {/* View Toggle */}
            <div className="flex space-x-2 mb-6">
              <button
                onClick={() => setActiveView('clinician')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 ${
                  activeView === 'clinician'
                    ? 'bg-medical-blue text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Clinician View
              </button>
              <button
                onClick={() => setActiveView('patient')}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 ${
                  activeView === 'patient'
                    ? 'bg-teal-accent text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Patient View
              </button>
            </div>

            {/* Summary Content */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeView}
                className="bg-white border border-gray-200 rounded-xl p-6 shadow-lg"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-semibold text-dark-blue-gray">
                    {summaries[activeView].title}
                  </h4>
                  <div className="flex space-x-2">
                    <button className="p-2 text-gray-500 hover:text-medical-blue transition-colors duration-200">
                      <Download className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-500 hover:text-medical-blue transition-colors duration-200">
                      <Eye className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                <div
                  className="prose prose-sm max-w-none text-gray-700"
                  dangerouslySetInnerHTML={{ __html: summaries[activeView].content }}
                ></div>
              </motion.div>
            </AnimatePresence>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button className="btn-primary flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Download Summary</span>
              </button>
              <button className="btn-secondary flex items-center space-x-2">
                <Eye className="w-4 h-4" />
                <span>View Original</span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Feature Highlights */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="text-center group"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05 }}
            >
              <div className="w-16 h-16 mx-auto mb-4 bg-medical-blue/10 rounded-full flex items-center justify-center group-hover:bg-medical-blue/20 transition-colors duration-300">
                <feature.icon className="w-8 h-8 text-medical-blue" />
              </div>
              <h4 className="text-lg font-semibold text-dark-blue-gray mb-2">
                {feature.title}
              </h4>
              <p className="text-gray-600 text-sm">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>

        {/* Live Demo CTA */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <div className="bg-gradient-to-r from-medical-blue to-teal-accent rounded-2xl p-8 md:p-12 text-white">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              Try the Interactive Demo Now
            </h3>
            <p className="text-blue-100 mb-8 max-w-2xl mx-auto text-lg">
              Upload a sample medical report and see our AI generate comprehensive summaries in real-time. No signup required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                onClick={toggleDemo}
                className="bg-white text-medical-blue font-semibold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors duration-300 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                <span>{isPlaying ? 'Pause Demo' : 'Start Live Demo'}</span>
              </motion.button>
              <motion.button
                className="border-2 border-white text-white font-semibold py-3 px-8 rounded-lg hover:bg-white hover:text-medical-blue transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                View Sample Reports
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Demo;
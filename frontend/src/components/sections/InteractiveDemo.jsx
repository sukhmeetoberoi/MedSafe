import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Download, Eye, AlertCircle, CheckCircle, X, Loader2, ChevronRight } from 'lucide-react';
import { useFileUpload, useProcessingStatus, useSummaries, useQuestionAnswer, useReportProcessing } from '../../hooks/useApi';

const InteractiveDemo = () => {
  const [activeView, setActiveView] = useState('clinician');
  const [currentReport, setCurrentReport] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [question, setQuestion] = useState('');

  const fileInputRef = useRef(null);

  // Custom hooks
  const { uploadFile, uploading, uploadProgress, uploadError, uploadResult } = useFileUpload();
  const { processReport, processing, error: processingError } = useReportProcessing();
  const { status, loading: statusLoading } = useProcessingStatus(currentReport?.id);
  const { summaries, loading: summariesLoading } = useSummaries(currentReport?.id);
  const { questions, askQuestion, loading: qaLoading } = useQuestionAnswer(currentReport?.id);

  const sampleReports = [
    {
      id: 1,
      title: 'Cardiology Consultation Report',
      type: 'PDF',
      description: 'Heart evaluation and ECG results',
      placeholder: true
    },
    {
      id: 2,
      title: 'Blood Test Results',
      type: 'PDF',
      description: 'Complete blood count and metabolic panel',
      placeholder: true
    },
    {
      id: 3,
      title: 'Radiology MRI Scan',
      type: 'Image',
      description: 'Brain MRI with radiologist findings',
      placeholder: true
    }
  ];

  const handleFileUpload = async (file) => {
    try {
      console.log('Starting file upload for:', file.name);
      const uploadResult = await uploadFile(file);
      console.log('Upload result:', uploadResult);

      if (uploadResult.success) {
        console.log('Upload successful, starting processing for report:', uploadResult.report_id);

        // Start processing automatically
        try {
          const processResult = await processReport(uploadResult.report_id, {
            includeSummaries: true,
            summaryTypes: 'clinician,patient',
            llmProvider: 'auto'
          });
          console.log('Processing started:', processResult);
        } catch (processError) {
          console.error('Processing error:', processError);
        }

        setCurrentReport({
          id: uploadResult.report_id,
          filename: uploadResult.filename,
          originalFilename: file.name
        });

        setShowResults(true);
      } else {
        console.error('Upload failed:', uploadResult);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleSampleReport = async (report) => {
    // In a real implementation, you'd fetch sample files from the server
    // For now, show a placeholder message
    setCurrentReport({
      ...report,
      placeholder: true
    });
    setShowResults(true);
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || !currentReport?.id) return;

    try {
      await askQuestion(question.trim());
      setQuestion('');
    } catch (error) {
      console.error('Q&A error:', error);
    }
  };

  const resetDemo = () => {
    setCurrentReport(null);
    setShowResults(false);
    setQuestion('');
  };

  // Get current summary based on active view
  const getCurrentSummary = () => {
    if (!summaries || summaries.length === 0) return null;

    const summary = summaries.find(s => s.summary_type === activeView);
    return summary || summaries[0];
  };

  const currentSummary = getCurrentSummary();

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
            Experience the power of AI-driven medical report analysis. Upload a real medical report and watch our AI generate comprehensive summaries in real-time.
          </motion.p>
        </motion.div>

        {/* Main Demo Area */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          {/* Upload Area */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-dark-blue-gray">
                {showResults ? 'Processing Status' : 'Upload Your Report'}
              </h3>
              {showResults && (
                <button
                  onClick={resetDemo}
                  className="text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
                >
                  <X className="w-4 h-4 inline mr-1" />
                  Reset
                </button>
              )}
            </div>

            {/* Upload Interface or Status */}
            {!showResults ? (
              <>
                {/* Upload Interface */}
                <motion.div
                  className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-medical-blue transition-colors duration-300 bg-light-blue-bg/50"
                  whileHover={{ scale: 1.02 }}
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif"
                    onChange={handleFileSelect}
                    className="hidden"
                  />

                  {uploading ? (
                    <div className="space-y-4">
                      <Loader2 className="w-16 h-16 text-medical-blue mx-auto animate-spin" />
                      <div>
                        <h4 className="text-lg font-semibold text-dark-blue-gray mb-2">
                          Uploading...
                        </h4>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                          <motion.div
                            className="bg-medical-blue h-2 rounded-full transition-all duration-300"
                            style={{ width: `${uploadProgress}%` }}
                          ></motion.div>
                        </div>
                        <p className="text-sm text-gray-600">{uploadProgress}% complete</p>
                      </div>
                    </div>
                  ) : (
                    <>
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
                    </>
                  )}
                </motion.div>

                {uploadError && (
                  <motion.div
                    className="bg-red-50 border border-red-200 rounded-lg p-4"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      <span className="text-red-800 text-sm">{uploadError}</span>
                    </div>
                  </motion.div>
                )}

                {/* Sample Reports */}
                <div>
                  <h4 className="font-semibold text-dark-blue-gray mb-3">Try Sample Reports:</h4>
                  <div className="space-y-2">
                    {sampleReports.map((report) => (
                      <motion.div
                        key={report.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200 cursor-pointer"
                        whileHover={{ x: 5 }}
                        onClick={() => handleSampleReport(report)}
                      >
                        <div className="flex items-center space-x-3">
                          <FileText className="w-5 h-5 text-medical-blue" />
                          <div>
                            <div className="font-medium text-dark-blue-gray">{report.title}</div>
                            <div className="text-sm text-gray-500">{report.description}</div>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                      </motion.div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              /* Processing Status */
              <div className="space-y-4">
                {status && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 className="font-semibold text-blue-900 mb-4">
                      Processing Progress
                    </h4>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-blue-800">Status:</span>
                        <span className="text-sm font-medium text-blue-900">
                          {status.current_step || status.status}
                        </span>
                      </div>

                      <div className="w-full bg-blue-200 rounded-full h-3">
                        <motion.div
                          className="bg-gradient-to-r from-medical-blue to-teal-accent h-3 rounded-full transition-all duration-500"
                          style={{ width: `${status.progress_percentage || 0}%` }}
                        ></motion.div>
                      </div>

                      <div className="text-sm text-blue-700">
                        Progress: {Math.round(status.progress_percentage || 0)}%
                      </div>

                      {status.error_message && (
                        <div className="mt-3 text-sm text-red-700">
                          Error: {status.error_message}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {currentReport?.placeholder && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="w-5 h-5 text-yellow-600" />
                      <span className="text-yellow-800 text-sm">
                        This is a demo placeholder. In a real implementation, you would upload an actual medical report.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Results Area */}
          {showResults && (
            <div className="space-y-6">
              <h3 className="text-2xl font-bold text-dark-blue-gray">AI Analysis Results</h3>

              {/* View Toggle */}
              <div className="flex space-x-2">
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
                  className="bg-white border border-gray-200 rounded-xl p-6 shadow-lg min-h-[300px]"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {currentSummary ? (
                    <>
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-xl font-semibold text-dark-blue-gray capitalize">
                          {activeView} Summary
                        </h4>
                        <div className="flex items-center space-x-2">
                          {currentSummary.confidence_score && (
                            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                              {Math.round(currentSummary.confidence_score * 100)}% confidence
                            </span>
                          )}
                          <button className="p-2 text-gray-500 hover:text-medical-blue transition-colors duration-200">
                            <Download className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                      <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                        {currentSummary.content || currentSummary.summary || JSON.stringify(currentSummary, null, 2)}
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center justify-center h-64 text-gray-500">
                      {summariesLoading ? (
                        <Loader2 className="w-8 h-8 animate-spin" />
                      ) : (
                        <div className="text-center">
                          <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                          <p>Waiting for summaries...</p>
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>

              {/* Q&A Section */}
              {currentReport?.id && (
                <div className="bg-gray-50 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-dark-blue-gray mb-4">Ask About This Report</h4>
                  <form onSubmit={handleQuestionSubmit} className="space-y-4">
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask a question about this medical report..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-medical-blue focus:border-transparent"
                      />
                      <button
                        type="submit"
                        disabled={!question.trim() || qaLoading}
                        className="btn-secondary disabled:opacity-50"
                      >
                        {qaLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Ask'}
                      </button>
                    </div>
                  </form>

                  {/* Q&A History */}
                  {questions.length > 0 && (
                    <div className="mt-4 space-y-3">
                      {questions.map((qa, index) => (
                        <div key={qa.id || index} className="bg-white rounded-lg p-4">
                          <div className="font-medium text-dark-blue-gray mb-2">Q: {qa.question}</div>
                          <div className="text-gray-700 text-sm mb-2">A: {qa.answer}</div>
                          <div className="text-xs text-gray-500">
                            Provider: {qa.provider} • Confidence: {Math.round(qa.confidence * 100)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </motion.div>

        {/* Success Messages */}
        <AnimatePresence>
          {uploadResult && (
            <motion.div
              className="fixed bottom-4 right-4 bg-green-500 text-white rounded-lg p-4 shadow-lg max-w-sm"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 50 }}
            >
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5" />
                <span>File uploaded successfully!</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

export default InteractiveDemo;
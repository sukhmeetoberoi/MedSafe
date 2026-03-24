import React, { useRef, useState } from "react";
import { motion } from "framer-motion";
import { Upload, ArrowRight, FileText, Brain, Shield, Clock } from "lucide-react";
import { API_BASE } from "../../apiConfig";

const Hero = ({ onReportsProcessed }) => {
  const fileInputRef = useRef(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  // report + summary state
  const [reportIds, setReportIds] = useState([]);
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);


  const features = [
    {
      icon: Brain,
      title: "AI-Powered",
      description: "Advanced OCR and NLP technology",
    },
    {
      icon: Shield,
      title: "HIPAA Compliant",
      description: "Secure and confidential processing",
    },
    {
      icon: Clock,
      title: "Fast Results",
      description: "Get summaries in seconds, not hours",
    },
  ];

  // Trigger the hidden file input
  const openFileDialog = () => {
    setUploadError(null);
    setUploadSuccess(null);
    fileInputRef.current?.click();
  };

  // Handle files selected by user
  const onFileSelected = (e) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length === 0) return;
    setSelectedFiles(files);
    uploadFiles(files);
  };

  // Fetch clinician summary for a given report (with polling)
  const fetchSummary = async (id, attempt = 1) => {
    const MAX_ATTEMPTS = 30; // 60 seconds total polling
    
    try {
      if (attempt === 1) {
        setSummaryLoading(true);
        setSummary(null);
      }

      console.log(`Fetching summary for report ${id} (Attempt ${attempt})...`);
      
      const res = await fetch(
        `${API_BASE}/api/summarize/report/${id}?summary_type=clinician`
      );

      if (!res.ok) {
        throw new Error(`Failed to fetch summary: ${res.status}`);
      }

      const data = await res.json();
      
      if (data.success && data.summary) {
        console.log("Summary received successfully!");
        setSummary(data.summary);
        setSummaryLoading(false);
        setUploadSuccess("Summary generated successfully!");
      } else if (attempt < MAX_ATTEMPTS) {
        // Not ready yet, poll again in 2 seconds
        console.log(`Summary not ready yet (${data.status}). Polling again...`);
        setUploadSuccess(`Processing report... (${Math.round((attempt/MAX_ATTEMPTS)*100)}%)`);
        setTimeout(() => fetchSummary(id, attempt + 1), 2000);
      } else {
        console.warn("Summary polling timed out.");
        setUploadError("Processing is taking longer than expected. Please check again in a minute.");
        setSummaryLoading(false);
      }
    } catch (err) {
      console.error("Summary fetch error:", err);
      setUploadError(`Failed to load summary: ${err.message}`);
      setSummaryLoading(false);
    }
  };

  // Upload function
  const uploadFiles = async (files) => {
    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append("files", file);
      });

      const url = `${API_BASE}/api/upload/reports`;
      console.log("Uploading to:", url);

      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`Upload failed: ${res.status} ${text}`);
      }

      const payload = await res.json().catch(() => null);
      setUploadSuccess(payload?.message || "Files uploaded successfully");
      console.log("Upload response:", payload);

      if (payload?.report_ids) {
        setReportIds(payload.report_ids);
        if (onReportsProcessed) onReportsProcessed(payload.report_ids);
        // fetch summary for the first one for hero display
        if (payload.report_ids.length > 0) {
          fetchSummary(payload.report_ids[0]);
        }
      }
    } catch (err) {
      console.error("Upload error:", err);
      setUploadError(err.message || "Upload error");
    } finally {
      setUploading(false);
    }
  };

  // Optional: allow user to clear selected file + summary
  const clearSelection = () => {
    setSelectedFiles([]);
    setUploadError(null);
    setUploadSuccess(null);
    setReportIds([]);
    if (onReportsProcessed) onReportsProcessed([]);
    setSummary(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center gradient-bg overflow-hidden"
    >
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,image/*,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        className="hidden"
        onChange={onFileSelected}
      />

      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-20 w-72 h-72 bg-white rounded-full filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-teal-accent rounded-full filter blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="container mx-auto px-4 pt-20 pb-16 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <motion.div
            className="text-white"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.h1
              className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              Understand Your Medical Reports in Seconds
            </motion.h1>

            <motion.p
              className="text-xl md:text-2xl mb-8 text-blue-100 leading-relaxed"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              AI-powered summarization for doctors and patients. Transform
              complex medical jargon into clear, actionable insights.
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4 mb-4"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              {/* Upload Button - triggers hidden input */}
              <motion.button
                className="btn-secondary bg-white text-medical-blue hover:bg-gray-100 flex items-center justify-center space-x-2 text-lg px-8 py-4 rounded-lg"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={openFileDialog}
                disabled={uploading}
              >
                <Upload className="w-5 h-5" />
                <span>{uploading ? "Uploading..." : "Upload Reports"}</span>
                <ArrowRight className="w-5 h-5" />
              </motion.button>

              {/* Watch Demo */}
              <motion.button
                className="border-2 border-white text-white hover:bg-white hover:text-medical-blue transition-all duration-300 px-8 py-4 rounded-lg text-lg font-semibold"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() =>
                  document
                    .getElementById("demo")
                    ?.scrollIntoView({ behavior: "smooth" })
                }
              >
                Watch Demo
              </motion.button>
            </motion.div>

            {/* File preview / status */}
            <div className="mb-6">
              {selectedFiles.length > 0 && (
                <div className="space-y-2">
                  {selectedFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center space-x-3 bg-white/5 p-3 rounded-lg border border-white/10">
                      <div className="text-sm text-white/90">
                        <div className="font-medium">{file.name}</div>
                        <div className="text-xs text-blue-200">
                          {(file.size / 1024).toFixed(1)} KB
                        </div>
                      </div>
                    </div>
                  ))}
                  <div className="flex items-center space-x-2">
                    <button
                      className="text-sm px-4 py-2 bg-white text-medical-blue rounded hover:bg-gray-100 font-semibold"
                      onClick={() => uploadFiles(selectedFiles)}
                      disabled={uploading}
                    >
                      {uploading ? "Uploading..." : "Start Upload"}
                    </button>
                    <button
                      className="text-sm px-4 py-2 bg-white/10 text-white rounded hover:bg-white/20"
                      onClick={clearSelection}
                    >
                      Clear All
                    </button>
                  </div>
                </div>
              )}

              {uploadSuccess && (
                <div className="mt-2 text-sm text-green-400">
                  {uploadSuccess}
                </div>
              )}
              {uploadError && (
                <div className="mt-2 text-sm text-rose-400">{uploadError}</div>
              )}
            </div>

            {/* Summary Section */}
            <div className="mt-4 bg-white/5 p-4 rounded-lg border border-white/10">
              <h3 className="text-white font-semibold mb-2">Report Summary</h3>

              {reportIds.length === 0 && (
                <p className="text-sm text-blue-200">
                  Upload reports to see summaries here.
                </p>
              )}

              {reportIds.length > 0 && summaryLoading && (
                <p className="text-sm text-blue-200">
                  Generating / fetching summary...
                </p>
              )}

              {reportIds.length > 0 && !summaryLoading && !summary && (
                <p className="text-sm text-blue-200">
                  No summary available yet.
                </p>
              )}

              {summary && (
                <div className="text-sm text-white/90 space-y-2">
                  {summary.title && (
                    <div className="font-semibold text-lg">
                      {summary.title}
                    </div>
                  )}
                  <p className="whitespace-pre-line">{summary.content}</p>
                </div>
              )}
            </div>

            {/* Feature Pills */}
            <motion.div
              className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
            >
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  className="bg-white/10 backdrop-blur-md rounded-lg p-4 border border-white/20"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  whileHover={{
                    scale: 1.05,
                    backgroundColor: "rgba(255, 255, 255, 0.2)",
                  }}
                >
                  <feature.icon className="w-6 h-6 text-teal-accent mb-2" />
                  <h3 className="font-semibold text-white mb-1">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-blue-100">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>

          {/* Right Content - Medical Illustration */}
          <motion.div
            className="relative"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {/* Main Document Circle */}
            <motion.div
              className="relative w-80 h-80 mx-auto"
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <div className="absolute inset-0 bg-white/10 backdrop-blur-md rounded-full border-4 border-white/30 flex items-center justify-center">
                <FileText className="w-32 h-32 text-white" />
              </div>

              {/* Orbiting Elements */}
              {[0, 120, 240].map((rotation, index) => (
                <motion.div
                  key={index}
                  className="absolute inset-0"
                  style={{ transform: `rotate(${rotation}deg)` }}
                >
                  <motion.div
                    className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-4"
                    animate={{ rotate: -360 }}
                    transition={{
                      duration: 20,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  >
                    <div className="bg-white rounded-full p-3 shadow-lg">
                      {index === 0 && (
                        <Brain className="w-6 h-6 text-medical-blue" />
                      )}
                      {index === 1 && (
                        <Shield className="w-6 h-6 text-medical-blue" />
                      )}
                      {index === 2 && (
                        <Clock className="w-6 h-6 text-medical-blue" />
                      )}
                    </div>
                  </motion.div>
                </motion.div>
              ))}
            </motion.div>

            {/* Floating Stats */}
            <motion.div
              className="absolute -top-8 -right-8 bg-white rounded-lg shadow-xl p-4"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 1 }}
            >
              <div className="text-2xl font-bold text-medical-blue">98%</div>
              <div className="text-sm text-gray-600">Accuracy Rate</div>
            </motion.div>

            <motion.div
              className="absolute -bottom-8 -left-8 bg-white rounded-lg shadow-xl p-4"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 1.2 }}
            >
              <div className="text-2xl font-bold text-teal-accent">2M+</div>
              <div className="text-sm text-gray-600">Reports Processed</div>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-6 h-10 border-2 border-white rounded-full flex justify-center">
          <div className="w-1 h-3 bg-white rounded-full mt-2"></div>
        </div>
      </motion.div>
    </section>
  );
};

export default Hero;

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  Download,
  Eye,
  ChevronRight,
} from "lucide-react";
import ChatBox from "./ChatBox";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const Demo = ({ reportIds = [], onReportsProcessed }) => {
  const [activeView, setActiveView] = useState("clinician"); // or "patient"
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [error, setError] = useState("");

  const [clinicianSummary, setClinicianSummary] = useState(null);
  const [patientSummary, setPatientSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  // ---------- upload ----------
  const onFilesSelected = async (e) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length === 0) return;

    setSelectedFiles(files);
    setError("");
    setUploadMessage("");
    setClinicianSummary(null);
    setPatientSummary(null);

    try {
      setUploading(true);
      const formData = new FormData();
      files.forEach(file => formData.append("files", file));

      const res = await fetch(`${API_BASE}/api/upload/reports`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Upload failed: ${res.status} ${txt}`);
      }

      const data = await res.json();
      setUploadMessage(data?.message || "Files uploaded successfully.");
      if (data?.report_ids) {
        if (onReportsProcessed) onReportsProcessed(data.report_ids);
        // fetch summaries for the first one for display
        if (data.report_ids.length > 0) {
          fetchSummaries(data.report_ids[0]);
        }
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Upload error");
    } finally {
      setUploading(false);
    }
  };

  const triggerFileInput = () => {
    document.getElementById("demo-file-input")?.click();
  };

  // ---------- fetch summaries ----------
  const fetchSummaries = async (id) => {
    if (!id) return; // Ensure an ID is provided

    try {
      setSummaryLoading(true);
      setClinicianSummary(null);
      setPatientSummary(null);
      setError("");

      const res = await fetch(`${API_BASE}/api/summarize/report/${id}/all`);

      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Summary fetch failed: ${res.status} ${txt}`);
      }

      const data = await res.json();
      const list = data?.summaries || [];

      // pick latest clinician + patient summaries
      const clinician = list.find((s) => s.summary_type === "clinician") || null;
      const patient = list.find((s) => s.summary_type === "patient") || null;

      setClinicianSummary(clinician);
      setPatientSummary(patient);
    } catch (err) {
      console.error("Summary fetch error:", err);
      setError(err.message || "Failed to fetch summaries");
    } finally {
      setSummaryLoading(false);
    }
  };

  const currentSummary =
    activeView === "clinician" ? clinicianSummary : patientSummary;

  return (
    <section id="demo" className="py-20 bg-white">
      <input
        type="file"
        multiple
        accept=".pdf,image/*"
        className="hidden"
        id="demo-file-input"
        onChange={onFilesSelected}
      />

      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* LEFT: Upload */}
          <div>
            <h2 className="text-3xl font-bold mb-6 text-dark-blue-gray">
              Upload Your Report
            </h2>

            <motion.div
              className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-medical-blue transition-colors duration-300 bg-light-blue-bg/50"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={triggerFileInput}
            >
              <Upload className="w-16 h-16 text-medical-blue mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-dark-blue-gray mb-2">
                Drop files here or click to upload
              </h4>
              <p className="text-gray-600 mb-4">
                Supports PDF, JPG, PNG, TIFF up to 10MB
              </p>
              <button className="btn-secondary" disabled={uploading}>
                {uploading ? "Uploading..." : "Choose Files"}
              </button>
            </motion.div>

            {selectedFiles.length > 0 && (
              <div className="mt-4 text-sm text-gray-700 bg-gray-50 p-4 rounded-xl border border-gray-200">
                <h4 className="font-semibold mb-2">Selected Files ({selectedFiles.length})</h4>
                <div className="space-y-1">
                  {selectedFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center text-xs">
                      <FileText className="w-3 h-3 mr-2 text-medical-blue" />
                      {file.name} ({(file.size / 1024).toFixed(0)} KB)
                    </div>
                  ))}
                </div>
              </div>
            )}

            {uploadMessage && (
              <p className="mt-3 text-sm text-green-600">{uploadMessage}</p>
            )}
            {error && <p className="mt-3 text-sm text-rose-600">{error}</p>}
          </div>

          {/* RIGHT: Summary */}
          <div>
            <h2 className="text-3xl font-bold mb-2 text-dark-blue-gray">
              Generated Summary
            </h2>
            <p className="text-sm text-emerald-700 mb-4">
              {reportIds.length > 0
                ? `Showing AI analysis for ${reportIds.length} report(s)`
                : "Upload reports to generate summaries and start chat"}
            </p>

            {/* View toggle */}
            <div className="flex mb-4 rounded-xl overflow-hidden border border-gray-200">
              <button
                onClick={() => setActiveView("clinician")}
                className={`flex-1 py-2 font-medium ${
                  activeView === "clinician"
                    ? "bg-medical-blue text-white"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                Clinician View
              </button>
              <button
                onClick={() => setActiveView("patient")}
                className={`flex-1 py-2 font-medium ${
                  activeView === "patient"
                    ? "bg-teal-accent text-white"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                Patient View
              </button>
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={activeView + (currentSummary ? currentSummary.id : "empty")}
                className="bg-white border border-gray-200 rounded-xl p-6 shadow-lg min-h-[220px]"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              >
                {summaryLoading && (
                  <p className="text-sm text-blue-600">
                    Generating / fetching summary…
                  </p>
                )}

                {!summaryLoading && reportIds.length === 0 && (
                  <p className="text-sm text-gray-500">
                    Upload reports to see summaries here.
                  </p>
                )}

                {!summaryLoading && reportIds.length > 0 && !currentSummary && (
                  <p className="text-sm text-gray-500">
                    Extracting data and generating {activeView} summary... Please wait.
                  </p>
                )}

                {!summaryLoading && currentSummary && (
                  <>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-xl font-semibold text-dark-blue-gray">
                        {currentSummary.title || "Summary"}
                      </h3>
                      <div className="flex space-x-2">
                        <button className="p-2 text-gray-500 hover:text-medical-blue">
                          <Download className="w-5 h-5" />
                        </button>
                        <button className="p-2 text-gray-500 hover:text-medical-blue">
                          <Eye className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                    <div className="text-sm text-gray-700 whitespace-pre-line">
                      {currentSummary.content}
                    </div>
                  </>
                )}
              </motion.div>
            </AnimatePresence>

            {/* Extra actions */}
            {reportIds.length > 0 && (
              <div className="mt-4 flex space-x-3">
                <button
                  className="btn-primary flex items-center space-x-2"
                  onClick={() => fetchSummaries(reportIds[0])}
                >
                  <FileText className="w-4 h-4" />
                  <span>Refresh Current</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Chat Section */}
        <div className="mt-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-dark-blue-gray mb-4">Ask MedSafe AI</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Have specific questions about your reports? Ask our AI assistant for instant, cited answers based on your clinical data.
            </p>
          </div>
          <div className="max-w-4xl mx-auto">
            <ChatBox reportIds={reportIds} />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Demo;

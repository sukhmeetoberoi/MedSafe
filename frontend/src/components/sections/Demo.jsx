import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  Download,
  Eye,
  ChevronRight,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const Demo = () => {
  const [activeView, setActiveView] = useState("clinician"); // or "patient"
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [error, setError] = useState("");

  const [reportId, setReportId] = useState(null);
  const [clinicianSummary, setClinicianSummary] = useState(null);
  const [patientSummary, setPatientSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  // ---------- upload ----------
  const onFileSelected = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setError("");
    setUploadMessage("");
    setClinicianSummary(null);
    setPatientSummary(null);

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/upload/report`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Upload failed: ${res.status} ${txt}`);
      }

      const data = await res.json();
      setUploadMessage(data?.message || "File uploaded successfully.");
      if (data?.report_id) {
        setReportId(data.report_id);
        // immediately fetch summaries
        fetchSummaries(data.report_id);
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
        id="demo-file-input"
        type="file"
        accept=".pdf,image/*"
        className="hidden"
        onChange={onFileSelected}
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

            {selectedFile && (
              <div className="mt-4 text-sm text-gray-700">
                <div className="font-medium">{selectedFile.name}</div>
                <div className="text-xs text-gray-500">
                  {(selectedFile.size / 1024).toFixed(1)} KB
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
              {reportId
                ? "Showing AI-generated summaries from backend"
                : "Upload a report to generate summaries"}
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

                {!summaryLoading && !reportId && (
                  <p className="text-sm text-gray-500">
                    Upload a report to see its summaries here.
                  </p>
                )}

                {!summaryLoading && reportId && !currentSummary && (
                  <p className="text-sm text-gray-500">
                    No {activeView} summary found yet. Try again in a moment.
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
            {reportId && (
              <div className="mt-4 flex space-x-3">
                <button
                  className="btn-primary flex items-center space-x-2"
                  onClick={() => fetchSummaries(reportId)}
                >
                  <FileText className="w-4 h-4" />
                  <span>Refresh Summary</span>
                </button>
                <button className="btn-secondary flex items-center space-x-2">
                  <ChevronRight className="w-4 h-4" />
                  <span>View Original</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Demo;

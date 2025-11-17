/**
 * Custom React hooks for API interactions
 * Provides state management for API calls
 */

import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

// Hook for file upload with progress tracking
export function useFileUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);

  const uploadFile = useCallback(async (file, userId = null) => {
    setUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResult(null);

    try {
      // Simulate progress updates (in real implementation, this would come from the upload API)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 100);

      const result = await apiService.uploadReport(file, userId);

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadResult(result);

      return result;
    } catch (error) {
      setUploadError(error.message || 'Upload failed');
      throw error;
    } finally {
      setUploading(false);
    }
  }, []);

  const resetUpload = useCallback(() => {
    setUploading(false);
    setUploadProgress(0);
    setUploadError(null);
    setUploadResult(null);
  }, []);

  return {
    uploadFile,
    uploading,
    uploadProgress,
    uploadError,
    uploadResult,
    resetUpload,
  };
}

// Hook for processing status tracking
export function useProcessingStatus(reportId, pollInterval = 2000) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = useCallback(async () => {
    try {
      const statusData = await apiService.getProcessingStatus(reportId);
      setStatus(statusData);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch status');
    } finally {
      setLoading(false);
    }
  }, [reportId]);

  useEffect(() => {
    if (!reportId) return;

    fetchStatus();

    // Set up polling for active processing
    const interval = setInterval(() => {
      if (status?.status && !['completed', 'summaries_complete', 'failed'].includes(status.status)) {
        fetchStatus();
      }
    }, pollInterval);

    return () => clearInterval(interval);
  }, [reportId, fetchStatus, status?.status, pollInterval]);

  return {
    status,
    loading,
    error,
    refetch: fetchStatus,
  };
}

// Hook for managing processing workflow
export function useReportProcessing() {
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const processReport = useCallback(async (reportId, options = {}) => {
    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const processingResult = await apiService.startProcessing(reportId, options);
      setResult(processingResult);
      return processingResult;
    } catch (err) {
      setError(err.message || 'Processing failed');
      throw err;
    } finally {
      setProcessing(false);
    }
  }, []);

  const uploadAndProcess = useCallback(async (file, options = {}) => {
    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const result = await apiService.uploadAndProcessReport(file, options);
      setResult(result);
      return result;
    } catch (err) {
      setError(err.message || 'Upload and processing failed');
      throw err;
    } finally {
      setProcessing(false);
    }
  }, []);

  return {
    processReport,
    uploadAndProcess,
    processing,
    error,
    result,
  };
}

// Hook for summaries management
export function useSummaries(reportId) {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSummaries = useCallback(async () => {
    if (!reportId) return;

    try {
      setLoading(true);
      const data = await apiService.getReportSummaries(reportId);
      setSummaries(data.summaries || []);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch summaries');
    } finally {
      setLoading(false);
    }
  }, [reportId]);

  const submitFeedback = useCallback(async (summaryId, rating, feedback) => {
    try {
      await apiService.submitSummaryFeedback(summaryId, rating, feedback);
      // Refresh summaries after feedback
      await fetchSummaries();
    } catch (err) {
      setError(err.message || 'Failed to submit feedback');
      throw err;
    }
  }, [fetchSummaries]);

  const toggleBookmark = useCallback(async (summaryId) => {
    try {
      const result = await apiService.toggleBookmark(summaryId);
      // Update local state
      setSummaries(prev =>
        prev.map(summary =>
          summary.id === summaryId
            ? { ...summary, is_bookmarked: result.is_bookmarked }
            : summary
        )
      );
      return result;
    } catch (err) {
      setError(err.message || 'Failed to toggle bookmark');
      throw err;
    }
  }, []);

  useEffect(() => {
    fetchSummaries();
  }, [fetchSummaries]);

  return {
    summaries,
    loading,
    error,
    refetch: fetchSummaries,
    submitFeedback,
    toggleBookmark,
  };
}

// Hook for Q&A functionality
export function useQuestionAnswer(reportId) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const askQuestion = useCallback(async (question, llmProvider = 'auto') => {
    if (!reportId) {
      throw new Error('Report ID is required');
    }

    setLoading(true);
    setError(null);

    try {
      const result = await apiService.askQuestionAboutReport(reportId, question, llmProvider);

      const qaEntry = {
        id: Date.now(),
        question,
        answer: result.answer,
        provider: result.provider_used,
        confidence: result.confidence,
        timestamp: new Date().toISOString(),
        disclaimer: result.disclaimer,
      };

      setQuestions(prev => [...prev, qaEntry]);
      return qaEntry;
    } catch (err) {
      setError(err.message || 'Failed to get answer');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [reportId]);

  const clearHistory = useCallback(() => {
    setQuestions([]);
  }, []);

  return {
    questions,
    loading,
    error,
    askQuestion,
    clearHistory,
  };
}

// Hook for user reports management
export function useUserReports(userId = null, filters = {}) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    limit: 50,
    offset: 0,
    total: 0,
  });

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getUserReports(userId, { ...filters, ...pagination });
      setReports(data.reports || []);
      setPagination(prev => ({ ...prev, total: data.total || 0 }));
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  }, [userId, filters, pagination.limit, pagination.offset]);

  const deleteReport = useCallback(async (reportId) => {
    try {
      await apiService.deleteReport(reportId);
      // Remove from local state
      setReports(prev => prev.filter(report => report.id !== reportId));
      return true;
    } catch (err) {
      setError(err.message || 'Failed to delete report');
      throw err;
    }
  }, []);

  const loadMore = useCallback(() => {
    setPagination(prev => ({
      ...prev,
      offset: prev.offset + prev.limit,
    }));
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  return {
    reports,
    loading,
    error,
    pagination,
    fetchReports,
    deleteReport,
    loadMore,
    hasMore: pagination.offset < pagination.total,
  };
}

// Hook for application health monitoring
export function useHealthMonitor() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkHealth = useCallback(async (detailed = false) => {
    try {
      setLoading(true);
      const healthData = detailed
        ? await apiService.getDetailedHealthStatus()
        : await apiService.getHealthStatus();
      setHealth(healthData);
      setError(null);
      return healthData;
    } catch (err) {
      setError(err.message || 'Health check failed');
      setHealth({ status: 'unhealthy', error: err.message });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();

    // Set up periodic health checks
    const interval = setInterval(() => {
      checkHealth(false); // Basic health check
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    health,
    loading,
    error,
    checkHealth,
    isHealthy: health?.status === 'healthy',
  };
}
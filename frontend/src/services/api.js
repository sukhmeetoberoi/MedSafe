/**
 * API Service for MedSummarize Backend
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios';

// Create axios instance with default configuration
import { API_BASE } from '../apiConfig';
const API_BASE_URL = API_BASE;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

class ApiService {
  /**
   * Upload a medical report
   */
  async uploadReport(file, userId = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (userId) {
      formData.append('user_id', userId);
    }

    const response = await apiClient.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        return progress;
      },
    });

    return response.data;
  }

  /**
   * Get upload status for a report
   */
  async getUploadStatus(reportId) {
    const response = await apiClient.get(`/api/upload/status/${reportId}`);
    return response.data;
  }

  /**
   * Start processing a medical report
   */
  async startProcessing(reportId, options = {}) {
    const {
      includeSummaries = true,
      summaryTypes = 'clinician,patient',
      llmProvider = 'auto'
    } = options;

    const response = await apiClient.post(`/api/process/report/${reportId}`, null, {
      params: {
        include_summaries: includeSummaries,
        summary_types: summaryTypes,
        llm_provider: llmProvider,
      },
    });

    return response.data;
  }

  /**
   * Get processing status for a report
   */
  async getProcessingStatus(reportId) {
    const response = await apiClient.get(`/api/process/status/${reportId}`);
    return response.data;
  }

  /**
   * Get all summaries for a report
   */
  async getReportSummaries(reportId, summaryType = null) {
    const params = {};
    if (summaryType) {
      params.summary_type = summaryType;
    }

    const response = await apiClient.get(`/api/summarize/report/${reportId}`, { params });
    return response.data;
  }

  /**
   * Get a specific summary by ID
   */
  async getSummary(summaryId) {
    const response = await apiClient.get(`/api/summarize/${summaryId}`);
    return response.data;
  }

  /**
   * Submit feedback for a summary
   */
  async submitSummaryFeedback(summaryId, rating, feedback = null) {
    const response = await apiClient.post(`/api/summarize/${summaryId}/feedback`, {
      rating,
      feedback,
    });

    return response.data;
  }

  /**
   * Toggle bookmark for a summary
   */
  async toggleBookmark(summaryId) {
    const response = await apiClient.post(`/api/summarize/${summaryId}/bookmark`);
    return response.data;
  }

  /**
   * Compare summaries for a report
   */
  async compareSummaries(reportId) {
    const response = await apiClient.get(`/api/summarize/report/${reportId}/compare`);
    return response.data;
  }

  /**
   * Ask a question about a report
   */
  async askQuestionAboutReport(reportId, question, llmProvider = 'auto') {
    const response = await apiClient.post(`/api/process/report/${reportId}/qa`, {
      question,
      llm_provider,
    });

    return response.data;
  }

  /**
   * Get list of user's reports
   */
  async getUserReports(userId = null, filters = {}) {
    const params = {
      limit: filters.limit || 50,
      offset: filters.offset || 0,
    };

    if (userId) {
      params.user_id = userId;
    }

    if (filters.status) {
      params.status_filter = filters.status;
    }

    const response = await apiClient.get('/api/upload/list', { params });
    return response.data;
  }

  /**
   * Delete a report
   */
  async deleteReport(reportId) {
    const response = await apiClient.delete(`/api/upload/${reportId}`);
    return response.data;
  }

  /**
   * Get API health status
   */
  async getHealthStatus() {
    const response = await apiClient.get('/api/health/');
    return response.data;
  }

  /**
   * Get detailed health status with dependencies
   */
  async getDetailedHealthStatus() {
    const response = await apiClient.get('/api/health/detailed');
    return response.data;
  }

  /**
   * Generate summaries for an already processed report
   */
  async generateSummaries(reportId, summaryTypes = 'clinician,patient', llmProvider = 'auto') {
    const response = await apiClient.post(`/api/process/report/${reportId}/summarize`, null, {
      params: {
        summary_types: summaryTypes,
        llm_provider: llmProvider,
      },
    });

    return response.data;
  }

  /**
   * Poll processing status until completion or timeout
   */
  async pollProcessingStatus(reportId, timeout = 300000, interval = 2000) {
    const startTime = Date.now();
    const timeoutTime = startTime + timeout;

    while (Date.now() < timeoutTime) {
      try {
        const status = await this.getProcessingStatus(reportId);

        // Return status if processing is complete or failed
        if (['completed', 'summaries_complete', 'failed'].includes(status.status)) {
          return status;
        }

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        console.error('Error polling status:', error);
        throw error;
      }
    }

    throw new Error('Processing timeout');
  }

  /**
   * Upload and process a report in one go
   */
  async uploadAndProcessReport(file, options = {}) {
    try {
      // Step 1: Upload file
      const uploadResult = await this.uploadReport(file, options.userId);

      // Step 2: Start processing
      await this.startProcessing(uploadResult.report_id, {
        includeSummaries: options.includeSummaries,
        summaryTypes: options.summaryTypes,
        llmProvider: options.llmProvider,
      });

      // Step 3: Return upload result for status tracking
      return {
        success: true,
        report_id: uploadResult.report_id,
        filename: uploadResult.filename,
        message: uploadResult.message,
      };

    } catch (error) {
      console.error('Error in upload and process:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export individual methods for easy importing
export const {
  uploadReport,
  getUploadStatus,
  startProcessing,
  getProcessingStatus,
  getReportSummaries,
  getSummary,
  submitSummaryFeedback,
  toggleBookmark,
  compareSummaries,
  askQuestionAboutReport,
  getUserReports,
  deleteReport,
  getHealthStatus,
  getDetailedHealthStatus,
  generateSummaries,
  pollProcessingStatus,
  uploadAndProcessReport,
} = apiService;
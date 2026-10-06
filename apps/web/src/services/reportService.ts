// apps/web/src/services/reportService.ts
/**
 * Frontend Service for Citizen Crime Reports and Incident Registry.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { CrimeReportCreate, CrimeReport, ReportListResponse } from '../types/apiTypes';

export const reportService = {
  async createReport(reportData: CrimeReportCreate): Promise<CrimeReport> {
    return apiClient<CrimeReport>(API_ENDPOINTS.REPORTS, {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  },

  async listReports(): Promise<ReportListResponse> {
    return apiClient<ReportListResponse>(API_ENDPOINTS.REPORTS);
  },

  async getReportById(reportId: string): Promise<CrimeReport> {
    return apiClient<CrimeReport>(`${API_ENDPOINTS.REPORTS}/${reportId}`);
  },
};

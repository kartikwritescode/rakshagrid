// frontend/nextjs/src/services/currencyService.ts
/**
 * Frontend Service for Module 1: Counterfeit Currency Detection APIs.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { CurrencyAnalysisResponse } from '../types/apiTypes';

export const currencyService = {
  async analyzeImage(imageFile: File): Promise<CurrencyAnalysisResponse> {
    const formData = new FormData();
    formData.append('file', imageFile);
    return apiClient<CurrencyAnalysisResponse>(API_ENDPOINTS.CURRENCY.ANALYZE_IMAGE, {
      method: 'POST',
      body: formData,
    });
  },
};

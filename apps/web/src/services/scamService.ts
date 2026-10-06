// frontend/nextjs/src/services/scamService.ts
/**
 * Frontend Service for Module 2: Scam Call Interceptor APIs.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { ScamVerdictResponse } from '../types/apiTypes';

export const scamService = {
  async analyzeText(transcript: string): Promise<ScamVerdictResponse> {
    return apiClient<ScamVerdictResponse>(API_ENDPOINTS.SCAM.ANALYZE_TEXT, {
      method: 'POST',
      body: JSON.stringify({ transcript }),
    });
  },

  async analyzeAudio(audioFile: File): Promise<ScamVerdictResponse> {
    const formData = new FormData();
    formData.append('file', audioFile);
    return apiClient<ScamVerdictResponse>(API_ENDPOINTS.SCAM.ANALYZE_AUDIO, {
      method: 'POST',
      body: formData,
    });
  },

  async analyzeStream(transcriptChunks: string[]): Promise<any[]> {
    return apiClient<any[]>(API_ENDPOINTS.SCAM.STREAM, {
      method: 'POST',
      body: JSON.stringify({ transcript_chunks: transcriptChunks }),
    });
  },
};

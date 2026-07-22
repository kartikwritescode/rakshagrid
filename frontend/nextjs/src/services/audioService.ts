// frontend/nextjs/src/services/audioService.ts
/**
 * Frontend Service for Audio Deepfake Detection & Speech Transcription.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

export const audioService = {
  async detectDeepfake(audioFile: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', audioFile);
    return apiClient<any>(API_ENDPOINTS.AUDIO.DETECT, {
      method: 'POST',
      body: formData,
    });
  },

  async transcribeAudio(audioFile: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', audioFile);
    return apiClient<any>(API_ENDPOINTS.AUDIO.TRANSCRIBE, {
      method: 'POST',
      body: formData,
    });
  },
};

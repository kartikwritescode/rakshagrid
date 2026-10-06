// apps/web/src/services/audioService.ts
/**
 * Frontend Service for Audio Deepfake Detection & Speech Transcription.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { AudioDetectResponse, TranscribeResponse } from '../types/apiTypes';

export const audioService = {
  async detectDeepfake(audioFile: File): Promise<AudioDetectResponse> {
    const formData = new FormData();
    formData.append('file', audioFile);
    return apiClient<AudioDetectResponse>(API_ENDPOINTS.AUDIO.DETECT, {
      method: 'POST',
      body: formData,
    });
  },

  async transcribeAudio(audioFile: File): Promise<TranscribeResponse> {
    const formData = new FormData();
    formData.append('file', audioFile);
    return apiClient<TranscribeResponse>(API_ENDPOINTS.AUDIO.TRANSCRIBE, {
      method: 'POST',
      body: formData,
    });
  },
};

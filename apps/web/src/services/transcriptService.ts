// frontend/nextjs/src/services/transcriptService.ts
/**
 * Dedicated Service for Speech-to-Text Transcription.
 */

import { audioService } from './audioService';

export const transcriptService = {
  async generateTranscript(audioFile: File) {
    return audioService.transcribeAudio(audioFile);
  }
};

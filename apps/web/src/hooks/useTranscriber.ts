// apps/web/src/hooks/useTranscriber.ts
import { useState } from 'react';
import { transcriptService } from '../services/transcriptService';
import { TranscribeResponse } from '../types/apiTypes';

export function useTranscriber() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);

  const transcribe = async (file: File): Promise<TranscribeResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await transcriptService.generateTranscript(file);
      setTranscript(res.transcript || null);
      return res;
    } catch (err: any) {
      setError(err.message || 'Speech transcription failed.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, transcript, transcribe };
}

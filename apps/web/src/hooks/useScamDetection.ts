// frontend/nextjs/src/hooks/useScamDetection.ts
/**
 * React Hook for executing text and audio scam analysis.
 */

import { useState } from 'react';
import { scamService } from '../services/scamService';
import { ScamVerdictResponse } from '../types/apiTypes';

export function useScamDetection() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScamVerdictResponse | null>(null);

  const analyzeText = async (transcript: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await scamService.analyzeText(transcript);
      setResult(res);
      return res;
    } catch (err: any) {
      setError(err.message || 'Scam analysis failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const analyzeAudio = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const res = await scamService.analyzeAudio(file);
      setResult(res);
      return res;
    } catch (err: any) {
      setError(err.message || 'Audio scam analysis failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    result,
    analyzeText,
    analyzeAudio,
  };
}

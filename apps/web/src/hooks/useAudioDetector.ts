// frontend/nextjs/src/hooks/useAudioDetector.ts
import { useState } from 'react';
import { audioService } from '../services/audioService';

export function useAudioDetector() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const detect = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const res = await audioService.detectDeepfake(file);
      setResult(res);
      return res;
    } catch (err: any) {
      setError(err.message || 'Deepfake audio analysis failed.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, result, detect };
}

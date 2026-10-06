// frontend/nextjs/src/hooks/useCrimeDetection.ts
import { useState } from 'react';
import { crimeService } from '../services/crimeService';

export function useCrimeDetection() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const predict = async (file?: File, city?: string, description?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await crimeService.predictCrime(file, city, description);
      setResult(res);
      return res;
    } catch (err: any) {
      setError(err.message || 'Crime prediction analysis failed.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, result, predict };
}

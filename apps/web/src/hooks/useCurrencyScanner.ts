// frontend/nextjs/src/hooks/useCurrencyScanner.ts
/**
 * React Hook for analyzing currency banknote images.
 */

import { useState } from 'react';
import { currencyService } from '../services/currencyService';
import { CurrencyAnalysisResponse } from '../types/apiTypes';

export function useCurrencyScanner() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CurrencyAnalysisResponse | null>(null);

  const scanImage = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const res = await currencyService.analyzeImage(file);
      setResult(res);
      return res;
    } catch (err: any) {
      setError(err.message || 'Currency scanning failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    result,
    scanImage,
  };
}

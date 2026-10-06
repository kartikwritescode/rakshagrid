// frontend/nextjs/src/api/client.ts
/**
 * Generic HTTP client wrapper for fetching backend APIs.
 */

import { API_BASE_URL } from '../constants/apiEndpoints';

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  
  const apiKey = process.env.NEXT_PUBLIC_API_KEY || 'rakshagrid-master-key-2026';
  const headers: Record<string, string> = {
    ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
    'X-API-Key': apiKey,
    ...((options.headers as Record<string, string>) || {}),
  };

  const config: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// frontend/nextjs/src/constants/apiEndpoints.ts
/**
 * Centralized API endpoint routing constants.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  SCAM: {
    ANALYZE_TEXT: `${API_BASE_URL}/api/scam/analyze-text`,
    ANALYZE_AUDIO: `${API_BASE_URL}/api/scam/analyze-audio`,
    STREAM: `${API_BASE_URL}/api/scam/stream`,
  },
  AUDIO: {
    DETECT: `${API_BASE_URL}/api/audio/detect`,
    TRANSCRIBE: `${API_BASE_URL}/api/audio/transcribe`,
  },
  CURRENCY: {
    PREDICT: `${API_BASE_URL}/api/currency/predict`,
    ANALYZE_IMAGE: `${API_BASE_URL}/api/currency/analyze-image`,
  },
  CRIME: {
    HEALTH: `${API_BASE_URL}/api/crime/health`,
    PREDICT: `${API_BASE_URL}/api/crime/predict`,
    INCIDENTS: `${API_BASE_URL}/api/crime/incidents`,
    HOTSPOTS: `${API_BASE_URL}/api/crime/hotspots`,
    POINTS: `${API_BASE_URL}/api/crime/points`,
    PATROL_ALLOCATION: `${API_BASE_URL}/api/crime/patrol-allocation`,
  },
};

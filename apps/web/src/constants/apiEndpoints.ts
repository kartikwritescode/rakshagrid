// apps/web/src/constants/apiEndpoints.ts
/**
 * Centralized API endpoint routing constants.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  CHAT: `${API_BASE_URL}/api/v1/chat`,
  SCAM: {
    ANALYZE_TEXT: `${API_BASE_URL}/api/v1/scam/analyze-text`,
    ANALYZE_AUDIO: `${API_BASE_URL}/api/v1/audio/detect`,
    STREAM: `${API_BASE_URL}/api/v1/scam/stream`,
  },
  AUDIO: {
    DETECT: `${API_BASE_URL}/api/v1/audio/detect`,
    TRANSCRIBE: `${API_BASE_URL}/api/v1/audio/transcribe`,
  },
  CURRENCY: {
    PREDICT: `${API_BASE_URL}/api/v1/currency/predict`,
    ANALYZE_IMAGE: `${API_BASE_URL}/api/v1/currency/analyze-image`,
  },
  CRIME: {
    HEALTH: `${API_BASE_URL}/api/v1/crime/health`,
    PREDICT: `${API_BASE_URL}/api/v1/crime/predict`,
    INCIDENTS: `${API_BASE_URL}/api/v1/crime/incidents`,
    HOTSPOTS: `${API_BASE_URL}/api/v1/crime/hotspots`,
    POINTS: `${API_BASE_URL}/api/v1/crime/points`,
    PATROL_ALLOCATION: `${API_BASE_URL}/api/v1/crime/patrol-allocation`,
  },
  GRAPH: {
    DATA: `${API_BASE_URL}/api/v1/graph`,
    NODES: `${API_BASE_URL}/api/v1/graph/nodes`,
    CENTRALITY: `${API_BASE_URL}/api/v1/graph/centrality`,
    CLUSTERS: `${API_BASE_URL}/api/v1/graph/clusters`,
  },
  REPORTS: `${API_BASE_URL}/api/v1/reports`,
};

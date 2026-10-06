// frontend/nextjs/src/types/apiTypes.ts
/**
 * Centralized TypeScript interface definitions matching FastAPI response payloads.
 */

export interface ScamVerdictResponse {
  stage: string;
  risk_score: number;
  risk_band: 'high' | 'low' | 'needs_review';
  fired_features: string[];
  fired_features_detail: Array<{
    feature: string;
    weight: number;
    matched: string[];
  }>;
  component_scores: {
    rules: number;
    tfidf: number;
    transformer: number;
    ensemble: number;
    llm_fallback?: number;
  };
  breakdown: {
    engineered_features: Record<string, number>;
    rules_detail: Array<any>;
    llm_analysis?: string;
    llm_reasons?: string[];
  };
  transcript: string;
  processing_time_ms?: number;
}

export interface CurrencyAnalysisResponse {
  status: 'genuine' | 'counterfeit';
  predicted_label: string;
  confidence: number;
  is_genuine: boolean;
  class_probabilities: Record<string, number>;
  processing_time_ms?: number;
}

export interface HotspotCluster {
  cluster: number;
  incidents: number;
  violent_share: number;
  lat: number;
  lon: number;
  weight: number;
  units_assigned?: number;
}

export interface HotspotsResponse {
  hotspots: HotspotCluster[];
}

export interface IncidentPoint {
  "Report Number": string;
  "Date of Occurrence": string;
  "City": string;
  "Crime Description": string;
  "Crime Domain": string;
  lat: number;
  lon: number;
  cluster?: number;
}

export interface PointsResponse {
  points: IncidentPoint[];
}

export interface PatrolAllocationResponse {
  n_units: number;
  allocation: HotspotCluster[];
}

export interface SystemHealthResponse {
  status: string;
  service: string;
  version: string;
  modules: {
    module1_currency: string;
    module2_scam: string;
    module4_crime: string;
  };
}

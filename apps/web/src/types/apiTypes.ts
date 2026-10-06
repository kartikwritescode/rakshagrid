// apps/web/src/types/apiTypes.ts
/**
 * Centralized TypeScript interface definitions matching FastAPI DTO response and request payloads.
 */

// ==========================================
// SCAM ANALYSIS DTOs
// ==========================================

export interface ScamFiredFeatureDetail {
  feature: string;
  weight: number;
  matched: string[];
}

export interface ScamComponentScores {
  rules: number;
  tfidf: number;
  transformer: number;
  ensemble: number;
  llm_fallback?: number;
}

export interface ScamBreakdown {
  engineered_features: Record<string, number>;
  rules_detail: Array<any>;
  llm_analysis?: string;
  llm_reasons?: string[];
}

export interface ScamVerdictResponse {
  stage: string;
  risk_score: number;
  risk_band: 'high' | 'low' | 'needs_review';
  fired_features: string[];
  fired_features_detail?: ScamFiredFeatureDetail[];
  component_scores: ScamComponentScores;
  breakdown?: ScamBreakdown;
  transcript: string;
  processing_time_ms?: number;
}

// ==========================================
// AUDIO & VOICE DEEPFAKE DTOs (DECOUPLED)
// ==========================================

export type VoiceDeepfakeStatus =
  | 'detected'
  | 'not_detected'
  | 'unavailable'
  | 'insufficient_quality'
  | 'processing_error';

export interface TranscriptionResult {
  status: 'success' | 'failed' | string;
  transcript?: string | null;
  reason_code?: string | null;
  message?: string | null;
  model?: string;
}

export interface ScamAnalysisResult {
  status: 'success' | 'not_analyzed' | 'failed' | string;
  is_scam?: boolean | null;
  risk_score?: number | null;
  risk_band?: 'low' | 'needs_review' | 'high' | null;
  stage?: string | null;
  fired_features?: string[];
  component_scores?: Record<string, number>;
  reason?: string | null;
}

export interface VoiceAnalysisResult {
  status: VoiceDeepfakeStatus;
  is_deepfake?: boolean | null;
  confidence?: number | null;
  model_name?: string | null;
  reason?: string | null;
  details?: Record<string, any>;
}

export interface AudioDetectResponse {
  status: 'success' | 'transcription_failed' | 'partial' | string;
  filename?: string;
  transcription: TranscriptionResult;
  scam_analysis?: ScamAnalysisResult | null;
  voice_analysis: VoiceAnalysisResult;
  processing_time_ms?: number;

  // Backward compatibility convenience mirrors
  stt_status?: string | null;
  transcript?: string | null;
  reason_code?: string | null;
  message?: string | null;
  is_scam?: boolean | null;
  risk_score?: number | null;
  risk_band?: string | null;
  stage?: string | null;
  scam_classification?: Record<string, any> | null;
  llm_fallback?: Record<string, any> | null;
  voice_deepfake_detection?: VoiceAnalysisResult | null;
}

export interface TranscribeResponse {
  status: string;
  transcript?: string | null;
  reason_code?: string | null;
  message?: string | null;
  filename?: string;
  model?: string;
  processing_time_ms?: number;
}

// ==========================================
// CURRENCY DTOs
// ==========================================

export interface CurrencyAnalysisResponse {
  status: 'genuine' | 'counterfeit';
  predicted_label: string;
  confidence: number;
  is_genuine: boolean;
  class_probabilities: Record<string, number>;
  processing_time_ms?: number;
}

// ==========================================
// CRIME & VIGILGRID DTOs
// ==========================================

export interface CrimeHealthResponse {
  status: string;
  points_loaded: number;
  hotspots_found: number;
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
  total?: number;
}

export interface PatrolAllocationResponse {
  n_units: number;
  allocation: HotspotCluster[];
}

export interface CrimeIncident {
  id: string;
  crime_type: string;
  category: string;
  confidence: number;
  timestamp: string;
  city: string;
  lat: number;
  lon: number;
  severity: string;
  status: string;
  units_deployed?: number;
}

export interface IncidentsResponse {
  incidents: CrimeIncident[];
  total: number;
}

// ==========================================
// FRAUD NETWORK GRAPH DTOs
// ==========================================

export interface GraphNodeData {
  id: string;
  type: string;
  label: string;
  properties?: Record<string, any>;
}

export interface GraphLinkData {
  source: string;
  target: string;
  relation: string;
  weight: number;
}

export interface NodesResponseData {
  nodes: GraphNodeData[];
  links: GraphLinkData[];
  total_nodes: number;
  total_links: number;
}

export interface TopInfluencer {
  node_id: string;
  type: string;
  label: string;
  pagerank: number;
  betweenness: number;
  degree: number;
}

export interface CentralityResponseData {
  pagerank: Record<string, number>;
  betweenness: Record<string, number>;
  top_influencers: TopInfluencer[];
}

export interface ClusterItemData {
  id: number;
  nodes: string[];
  size: number;
  entity_counts: Record<string, number>;
  risk_score: number;
}

export interface ClustersResponseData {
  clusters: ClusterItemData[];
  total_clusters: number;
}

export interface FullGraphResponseData {
  nodes: GraphNodeData[];
  links: GraphLinkData[];
  centrality: {
    pagerank: Record<string, number>;
    betweenness: Record<string, number>;
  };
  confidence_scores: Record<string, number>;
  syndicates_detected: number;
}

// ==========================================
// CITIZEN CRIME REPORT DTOs
// ==========================================

export interface CrimeReportCreate {
  id?: string;
  victimName: string;
  phoneNumber?: string;
  upiId?: string;
  bankAccount?: string;
  deviceFingerprint?: string;
  typeOfScam: string;
  description: string;
  amountLost: number;
  city?: string;
  state?: string;
}

export interface CrimeReport extends CrimeReportCreate {
  id: string;
  timestamp: string;
  riskScore: number;
  riskBand: string;
}

export interface ReportListResponse {
  reports: CrimeReport[];
  total: number;
}

// ==========================================
// CITIZEN CHAT ADVISOR DTOs
// ==========================================

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  transcript?: string;
}

export interface ChatResponse {
  reply: string;
  risk_score: number;
  risk_band: 'low' | 'needs_review' | 'high';
  flagged_indicators: string[];
  recommended_action: string;
}

// ==========================================
// SYSTEM HEALTH DTOs
// ==========================================

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

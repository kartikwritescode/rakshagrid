// apps/web/src/services/graphService.ts
/**
 * Frontend Service for Module 3: Fraud Network Graph Intelligence APIs.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

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

export interface CentralityResponseData {
  pagerank: Record<string, number>;
  betweenness: Record<string, number>;
  top_influencers: Array<{
    node_id: string;
    type: string;
    label: string;
    pagerank: number;
    betweenness: number;
    degree: number;
  }>;
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

export const graphService = {
  async getNodes(entityType?: string, incidentId?: string, limit: number = 1000): Promise<NodesResponseData> {
    const params = new URLSearchParams();
    if (entityType) params.append('entity_type', entityType);
    if (incidentId) params.append('incident_id', incidentId);
    if (limit) params.append('limit', limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiClient<NodesResponseData>(`${API_ENDPOINTS.GRAPH.NODES}${query}`);
  },

  async getCentrality(topN: number = 15): Promise<CentralityResponseData> {
    return apiClient<CentralityResponseData>(`${API_ENDPOINTS.GRAPH.CENTRALITY}?top_n=${topN}`);
  },

  async getClusters(): Promise<ClustersResponseData> {
    return apiClient<ClustersResponseData>(API_ENDPOINTS.GRAPH.CLUSTERS);
  },

  async getFullGraph(): Promise<FullGraphResponseData> {
    return apiClient<FullGraphResponseData>(API_ENDPOINTS.GRAPH.DATA);
  },

  async getReports(): Promise<{ reports: any[]; total: number }> {
    return apiClient<{ reports: any[]; total: number }>(API_ENDPOINTS.REPORTS);
  },
};

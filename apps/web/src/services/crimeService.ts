// frontend/nextjs/src/services/crimeService.ts
/**
 * Frontend Service for Module 4: VigilGrid Geospatial Crime Intelligence APIs.
 */

import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { HotspotsResponse, PointsResponse, PatrolAllocationResponse } from '../types/apiTypes';

export const crimeService = {
  async getHotspots(): Promise<HotspotsResponse> {
    return apiClient<HotspotsResponse>(API_ENDPOINTS.CRIME.HOTSPOTS);
  },

  async getIncidents(limit: number = 5000): Promise<any> {
    return apiClient<any>(`${API_ENDPOINTS.CRIME.INCIDENTS}?limit=${limit}`);
  },

  async getPoints(limit: number = 5000): Promise<PointsResponse> {
    return apiClient<PointsResponse>(`${API_ENDPOINTS.CRIME.POINTS}?limit=${limit}`);
  },

  async getPatrolAllocation(nUnits: number = 10): Promise<PatrolAllocationResponse> {
    return apiClient<PatrolAllocationResponse>(`${API_ENDPOINTS.CRIME.PATROL_ALLOCATION}?n_units=${nUnits}`);
  },

  async predictCrime(mediaFile?: File, city: string = "Mumbai", description: string = "Cyber Crime"): Promise<any> {
    const formData = new FormData();
    if (mediaFile) formData.append('file', mediaFile);
    formData.append('city', city);
    formData.append('crime_description', description);

    return apiClient<any>(API_ENDPOINTS.CRIME.PREDICT, {
      method: 'POST',
      body: formData,
    });
  }
};

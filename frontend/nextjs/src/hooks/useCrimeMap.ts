// frontend/nextjs/src/hooks/useCrimeMap.ts
/**
 * React Hook for fetching VigilGrid crime hotspots and patrol allocations.
 */

import { useState, useEffect } from 'react';
import { crimeService } from '../services/crimeService';
import { HotspotCluster, IncidentPoint } from '../types/apiTypes';

export function useCrimeMap() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hotspots, setHotspots] = useState<HotspotCluster[]>([]);
  const [points, setPoints] = useState<IncidentPoint[]>([]);

  const fetchCrimeData = async (limit: number = 5000) => {
    setLoading(true);
    setError(null);
    try {
      const [hotspotsData, pointsData] = await Promise.all([
        crimeService.getHotspots(),
        crimeService.getPoints(limit),
      ]);
      setHotspots(hotspotsData.hotspots);
      setPoints(pointsData.points);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch crime intelligence data');
    } finally {
      setLoading(false);
    }
  };

  const allocatePatrols = async (nUnits: number) => {
    try {
      const res = await crimeService.getPatrolAllocation(nUnits);
      setHotspots(res.allocation);
      return res.allocation;
    } catch (err: any) {
      setError(err.message || 'Patrol allocation failed');
      throw err;
    }
  };

  useEffect(() => {
    fetchCrimeData();
  }, []);

  return {
    loading,
    error,
    hotspots,
    points,
    fetchCrimeData,
    allocatePatrols,
  };
}

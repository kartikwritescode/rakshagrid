// apps/web/src/components/map/LeafletCrimeMap.tsx
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

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

export interface LeafletCrimeMapProps {
  incidents: CrimeIncident[];
  selectedIncidentId?: string | null;
  onSelectIncident?: (incident: CrimeIncident) => void;
  showHeatmap?: boolean;
}

export default function LeafletCrimeMap({
  incidents,
  selectedIncidentId,
  onSelectIncident,
  showHeatmap = false,
}: LeafletCrimeMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Record<string, L.Marker>>({});

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (leafletInstanceRef.current) {
        leafletInstanceRef.current.remove();
        leafletInstanceRef.current = null;
      }
    };
  }, []);

  // Initialize or update map markers
  useEffect(() => {
    if (typeof window === 'undefined' || !mapRef.current) return;

    // Initialize map instance once
    if (!leafletInstanceRef.current) {
      // Prevent duplicate initialization on same container
      if ((mapRef.current as any)._leaflet_id) {
        return;
      }

      const map = L.map(mapRef.current).setView([19.0760, 72.8777], 5);

      // Use 100% free OpenStreetMap with dark tactical filter (eliminates Carto watermark)
      // Supports optional CARTO key if user configures NEXT_PUBLIC_CARTO_API_KEY
      const cartoKey = process.env.NEXT_PUBLIC_CARTO_API_KEY;
      const tileUrl = cartoKey
        ? `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?api_key=${cartoKey}`
        : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

      L.tileLayer(tileUrl, {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
        className: cartoKey ? '' : 'map-tiles-dark',
        maxZoom: 19,
      }).addTo(map);

      leafletInstanceRef.current = map;
    }

    const map = leafletInstanceRef.current;
    if (!map) return;

    // Clean existing layers and listeners
    Object.values(markersRef.current).forEach((marker) => {
      marker.off();
      map.removeLayer(marker);
    });
    markersRef.current = {};

    // Render incidents
    incidents.forEach((inc) => {
      const isCritical = inc.severity === 'Critical' || inc.severity === 'High';
      const color = isCritical ? '#e11d48' : '#0ea5e9';

      const customIcon = L.divIcon({
        className: 'custom-leaflet-marker',
        html: `<div style="
          background-color: ${color};
          width: 14px;
          height: 14px;
          border-radius: 50%;
          border: 2px solid #ffffff;
          box-shadow: 0 0 10px ${color};
        "></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      });

      const marker = L.marker([inc.lat, inc.lon], { icon: customIcon }).addTo(map);

      const popupContent = `
        <div style="font-family: monospace; color: #0f172a; padding: 4px;">
          <h4 style="margin: 0; font-weight: bold; color: ${color}; text-transform: uppercase; font-size: 13px;">${inc.crime_type}</h4>
          <p style="margin: 4px 0; font-size: 11px;"><b>City:</b> ${inc.city} (${inc.lat.toFixed(4)}, ${inc.lon.toFixed(4)})</p>
          <p style="margin: 4px 0; font-size: 11px;"><b>Confidence:</b> ${(inc.confidence * 100).toFixed(1)}%</p>
          <p style="margin: 4px 0; font-size: 11px;"><b>Severity:</b> ${inc.severity}</p>
          <p style="margin: 4px 0; font-size: 11px;"><b>Status:</b> ${inc.status}</p>
          <p style="margin: 4px 0; font-size: 11px;"><b>Time:</b> ${inc.timestamp}</p>
        </div>
      `;

      marker.bindPopup(popupContent);
      marker.on('click', () => {
        if (onSelectIncident) onSelectIncident(inc);
      });

      markersRef.current[inc.id] = marker;
    });

    // Pan to selected incident if specified
    if (selectedIncidentId && markersRef.current[selectedIncidentId]) {
      const targetMarker = markersRef.current[selectedIncidentId];
      const latLng = targetMarker.getLatLng();
      map.setView(latLng, 12, { animate: true });
      targetMarker.openPopup();
    }
  }, [incidents, selectedIncidentId, onSelectIncident]);

  return (
    <div className="relative w-full h-full min-h-[500px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
      <div ref={mapRef} className="w-full h-full min-h-[500px] z-0 bg-[#090d16]" />
    </div>
  );
}

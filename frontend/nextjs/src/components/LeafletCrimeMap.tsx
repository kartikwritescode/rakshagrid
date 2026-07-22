import React, { useEffect, useRef, useState } from 'react';
import Head from 'next/head';

declare global {
  interface Window {
    L: any;
  }
}

interface Incident {
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

interface LeafletCrimeMapProps {
  incidents: Incident[];
  selectedIncidentId?: string | null;
  onSelectIncident?: (incident: Incident) => void;
  showHeatmap?: boolean;
}

export default function LeafletCrimeMap({
  incidents,
  selectedIncidentId,
  onSelectIncident,
  showHeatmap = false
}: LeafletCrimeMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletInstanceRef = useRef<any>(null);
  const markersRef = useRef<Record<string, any>>({});
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.async = true;
    script.onload = () => {
      setMapLoaded(true);
    };
    if (window.L) {
      setMapLoaded(true);
    } else {
      document.body.appendChild(script);
    }
  }, []);

  useEffect(() => {
    if (!mapLoaded || !mapRef.current || !window.L) return;

    if (!leafletInstanceRef.current) {
      const L = window.L;
      const map = L.map(mapRef.current).setView([19.0760, 72.8777], 5);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(map);

      leafletInstanceRef.current = map;
    }

    const L = window.L;
    const map = leafletInstanceRef.current;

    Object.values(markersRef.current).forEach((m: any) => map.removeLayer(m));
    markersRef.current = {};

    incidents.forEach((inc) => {
      const isCritical = inc.severity === 'Critical';
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
        iconAnchor: [7, 7]
      });

      const marker = L.marker([inc.lat, inc.lon], { icon: customIcon }).addTo(map);

      const popupContent = `
        <div style="font-family: monospace; color: #0f172a; padding: 4px;">
          <h4 style="margin: 0; font-weight: bold; color: ${color}; uppercase; font-size: 13px;">${inc.crime_type}</h4>
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

    if (selectedIncidentId && markersRef.current[selectedIncidentId]) {
      const targetMarker = markersRef.current[selectedIncidentId];
      const latLng = targetMarker.getLatLng();
      map.setView(latLng, 12, { animate: true });
      targetMarker.openPopup();
    }
  }, [mapLoaded, incidents, selectedIncidentId]);

  return (
    <div className="relative w-full h-full min-h-[500px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
      <div ref={mapRef} className="w-full h-full min-h-[500px] z-0 bg-[#090d16]" />
    </div>
  );
}

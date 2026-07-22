import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import dynamic from 'next/dynamic';
import { MapPin, Filter, Search, RefreshCw, ShieldAlert, Layers } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';
import { crimeService } from '../services/crimeService';

const LeafletCrimeMap = dynamic(
  () => import('../components/LeafletCrimeMap'),
  { ssr: false }
);

export default function MapPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);

  const fetchMapData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await crimeService.getIncidents(5000);
      setIncidents(res.incidents || []);
    } catch (err: any) {
      console.error(err);
      setError('Failed to fetch crime incident points from FastAPI.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMapData();
  }, []);

  const filteredIncidents = incidents.filter(inc => {
    const matchesSearch = inc.crime_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          inc.city.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          inc.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = filterSeverity === 'all' || inc.severity.toLowerCase() === filterSeverity.toLowerCase();
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-6">
      <Head>
        <title>Leaflet Geospatial Crime Intelligence Map | Raksha Grid</title>
      </Head>

      <OnboardingGuide
        pageName="map"
        message="Interactive Leaflet.js Crime Map consuming live incident point cloud and DBSCAN hotspots from FastAPI."
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <MapPin className="w-8 h-8 text-cyan-400" />
            VigilGrid Interactive Crime Map
          </h1>
          <p className="text-slate-400 text-xs font-mono mt-1">
            Displaying {filteredIncidents.length} geocoded crime incidents dynamically from FastAPI
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchMapData}
            className="px-3 py-2 bg-black/40 border border-white/10 hover:bg-white/10 text-cyan-400 text-xs font-mono rounded-xl flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Live Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-1 glass-panel p-5 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-xs uppercase tracking-wider font-mono flex items-center gap-2">
            <Filter className="w-4 h-4 text-cyan-400" /> Map Controls & Filters
          </h3>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <label className="text-[10px] text-slate-500 uppercase block mb-1">Search City or Crime</label>
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g. Mumbai, Theft..."
                  className="w-full bg-black/50 border border-white/10 rounded-xl pl-8 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-500 uppercase block mb-1">Filter Severity</label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical Only</option>
                <option value="moderate">Moderate Only</option>
              </select>
            </div>

            <div className="pt-2 border-t border-white/5 space-y-2">
              <span className="text-[10px] text-slate-500 uppercase block">Incidents List ({filteredIncidents.length})</span>
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {filteredIncidents.slice(0, 15).map(inc => (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncidentId(inc.id)}
                    className={`p-2.5 rounded-xl border transition-all cursor-pointer ${selectedIncidentId === inc.id ? 'bg-cyan-500/20 border-cyan-500 text-white' : 'bg-black/40 border-white/5 text-slate-300 hover:bg-white/5'}`}
                  >
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-[11px] truncate max-w-[140px]">{inc.crime_type}</span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${inc.severity === 'Critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-cyan-500/20 text-cyan-300'}`}>{inc.severity}</span>
                    </div>
                    <p className="text-[9px] text-slate-400 mt-1">{inc.city} | Conf: {(inc.confidence * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-3 min-h-[550px]">
          <LeafletCrimeMap
            incidents={filteredIncidents}
            selectedIncidentId={selectedIncidentId}
            onSelectIncident={(inc) => setSelectedIncidentId(inc.id)}
          />
        </div>
      </div>
    </div>
  );
}

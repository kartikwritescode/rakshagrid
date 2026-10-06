import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Terminal, ShieldCheck, Cpu, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';
import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { SystemHealthResponse } from '../types/apiTypes';

interface TelemetryItem {
  id: string;
  module: string;
  service: string;
  status: string;
  detail: string;
}

export default function PredictionsPage() {
  const [telemetry, setTelemetry] = useState<TelemetryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTelemetry = async () => {
    setLoading(true);
    setError(null);
    try {
      const health = await apiClient<SystemHealthResponse>(API_ENDPOINTS.HEALTH);
      const items: TelemetryItem[] = [
        {
          id: 'mod-1',
          module: 'Module 1 — Currency Classifier',
          service: 'EfficientNetB0 Vision Model',
          status: health.modules?.module1_currency === 'ready' ? 'READY' : health.modules?.module1_currency || 'OFFLINE',
          detail: 'Authenticity & counterfeit security feature analyzer',
        },
        {
          id: 'mod-2',
          module: 'Module 2 — Scam Interceptor',
          service: 'Stacked Ensemble & Rules',
          status: health.modules?.module2_scam === 'ready' ? 'READY' : health.modules?.module2_scam || 'OFFLINE',
          detail: 'Linguistic phishing & coercion classifier with Whisper STT pipeline',
        },
        {
          id: 'mod-3',
          module: 'Module 3 — Fraud Network Graph',
          service: 'GraphSyndicate Intelligence',
          status: 'READY',
          detail: 'Network centrality (PageRank, Betweenness) & Louvain syndicate community detection',
        },
        {
          id: 'mod-4',
          module: 'Module 4 — VigilGrid Crime Engine',
          service: 'DBSCAN Hotspot Engine',
          status: health.modules?.module4_crime === 'ready' ? 'READY' : health.modules?.module4_crime || 'OFFLINE',
          detail: 'Geospatial crime cluster analysis & patrol resource allocation',
        },
      ];
      setTelemetry(items);
    } catch (err: any) {
      console.error('Failed to load telemetry:', err);
      setError('Unable to connect to FastAPI backend service on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, []);

  return (
    <div className="space-y-6">
      <Head>
        <title>Prediction Telemetry Logs | Raksha Grid</title>
      </Head>

      <OnboardingGuide 
        pageName="predictions" 
        message="Real-time model prediction engine status and module diagnostic telemetry queried directly from FastAPI." 
      />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <Cpu className="w-8 h-8 text-cyan-400" />
            Model Prediction Telemetry
          </h1>
          <p className="text-slate-400 text-xs font-mono mt-1">Live status of ML inference services and prediction subsystems</p>
        </div>

        <button
          onClick={fetchTelemetry}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 text-slate-300 rounded-xl text-xs font-mono transition-colors self-start sm:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Status
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs font-mono flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs font-mono animate-pulse">
            Querying backend ML telemetry from FastAPI...
          </div>
        ) : telemetry.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs font-mono">
            No telemetry data available.
          </div>
        ) : (
          <div className="space-y-3 font-mono text-xs">
            {telemetry.map((item) => {
              const isReady = item.status === 'READY';
              return (
                <div key={item.id} className="p-4 bg-black/50 border border-white/5 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-cyan-400 font-bold">{item.module}</span>
                      <span className="text-slate-500 text-[10px]">({item.service})</span>
                    </div>
                    <p className="text-slate-300 mt-1 text-[11px]">{item.detail}</p>
                  </div>
                  <div className="sm:text-right shrink-0">
                    <span className={`px-2.5 py-1 rounded text-[10px] font-bold inline-flex items-center gap-1 ${
                      isReady 
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                        : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                      {isReady && <CheckCircle2 className="w-3 h-3" />}
                      {item.status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

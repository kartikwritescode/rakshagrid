import React from 'react';
import Head from 'next/head';
import { Terminal, ShieldCheck, Cpu } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

export default function PredictionsPage() {
  const mockLogs = [
    { time: '22:48:03', module: 'Module 4 Crime', status: 'SUCCESS', target: 'Mumbai DBSCAN Hotspots', confidence: '0.94' },
    { time: '22:45:12', module: 'Module 2 Scam Interceptor', status: 'SUCCESS', target: 'Call Transcript #8812', confidence: '0.965' },
    { time: '22:40:01', module: 'Module 1 Currency', status: 'SUCCESS', target: 'Banknote Scan #551', confidence: '0.982' }
  ];

  return (
    <div className="space-y-6">
      <Head>
        <title>Prediction Telemetry Logs | Raksha Grid</title>
      </Head>

      <OnboardingGuide pageName="predictions" message="Real-time model prediction execution logs across all 4 ML modules." />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <Cpu className="w-8 h-8 text-cyan-400" />
          Model Prediction Telemetry Logs
        </h1>
      </div>

      <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
        <div className="space-y-3 font-mono text-xs">
          {mockLogs.map((log, idx) => (
            <div key={idx} className="p-4 bg-black/50 border border-white/5 rounded-xl flex items-center justify-between">
              <div>
                <span className="text-cyan-400 font-bold">[{log.time}] {log.module}</span>
                <p className="text-slate-300 mt-1">Target: {log.target}</p>
              </div>
              <div className="text-right">
                <span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 font-bold rounded text-[10px]">{log.status}</span>
                <p className="text-slate-400 text-[10px] mt-1">Confidence: {log.confidence}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

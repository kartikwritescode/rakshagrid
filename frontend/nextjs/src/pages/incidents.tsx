import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Clock, ShieldAlert, CheckCircle2, Search } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';
import { crimeService } from '../services/crimeService';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadIncidents() {
      try {
        setLoading(true);
        const res = await crimeService.getIncidents(100);
        setIncidents(res.incidents || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadIncidents();
  }, []);

  const filtered = incidents.filter(i =>
    i.crime_type.toLowerCase().includes(search.toLowerCase()) ||
    i.city.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <Head>
        <title>Incident History Log | Raksha Grid</title>
      </Head>

      <OnboardingGuide pageName="incidents" message="Historical incident database log queried directly from FastAPI." />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <Clock className="w-8 h-8 text-cyan-400" />
            Historical Incident Telemetry
          </h1>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter incidents..."
            className="w-full bg-black/50 border border-white/10 rounded-xl pl-9 pr-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs text-slate-300">
            <thead>
              <tr className="border-b border-white/10 bg-black/40 text-slate-400 uppercase text-[10px]">
                <th className="p-4">Report ID</th>
                <th className="p-4">Crime Type</th>
                <th className="p-4">Location</th>
                <th className="p-4">Severity</th>
                <th className="p-4">Status</th>
                <th className="p-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filtered.slice(0, 15).map((inc) => (
                <tr key={inc.id} className="hover:bg-white/5 transition-colors">
                  <td className="p-4 text-cyan-400 font-bold">{inc.id}</td>
                  <td className="p-4 text-white font-bold">{inc.crime_type}</td>
                  <td className="p-4">{inc.city}</td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${inc.severity === 'Critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-cyan-500/20 text-cyan-300'}`}>{inc.severity}</span>
                  </td>
                  <td className="p-4">{inc.status}</td>
                  <td className="p-4 text-slate-400">{inc.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

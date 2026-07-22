import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { TableSkeleton } from '../components/Skeleton';
import { 
  Users, 
  User, 
  Smartphone, 
  PhoneCall, 
  Wallet, 
  CreditCard,
  ArrowRight,
  ShieldAlert,
  Network
} from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

interface Cluster {
  id: number;
  nodes: string[];
}

interface AnalysisData {
  communities: Cluster[]; // Matches the backend API field name "communities"
}

export default function ClustersPage() {
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAnalysis() {
      try {
        setLoading(true);
        const res = await fetch('http://localhost:5000/api/graph-analysis');
        if (!res.ok) throw new Error('Failed to load analysis');
        const json = await res.json();
        setAnalysis(json.data || null);
        setError(null);
      } catch (err) {
        console.error(err);
        setError('Connection to backend services failed.');
      } finally {
        setLoading(false);
      }
    }

    fetchAnalysis();
  }, []);

  // Helper to parse entity types in a cluster
  const classifyNodes = (nodeIds: string[]) => {
    const victims: string[] = [];
    const phones: string[] = [];
    const upis: string[] = [];
    const banks: string[] = [];
    const devices: string[] = [];

    nodeIds.forEach(nodeId => {
      const [type, ...parts] = nodeId.split(':');
      const val = parts.join(':');

      if (type === 'victim') victims.push(val);
      else if (type === 'phone') phones.push(val);
      else if (type === 'upi') upis.push(val);
      else if (type === 'bank') banks.push(val);
      else if (type === 'device') devices.push(val);
    });

    return { victims, phones, upis, banks, devices };
  };

  const clusters = analysis?.communities || [];
  
  // Filter for actual fraud rings (size > 5, indicating resource sharing across victims)
  const fraudRings = clusters
    .filter(c => c.nodes.length > 5)
    .map(c => ({
      ...c,
      entities: classifyNodes(c.nodes)
    }))
    .sort((a, b) => b.nodes.length - a.nodes.length); // largest first

  return (
    <div className="space-y-6">
      {/* Onboarding tooltips */}
      <OnboardingGuide 
        pageName="clusters"
        message="This page shows clusters of related fraud cases identified using graph analysis."
      />

      {/* Header */}
      <div>
        <h1 className="text-4xl font-black text-white flex items-center gap-3 tracking-tighter uppercase drop-shadow-lg">
          <Users className="w-8 h-8 text-cyan-500 drop-shadow-[0_0_10px_rgba(6,182,212,0.8)]" />
          Fraud Ring Clusters
        </h1>
        <p className="text-cyan-400/80 font-mono text-xs mt-2 flex items-center gap-2 uppercase tracking-widest">
          Clusters detected via the Louvain Modularity algorithm. High modularity groups represent coordinated syndicates sharing assets.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <TableSkeleton rows={4} />
      ) : fraudRings.length === 0 ? (
        <div className="glass-panel border-white/10 rounded-2xl p-16 text-center text-slate-500 space-y-5 bg-black/40">
          <Network className="w-16 h-16 mx-auto text-cyan-500 animate-pulse drop-shadow-[0_0_15px_rgba(6,182,212,0.5)]" />
          <h3 className="font-bold text-slate-300 text-lg uppercase tracking-widest">No Multi-Victim Fraud Clusters Detected</h3>
          <p className="text-xs max-w-sm mx-auto font-mono text-slate-500 leading-relaxed uppercase">
            All logged reports represent isolated incidents with unique attributes. Coordinated scam clusters will be listed here when shared resources are detected.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {fraudRings.map((ring, idx) => {
            const { victims, phones, upis, banks, devices } = ring.entities;
            return (
              <div 
                key={ring.id} 
                className="glass-panel bg-black/40 border-white/10 rounded-2xl p-6 flex flex-col justify-between hover:border-cyan-500/50 hover:shadow-[0_0_30px_rgba(6,182,212,0.15)] transition-all group"
              >
                <div className="space-y-6">
                  {/* Title card */}
                  <div className="flex justify-between items-start border-b border-white/10 pb-4">
                    <div>
                      <h3 className="text-xl font-black text-white flex items-center gap-3 uppercase tracking-widest group-hover:text-cyan-400 transition-colors">
                        <ShieldAlert className="w-5 h-5 text-rose-500 group-hover:animate-pulse" />
                        Fraud Cluster #{idx + 1}
                      </h3>
                      <span className="text-[10px] text-cyan-500/70 font-mono uppercase tracking-widest">Cluster ID: {ring.id}</span>
                    </div>
                    <span className="px-3 py-1.5 text-[10px] font-bold bg-rose-950/40 border border-rose-500/50 text-rose-400 rounded-md shadow-[0_0_10px_rgba(225,29,72,0.2)] uppercase tracking-widest">
                      {victims.length} Victims Linked
                    </span>
                  </div>

                  {/* Ring Entities Classifications */}
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3 text-xs text-slate-400">
                      <div className="bg-black/60 p-3 rounded-xl border border-white/5 shadow-inner">
                        <span className="block text-[9px] text-yellow-500/80 uppercase font-bold tracking-widest mb-1.5 flex items-center gap-1.5"><Wallet className="w-3 h-3" /> UPI Mules</span>
                        <div className="font-mono text-yellow-400 font-bold text-sm">{upis.length || 0} handles</div>
                      </div>
                      <div className="bg-black/60 p-3 rounded-xl border border-white/5 shadow-inner">
                        <span className="block text-[9px] text-emerald-500/80 uppercase font-bold tracking-widest mb-1.5 flex items-center gap-1.5"><CreditCard className="w-3 h-3" /> Mule Accounts</span>
                        <div className="font-mono text-emerald-400 font-bold text-sm">{banks.length || 0} accounts</div>
                      </div>
                      <div className="bg-black/60 p-3 rounded-xl border border-white/5 shadow-inner">
                        <span className="block text-[9px] text-rose-500/80 uppercase font-bold tracking-widest mb-1.5 flex items-center gap-1.5"><Smartphone className="w-3 h-3" /> Device IDs</span>
                        <div className="font-mono text-rose-400 font-bold text-sm">{devices.length || 0} emulators</div>
                      </div>
                      <div className="bg-black/60 p-3 rounded-xl border border-white/5 shadow-inner">
                        <span className="block text-[9px] text-amber-500/80 uppercase font-bold tracking-widest mb-1.5 flex items-center gap-1.5"><PhoneCall className="w-3 h-3" /> Phone Links</span>
                        <div className="font-mono text-amber-400 font-bold text-sm">{phones.length || 0} numbers</div>
                      </div>
                    </div>

                    {/* Victims List preview */}
                    <div className="space-y-2 pt-2 border-t border-white/5">
                      <span className="text-[10px] text-cyan-500 uppercase font-bold tracking-widest block flex items-center gap-2">
                        <span className="w-1 h-1 bg-cyan-500 rounded-full"></span> Linked Victims
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {victims.map((name, i) => (
                          <div 
                            key={i} 
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-[10px] rounded-md font-bold uppercase tracking-wider shadow-inner"
                          >
                            <User className="w-3 h-3 text-cyan-400" />
                            <span>{name}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Shared entities preview */}
                    {(upis.length > 0 || devices.length > 0) && (
                      <div className="space-y-2 pt-4 border-t border-white/5 mt-2">
                        <span className="text-[10px] text-rose-500 uppercase font-bold tracking-widest block flex items-center gap-2">
                          <span className="w-1 h-1 bg-rose-500 rounded-full animate-pulse"></span> Primary Infrastructure Hubs
                        </span>
                        <div className="space-y-1.5 text-[11px] text-slate-300 bg-black/40 p-3 rounded-xl shadow-inner border border-white/5">
                          {upis.slice(0, 1).map((upi, i) => (
                            <div key={i} className="flex items-center gap-3">
                              <Wallet className="w-3.5 h-3.5 text-yellow-500" />
                              <span className="font-mono text-yellow-400 font-bold tracking-widest uppercase">{upi}</span>
                            </div>
                          ))}
                          {devices.slice(0, 1).map((dev, i) => (
                            <div key={i} className="flex items-center gap-3">
                              <Smartphone className="w-3.5 h-3.5 text-rose-500" />
                              <span className="font-mono text-rose-400 font-bold tracking-widest uppercase">{dev}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Open Packet Button */}
                <div className="pt-6 mt-6 border-t border-white/10">
                  <Link
                    href={`/intelligence?node=victim:${victims[0]}`}
                    className="btn-primary w-full flex items-center justify-center gap-3 uppercase tracking-widest text-[10px] py-3"
                  >
                    Investigate Syndicate Network
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

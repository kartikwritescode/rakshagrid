import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { TableSkeleton } from '../components/Skeleton';
import { Users, ArrowRight, ShieldAlert } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

interface Cluster {
  id: number;
  nodes: string[];
}

export default function ClustersPage() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setClusters([
      { id: 1, nodes: ['phone:+919876543210', 'device:dev_8f21a', 'victim:VIC-9021', 'victim:VIC-4412'] },
      { id: 2, nodes: ['upi:scam@okaxis', 'account:501002345678', 'victim:VIC-9021'] }
    ]);
    setLoading(false);
  }, []);

  return (
    <div className="space-y-6">
      <OnboardingGuide 
        pageName="clusters"
        message="Clusters represent grouped suspicious entities identified across multiple reports."
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <Users className="w-8 h-8 text-cyan-400" />
            Detected Fraud Clusters
          </h1>
          <p className="text-slate-400 text-xs font-mono mt-1">
            Mule rings and infrastructure networks
          </p>
        </div>
      </div>

      {loading ? (
        <TableSkeleton />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {clusters.map((cluster) => (
            <div key={cluster.id} className="glass-panel p-6 rounded-2xl border-white/5 space-y-4 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between border-b border-white/5 pb-3">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-rose-500" />
                  <h3 className="font-bold text-white font-mono text-sm uppercase">Cluster #{cluster.id}</h3>
                </div>
                <span className="text-xs text-cyan-400 font-mono font-bold">{cluster.nodes.length} Linked Entities</span>
              </div>

              <div className="space-y-2">
                <p className="text-[10px] text-slate-500 uppercase font-mono">Linked Entity IDs</p>
                <div className="flex flex-wrap gap-2">
                  {cluster.nodes.map((node, i) => (
                    <span key={i} className="px-2.5 py-1 rounded bg-black/40 border border-white/10 text-xs font-mono text-slate-300">
                      {node}
                    </span>
                  ))}
                </div>
              </div>

              <Link
                href={`/chat?cluster=${cluster.id}`}
                className="inline-flex items-center gap-2 text-xs text-cyan-400 font-bold hover:underline font-mono pt-2"
              >
                Open Cluster Intelligence Chat
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

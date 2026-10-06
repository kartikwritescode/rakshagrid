import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { TableSkeleton } from '../components/common/Skeleton';
import { Users, ArrowRight, ShieldAlert, Database } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';
import { graphService, ClusterItemData } from '../services/graphService';

export default function ClustersPage() {
  const [clusters, setClusters] = useState<ClusterItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchClusters() {
      try {
        setLoading(true);
        const data = await graphService.getClusters();
        setClusters(data.clusters || []);
        setError(null);
      } catch (err) {
        console.error('Failed to load clusters:', err);
        setError('Failed to fetch syndicate clusters.');
      } finally {
        setLoading(false);
      }
    }
    fetchClusters();
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
            Mule rings and infrastructure networks ({clusters.length} active communities)
          </p>
        </div>
      </div>

      {loading ? (
        <TableSkeleton />
      ) : clusters.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl border-white/5 text-center flex flex-col items-center justify-center space-y-3">
          <Database className="w-10 h-10 text-slate-600 animate-pulse" />
          <h3 className="text-base font-bold text-slate-300">No Syndicate Clusters Detected</h3>
          <p className="text-xs text-slate-500 max-w-md font-mono">
            No connected crime syndicates or multi-victim rings have been discovered yet.
            Clusters will automatically form as matching payment and contact nodes are registered.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {clusters.map((cluster) => (
            <div key={cluster.id} className="glass-panel p-6 rounded-2xl border-white/5 space-y-4 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between border-b border-white/5 pb-3">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-rose-500" />
                  <h3 className="font-bold text-white font-mono text-sm uppercase">Syndicate Ring #{cluster.id}</h3>
                </div>
                <div className="flex items-center gap-3">
                  {cluster.risk_score && (
                    <span className="text-[10px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded font-mono font-bold">
                      Risk: {(cluster.risk_score * 100).toFixed(0)}%
                    </span>
                  )}
                  <span className="text-xs text-cyan-400 font-mono font-bold">{cluster.size} Entities</span>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-[10px] text-slate-500 uppercase font-mono">Linked Entity IDs</p>
                <div className="flex flex-wrap gap-2">
                  {cluster.nodes.map((node) => (
                    <span 
                      key={node}
                      className="px-2.5 py-1 bg-slate-900 border border-slate-800 text-slate-300 text-xs font-mono rounded-lg break-all"
                    >
                      {node}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <Link
                  href={`/graph`}
                  className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-mono font-bold uppercase tracking-wider"
                >
                  Explore in Graph Explorer
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect, useCallback } from 'react';
import GraphView from '../components/graph/GraphView';
import { GraphSkeleton } from '../components/common/Skeleton';
import Link from 'next/link';
import { Network, Search, ShieldAlert, ArrowRight, Database, RefreshCw, Filter } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';
import { graphService, GraphNodeData, GraphLinkData } from '../services/graphService';

const ENTITY_TYPES = ['All', 'Victim', 'Phone', 'UPI', 'BankAccount', 'Device'] as const;

export default function GraphPage() {
  const [nodes, setNodes] = useState<GraphNodeData[]>([]);
  const [links, setLinks] = useState<GraphLinkData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEntityType, setSelectedEntityType] = useState<string>('All');

  const fetchGraphData = useCallback(async (entityType?: string) => {
    try {
      setLoading(true);
      setError(null);
      const filterType = entityType && entityType !== 'All' ? entityType : undefined;
      const data = await graphService.getNodes(filterType);
      setNodes(data.nodes || []);
      setLinks(data.links || []);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.message || 'Failed to load graph data from server.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGraphData(selectedEntityType);
  }, [fetchGraphData, selectedEntityType]);

  const filteredNodes = searchQuery.trim()
    ? nodes.filter(n => n.id.toLowerCase().includes(searchQuery.toLowerCase()) || n.label.toLowerCase().includes(searchQuery.toLowerCase()))
    : nodes;

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <div className="space-y-6">
      <OnboardingGuide 
        pageName="graph"
        message="Interactive graph visualization of multi-entity fraud networks with real-time community discovery."
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <Network className="w-8 h-8 text-cyan-400" />
            Network Graph Explorer
          </h1>
          <p className="text-slate-400 text-xs font-mono mt-1">
            Visualizing {nodes.length} registered nodes and {links.length} connections
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search node ID or label..."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <button
            onClick={() => fetchGraphData(selectedEntityType)}
            disabled={loading}
            className="flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 rounded-lg text-xs font-mono transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Entity Type Filter Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs font-mono">
        <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0" />
        <span className="text-slate-500 uppercase text-[10px] shrink-0">Filter:</span>
        {ENTITY_TYPES.map((type) => (
          <button
            key={type}
            onClick={() => setSelectedEntityType(type)}
            className={`px-3 py-1 rounded-full text-xs transition-colors shrink-0 ${
              selectedEntityType === type
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                : 'bg-black/40 text-slate-400 border border-white/5 hover:bg-white/5 hover:text-white'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs font-mono">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 h-[600px] glass-panel rounded-2xl overflow-hidden p-2 relative">
          {loading ? (
            <GraphSkeleton />
          ) : nodes.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-6 space-y-3">
              <Database className="w-12 h-12 text-slate-600 animate-pulse" />
              <h3 className="text-lg font-bold text-slate-300">Graph Registry is Empty</h3>
              <p className="text-xs text-slate-500 max-w-md font-mono">
                No incident reports or connections are currently registered in the database.
                Submit citizen reports to dynamically construct syndicate intelligence.
              </p>
              <Link
                href="/citizen-shield"
                className="mt-2 inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider transition-colors"
              >
                Submit Incident Report
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ) : (
            <GraphView
              nodes={filteredNodes}
              links={links}
              selectedNodeId={selectedNodeId}
              onNodeSelect={(id) => setSelectedNodeId(id)}
            />
          )}
        </div>

        <div className="lg:col-span-1 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border-white/5 space-y-4">
            <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Node Inspector
            </h3>

            {selectedNode ? (
              <div className="space-y-3 font-mono text-xs">
                <div>
                  <span className="text-slate-500 uppercase text-[10px]">Node ID</span>
                  <p className="text-cyan-300 font-bold break-all">{selectedNode.id}</p>
                </div>
                <div>
                  <span className="text-slate-500 uppercase text-[10px]">Type</span>
                  <p className="text-slate-200">{selectedNode.type}</p>
                </div>
                <div>
                  <span className="text-slate-500 uppercase text-[10px]">Label</span>
                  <p className="text-slate-200">{selectedNode.label}</p>
                </div>
                <Link
                  href={`/intelligence?node=${selectedNode.id}`}
                  className="inline-flex items-center gap-1.5 w-full justify-center px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-bold uppercase text-[10px] tracking-wider transition-colors"
                >
                  Investigate Node
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ) : (
              <p className="text-xs text-slate-500 font-mono">
                Click any node on the graph canvas to inspect syndicate connections and properties.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

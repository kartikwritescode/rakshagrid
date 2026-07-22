import React, { useState, useEffect } from 'react';
import GraphView from '../components/GraphView';
import { GraphSkeleton } from '../components/Skeleton';
import Link from 'next/link';
import { Network, Search, ShieldAlert, ArrowRight, Info, Eye, Layers } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

interface Report {
  victimId: string;
  victimName: string;
  phoneNumber: string;
  upiId: string;
  bankAccount: string;
  deviceFingerprint: string;
}

interface AnalysisData {
  centrality: {
    pagerank: Record<string, number>;
    betweenness: Record<string, number>;
  };
  "confidence scores": Record<string, number>;
}

interface Node {
  id: string;
  type: string;
  label: string;
}

interface LinkType {
  source: string;
  target: string;
}

export default function GraphPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // View mode toggle
  const [viewMode, setViewMode] = useState<'pyvis' | 'canvas'>('pyvis');

  // Interactive selected state
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // Fetch reports
        const reportsRes = await fetch('http://localhost:5000/api/report');
        if (!reportsRes.ok) throw new Error('Failed to load reports');
        const reportsJson = await reportsRes.json();
        setReports(reportsJson.data || []);

        // Fetch graph analysis (which also regenerates graph.html on the fly)
        const analysisRes = await fetch('http://localhost:5000/api/graph-analysis');
        if (!analysisRes.ok) throw new Error('Failed to load graph analysis');
        const analysisJson = await analysisRes.json();
        setAnalysis(analysisJson.data || null);
        
        setError(null);
      } catch (err) {
        console.error(err);
        setError('Connection to backend services failed.');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // Construct graph nodes and links from MongoDB reports
  const nodesMap = new Map<string, Node>();
  const links: LinkType[] = [];

  reports.forEach(report => {
    const vicId = `victim:${report.victimId}`;
    if (!nodesMap.has(vicId)) {
      nodesMap.set(vicId, { id: vicId, type: 'Victim', label: report.victimName });
    }

    if (report.phoneNumber && report.phoneNumber.trim()) {
      const pId = `phone:${report.phoneNumber.trim()}`;
      if (!nodesMap.has(pId)) {
        nodesMap.set(pId, { id: pId, type: 'Phone', label: report.phoneNumber });
      }
      links.push({ source: vicId, target: pId });
    }

    if (report.upiId && report.upiId.trim()) {
      const uId = `upi:${report.upiId.trim()}`;
      if (!nodesMap.has(uId)) {
        nodesMap.set(uId, { id: uId, type: 'UPI', label: report.upiId });
      }
      links.push({ source: vicId, target: uId });
    }

    if (report.bankAccount && report.bankAccount.trim()) {
      const bId = `bank:${report.bankAccount.trim()}`;
      if (!nodesMap.has(bId)) {
        nodesMap.set(bId, { id: bId, type: 'BankAccount', label: report.bankAccount });
      }
      links.push({ source: vicId, target: bId });
    }

    if (report.deviceFingerprint && report.deviceFingerprint.trim()) {
      const dId = `device:${report.deviceFingerprint.trim()}`;
      if (!nodesMap.has(dId)) {
        nodesMap.set(dId, { id: dId, type: 'Device', label: report.deviceFingerprint });
      }
      links.push({ source: vicId, target: dId });
    }
  });

  const nodes = Array.from(nodesMap.values());

  // Search filter
  const filteredNodes = searchQuery.trim()
    ? nodes.filter(n => n.label.toLowerCase().includes(searchQuery.toLowerCase()) || n.id.toLowerCase().includes(searchQuery.toLowerCase()))
    : [];

  // Selected node details
  const selectedNode = selectedNodeId ? nodesMap.get(selectedNodeId) : null;
  const pagerank = selectedNodeId && analysis ? analysis.centrality.pagerank[selectedNodeId] : null;
  const betweenness = selectedNodeId && analysis ? analysis.centrality.betweenness[selectedNodeId] : null;
  const confidence = selectedNodeId && analysis ? analysis["confidence scores"][selectedNodeId] : null;

  // Calculate degrees for the selected node
  const degree = selectedNodeId 
    ? links.filter(l => l.source === selectedNodeId || l.target === selectedNodeId).length
    : 0;

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* Onboarding tooltips */}
      <OnboardingGuide 
        pageName="graph"
        message="This page visualizes the relationships between victims, devices, phone numbers, bank accounts, and UPI IDs."
      />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 relative z-10">
        <div>
          <h1 className="text-4xl font-black text-white flex items-center gap-3 tracking-tighter uppercase drop-shadow-lg">
            <Network className="w-8 h-8 text-cyan-500 drop-shadow-[0_0_10px_rgba(6,182,212,0.8)]" />
            Network Graph Explorer
          </h1>
          <p className="text-cyan-400/80 font-mono text-xs mt-2 flex items-center gap-2 uppercase tracking-widest">
            Visual connection mapping. Select view modes, zoom to inspect details, and hover over elements to read telemetry.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 relative z-10 w-full md:w-auto">
          {/* View Mode Toggle */}
          <div className="glass-panel p-1 rounded-xl flex justify-center sm:justify-start items-center gap-1 border-white/10">
            <button
              onClick={() => setViewMode('pyvis')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all uppercase tracking-wider ${
                viewMode === 'pyvis'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              PyVis Graph
            </button>
            <button
              onClick={() => setViewMode('canvas')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all uppercase tracking-wider ${
                viewMode === 'canvas'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              Canvas View
            </button>
          </div>

          {/* Search */}
          <div className="relative w-full md:w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search entities (e.g. UPI, Device)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
            {searchQuery && filteredNodes.length > 0 && (
              <div className="absolute top-11 left-0 z-20 w-full bg-slate-900 border border-slate-800 rounded-lg max-h-48 overflow-y-auto shadow-2xl divide-y divide-slate-800/40">
                {filteredNodes.map(node => (
                  <button
                    key={node.id}
                    onClick={() => {
                      setSelectedNodeId(node.id);
                      setSearchQuery('');
                    }}
                    className="w-full text-left px-4 py-2.5 hover:bg-slate-800/50 text-xs text-slate-300 transition-colors flex justify-between items-center"
                  >
                    <span className="truncate font-semibold">{node.label}</span>
                    <span className="text-[10px] text-slate-500 uppercase">{node.type}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Main split layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow min-h-[500px]">
        {/* Graph Render Container */}
        <div className="lg:col-span-3 h-[600px] relative">
          {loading ? (
            <GraphSkeleton />
          ) : viewMode === 'pyvis' ? (
            <div className="w-full h-full rounded-2xl border border-white/10 overflow-hidden bg-black/60 backdrop-blur-xl relative shadow-[0_0_30px_rgba(0,0,0,0.5)]">
              {/* Legend overlay inside PyVis */}
              <div className="absolute top-4 left-4 z-10 glass-panel p-4 rounded-xl text-[10px] uppercase font-mono tracking-widest space-y-3 select-none pointer-events-none border-cyan-500/20 bg-black/60">
                <h4 className="font-bold text-cyan-400 border-b border-white/10 pb-2 mb-2 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span> Network Legend
                </h4>
                <div className="flex items-center gap-3 text-slate-300">
                  <span className="w-3 h-3 rounded-full bg-[#0ea5e9] shadow-[0_0_8px_#0ea5e9] inline-block"></span>
                  <span>Victims</span>
                </div>
                <div className="flex items-center gap-3 text-slate-300">
                  <span className="w-3 h-3 rounded-full bg-[#f59e0b] shadow-[0_0_8px_#f59e0b] inline-block"></span>
                  <span>Phones</span>
                </div>
                <div className="flex items-center gap-3 text-slate-300">
                  <span className="w-3 h-3 rounded-full bg-[#8b5cf6] shadow-[0_0_8px_#8b5cf6] inline-block"></span>
                  <span>UPI handles</span>
                </div>
                <div className="flex items-center gap-3 text-slate-300">
                  <span className="w-3 h-3 rounded-full bg-[#10b981] shadow-[0_0_8px_#10b981] inline-block"></span>
                  <span>Bank Accounts</span>
                </div>
                <div className="flex items-center gap-3 text-slate-300">
                  <span className="w-3 h-3 rounded-full bg-[#e11d48] shadow-[0_0_8px_#e11d48] inline-block"></span>
                  <span>Devices</span>
                </div>
              </div>
              
              <iframe
                src="/graph.html"
                className="w-full h-full border-0"
                title="PyVis Fraud Connection Graph"
              />
            </div>
          ) : (
            <GraphView
              nodes={nodes}
              links={links}
              selectedNodeId={selectedNodeId}
              onNodeSelect={setSelectedNodeId}
            />
          )}
        </div>

        {/* Sidebar Info Panel */}
        <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between h-[600px] overflow-y-auto bg-black/40">
          {selectedNode ? (
            <div className="space-y-6">
              <div>
                <span className="inline-block px-3 py-1 rounded-md text-[10px] font-bold bg-cyan-900/30 text-cyan-400 border border-cyan-500/20 uppercase tracking-widest mb-3 shadow-inner">
                  {selectedNode.type} Node
                </span>
                <h3 className="text-2xl font-black text-white break-all tracking-tight drop-shadow-md">{selectedNode.label}</h3>
                <p className="text-slate-500 font-mono text-[11px] mt-2 break-all">{selectedNode.id}</p>
              </div>

              {/* Centrality Metrics */}
              <div className="space-y-3.5 border-t border-white/10 pt-5">
                <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono flex items-center gap-2">
                  <span className="w-1 h-1 bg-blue-500 rounded-full" /> Network Centralities
                </h4>
                
                <div className="flex justify-between items-center bg-black/40 border border-white/5 p-3 rounded-xl shadow-inner">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">Degree</span>
                  <span className="text-sm font-bold text-white font-mono">{degree} edges</span>
                </div>

                <div className="flex justify-between items-center bg-black/40 border border-white/5 p-3 rounded-xl shadow-inner">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">PageRank</span>
                  <span className="text-sm font-bold text-cyan-400 font-mono">
                    {pagerank !== null && pagerank !== undefined ? pagerank.toFixed(5) : '0.00000'}
                  </span>
                </div>

                <div className="flex justify-between items-center bg-black/40 border border-white/5 p-3 rounded-xl shadow-inner">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">Betweenness</span>
                  <span className="text-sm font-bold text-purple-400 font-mono">
                    {betweenness !== null && betweenness !== undefined ? betweenness.toFixed(5) : '0.00000'}
                  </span>
                </div>
              </div>

              {/* Confidence Risk Score */}
              {selectedNode.type !== 'Victim' && (
                <div className="space-y-4 border-t border-white/10 pt-5">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono flex items-center gap-2">
                    <span className="w-1 h-1 bg-rose-500 rounded-full animate-pulse" /> Fraud Risk Engine
                  </h4>
                  
                  {confidence !== null && confidence !== undefined ? (
                    <div className="bg-rose-950/40 border border-rose-500/30 p-5 rounded-xl space-y-3 shadow-[0_0_15px_rgba(225,29,72,0.1)] relative overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-br from-rose-500/10 to-transparent pointer-events-none"></div>
                      <div className="flex justify-between items-center relative z-10">
                        <span className="text-[10px] uppercase tracking-widest text-rose-300 font-bold flex items-center gap-2">
                          <ShieldAlert className="w-4 h-4 text-rose-400 animate-pulse" />
                          Risk Confidence
                        </span>
                        <span className="text-2xl font-black text-rose-400 drop-shadow-md">{(confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-black/50 rounded-full h-1.5 relative z-10 border border-white/5">
                        <div className="bg-rose-500 h-1.5 rounded-full shadow-[0_0_8px_#e11d48]" style={{ width: `${confidence * 100}%` }}></div>
                      </div>
                      <p className="text-[10px] text-rose-300/80 leading-relaxed font-mono uppercase tracking-wider relative z-10">
                        This entity is shared by multiple victims. High risk indicator.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-emerald-950/40 border border-emerald-500/30 p-4 rounded-xl text-emerald-400 text-xs flex gap-3 shadow-inner">
                      <Info className="w-4 h-4 flex-shrink-0" />
                      <span className="font-mono uppercase tracking-widest text-[10px]">Not shared. Degree is low. Safe / Unlinked.</span>
                    </div>
                  )}
                </div>
              )}
              
              {/* Investigate Action */}
              <div className="pt-4 border-t border-white/10">
                <Link
                  href={`/intelligence?node=${selectedNode.id}`}
                  className="btn-primary w-full flex items-center justify-center gap-2 uppercase tracking-widest text-[10px]"
                >
                  View Intelligence Packet
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center h-full text-slate-500">
              <Network className="w-12 h-12 mb-3 text-slate-700 animate-pulse" />
              <h4 className="font-semibold text-slate-400 mb-1">Select an Entity</h4>
              <p className="text-xs max-w-[200px]">
                {viewMode === 'canvas' 
                  ? 'Click on any node in the canvas layout to audit its centralities and risk scores.' 
                  : 'Search for an entity inside the input box to examine specific risk score details.'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

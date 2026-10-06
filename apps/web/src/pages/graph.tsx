import React, { useState, useEffect } from 'react';
import GraphView from '../components/GraphView';
import { GraphSkeleton } from '../components/Skeleton';
import Link from 'next/link';
import { Network, Search, ShieldAlert, ArrowRight } from 'lucide-react';
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
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const mockReports: Report[] = [
          { victimId: 'VIC-9021', victimName: 'Ramesh Kumar', phoneNumber: '+91 98765 43210', upiId: 'scam@okaxis', bankAccount: '501002345678', deviceFingerprint: 'dev_8f21a' },
          { victimId: 'VIC-4412', victimName: 'Priya Sharma', phoneNumber: '+91 98112 33445', upiId: 'refund@paytm', bankAccount: '309911223344', deviceFingerprint: 'dev_11b4c' }
        ];
        setReports(mockReports);

        setAnalysis({
          centrality: {
            pagerank: { "phone:+919876543210": 0.12, "device:dev_8f21a": 0.18 },
            betweenness: { "phone:+919876543210": 0.25, "device:dev_8f21a": 0.35 }
          },
          "confidence scores": { "phone:+919876543210": 0.92, "device:dev_8f21a": 0.88 }
        });
        setError(null);
      } catch (err) {
        console.error('Fetch error:', err);
        setError('Failed to load graph data.');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const nodesMap = new Map<string, Node>();
  const links: LinkType[] = [];

  reports.forEach(r => {
    const vId = `victim:${r.victimId}`;
    if (!nodesMap.has(vId)) {
      nodesMap.set(vId, { id: vId, type: 'Victim', label: r.victimName || r.victimId });
    }

    if (r.phoneNumber) {
      const pId = `phone:${r.phoneNumber}`;
      if (!nodesMap.has(pId)) nodesMap.set(pId, { id: pId, type: 'Phone', label: r.phoneNumber });
      links.push({ source: vId, target: pId });
    }

    if (r.upiId) {
      const uId = `upi:${r.upiId}`;
      if (!nodesMap.has(uId)) nodesMap.set(uId, { id: uId, type: 'UPI', label: r.upiId });
      links.push({ source: vId, target: uId });
    }

    if (r.bankAccount) {
      const bId = `account:${r.bankAccount}`;
      if (!nodesMap.has(bId)) nodesMap.set(bId, { id: bId, type: 'BankAccount', label: r.bankAccount });
      links.push({ source: vId, target: bId });
    }

    if (r.deviceFingerprint) {
      const dId = `device:${r.deviceFingerprint}`;
      if (!nodesMap.has(dId)) nodesMap.set(dId, { id: dId, type: 'Device', label: r.deviceFingerprint });
      links.push({ source: vId, target: dId });
    }
  });

  const nodes = Array.from(nodesMap.values());
  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <div className="space-y-6">
      <OnboardingGuide 
        pageName="graph"
        message="Interactive graph visualization of victim-scammer connections."
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <Network className="w-8 h-8 text-cyan-400" />
            Network Graph Explorer
          </h1>
          <p className="text-slate-400 text-xs font-mono mt-1">
            Visualizing {nodes.length} nodes and {links.length} connections
          </p>
        </div>

        <div className="relative w-full md:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search node ID..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 h-[600px] glass-panel rounded-2xl overflow-hidden p-2">
          {loading ? (
            <GraphSkeleton />
          ) : (
            <GraphView
              nodes={nodes}
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
                <Link
                  href={`/intelligence?node=${selectedNode.id}`}
                  className="inline-flex items-center gap-1.5 w-full justify-center px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-bold uppercase text-[10px] tracking-wider transition-colors"
                >
                  Investigate Node
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ) : (
              <p className="text-xs text-slate-500 font-mono">Click any node on the graph canvas to inspect details.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

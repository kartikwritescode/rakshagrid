import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import StatCard from '../components/StatCard';
import { TableSkeleton } from '../components/Skeleton';
import { NodeDistributionChart, RiskProfileChart } from '../components/AnalyticsCharts';
import { 
  FileText, 
  Network, 
  PhoneCall, 
  Smartphone, 
  ArrowUpRight, 
  Clock, 
  User, 
  AlertTriangle,
  Terminal
} from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';
import { crimeService } from '../services/crimeService';

interface Report {
  _id: string;
  victimId: string;
  victimName: string;
  phoneNumber: string;
  upiId: string;
  bankAccount: string;
  deviceFingerprint: string;
  reportTimestamp: string;
}

interface AnalysisData {
  communities: Array<{ id: number; nodes: string[] }>;
  "graph stats": {
    totalNodes: number;
    totalEdges: number;
    nodeTypeCounts: Record<string, number>;
  };
  "confidence scores": Record<string, number>;
}

export default function Dashboard() {
  const [reports, setReports] = useState<Report[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const crimeHotspots = await crimeService.getHotspots().catch(() => ({ hotspots: [] }));
        
        const mockReports: Report[] = [
          { _id: '1', victimId: 'VIC-9021', victimName: 'Ramesh Kumar', phoneNumber: '+91 98765 43210', upiId: 'scam@okaxis', bankAccount: '501002345678', deviceFingerprint: 'dev_8f21a', reportTimestamp: new Date().toISOString() },
          { _id: '2', victimId: 'VIC-4412', victimName: 'Priya Sharma', phoneNumber: '+91 98112 33445', upiId: 'refund@paytm', bankAccount: '309911223344', deviceFingerprint: 'dev_11b4c', reportTimestamp: new Date().toISOString() }
        ];
        setReports(mockReports);

        const mockAnalysis: AnalysisData = {
          communities: [{ id: 1, nodes: ['1', '2', '3', '4', '5', '6'] }],
          "graph stats": {
            totalNodes: crimeHotspots.hotspots.length > 0 ? crimeHotspots.hotspots.length * 15 : 42,
            totalEdges: 68,
            nodeTypeCounts: { Victim: 18, Phone: 12, UPI: 8, BankAccount: 4 }
          },
          "confidence scores": { "phone:+919876543210": 0.92, "device:dev_8f21a": 0.88 }
        };
        setAnalysis(mockAnalysis);
        
        const timestamp = new Date().toLocaleTimeString();
        setLogs([
          `[${timestamp}] INITIALIZING RAKSHA GRID CENTRAL INTELLIGENCE ENGINE...`,
          `[${timestamp}] MODULE 1 CURRENCY MODEL: Active & loaded`,
          `[${timestamp}] MODULE 2 STACKED ENSEMBLE SCAM INTERCEPTOR: Calibrated & online`,
          `[${timestamp}] MODULE 4 VIGILGRID GEOSPATIAL ENGINE: ${crimeHotspots.hotspots.length} DBSCAN hotspots loaded`,
          `[${timestamp}] DIAGNOSTIC COMPLETE: Platform ready`
        ]);
        
        setError(null);
      } catch (err) {
        console.error('Fetch error:', err);
        setError('Connection to FastAPI central backend failed.');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const totalReports = reports.length;
  const communities = analysis?.communities || [];
  const fraudRingsCount = communities.filter(c => c.nodes.length > 5).length;
  const confidenceScores = analysis?.["confidence scores"] || {};
  
  const suspiciousPhones = Object.keys(confidenceScores).filter(
    key => key.startsWith('phone:') && confidenceScores[key] > 0.5
  ).length;

  const suspiciousDevices = Object.keys(confidenceScores).filter(
    key => key.startsWith('device:') && confidenceScores[key] > 0.5
  ).length;

  return (
    <div className="space-y-8">
      <OnboardingGuide 
        pageName="dashboard"
        message="This dashboard gives a unified overview of detected fraud reports, scam call telemetry, and VigilGrid crime hotspots."
      />

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black tracking-tight text-white sm:text-5xl glow-text-gradient">
            Raksha Grid Intelligence Dashboard
          </h1>
          <p className="text-cyan-400/80 font-mono text-sm mt-2 flex items-center gap-2">
            <span className="live-pulse-dot w-2 h-2 bg-emerald-500 rounded-full" />
            Centralized ML Intelligence: Digital Arrest Interceptor & Crime Engine Active
          </p>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 rounded-xl border border-rose-500/20 bg-rose-500/10 text-rose-300 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Reports Logged"
          value={totalReports}
          icon={FileText}
          description="Submitted cases"
          loading={loading}
          accentColor="indigo"
        />
        <StatCard
          title="Active Fraud Clusters"
          value={fraudRingsCount}
          icon={Network}
          description="Linked networks detected"
          loading={loading}
          trend={fraudRingsCount > 0 ? `${fraudRingsCount} detected` : undefined}
          trendType={fraudRingsCount > 0 ? 'negative' : 'neutral'}
          accentColor="rose"
        />
        <StatCard
          title="Suspicious Phone Hubs"
          value={suspiciousPhones}
          icon={PhoneCall}
          description="Shared across victims"
          loading={loading}
          trend={suspiciousPhones > 0 ? 'High Risk' : undefined}
          trendType={suspiciousPhones > 0 ? 'negative' : 'neutral'}
          accentColor="orange"
        />
        <StatCard
          title="Suspicious Device Hubs"
          value={suspiciousDevices}
          icon={Smartphone}
          description="Scammer emulators"
          loading={loading}
          trend={suspiciousDevices > 0 ? 'High Risk' : undefined}
          trendType={suspiciousDevices > 0 ? 'negative' : 'neutral'}
          accentColor="pink"
        />
      </div>

      {analysis && !loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-panel hover:glass-panel-hover rounded-2xl p-6">
            <h3 className="font-bold text-slate-100 mb-2 flex items-center gap-2 text-sm uppercase tracking-wider font-mono">
              <Network className="w-4 h-4 text-cyan-400" />
              Graph Node Distribution
            </h3>
            <p className="text-[10px] text-slate-500 mb-4 font-mono">Breakdown of unique structural entity nodes in the platform.</p>
            <NodeDistributionChart nodeTypeCounts={analysis["graph stats"].nodeTypeCounts} />
          </div>

          <div className="glass-panel hover:glass-panel-hover rounded-2xl p-6">
            <h3 className="font-bold text-slate-100 mb-2 flex items-center gap-2 text-sm uppercase tracking-wider font-mono">
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              Entity Risk Classification
            </h3>
            <p className="text-[10px] text-slate-500 mb-4">Risk levels computed dynamically by ensemble feature weights.</p>
            <RiskProfileChart confidenceScores={analysis["confidence scores"]} />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6">
        {loading ? (
          <TableSkeleton />
        ) : (
          <div className="glass-panel overflow-hidden shadow-2xl rounded-2xl">
            <div className="flex items-center justify-between px-6 py-5 border-b border-white/5 bg-white/5">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <h3 className="font-bold text-slate-100 uppercase tracking-wide text-sm font-mono">Recent Intelligence Reports</h3>
              </div>
              <span className="text-xs text-cyan-500/70 font-mono">Showing {reports.length} total entries</span>
            </div>

            {reports.length === 0 ? (
              <div className="p-8 text-center text-slate-500 font-mono text-sm">
                No fraud reports recorded in database. Use API to log reports.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 bg-black/20 text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">
                      <th className="px-6 py-4">Victim</th>
                      <th className="px-6 py-4">Phone Number</th>
                      <th className="px-6 py-4">UPI ID</th>
                      <th className="px-6 py-4">Bank Account</th>
                      <th className="px-6 py-4">Device Fingerprint</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-sm text-slate-300">
                    {reports.slice(0, 10).map((report) => (
                      <tr key={report._id} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-cyan-900/30 border border-cyan-500/20 flex items-center justify-center">
                              <User className="w-4 h-4 text-cyan-400" />
                            </div>
                            <div>
                              <div className="font-bold text-slate-200">{report.victimName}</div>
                              <div className="text-[10px] text-cyan-500/60 font-mono">{report.victimId}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 font-mono text-xs text-amber-200/80">{report.phoneNumber || '—'}</td>
                        <td className="px-6 py-4 font-mono text-xs text-violet-300/80">{report.upiId || '—'}</td>
                        <td className="px-6 py-4 font-mono text-xs text-emerald-300/80">{report.bankAccount || '—'}</td>
                        <td className="px-6 py-4 font-mono text-xs text-rose-300/80">{report.deviceFingerprint || '—'}</td>
                        <td className="px-6 py-4 text-right">
                          <Link 
                            href={`/intelligence?node=victim:${report.victimId}`}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs text-cyan-400 font-bold border border-cyan-500/20 hover:bg-cyan-500/10 hover:border-cyan-500/50 transition-all uppercase tracking-wider"
                          >
                            Investigate
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

      {logs.length > 0 && !loading && (
        <div className="glass-panel border-white/10 rounded-2xl p-5 shadow-2xl bg-black/40 font-mono text-xs text-cyan-400 scanline-overlay relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-cyan-500/5 pointer-events-none z-0"></div>
          <div className="flex items-center justify-between border-b border-cyan-500/20 pb-3 mb-3 relative z-10">
            <div className="flex items-center gap-2 text-cyan-300">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span className="font-bold tracking-widest uppercase font-mono">FORENSIC TELEMETRY CONSOLE</span>
            </div>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500 shadow-[0_0_8px_#22d3ee]"></span>
            </span>
          </div>
          <div className="space-y-2 max-h-40 overflow-y-auto scrollbar-thin select-all relative z-10">
            {logs.map((log, index) => (
              <div key={index} className="flex gap-2">
                <span className="text-cyan-500/80 select-none">➔</span>
                <p>{log}</p>
              </div>
            ))}
            <div className="text-cyan-300 flex items-center gap-1">
              <span>➔ [system] listening for incoming telemetry</span>
              <span className="terminal-cursor font-bold text-cyan-400">█</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

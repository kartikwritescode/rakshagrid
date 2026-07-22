import React, { useState, useEffect } from 'react';
import { TableSkeleton } from '../components/Skeleton';
import { 
  FileSearch, 
  Download, 
  ShieldAlert, 
  Calendar, 
  User, 
  PhoneCall, 
  Wallet, 
  CreditCard, 
  Smartphone, 
  ArrowRight,
  ShieldCheck,
  Network,
  Scale,
  Hash,
  AlertTriangle,
  FolderOpen,
  Info
} from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

interface Report {
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
  centrality: {
    pagerank: Record<string, number>;
    betweenness: Record<string, number>;
  };
  "confidence scores": Record<string, number>;
}

interface Dossier {
  id: string;
  communityId: number;
  confidenceScore: number;
  victims: string[];
  phones: string[];
  upis: string[];
  banks: string[];
  devices: string[];
  suspicionReasons: string[];
  evidenceChain: Array<{ hub: string; type: string; label: string; connectedVictims: string[] }>;
  timeline: Array<{ timestamp: string; victim: string; phone: string; upi: string; bank: string; device: string }>;
}

export default function IntelligencePage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected dossier state
  const [selectedDossierId, setSelectedDossierId] = useState<string | null>(null);
  const [dossiers, setDossiers] = useState<Dossier[]>([]);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // Fetch reports
        const reportsRes = await fetch('http://localhost:5000/api/report');
        if (!reportsRes.ok) throw new Error('Failed to load reports');
        const reportsJson = await reportsRes.json();
        const allReports = reportsJson.data || [];
        setReports(allReports);

        // Fetch graph analysis
        const analysisRes = await fetch('http://localhost:5000/api/graph-analysis');
        if (!analysisRes.ok) throw new Error('Failed to load graph analysis');
        const analysisJson = await analysisRes.json();
        const analysisData = analysisJson.data || null;
        setAnalysis(analysisData);

        if (analysisData && allReports.length > 0) {
          // Construct dossiers from Louvain communities (fraud clusters) of size > 5
          const communities = analysisData.communities || [];
          const confidenceScores = analysisData["confidence scores"] || {};
          const pagerank = analysisData.centrality.pagerank || {};

          const activeDossiers: Dossier[] = communities
            .filter((c: any) => c.nodes.length > 5)
            .map((c: any, index: number) => {
              const caseId = `CASE-FR-${(index + 1).toString().padStart(3, '0')}`;
              
              // 1. Group nodes by type
              const victims: string[] = [];
              const phones: string[] = [];
              const upis: string[] = [];
              const banks: string[] = [];
              const devices: string[] = [];

              c.nodes.forEach((nodeId: string) => {
                const [type, ...parts] = nodeId.split(':');
                const val = parts.join(':');

                if (type === 'victim') victims.push(val);
                else if (type === 'phone') phones.push(val);
                else if (type === 'upi') upis.push(val);
                else if (type === 'bank') banks.push(val);
                else if (type === 'device') devices.push(val);
              });

              // 2. Fetch involved reports and construct Timeline
              const victimsSet = new Set(victims);
              const ringReports = allReports.filter((r: Report) => victimsSet.has(r.victimId));
              
              // Sort reports chronologically
              const timeline = ringReports
                .map((r: Report) => ({
                  timestamp: r.reportTimestamp,
                  victim: r.victimName,
                  phone: r.phoneNumber,
                  upi: r.upiId,
                  bank: r.bankAccount,
                  device: r.deviceFingerprint
                }))
                .sort((a: any, b: any) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

              // 3. Trace Evidence Chain (find which shared hubs connect which victims)
              const evidenceChain: Dossier['evidenceChain'] = [];
              const sharedEntities = [...phones.map(p => ({ id: `phone:${p}`, type: 'Phone', val: p })),
                                      ...upis.map(u => ({ id: `upi:${u}`, type: 'UPI', val: u })),
                                      ...banks.map(b => ({ id: `bank:${b}`, type: 'BankAccount', val: b })),
                                      ...devices.map(d => ({ id: `device:${d}`, type: 'Device', val: d }))];

              sharedEntities.forEach(ent => {
                // Find all victims in the cluster linked to this entity
                const connectedVics: string[] = [];
                ringReports.forEach((r: Report) => {
                  const match = (ent.type === 'Phone' && r.phoneNumber === ent.val) ||
                                (ent.type === 'UPI' && r.upiId === ent.val) ||
                                (ent.type === 'BankAccount' && r.bankAccount === ent.val) ||
                                (ent.type === 'Device' && r.deviceFingerprint === ent.val);
                  
                  if (match) {
                    connectedVics.push(r.victimName);
                  }
                });

                // If shared by more than 1 victim, it is evidence of collusion
                if (connectedVics.length > 1) {
                  evidenceChain.push({
                    hub: ent.id,
                    type: ent.type,
                    label: ent.val,
                    connectedVictims: connectedVics
                  });
                }
              });

              // Sort evidence chain hubs by number of connections (descending)
              evidenceChain.sort((a, b) => b.connectedVictims.length - a.connectedVictims.length);

              // 4. Calculate Combined Confidence Score
              // Take the average of confidence scores of shared hubs, fallback to 0.75 if empty
              const confs = evidenceChain.map(ec => confidenceScores[ec.hub] || 0.5);
              const confidenceScore = confs.length > 0 
                ? confs.reduce((a, b) => a + b, 0) / confs.length
                : 0.75;

              // 5. Generate Suspicion Profiling reasons
              const suspicionReasons: string[] = [];
              if (devices.length > 0 && evidenceChain.some(e => e.type === 'Device')) {
                suspicionReasons.push("Centralized Device Fingerprint detected: Multiple victims logging scam complaints from the same hardware signature, implying emulator spoofing or coordinated centralized scam terminals.");
              }
              if (banks.length > 0 && evidenceChain.some(e => e.type === 'BankAccount')) {
                suspicionReasons.push("Money-Mule Bank Repositories: Coordinated transfers routed to shared mule bank accounts. High probability of structured financial layering.");
              }
              if (upis.length > 0 && evidenceChain.some(e => e.type === 'UPI')) {
                suspicionReasons.push("Shared UPI Mule Destination Handles: Victims reported sending funds to identical UPI addresses, mapping directly to money mule networks.");
              }
              if (phones.length > 0 && evidenceChain.some(e => e.type === 'Phone')) {
                suspicionReasons.push("Scammer Contact Linkage: Multi-victim linkages established via common calling phone numbers, mapping scam campaigns to a single calling cell.");
              }
              
              // Find node with highest PageRank centrality in this cluster
              let maxPrNode = "";
              let maxPrVal = 0;
              c.nodes.forEach((nId: string) => {
                const pr = pagerank[nId] || 0;
                if (pr > maxPrVal) {
                  maxPrVal = pr;
                  maxPrNode = nId;
                }
              });
              if (maxPrNode) {
                const [type, ...parts] = maxPrNode.split(':');
                const lbl = parts.join(':');
                suspicionReasons.push(`Centralized Routing Bottleneck: Network flow PageRank flags '${lbl}' (${type.toUpperCase()}) as the highest-influence routing hub with an importance score of ${maxPrVal.toFixed(5)}.`);
              }

              return {
                id: caseId,
                communityId: c.id,
                confidenceScore: roundScore(confidenceScore),
                victims,
                phones,
                upis,
                banks,
                devices,
                suspicionReasons,
                evidenceChain,
                timeline
              };
            });
            
          setDossiers(activeDossiers);
          if (activeDossiers.length > 0) {
            setSelectedDossierId(activeDossiers[0].id);
          }
        }
        
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

  const roundScore = (num: number) => {
    return Math.round(num * 100) / 100;
  };

  const selectedDossier = dossiers.find(d => d.id === selectedDossierId);

  // JSON exporter handler
  const handleDownloadJSON = (dossier: Dossier) => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(dossier, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `et_AI_dossier_${dossier.id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'Victim': return User;
      case 'Phone': return PhoneCall;
      case 'UPI': return Wallet;
      case 'BankAccount': return CreditCard;
      case 'Device': return Smartphone;
      default: return Info;
    }
  };

  const getAccentColor = (type: string) => {
    switch (type) {
      case 'Victim': return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20';
      case 'Phone': return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
      case 'UPI': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'BankAccount': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'Device': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Onboarding tooltips */}
      <OnboardingGuide 
        pageName="intelligence"
        message="This page generates investigation-ready reports with confidence scores and evidence chains."
      />

      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-black text-white flex items-center gap-3 tracking-tighter uppercase drop-shadow-lg">
          <FileSearch className="w-8 h-8 text-cyan-500 drop-shadow-[0_0_10px_rgba(6,182,212,0.8)]" />
          Intelligence Packet Case Dossier
        </h1>
        <p className="text-cyan-400/80 font-mono text-xs mt-2 flex items-center gap-2 uppercase tracking-widest">
          Forensics investigation dossiers for identified fraud clusters. Formatted for cybercrime intelligence reporting.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <TableSkeleton rows={4} />
      ) : dossiers.length === 0 ? (
        <div className="glass-panel border-white/10 rounded-2xl p-16 text-center text-slate-500 space-y-5 bg-black/40">
          <ShieldCheck className="w-16 h-16 mx-auto text-emerald-500 animate-pulse drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]" />
          <h3 className="font-bold text-slate-300 text-lg uppercase tracking-widest">No Multi-Victim Fraud Clusters Logged</h3>
          <p className="text-xs max-w-sm mx-auto font-mono text-slate-500 leading-relaxed uppercase">
            All submitted cases represent isolated reports with unique characteristics. Dossiers will be compiled here once the graph engine identifies connections.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
          {/* Left Case Index Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <div className="glass-panel bg-black/40 border-white/10 p-4 rounded-2xl space-y-4 shadow-xl">
              <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2 border-b border-white/10 pb-3">
                <FolderOpen className="w-4 h-4 text-cyan-400" />
                Active Cyber Files
              </h3>
              
              <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                {dossiers.map(d => (
                  <button
                    key={d.id}
                    onClick={() => setSelectedDossierId(d.id)}
                    className={`w-full text-left p-3.5 rounded-xl border text-xs transition-all flex justify-between items-center ${
                      selectedDossierId === d.id
                        ? 'bg-cyan-900/30 border-cyan-500/50 text-white shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                        : 'bg-black/60 border-white/5 hover:border-cyan-500/30 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div>
                      <div className="font-mono font-bold tracking-wider text-[11px]">{d.id}</div>
                      <div className="text-[10px] text-cyan-400/70 mt-1 uppercase tracking-widest">{d.victims.length} Victims linked</div>
                    </div>
                    <span className={`px-2 py-1 rounded-md text-[10px] font-mono font-bold border ${
                      d.confidenceScore > 0.85
                        ? 'bg-rose-950/40 border-rose-500/50 text-rose-400 shadow-[0_0_10px_rgba(225,29,72,0.2)]'
                        : 'bg-amber-950/40 border-amber-500/50 text-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.2)]'
                    }`}>
                      {(d.confidenceScore * 100).toFixed(0)}% Risk
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Police Case Dossier */}
          {selectedDossier && (
            <div className="lg:col-span-3 space-y-6">
              {/* Dossier paper container */}
              <div className="relative glass-panel bg-black/60 border-white/10 rounded-2xl overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.8)] backdrop-blur-xl">
                
                {/* Dossier Warning Ribbon */}
                <div className="absolute top-0 right-0 left-0 h-1 bg-gradient-to-r from-cyan-500 via-rose-500 to-cyan-600"></div>

                {/* Dossier Header block */}
                <div className="bg-black/40 px-8 py-8 border-b border-white/10 flex flex-col md:flex-row md:items-center md:justify-between gap-6 relative shadow-inner">
                  {/* Watermark stamp background */}
                  <div className="absolute right-8 top-6 text-white/5 font-black font-mono text-6xl select-none pointer-events-none transform -rotate-6 tracking-widest uppercase border-4 border-white/5 p-4 mix-blend-overlay">
                    CONFIDENTIAL
                  </div>

                  <div className="space-y-2 z-10">
                    <span className="inline-flex items-center gap-2 text-[10px] text-rose-400 font-mono tracking-widest font-bold uppercase mb-1 drop-shadow-md">
                      <ShieldAlert className="w-3.5 h-3.5 text-rose-500 animate-pulse" />
                      Cybercrime Intelligence Dossier
                    </span>
                    <h2 className="text-3xl font-black tracking-widest text-white font-mono uppercase flex items-center gap-3 drop-shadow-lg">
                      <Hash className="w-6 h-6 text-cyan-500" />
                      {selectedDossier.id}
                    </h2>
                    <p className="text-[10px] text-cyan-400/60 font-mono tracking-widest uppercase">SYSTEM CLUSTER MODULE: LOUVAIN-{selectedDossier.communityId}</p>
                  </div>

                  {/* Actions & Risk */}
                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 z-10">
                    {/* Confidence score badge */}
                    <div className="flex items-center gap-3 bg-rose-950/40 border border-rose-500/30 px-5 py-3 rounded-xl shadow-[0_0_15px_rgba(225,29,72,0.15)]">
                      <Scale className="w-5 h-5 text-rose-400" />
                      <div>
                        <span className="block text-[9px] text-rose-300/80 uppercase font-mono tracking-widest leading-none mb-1">Confidence Score</span>
                        <span className="text-xl font-black text-rose-400 font-mono">{(selectedDossier.confidenceScore * 100).toFixed(0)}% <span className="text-[10px] text-rose-500">CERTAINTY</span></span>
                      </div>
                    </div>

                    {/* Download Dossier */}
                    <button
                      onClick={() => handleDownloadJSON(selectedDossier)}
                      className="btn-primary flex items-center gap-2 text-[10px] uppercase tracking-widest px-6 py-3"
                    >
                      <Download className="w-4 h-4" />
                      Download Case File
                    </button>
                  </div>
                </div>

                {/* Dossier Body */}
                <div className="p-8 space-y-8">
                  
                  {/* Suspicion Profiling */}
                  <div className="space-y-4">
                    <h3 className="text-[11px] font-bold text-cyan-400 uppercase tracking-widest font-mono border-l-2 border-cyan-500 pl-3 shadow-[inset_1px_0_0_rgba(6,182,212,0.5)]">
                      I. Grounds for Suspicion & Structural Assessment
                    </h3>
                    <div className="bg-black/40 border border-white/5 rounded-xl p-5 space-y-3 text-xs text-slate-300 leading-relaxed shadow-inner">
                      {selectedDossier.suspicionReasons.map((reason, i) => (
                        <div key={i} className="flex gap-3 items-start">
                          <span className="text-cyan-500 font-mono font-bold select-none">[{i+1}]</span>
                          <p className="font-mono tracking-tight">{reason}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Evidence Chain Link Analysis */}
                  <div className="space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono border-l-2 border-indigo-500 pl-2">
                      II. Evidence Chain & Graph Linkages
                    </h3>
                    
                    <div className="space-y-3">
                      {selectedDossier.evidenceChain.map((link, i) => {
                        const Icon = getIcon(link.type);
                        return (
                          <div 
                            key={i} 
                            className="bg-slate-900/30 border border-slate-900 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4"
                          >
                            {/* Hub Entity details */}
                            <div className="flex items-center gap-3">
                              <div className={`p-2 rounded border ${getAccentColor(link.type)}`}>
                                <Icon className="w-4 h-4" />
                              </div>
                              <div>
                                <span className="text-[9px] uppercase font-bold text-slate-500 font-mono">{link.type} Link Hub</span>
                                <div className="font-mono text-xs text-slate-200 font-semibold break-all">{link.label}</div>
                              </div>
                            </div>

                            {/* Connected Victims links */}
                            <div className="flex-grow flex items-center justify-end gap-2 flex-wrap text-xs">
                              <span className="text-[10px] text-slate-500 font-mono uppercase mr-1">Binds Victims:</span>
                              {link.connectedVictims.map((vic, index) => (
                                <span 
                                  key={index} 
                                  className="px-2 py-0.5 bg-slate-950 border border-slate-800 text-slate-400 rounded flex items-center gap-1"
                                >
                                  <User className="w-3 h-3 text-slate-500" />
                                  {vic}
                                </span>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Chronological Incident Timeline */}
                  <div className="space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono border-l-2 border-indigo-500 pl-2">
                      III. Chronological Crime Timeline
                    </h3>

                    <div className="relative border-l border-slate-800 ml-4 pl-6 space-y-6">
                      {selectedDossier.timeline.map((event, i) => (
                        <div key={i} className="relative">
                          {/* Timeline dot */}
                          <span className="absolute -left-[31px] top-1 w-2.5 h-2.5 rounded-full bg-indigo-500 border border-slate-950"></span>
                          
                          <div className="space-y-1.5">
                            {/* Time details */}
                            <div className="flex items-center gap-2 text-xs font-mono">
                              <Calendar className="w-3.5 h-3.5 text-slate-500" />
                              <span className="text-slate-400">{new Date(event.timestamp).toLocaleString()}</span>
                            </div>
                            
                            {/* Victim information */}
                            <div className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
                              {event.victim}
                              <span className="text-xs font-normal text-slate-500 font-mono">(Incident Logged)</span>
                            </div>

                            {/* Attribute details */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[10px] text-slate-400 font-mono">
                              {event.phone && (
                                <div className="bg-slate-900/10 p-1.5 rounded border border-slate-900 flex items-center gap-1">
                                  <PhoneCall className="w-3 h-3 text-orange-400/80" />
                                  <span className="truncate">{event.phone}</span>
                                </div>
                              )}
                              {event.upi && (
                                <div className="bg-slate-900/10 p-1.5 rounded border border-slate-900 flex items-center gap-1">
                                  <Wallet className="w-3 h-3 text-yellow-400/80" />
                                  <span className="truncate">{event.upi}</span>
                                </div>
                              )}
                              {event.bank && (
                                <div className="bg-slate-900/10 p-1.5 rounded border border-slate-900 flex items-center gap-1">
                                  <CreditCard className="w-3 h-3 text-emerald-400/80" />
                                  <span className="truncate">{event.bank}</span>
                                </div>
                              )}
                              {event.device && (
                                <div className="bg-slate-900/10 p-1.5 rounded border border-slate-900 flex items-center gap-1">
                                  <Smartphone className="w-3 h-3 text-rose-400/80" />
                                  <span className="truncate">{event.device}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Complete Syndicate Members Listing */}
                  <div className="space-y-4 border-t border-white/10 pt-8">
                    <h3 className="text-[11px] font-bold text-cyan-400 uppercase tracking-widest font-mono border-l-2 border-cyan-500 pl-3 shadow-[inset_1px_0_0_rgba(6,182,212,0.5)]">
                      IV. Syndicate Inventory List
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                      {/* Victims */}
                      <div className="bg-black/40 border border-white/5 rounded-xl p-5 space-y-3 shadow-inner">
                        <span className="text-[10px] text-cyan-500 font-bold uppercase tracking-widest block flex items-center gap-2">
                          <User className="w-3 h-3" /> Connected Victims ({selectedDossier.victims.length})
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {selectedDossier.victims.map((vic, i) => (
                            <span key={i} className="px-2 py-1 bg-cyan-950/40 border border-cyan-500/20 rounded-md text-cyan-300 text-[10px] uppercase tracking-wider">
                              {vic}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Phone numbers */}
                      <div className="bg-black/40 border border-white/5 rounded-xl p-5 space-y-3 shadow-inner">
                        <span className="text-[10px] text-amber-500 font-bold uppercase tracking-widest block flex items-center gap-2">
                          <PhoneCall className="w-3 h-3" /> Phone Links ({selectedDossier.phones.length})
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {selectedDossier.phones.map((ph, i) => (
                            <span key={i} className="px-2 py-1 bg-amber-950/40 border border-amber-500/20 rounded-md text-amber-300 text-[10px] uppercase tracking-wider">
                              {ph}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* UPI Handles */}
                      <div className="bg-black/40 border border-white/5 rounded-xl p-5 space-y-3 shadow-inner">
                        <span className="text-[10px] text-yellow-500 font-bold uppercase tracking-widest block flex items-center gap-2">
                          <Wallet className="w-3 h-3" /> UPI Mules ({selectedDossier.upis.length})
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {selectedDossier.upis.map((upi, i) => (
                            <span key={i} className="px-2 py-1 bg-yellow-950/40 border border-yellow-500/20 rounded-md text-yellow-300 text-[10px] uppercase tracking-wider">
                              {upi}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Bank Accounts */}
                      <div className="bg-black/40 border border-white/5 rounded-xl p-5 space-y-3 shadow-inner">
                        <span className="text-[10px] text-emerald-500 font-bold uppercase tracking-widest block flex items-center gap-2">
                          <CreditCard className="w-3 h-3" /> Mule Bank Accounts ({selectedDossier.banks.length})
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {selectedDossier.banks.map((bank, i) => (
                            <span key={i} className="px-2 py-1 bg-emerald-950/40 border border-emerald-500/20 rounded-md text-emerald-300 text-[10px] uppercase tracking-wider">
                              {bank}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Devices */}
                      <div className="bg-black/40 border border-white/5 rounded-xl p-5 space-y-3 shadow-inner md:col-span-2">
                        <span className="text-[10px] text-rose-500 font-bold uppercase tracking-widest block flex items-center gap-2">
                          <Smartphone className="w-3 h-3" /> Centralized Devices / Emulators ({selectedDossier.devices.length})
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {selectedDossier.devices.map((dev, i) => (
                            <span key={i} className="px-2 py-1 bg-rose-950/40 border border-rose-500/20 rounded-md text-rose-300 text-[10px] uppercase tracking-wider">
                              {dev}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

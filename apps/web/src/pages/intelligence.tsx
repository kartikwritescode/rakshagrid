import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { FileSearch, ShieldAlert, CheckCircle2 } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';

export default function IntelligencePage() {
  const router = useRouter();
  const { node } = router.query;
  const targetNode = (node as string) || 'phone:+919876543210';

  return (
    <div className="space-y-6">
      <OnboardingGuide 
        pageName="intelligence"
        message="Detailed forensic packet intelligence for a targeted suspicious entity."
      />

      <div className="flex items-center justify-between border-b border-white/5 pb-4">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <FileSearch className="w-8 h-8 text-cyan-400" />
            Forensic Intelligence Packet
          </h1>
          <p className="text-slate-400 text-xs font-mono mt-1">
            Target Entity: <span className="text-cyan-300 font-bold">{targetNode}</span>
          </p>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base">High Confidence Threat Entity</h3>
            <p className="text-xs text-slate-400 font-mono">Risk Score: 92.4% | Classification: Credential Harvesting & Authority Impersonation</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-black/40 border border-white/5 space-y-2">
            <span className="text-slate-500 uppercase text-[10px]">Primary Linked Accounts</span>
            <p className="text-slate-200">501002345678 (HDFC Bank)</p>
            <p className="text-slate-200">scam@okaxis (UPI)</p>
          </div>
          <div className="p-4 rounded-xl bg-black/40 border border-white/5 space-y-2">
            <span className="text-slate-500 uppercase text-[10px]">Incident Telemetry</span>
            <p className="text-slate-200">First Seen: 2026-07-01</p>
            <p className="text-slate-200">Total Linked Victims: 4</p>
          </div>
        </div>
      </div>
    </div>
  );
}

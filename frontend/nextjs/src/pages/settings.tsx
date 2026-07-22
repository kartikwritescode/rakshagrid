import React, { useState } from 'react';
import Head from 'next/head';
import { Settings as SettingsIcon, Save } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState("http://localhost:8000");
  const [highThreshold, setHighThreshold] = useState("0.55");
  const [lowThreshold, setLowThreshold] = useState("0.12");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6">
      <Head>
        <title>Platform Settings | Raksha Grid</title>
      </Head>

      <OnboardingGuide pageName="settings" message="Configure backend REST API endpoint URLs and risk band threshold defaults." />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <SettingsIcon className="w-8 h-8 text-cyan-400" />
          Platform System Settings
        </h1>
      </div>

      <div className="glass-panel p-6 rounded-2xl border-white/5 max-w-2xl space-y-4 font-mono text-xs">
        <div>
          <label className="text-[10px] text-slate-400 uppercase block mb-1">FastAPI Central Backend URL</label>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-[10px] text-slate-400 uppercase block mb-1">High Risk Threshold</label>
            <input
              type="text"
              value={highThreshold}
              onChange={(e) => setHighThreshold(e.target.value)}
              className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-[10px] text-slate-400 uppercase block mb-1">Low Risk Threshold</label>
            <input
              type="text"
              value={lowThreshold}
              onChange={(e) => setLowThreshold(e.target.value)}
              className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <button
          onClick={handleSave}
          className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-xl uppercase text-xs tracking-wider transition-colors flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          {saved ? 'Settings Saved!' : 'Save System Settings'}
        </button>
      </div>
    </div>
  );
}

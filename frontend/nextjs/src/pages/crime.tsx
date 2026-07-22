import React, { useState } from 'react';
import Head from 'next/head';
import { ShieldAlert, Upload, Camera, Video, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';
import { useCrimeDetection } from '../hooks/useCrimeDetection';

export default function CrimePage() {
  const { predict, loading, result, error } = useCrimeDetection();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [city, setCity] = useState("Mumbai");
  const [description, setDescription] = useState("Cyber Theft / Scam Incident");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleAnalyze = async () => {
    await predict(selectedFile || undefined, city, description);
  };

  return (
    <div className="space-y-6">
      <Head>
        <title>Crime Scene & Incident Detector | Raksha Grid</title>
      </Head>

      <OnboardingGuide
        pageName="crime"
        message="Upload crime scene image/video or incident metadata to execute ML incident classification and severity scoring."
      />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <ShieldAlert className="w-8 h-8 text-cyan-400" />
          Crime Scene & Incident Telemetry Analyzer
        </h1>
        <p className="text-slate-400 text-xs font-mono mt-1">Module 4 — VigilGrid Crime Intelligence Classifier</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Incident Media & Telemetry</h3>

          <div className="space-y-3">
            <div>
              <label className="text-[10px] text-slate-400 font-mono uppercase block mb-1">Target Location / City</label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-400 font-mono uppercase block mb-1">Crime Description / Category</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="border-2 border-dashed border-white/10 hover:border-cyan-500/40 bg-black/40 rounded-2xl p-6 text-center cursor-pointer relative min-h-[160px] flex flex-col items-center justify-center gap-2 transition-colors">
            <input type="file" accept="image/*,video/*" onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
            {previewUrl ? (
              <img src={previewUrl} alt="Crime scene evidence" className="max-h-36 rounded-lg object-contain" />
            ) : (
              <>
                <Upload className="w-8 h-8 text-slate-500" />
                <p className="text-xs text-slate-300 font-mono">Upload Crime Scene Image, Screenshot, or Video Evidence</p>
              </>
            )}
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-bold uppercase tracking-wider text-xs shadow-lg shadow-cyan-500/20 disabled:opacity-50 hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? 'Executing Incident Classification...' : 'Run Crime Analysis Prediction'}
          </button>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Prediction Telemetry Output</h3>

          {result ? (
            <div className="space-y-4 font-mono text-xs">
              <div className="p-4 rounded-xl border bg-cyan-500/10 border-cyan-500/30 text-cyan-300 flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-cyan-400" />
                <div>
                  <h4 className="font-bold text-sm uppercase">{result.crime_type}</h4>
                  <p className="text-[10px] opacity-80">Category: {result.category} | Location: {result.location}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase">Confidence</span>
                  <p className="text-base font-bold text-cyan-400">{(result.confidence * 100).toFixed(1)}%</p>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase">Severity Level</span>
                  <p className="text-base font-bold text-rose-400">{result.severity}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 font-mono text-xs text-center p-6 border border-dashed border-white/5 rounded-2xl">
              Submit crime incident metadata or evidence file to display prediction results.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

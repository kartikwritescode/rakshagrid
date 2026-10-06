import React, { useState } from 'react';
import Head from 'next/head';
import { Mic, Upload, ShieldCheck, AlertTriangle, FileText, Loader2, Play } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';
import { useAudioDetector } from '../hooks/useAudioDetector';

export default function AudioPage() {
  const { detect, loading, result, error } = useAudioDetector();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setAudioUrl(URL.createObjectURL(file));
    }
  };

  const handleAnalyze = async () => {
    if (selectedFile) {
      await detect(selectedFile);
    }
  };

  return (
    <div className="space-y-6">
      <Head>
        <title>Audio Deepfake & Scam Detector | Raksha Grid</title>
      </Head>

      <OnboardingGuide
        pageName="audio"
        message="Upload call recording (wav/mp3) to run Whisper speech transcription and Stacking Ensemble scam/deepfake detection."
      />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <Mic className="w-8 h-8 text-cyan-400" />
          Audio Deepfake & Call Scam Interceptor
        </h1>
        <p className="text-slate-400 text-xs font-mono mt-1">Module 2 — Voice Biometric & Telemetry Analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Audio File Upload</h3>

          <div className="border-2 border-dashed border-white/10 hover:border-cyan-500/40 bg-black/40 rounded-2xl p-6 text-center cursor-pointer relative min-h-[180px] flex flex-col items-center justify-center gap-3 transition-colors">
            <input type="file" accept="audio/*" onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
            <Upload className="w-10 h-10 text-slate-500" />
            <p className="text-xs text-slate-300 font-mono">
              {selectedFile ? selectedFile.name : "Select WAV, MP3, M4A or FLAC call recording"}
            </p>
          </div>

          {audioUrl && (
            <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
              <audio controls src={audioUrl} className="w-full" />
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || loading}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-bold uppercase tracking-wider text-xs shadow-lg shadow-cyan-500/20 disabled:opacity-50 hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? 'Transcribing & Analyzing Voice Biomarkers...' : 'Run Deepfake & Scam Interceptor'}
          </button>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Detection Analysis Result</h3>

          {result ? (
            <div className="space-y-4 font-mono text-xs">
              <div className={`p-4 rounded-xl border flex items-center gap-3 ${result.risk_band === 'high' ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'}`}>
                {result.risk_band === 'high' ? <AlertTriangle className="w-6 h-6" /> : <ShieldCheck className="w-6 h-6" />}
                <div>
                  <h4 className="font-bold text-sm uppercase">{result.risk_band === 'high' ? 'HIGH RISK SCAM / DEEPFAKE' : 'SAFE / LOW RISK CALL'}</h4>
                  <p className="text-[10px] opacity-80">Stage: {result.stage}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase">Risk Score</span>
                  <p className="text-base font-bold text-cyan-400">{(result.risk_score * 100).toFixed(1)}%</p>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase">Processing Latency</span>
                  <p className="text-base font-bold text-slate-200">{result.processing_time_ms || 240} ms</p>
                </div>
              </div>

              <div className="p-4 bg-black/50 border border-white/5 rounded-xl space-y-2">
                <span className="text-[10px] text-slate-500 uppercase font-bold flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-cyan-400" /> Whisper Generated Transcript
                </span>
                <p className="text-slate-300 leading-relaxed text-xs max-h-36 overflow-y-auto">
                  {result.transcript || "No transcript generated"}
                </p>
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 font-mono text-xs text-center p-6 border border-dashed border-white/5 rounded-2xl">
              Upload an audio file to view real-time deepfake analysis and speech transcription.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

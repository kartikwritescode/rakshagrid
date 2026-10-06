import React, { useState } from 'react';
import Head from 'next/head';
import { Upload, CheckCircle2, AlertTriangle, ShieldCheck, Clock, Image as ImageIcon, Loader2 } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';
import { useCurrencyScanner } from '../hooks/useCurrencyScanner';

export default function CurrencyPage() {
  const { scanImage, loading, result, error } = useCurrencyScanner();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleScan = async () => {
    if (selectedFile) {
      await scanImage(selectedFile);
    }
  };

  return (
    <div className="space-y-6">
      <Head>
        <title>Counterfeit Currency Detector | Raksha Grid</title>
      </Head>

      <OnboardingGuide
        pageName="currency"
        message="Upload banknote image to detect counterfeit print defects, color shifts, and missing security threads via EfficientNetB0."
      />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <ImageIcon className="w-8 h-8 text-cyan-400" />
          Counterfeit Currency Identification
        </h1>
        <p className="text-slate-400 text-xs font-mono mt-1">Module 1 — Deep Vision Banknote Authenticity Analyzer</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Banknote Image Input</h3>
          
          <div className="border-2 border-dashed border-white/10 hover:border-cyan-500/40 bg-black/40 rounded-2xl p-6 text-center cursor-pointer relative min-h-[220px] flex flex-col items-center justify-center gap-3 transition-colors">
            <input type="file" accept="image/*" onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
            {previewUrl ? (
              <img src={previewUrl} alt="Banknote preview" className="max-h-48 rounded-lg object-contain" />
            ) : (
              <>
                <Upload className="w-10 h-10 text-slate-500" />
                <p className="text-xs text-slate-300 font-mono">Drag & drop banknote photo or click to upload</p>
              </>
            )}
          </div>

          <button
            onClick={handleScan}
            disabled={!selectedFile || loading}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-bold uppercase tracking-wider text-xs shadow-lg shadow-cyan-500/20 disabled:opacity-50 hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? 'Analyzing Banknote Defect Patterns...' : 'Run Authenticity Scan'}
          </button>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Authenticity Verdict</h3>

          {result ? (
            <div className="space-y-4 font-mono text-xs">
              <div className={`p-4 rounded-xl border flex items-center gap-3 ${result.is_genuine ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'}`}>
                {result.is_genuine ? <CheckCircle2 className="w-6 h-6" /> : <AlertTriangle className="w-6 h-6" />}
                <div>
                  <h4 className="font-bold text-sm uppercase">{result.status} Banknote</h4>
                  <p className="text-[10px] opacity-80">Predicted Class: {result.predicted_label}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase">Confidence</span>
                  <p className="text-base font-bold text-cyan-400">{(result.confidence * 100).toFixed(2)}%</p>
                </div>
                <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                  <span className="text-[10px] text-slate-500 uppercase">Latency</span>
                  <p className="text-base font-bold text-slate-200">{result.processing_time_ms || 120} ms</p>
                </div>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 uppercase block mb-2">Defect Class Probabilities</span>
                <div className="space-y-2">
                  {Object.entries(result.class_probabilities || {}).map(([cls, prob]) => (
                    <div key={cls} className="flex justify-between items-center bg-black/30 p-2 rounded border border-white/5">
                      <span className="text-slate-300">{cls}</span>
                      <span className="font-bold text-cyan-400">{((prob as number) * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 font-mono text-xs text-center p-6 border border-dashed border-white/5 rounded-2xl">
              Upload a banknote photo and run the scan to display detection verdict.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

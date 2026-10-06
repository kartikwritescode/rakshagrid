import React from 'react';
import Head from 'next/head';
import { Shield, Cpu, Layers, CheckCircle2 } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <Head>
        <title>About Platform Architecture | Raksha Grid</title>
      </Head>

      <OnboardingGuide pageName="about" message="Detailed architectural layout of all 4 Machine Learning models and microservice design." />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <Shield className="w-8 h-8 text-cyan-400" />
          About Raksha Grid Production Platform
        </h1>
      </div>

      <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-6 font-mono text-xs text-slate-300">
        <div>
          <h3 className="font-bold text-white text-sm uppercase mb-2">Integrated ML Architecture</h3>
          <p className="leading-relaxed">
            Raksha Grid integrates four specialized AI models into a single microservice platform backed by FastAPI and Next.js.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-black/40 border border-white/5 rounded-xl space-y-2">
            <h4 className="font-bold text-cyan-400">Module 1: Banknote Authenticity</h4>
            <p className="text-[11px] text-slate-400">EfficientNetB0 deep vision network classifying print defects and missing security threads.</p>
          </div>
          <div className="p-4 bg-black/40 border border-white/5 rounded-xl space-y-2">
            <h4 className="font-bold text-cyan-400">Module 2: Scam Interceptor</h4>
            <p className="text-[11px] text-slate-400">Bounded Stacking Ensemble (scipy L-BFGS-B non-negative constraints) + Groq Llama-3.3-70b LLM fallback.</p>
          </div>
          <div className="p-4 bg-black/40 border border-white/5 rounded-xl space-y-2">
            <h4 className="font-bold text-cyan-400">Module 3: Speech Transcription</h4>
            <p className="text-[11px] text-slate-400">Whisper speech-to-text model generating transcripts from multi-format audio files.</p>
          </div>
          <div className="p-4 bg-black/40 border border-white/5 rounded-xl space-y-2">
            <h4 className="font-bold text-cyan-400">Module 4: VigilGrid Crime Engine</h4>
            <p className="text-[11px] text-slate-400">DBSCAN spatial clustering over lat/lon point clouds for hotspot detection and patrol allocation.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

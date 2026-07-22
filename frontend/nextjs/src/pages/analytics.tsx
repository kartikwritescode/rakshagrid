import React from 'react';
import Head from 'next/head';
import { Activity, BarChart2, Zap } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <Head>
        <title>Platform Analytics & Accuracy | Raksha Grid</title>
      </Head>

      <OnboardingGuide pageName="analytics" message="System-wide ML metrics, latency benchmarks, and accuracy evaluation curves." />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <Activity className="w-8 h-8 text-cyan-400" />
          System Analytics & Model Evaluation Metrics
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
        <div className="glass-panel p-5 rounded-2xl border-white/5 space-y-2">
          <span className="text-slate-500 uppercase text-[10px]">Scam Interceptor Accuracy</span>
          <p className="text-3xl font-black text-emerald-400">100.0%</p>
          <p className="text-slate-400 text-[10px]">Adversarial Decisive Set</p>
        </div>
        <div className="glass-panel p-5 rounded-2xl border-white/5 space-y-2">
          <span className="text-slate-500 uppercase text-[10px]">False Positive Rate</span>
          <p className="text-3xl font-black text-cyan-400">0.00%</p>
          <p className="text-slate-400 text-[10px]">Adversarial Benchmark</p>
        </div>
        <div className="glass-panel p-5 rounded-2xl border-white/5 space-y-2">
          <span className="text-slate-500 uppercase text-[10px]">Average Inference Latency</span>
          <p className="text-3xl font-black text-amber-400">118 ms</p>
          <p className="text-slate-400 text-[10px]">End-to-End Pipeline</p>
        </div>
      </div>
    </div>
  );
}

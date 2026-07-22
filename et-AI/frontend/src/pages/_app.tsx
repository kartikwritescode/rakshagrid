import React from 'react';
import type { AppProps } from 'next/app';
import Navbar from '../components/Navbar';
import Link from 'next/link';
import { Bot } from 'lucide-react';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className="flex flex-col min-h-screen bg-[#030712] text-slate-100 font-sans selection:bg-cyan-600/30 selection:text-cyan-200">
      {/* Global Intelligence Backgrounds */}
      <div className="bg-grid-pattern" />
      <div className="radar-sweep" />
      
      {/* Ambient Aurora Accents */}
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-cyan-600/5 rounded-full blur-[120px] pointer-events-none" />

      <Navbar />
      
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 md:px-6 py-8 relative z-10">
        <Component {...pageProps} />
      </main>
      
      <footer className="border-t border-slate-900 bg-slate-950/40 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4">
          © 2026 et-AI GraphIntel. Module 3 Fraud Network Graph Analyzer.
        </div>
      </footer>

      {/* Right Side Small Bar for Chat API Hit */}
      <div className="fixed top-1/2 right-0 -translate-y-1/2 z-50">
        <Link 
          href="/citizen-shield"
          className="flex flex-col items-center justify-center bg-slate-900 border border-slate-700 border-r-0 rounded-l-xl p-3 shadow-2xl hover:bg-slate-800 transition-colors group"
          title="Citizen Shield"
        >
          <div className="bg-blue-600/20 p-2 rounded-lg group-hover:bg-blue-600/40 transition-colors">
            <Bot className="w-6 h-6 text-blue-400" />
          </div>
        </Link>
      </div>
    </div>
  );
}

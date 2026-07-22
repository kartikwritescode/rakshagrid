import React from 'react';
import Head from 'next/head';
import { FraudShieldChat } from '../components/FraudShieldChat';

export default function CitizenShield() {
  return (
    <div className="min-h-screen bg-black text-slate-200">
      <Head>
        <title>Citizen Fraud Shield | Raksha Grid</title>
        <meta name="description" content="AI-powered fraud detection and citizen assistance" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 border-b border-slate-800 pb-6">
          <h1 className="text-3xl font-black text-white mb-2">Citizen Fraud Shield</h1>
          <p className="text-slate-400">Real-time scam analysis and official I4C advisory guidance.</p>
        </div>

        <FraudShieldChat />
      </main>
    </div>
  );
}

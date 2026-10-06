import React, { useState } from 'react';
import Head from 'next/head';
import { FileText, Upload, Copy, Check, Loader2 } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';
import { useTranscriber } from '../hooks/useTranscriber';

export default function TranscriptionPage() {
  const { transcribe, loading, transcript, error } = useTranscriber();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [copied, setCopied] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleTranscribe = async () => {
    if (selectedFile) {
      await transcribe(selectedFile);
    }
  };

  const handleCopy = () => {
    if (transcript) {
      navigator.clipboard.writeText(transcript);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <Head>
        <title>Speech-to-Text Transcriber | Raksha Grid</title>
      </Head>

      <OnboardingGuide
        pageName="transcription"
        message="Dedicated speech transcription engine powered by faster-whisper model."
      />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <FileText className="w-8 h-8 text-cyan-400" />
          Speech-to-Text Audio Transcription
        </h1>
        <p className="text-slate-400 text-xs font-mono mt-1">Module 3 — High Precision Whisper Transcription Engine</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Audio Upload</h3>

          <div className="border-2 border-dashed border-white/10 hover:border-cyan-500/40 bg-black/40 rounded-2xl p-6 text-center cursor-pointer relative min-h-[160px] flex flex-col items-center justify-center gap-3 transition-colors">
            <input type="file" accept="audio/*" onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" />
            <Upload className="w-10 h-10 text-slate-500" />
            <p className="text-xs text-slate-300 font-mono">
              {selectedFile ? selectedFile.name : "Select audio file to transcribe"}
            </p>
          </div>

          <button
            onClick={handleTranscribe}
            disabled={!selectedFile || loading}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-bold uppercase tracking-wider text-xs shadow-lg shadow-cyan-500/20 disabled:opacity-50 hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {loading ? 'Transcribing Speech to Text...' : 'Generate Full Transcript'}
          </button>
        </div>

        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4 flex flex-col">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">Generated Output Transcript</h3>
            {transcript && (
              <button onClick={handleCopy} className="flex items-center gap-1.5 text-xs text-cyan-400 font-mono hover:underline">
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied' : 'Copy Text'}
              </button>
            )}
          </div>

          {transcript ? (
            <div className="flex-1 p-4 bg-black/50 border border-white/5 rounded-xl font-mono text-xs text-slate-200 leading-relaxed overflow-y-auto max-h-[300px]">
              {transcript}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 font-mono text-xs text-center p-6 border border-dashed border-white/5 rounded-2xl">
              Upload an audio file to generate exact text transcript.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

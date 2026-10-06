import React, { useState } from 'react';
import Head from 'next/head';
import { 
  Mic, 
  Upload, 
  ShieldCheck, 
  AlertTriangle, 
  FileText, 
  Loader2, 
  Volume2, 
  Cpu, 
  Info,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';
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

  // Helper for voice deepfake status styling
  const getVoiceStatusBadge = (status?: string) => {
    switch (status) {
      case 'detected':
        return {
          label: 'SYNTHETIC VOICE DETECTED',
          bg: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
          icon: AlertTriangle,
        };
      case 'not_detected':
        return {
          label: 'NATURAL GENUINE VOICE',
          bg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
          icon: CheckCircle2,
        };
      case 'insufficient_quality':
        return {
          label: 'INSUFFICIENT AUDIO QUALITY',
          bg: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
          icon: AlertCircle,
        };
      case 'processing_error':
        return {
          label: 'ACOUSTIC PROCESSING ERROR',
          bg: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
          icon: AlertCircle,
        };
      case 'unavailable':
      default:
        return {
          label: 'ACOUSTIC MODEL UNAVAILABLE',
          bg: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
          icon: Info,
        };
    }
  };

  const voiceBadge = getVoiceStatusBadge(result?.voice_analysis?.status);
  const VoiceBadgeIcon = voiceBadge.icon;

  return (
    <div className="space-y-6">
      <Head>
        <title>Audio Telemetry: Speech & Acoustic Voice Analysis | Raksha Grid</title>
      </Head>

      <OnboardingGuide
        pageName="audio"
        message="Independent audio analysis channels: Speech-to-Text + Linguistic Scam Classifier running in parallel with Acoustic Voice Deepfake Biometrics."
      />

      <div className="border-b border-white/5 pb-4">
        <h1 className="text-3xl font-black text-white flex items-center gap-3">
          <Mic className="w-8 h-8 text-cyan-400" />
          Audio Telemetry & Voice Biometrics
        </h1>
        <p className="text-slate-400 text-xs font-mono mt-1">
          Decoupled Dual-Channel Pipeline: Linguistic Scam Interception & Acoustic Voice Deepfake Detection
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload & Player */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
            <h3 className="font-bold text-white text-sm uppercase tracking-wider font-mono">
              Call Recording Audio Input
            </h3>

            <div className="border-2 border-dashed border-white/10 hover:border-cyan-500/40 bg-black/40 rounded-2xl p-6 text-center cursor-pointer relative min-h-[180px] flex flex-col items-center justify-center gap-3 transition-colors">
              <input 
                type="file" 
                accept="audio/*" 
                onChange={handleFileChange} 
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" 
              />
              <Upload className="w-10 h-10 text-slate-500" />
              <p className="text-xs text-slate-300 font-mono">
                {selectedFile ? selectedFile.name : "Select WAV, MP3, OGG, or FLAC audio"}
              </p>
              <p className="text-[10px] text-slate-500 font-mono">PCM 16kHz recommended for acoustic biometrics</p>
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
              {loading ? 'Executing Dual Audio Pipelines...' : 'Run Audio Analysis'}
            </button>
          </div>

          {/* Architectural Separation Notice */}
          <div className="glass-panel p-5 rounded-2xl border-white/5 font-mono text-[11px] text-slate-400 space-y-2">
            <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs">
              <Cpu className="w-4 h-4" />
              Architectural Separation Note
            </div>
            <p>
              Voice deepfake detection and scam classification are strictly independent signals:
            </p>
            <ul className="list-disc list-inside space-y-1 text-slate-400 text-[10px]">
              <li>Scam risk high does <strong>NOT</strong> imply voice clone/deepfake.</li>
              <li>Benign conversation does <strong>NOT</strong> imply authentic human voice.</li>
              <li>Acoustic analysis runs on raw waveform, not on transcript text.</li>
            </ul>
          </div>
        </div>

        {/* Right Column: Independent Analysis Results */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs font-mono flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {result ? (
            <div className="space-y-6">
              {/* Channel 1: Acoustic Voice Deepfake Detection */}
              <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Volume2 className="w-4 h-4 text-cyan-400" />
                    <h3 className="font-bold text-white text-xs uppercase tracking-wider font-mono">
                      Channel 1: Acoustic Voice Biometrics
                    </h3>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-[10px] font-bold border inline-flex items-center gap-1.5 ${voiceBadge.bg}`}>
                    <VoiceBadgeIcon className="w-3.5 h-3.5" />
                    {voiceBadge.label}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase">Synthetic Voice Flag</span>
                    <p className="text-sm font-bold text-white mt-0.5">
                      {result.voice_analysis?.is_deepfake === true 
                        ? 'Detected (Synthetic)' 
                        : result.voice_analysis?.is_deepfake === false 
                        ? 'Natural (Human)' 
                        : 'Unavailable (None)'}
                    </p>
                  </div>
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase">Acoustic Confidence</span>
                    <p className="text-sm font-bold text-cyan-400 mt-0.5">
                      {result.voice_analysis?.confidence != null
                        ? `${(result.voice_analysis.confidence * 100).toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </div>
                </div>

                {result.voice_analysis?.reason && (
                  <div className="p-3 bg-black/30 border border-white/5 rounded-xl font-mono text-[11px] text-slate-400">
                    <span className="text-[10px] text-slate-500 uppercase block mb-1">Status Explanation</span>
                    {result.voice_analysis.reason}
                  </div>
                )}
              </div>

              {/* Channel 2: Linguistic Scam Analysis */}
              <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-blue-400" />
                    <h3 className="font-bold text-white text-xs uppercase tracking-wider font-mono">
                      Channel 2: Linguistic Scam Classification
                    </h3>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                    result.scam_analysis?.risk_band === 'high'
                      ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                      : result.scam_analysis?.risk_band === 'needs_review'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                      : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                  }`}>
                    RISK BAND: {result.scam_analysis?.risk_band?.toUpperCase() || result.risk_band?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-3 font-mono text-xs">
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase">Scam Probability</span>
                    <p className="text-base font-bold text-cyan-400 mt-0.5">
                      {result.scam_analysis?.risk_score != null
                        ? `${(result.scam_analysis.risk_score * 100).toFixed(1)}%`
                        : result.risk_score != null
                        ? `${(result.risk_score * 100).toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </div>
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase">Classifier Stage</span>
                    <p className="text-xs font-bold text-slate-300 mt-1 truncate">
                      {result.scam_analysis?.stage || result.stage || 'N/A'}
                    </p>
                  </div>
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase">Processing Time</span>
                    <p className="text-base font-bold text-slate-200 mt-0.5">
                      {result.processing_time_ms ? `${result.processing_time_ms} ms` : 'N/A'}
                    </p>
                  </div>
                </div>

                {result.scam_analysis?.fired_features && result.scam_analysis.fired_features.length > 0 && (
                  <div className="p-3 bg-black/30 border border-white/5 rounded-xl font-mono text-[11px]">
                    <span className="text-[10px] text-slate-500 uppercase block mb-1">Flagged Indicators</span>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {result.scam_analysis.fired_features.map((feat, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded text-[10px]">
                          {feat}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Channel 3: Whisper Audio Transcription */}
              <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-cyan-400" /> Whisper Speech-to-Text Transcript
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                    result.transcription?.status === 'success'
                      ? 'bg-emerald-500/10 text-emerald-300'
                      : 'bg-rose-500/10 text-rose-300'
                  }`}>
                    STT: {result.transcription?.status?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
                <div className="p-4 bg-black/50 border border-white/5 rounded-xl">
                  <p className="text-slate-300 leading-relaxed text-xs max-h-36 overflow-y-auto">
                    {result.transcription?.transcript || result.transcript || (
                      <span className="text-slate-500 italic">
                        {result.transcription?.message || "No transcription generated"}
                      </span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 font-mono text-xs text-center p-6 border border-dashed border-white/5 rounded-2xl glass-panel">
              <Mic className="w-8 h-8 mb-2 opacity-40 text-cyan-400" />
              Upload an audio recording to run independent acoustic voice biometrics and linguistic scam classification.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

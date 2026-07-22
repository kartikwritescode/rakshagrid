import React from 'react';
import { AlertTriangle, ShieldCheck, ShieldAlert, AlertCircle } from 'lucide-react';

interface RiskScorePanelProps {
  score: number;
  level: string;
  flaggedFeatures: string[];
  reasoning: string;
}

export const RiskScorePanel: React.FC<RiskScorePanelProps> = ({ score, level, flaggedFeatures, reasoning }) => {
  const getColors = () => {
    if (score < 30) return { bg: 'bg-emerald-950/40', border: 'border-emerald-500/30', text: 'text-emerald-400', stroke: '#10b981' };
    if (score < 60) return { bg: 'bg-amber-950/40', border: 'border-amber-500/30', text: 'text-amber-400', stroke: '#f59e0b' };
    if (score < 80) return { bg: 'bg-orange-950/40', border: 'border-orange-500/30', text: 'text-orange-400', stroke: '#f97316' };
    return { bg: 'bg-rose-950/40', border: 'border-rose-500/30', text: 'text-rose-400', stroke: '#e11d48' };
  };

  const getIcon = () => {
    if (score < 30) return <ShieldCheck className={`w-6 h-6 ${getColors().text}`} />;
    if (score < 60) return <AlertCircle className={`w-6 h-6 ${getColors().text}`} />;
    if (score < 80) return <AlertTriangle className={`w-6 h-6 ${getColors().text}`} />;
    return <ShieldAlert className={`w-6 h-6 ${getColors().text} animate-pulse`} />;
  };

  const colors = getColors();
  
  // Circle gauge calculations
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`glass-panel p-6 rounded-2xl border transition-colors duration-500 flex flex-col gap-5 ${colors.bg} ${colors.border}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-black/40 border border-white/5 shadow-inner`}>
            {getIcon()}
          </div>
          <div>
            <h3 className={`font-black text-lg tracking-widest uppercase ${colors.text} drop-shadow-md`}>{level}</h3>
            <p className="text-[10px] uppercase font-mono tracking-widest text-slate-400 mt-0.5">Real-time Risk Assessment</p>
          </div>
        </div>
        
        {/* Animated Circular Score */}
        <div className="relative w-20 h-20 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            <circle cx="40" cy="40" r={radius} fill="transparent" stroke="rgba(255,255,255,0.05)" strokeWidth="6" />
            <circle 
              cx="40" cy="40" r={radius} fill="transparent" 
              stroke={colors.stroke} strokeWidth="6" strokeLinecap="round"
              strokeDasharray={circumference} strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000 ease-out"
              style={{ filter: `drop-shadow(0 0 6px ${colors.stroke}80)` }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <span className="text-xl font-black text-white">{score}</span>
          </div>
        </div>
      </div>
      
      <div className="mt-1">
        <h4 className="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-widest font-mono flex items-center gap-2">
          <span className="w-1 h-1 bg-cyan-400 rounded-full" /> Analysis Reasoning
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed bg-black/40 p-4 rounded-xl border border-white/5 shadow-inner font-mono">
          {reasoning}
        </p>
      </div>

      {flaggedFeatures.length > 0 && (
        <div className="mt-1">
          <h4 className="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-widest font-mono flex items-center gap-2">
            <span className="w-1 h-1 bg-rose-500 rounded-full animate-pulse" /> Flagged Signals
          </h4>
          <div className="flex flex-wrap gap-2">
            {flaggedFeatures.map((feature, idx) => (
              <span key={idx} className="px-3 py-1.5 rounded-md bg-rose-500/10 text-[10px] font-bold text-rose-300 border border-rose-500/20 shadow-[0_0_10px_rgba(225,29,72,0.1)] uppercase tracking-wider">
                {feature}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

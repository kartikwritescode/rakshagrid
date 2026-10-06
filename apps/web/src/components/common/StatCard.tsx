import React from 'react';
import { LucideIcon } from 'lucide-react';
import { CardSkeleton } from './Skeleton';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  loading?: boolean;
  trend?: string;
  trendType?: 'positive' | 'negative' | 'neutral';
  accentColor?: string;
}

export default function StatCard({
  title,
  value,
  icon: Icon,
  description,
  loading = false,
  trend,
  trendType = 'neutral',
  accentColor = 'indigo'
}: StatCardProps) {
  if (loading) {
    return <CardSkeleton />;
  }

  const borderAccents: Record<string, string> = {
    indigo: 'hover:border-indigo-500/30 hover:shadow-indigo-500/5',
    pink: 'hover:border-pink-500/30 hover:shadow-pink-500/5',
    orange: 'hover:border-orange-500/30 hover:shadow-orange-500/5',
    rose: 'hover:border-rose-500/30 hover:shadow-rose-500/5',
    emerald: 'hover:border-emerald-500/30 hover:shadow-emerald-500/5'
  };

  const bgAccents: Record<string, string> = {
    indigo: 'bg-indigo-500/10 text-indigo-400',
    pink: 'bg-pink-500/10 text-pink-400',
    orange: 'bg-orange-500/10 text-orange-400',
    rose: 'bg-rose-500/10 text-rose-400',
    emerald: 'bg-emerald-500/10 text-emerald-400'
  };

  const getTrendColor = () => {
    if (trendType === 'positive') return 'text-emerald-400';
    if (trendType === 'negative') return 'text-rose-400';
    return 'text-slate-400';
  };

  return (
    <div className={`glass-panel border-slate-800/80 rounded-xl p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 ${borderAccents[accentColor] || borderAccents.indigo}`}>
      <div className="flex justify-between items-start">
        <div className="flex flex-col">
          <p className="text-[11px] font-mono uppercase tracking-widest text-slate-400 mb-2">{title}</p>
          <h3 className="text-4xl font-black tracking-tighter text-white mb-2 drop-shadow-md">{value}</h3>
        </div>
        <div className={`p-3 rounded-xl border border-white/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] relative overflow-hidden ${bgAccents[accentColor] || bgAccents.indigo}`}>
          <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent pointer-events-none"></div>
          <Icon className="w-6 h-6 relative z-10" />
        </div>
      </div>
      
      {(description || trend) && (
        <div className="flex items-center gap-2 mt-2 text-xs">
          {trend && (
            <span className={`font-semibold ${getTrendColor()}`}>
              {trend}
            </span>
          )}
          {description && <span className="text-slate-400">{description}</span>}
        </div>
      )}
    </div>
  );
}

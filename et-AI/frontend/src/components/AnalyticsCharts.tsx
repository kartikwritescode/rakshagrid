import React from 'react';

interface NodeDistributionProps {
  nodeTypeCounts: Record<string, number>;
}

export function NodeDistributionChart({ nodeTypeCounts }: NodeDistributionProps) {
  // Parse data
  const data = Object.entries(nodeTypeCounts).map(([type, count]) => ({
    name: type === 'BankAccount' ? 'Bank Account' : type,
    value: count,
    color: type === 'Victim' ? '#0ea5e9' : // cyan-500
           type === 'Phone' ? '#f59e0b' : // amber-500
           type === 'UPI' ? '#8b5cf6' : // violet-500
           type === 'BankAccount' ? '#10b981' : // emerald-500
           '#f43f5e' // rose-500
  }));

  const total = data.reduce((acc, curr) => acc + curr.value, 0);

  // SVG Calculations for segments using stroke-dasharray on r=50 (Circumference ~314.16)
  const radius = 50;
  const circ = 2 * Math.PI * radius; // 314.159
  let accumulatedPercent = 0;

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-6 p-4">
      {/* Donut SVG */}
      <div className="relative w-36 h-36 flex-shrink-0">
        <svg viewBox="0 0 120 120" className="w-full h-full transform -rotate-90">
          {/* Base track */}
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="transparent"
            stroke="#1e293b"
            strokeWidth="10"
          />
          {total > 0 && data.map((item, idx) => {
            const percent = item.value / total;
            const strokeLength = circ * percent;
            const strokeOffset = circ - (circ * accumulatedPercent);
            accumulatedPercent += percent;

            return (
              <circle
                key={idx}
                cx="60"
                cy="60"
                r={radius}
                fill="transparent"
                stroke={item.color}
                strokeWidth="12"
                strokeDasharray={`${strokeLength} ${circ}`}
                strokeDashoffset={strokeOffset}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out hover:scale-[1.03] origin-center cursor-pointer"
                style={{
                  transitionDelay: `${idx * 150}ms`,
                  filter: `drop-shadow(0 0 4px ${item.color}80)`
                }}
              />
            );
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-xl font-bold font-mono text-white">{total}</span>
          <span className="text-[9px] text-slate-500 font-mono uppercase tracking-wider">Total Nodes</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex-grow space-y-2.5 w-full">
        {data.map((item, idx) => {
          const percent = total > 0 ? ((item.value / total) * 100).toFixed(1) : '0';
          return (
            <div key={idx} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-slate-300 font-medium">{item.name}</span>
              </div>
              <div className="flex items-center gap-2 font-mono">
                <span className="text-slate-200 font-semibold">{item.value}</span>
                <span className="text-slate-500 text-[10px] w-12 text-right">({percent}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface RiskProfileProps {
  confidenceScores: Record<string, number>;
}

export function RiskProfileChart({ confidenceScores }: RiskProfileProps) {
  // Classify risk scores
  let critical = 0; // > 0.90
  let high = 0;     // 0.70 - 0.90
  let low = 0;      // < 0.70

  Object.values(confidenceScores).forEach(score => {
    if (score >= 0.90) critical++;
    else if (score >= 0.70) high++;
    else low++;
  });

  const categories = [
    { label: 'Critical', count: critical, color: '#e11d48', desc: 'Score >= 90%' }, // rose-600
    { label: 'High', count: high, color: '#f59e0b', desc: 'Score 70-89%' },       // amber-500
    { label: 'Low', count: low, color: '#0ea5e9', desc: 'Score < 70%' }         // cyan-500
  ];

  const maxCount = Math.max(...categories.map(c => c.count), 1);

  return (
    <div className="p-4 space-y-4">
      <div className="space-y-3.5">
        {categories.map((cat, idx) => {
          const percentWidth = (cat.count / maxCount) * 100;
          return (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between text-xs items-center">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cat.color }} />
                  <span className="font-semibold text-slate-300">{cat.label} Risk</span>
                  <span className="text-[10px] text-slate-500 font-mono">({cat.desc})</span>
                </div>
                <span className="font-bold text-slate-200 font-mono">{cat.count} hubs</span>
              </div>
              <div className="h-2.5 bg-slate-900 border border-slate-900 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-1000 ease-out"
                  style={{
                    backgroundColor: cat.color,
                    width: `${percentWidth}%`,
                    transitionDelay: `${idx * 100}ms`,
                    boxShadow: `0 0 8px ${cat.color}40`
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

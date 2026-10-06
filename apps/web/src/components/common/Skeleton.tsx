import React from 'react';

export function CardSkeleton() {
  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 animate-pulse">
      <div className="flex justify-between items-start mb-4">
        <div className="h-4 w-24 bg-slate-800 rounded"></div>
        <div className="h-8 w-8 bg-slate-800 rounded-lg"></div>
      </div>
      <div className="h-8 w-16 bg-slate-800 rounded mb-2"></div>
      <div className="h-3 w-32 bg-slate-800 rounded"></div>
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="w-full bg-slate-900/40 border border-slate-800 rounded-xl p-6 animate-pulse">
      <div className="h-6 w-32 bg-slate-800 rounded mb-6"></div>
      <div className="space-y-4">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex justify-between items-center py-2 border-b border-slate-800/40">
            <div className="space-y-2">
              <div className="h-4 w-36 bg-slate-800 rounded"></div>
              <div className="h-3 w-20 bg-slate-800 rounded"></div>
            </div>
            <div className="h-6 w-24 bg-slate-800 rounded-full"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function GraphSkeleton() {
  return (
    <div className="w-full h-[600px] bg-slate-900/40 border border-slate-800 rounded-xl flex flex-col items-center justify-center p-6 animate-pulse">
      <div className="relative w-48 h-48 flex items-center justify-center">
        <div className="absolute w-24 h-24 rounded-full border-4 border-slate-800 border-t-indigo-600 animate-spin"></div>
        <div className="w-16 h-16 rounded-full bg-slate-800"></div>
      </div>
      <div className="h-4 w-48 bg-slate-800 rounded mt-6 mb-2"></div>
      <div className="h-3 w-36 bg-slate-800 rounded"></div>
    </div>
  );
}

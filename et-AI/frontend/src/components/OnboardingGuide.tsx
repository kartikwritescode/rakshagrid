import React, { useState, useEffect } from 'react';
import { HelpCircle, X, Check } from 'lucide-react';

interface OnboardingGuideProps {
  pageName: string;
  message: string;
}

export default function OnboardingGuide({ pageName, message }: OnboardingGuideProps) {
  const [visible, setVisible] = useState(false);
  const [isDismissing, setIsDismissing] = useState(false);
  const storageKey = `has_visited_${pageName}`;

  useEffect(() => {
    // Check if the user has already visited this page
    const hasVisited = localStorage.getItem(storageKey);
    if (!hasVisited) {
      // Small timeout to allow the page mount animations to complete
      const timer = setTimeout(() => {
        setVisible(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [storageKey]);

  const handleDismiss = () => {
    setIsDismissing(true);
    // Wait for fade-out animation to finish
    setTimeout(() => {
      localStorage.setItem(storageKey, 'true');
      setVisible(false);
    }, 300);
  };

  if (!visible) return null;

  return (
    <div 
      className={`glass-panel border-indigo-500/20 bg-slate-900/50 p-4 rounded-xl shadow-xl flex items-start gap-4 transition-all duration-300 transform ${
        isDismissing 
          ? 'opacity-0 scale-95 -translate-y-4' 
          : 'opacity-100 scale-100 translate-y-0 animate-fadeIn'
      }`}
    >
      {/* Icon Badge */}
      <div className="flex-shrink-0 p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
        <HelpCircle className="w-5 h-5 text-indigo-400" />
      </div>

      {/* Message and Details */}
      <div className="flex-grow space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold font-mono tracking-wider text-indigo-400 uppercase">
            Guide // Onboarding Tutorial
          </span>
          <button 
            onClick={handleDismiss} 
            className="text-slate-500 hover:text-slate-300 p-1 rounded-md transition-colors"
            title="Dismiss Guide"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed pr-6">
          {message}
        </p>
        <div className="pt-2">
          <button
            onClick={handleDismiss}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition-all hover:shadow-md hover:shadow-indigo-500/10"
          >
            <Check className="w-3.5 h-3.5" />
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}

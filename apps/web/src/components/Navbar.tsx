import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { 
  Shield, 
  LayoutDashboard, 
  Image as ImageIcon,
  Mic,
  FileText,
  ShieldAlert,
  MapPin,
  Clock,
  Cpu,
  Activity,
  Settings,
  Info,
  AlertOctagon 
} from 'lucide-react';
import ReportCrimeModal from './ReportCrimeModal';

export default function Navbar() {
  const router = useRouter();
  const [modalOpen, setModalOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Currency', path: '/currency', icon: ImageIcon },
    { name: 'Audio Interceptor', path: '/audio', icon: Mic },
    { name: 'Transcription', path: '/transcription', icon: FileText },
    { name: 'Crime Scene', path: '/crime', icon: ShieldAlert },
    { name: 'Crime Map', path: '/map', icon: MapPin },
    { name: 'Incidents', path: '/incidents', icon: Clock },
    { name: 'Predictions', path: '/predictions', icon: Cpu },
    { name: 'Analytics', path: '/analytics', icon: Activity },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'About', path: '/about', icon: Info }
  ];

  return (
    <>
      <nav className="sticky top-4 z-40 w-full max-w-7xl mx-auto px-2 md:px-4">
        <div className="glass-panel px-3 md:px-6 py-2.5 flex items-center justify-between rounded-full border border-white/10 bg-[#0A101F]/90 backdrop-blur-2xl shadow-2xl">
          <Link href="/" className="flex items-center gap-3 shrink-0 group">
            <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.5)]">
              <Shield className="w-5 h-5 text-[#030712] fill-current" />
            </div>
            <div className="hidden sm:flex flex-col">
              <span className="font-bold text-sm md:text-base tracking-wide text-white leading-none">
                RAKSHA GRID
              </span>
              <span className="text-[8px] uppercase tracking-widest text-cyan-400 font-mono mt-0.5">
                Unified AI Platform
              </span>
            </div>
          </Link>

          <div className="flex items-center gap-1 overflow-x-auto hide-scrollbar max-w-full px-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = router.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`relative group px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all text-xs whitespace-nowrap ${isActive ? 'bg-cyan-500/20 text-white border border-cyan-500/40 font-bold' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>

          <button
            onClick={() => setModalOpen(true)}
            className="shrink-0 ml-2 px-3 py-1.5 rounded-full text-xs font-bold bg-gradient-to-r from-red-600 to-rose-500 hover:from-red-500 hover:to-rose-400 text-white shadow-lg shadow-red-900/40 transition-all border border-red-400/30 whitespace-nowrap"
          >
            Report
          </button>
        </div>
      </nav>

      <ReportCrimeModal 
        isOpen={modalOpen} 
        onClose={() => setModalOpen(false)} 
      />
    </>
  );
}

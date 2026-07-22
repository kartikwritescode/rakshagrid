import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { 
  Shield, 
  LayoutDashboard, 
  Share2, 
  Users, 
  FileSearch, 
  MessageSquare, 
  AlertOctagon 
} from 'lucide-react';
import ReportCrimeModal from './ReportCrimeModal';

export default function Navbar() {
  const router = useRouter();
  const [modalOpen, setModalOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Network Graph', path: '/graph', icon: Share2 },
    { name: 'Clusters', path: '/clusters', icon: Users },
    { name: 'Intel Packet', path: '/intelligence', icon: FileSearch },
    { name: 'Cluster Chat', path: '/chat', icon: MessageSquare }
  ];

  return (
    <>
      <nav className="sticky top-4 md:top-6 z-40 w-full max-w-6xl mx-auto px-2 md:px-4">
        <div className="glass-panel px-3 md:px-6 py-2 md:py-3 flex items-center justify-between rounded-full border border-white/10 bg-[#0A101F]/80 backdrop-blur-2xl shadow-2xl">
          {/* Brand logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.5)]">
              <Shield className="w-5 h-5 text-[#030712] fill-current" />
              <div className="absolute inset-0 rounded-xl bg-cyan-400 blur-md opacity-40 group-hover:opacity-70 transition-opacity duration-300"></div>
            </div>
            <div className="hidden sm:flex flex-col">
              <span className="font-bold text-base md:text-lg tracking-wide text-white leading-none">
                RAKSHA GRID
              </span>
              <span className="text-[8px] md:text-[10px] uppercase tracking-widest text-cyan-400 font-mono mt-0.5">
                Intelligence
              </span>
            </div>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-1 md:gap-2 flex-1 sm:flex-none justify-end overflow-x-auto hide-scrollbar">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = router.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className="relative group px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-300"
                >
                  {/* Hover background */}
                  <div className="absolute inset-0 bg-white/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  
                  <Icon className={`w-4 h-4 relative z-10 transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  <span className={`hidden lg:inline relative z-10 text-sm font-medium transition-colors ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'}`}>
                    {item.name}
                  </span>

                  {/* Active Indicator */}
                  {isActive && (
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-1 bg-cyan-400 rounded-t-full shadow-[0_-2px_10px_rgba(34,211,238,0.8)]"></div>
                  )}
                </Link>
              );
            })}

            {/* Report Crime CTA */}
            <button
              onClick={() => setModalOpen(true)}
              className="ml-2 md:ml-4 flex items-center gap-1 md:gap-2 px-3 md:px-5 py-2 rounded-full text-xs md:text-sm font-bold bg-gradient-to-r from-red-600 to-rose-500 hover:from-red-500 hover:to-rose-400 text-white shadow-[0_0_15px_rgba(225,29,72,0.4)] transition-all duration-300 hover:scale-[1.03] hover:shadow-[0_0_20px_rgba(225,29,72,0.6)] border border-red-400/30 whitespace-nowrap"
            >
              <AlertOctagon className="w-3.5 h-3.5 md:w-4 md:h-4" />
              <span className="hidden sm:inline">Report Crime</span>
              <span className="sm:hidden">Report</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Crime submission modal */}
      <ReportCrimeModal 
        isOpen={modalOpen} 
        onClose={() => setModalOpen(false)} 
        onSuccessSubmit={() => {
          if (router.pathname === '/') {
            router.replace(router.asPath);
          }
        }}
      />
    </>
  );
}

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
  AlertOctagon,
  Bot
} from 'lucide-react';
import ReportCrimeModal from './ReportCrimeModal';

export default function Sidebar() {
  const router = useRouter();
  const [modalOpen, setModalOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Network Graph', path: '/graph', icon: Share2 },
    { name: 'Clusters', path: '/clusters', icon: Users },
    { name: 'Intel Packet', path: '/intelligence', icon: FileSearch },
    { name: 'Cluster Chat', path: '/chat', icon: MessageSquare },
    { name: 'Citizen Shield', path: '/citizen-shield', icon: Bot }
  ];

  return (
    <>
      <aside className="sticky top-0 z-40 h-screen w-64 border-r border-slate-800 bg-slate-950/80 backdrop-blur-md flex flex-col hidden md:flex">
        <div className="p-6 border-b border-slate-800">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-tr from-indigo-600 to-pink-500 shadow-md shadow-indigo-600/30 shrink-0">
              <Shield className="w-5 h-5 text-white" />
              <div className="absolute inset-0 rounded-lg bg-gradient-to-tr from-indigo-600 to-pink-500 blur opacity-0 group-hover:opacity-40 transition-opacity duration-300"></div>
            </div>
            <div className="flex flex-col">
              <span className="font-semibold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                et-AI
              </span>
              <span className="text-xs font-light text-slate-400">GraphIntel</span>
            </div>
          </Link>
        </div>

        <div className="flex-1 overflow-y-auto py-6 px-4 space-y-2 flex flex-col">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = router.pathname === item.path;
            return (
              <Link
                key={item.path}
                href={item.path}
                className={`flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                }`}
              >
                <Icon className="w-5 h-5 shrink-0" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </div>

        <div className="p-4 border-t border-slate-800">
          <button
            onClick={() => setModalOpen(true)}
            className="w-full flex items-center justify-center gap-2 px-3 py-3 rounded-lg text-sm font-semibold bg-gradient-to-r from-red-600 to-indigo-600 hover:from-red-500 hover:to-indigo-500 text-white shadow-md shadow-red-900/25 transition-all duration-200 hover:scale-[1.02]"
          >
            <AlertOctagon className="w-5 h-5 text-white animate-pulse shrink-0" />
            <span>Report Crime</span>
          </button>
        </div>
      </aside>

      {/* Mobile Bottom Nav (Optional, simplified for mobile) */}
      <nav className="md:hidden fixed bottom-0 z-40 w-full border-t border-slate-800 bg-slate-950 flex justify-around p-2">
         {navItems.slice(0, 5).map((item) => {
            const Icon = item.icon;
            const isActive = router.pathname === item.path;
            return (
              <Link
                key={item.path}
                href={item.path}
                className={`p-3 rounded-lg ${isActive ? 'text-indigo-400 bg-indigo-600/10' : 'text-slate-400'}`}
              >
                <Icon className="w-6 h-6" />
              </Link>
            );
          })}
      </nav>

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

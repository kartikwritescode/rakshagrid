import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User } from 'lucide-react';
import OnboardingGuide from '../components/OnboardingGuide';

export default function ChatPage() {
  const [messages, setMessages] = useState<Array<{ role: string, content: string }>>([
    { role: 'assistant', content: 'Welcome to the Raksha Grid Intelligence Chat. How can I assist with your investigation today?' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    const newMsgs = [...messages, { role: 'user', content: input }];
    setMessages(newMsgs);
    setInput('');
    setTimeout(() => {
      setMessages([...newMsgs, { role: 'assistant', content: 'Cluster telemetry loaded. Entity link verified across 4 victim reports.' }]);
    }, 600);
  };

  return (
    <div className="space-y-6">
      <OnboardingGuide 
        pageName="chat"
        message="Investigative chat assistant for interrogating detected fraud clusters."
      />

      <div className="flex items-center justify-between border-b border-white/5 pb-4">
        <div>
          <h1 className="text-3xl font-black text-white flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-cyan-400" />
            Cluster Intelligence Chat
          </h1>
        </div>
      </div>

      <div className="glass-panel rounded-2xl border-white/5 flex flex-col h-[550px] overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-cyan-400" />
                </div>
              )}
              <div className={`max-w-[75%] rounded-2xl p-4 text-xs font-mono ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-black/60 border border-white/10 text-slate-200 rounded-bl-none'
              }`}>
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-indigo-400" />
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-white/5 bg-black/40 flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about cluster intelligence or entity linkages..."
            className="flex-1 bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
          <button
            onClick={handleSend}
            className="p-3 bg-cyan-600 text-white rounded-xl hover:bg-cyan-500 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

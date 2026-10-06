import React, { useState } from 'react';
import Head from 'next/head';
import { MessageSquare, Send, Bot, User, Loader2, AlertCircle } from 'lucide-react';
import OnboardingGuide from '../components/common/OnboardingGuide';
import { chatService } from '../services/chatService';

export default function ChatPage() {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([
    { role: 'assistant', content: 'Welcome to the Raksha Grid Intelligence Chat. How can I assist with your investigation today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMessage = input.trim();
    const newMsgs = [...messages, { role: 'user' as const, content: userMessage }];
    setMessages(newMsgs);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await chatService.sendMessage({
        messages: newMsgs.map(m => ({ role: m.role, content: m.content })),
        transcript: userMessage
      });
      setMessages([...newMsgs, { role: 'assistant', content: response.reply }]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError('Failed to reach backend AI chat advisor.');
      setMessages([...newMsgs, {
        role: 'assistant',
        content: '⚠️ Unable to connect to the backend AI intelligence advisor. Please check that FastAPI is running on port 8000.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Head>
        <title>Cluster Intelligence Chat | Raksha Grid</title>
      </Head>

      <OnboardingGuide 
        pageName="chat"
        message="Investigative chat assistant for interrogating detected fraud clusters and receiving real-time safety advice."
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

          {loading && (
            <div className="flex gap-3 justify-start items-center">
              <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="bg-black/60 border border-white/10 text-slate-400 rounded-2xl rounded-bl-none p-4 text-xs font-mono flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                Analyzing cluster telemetry & safety indicators...
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="px-4 py-2 bg-rose-500/10 border-t border-rose-500/20 text-rose-400 text-xs font-mono flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        <div className="p-4 border-t border-white/5 bg-black/40 flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about cluster intelligence or investigate scam indicators..."
            className="flex-1 bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono disabled:opacity-50"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="p-3 bg-cyan-600 text-white rounded-xl hover:bg-cyan-500 transition-colors disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}

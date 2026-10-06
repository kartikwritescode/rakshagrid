import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Loader2, Bot, User, ShieldCheck } from 'lucide-react';
import { RiskScorePanel } from './RiskScorePanel';
import ReactMarkdown from 'react-markdown';
import { scamService } from '../../services/scamService';
import { chatService } from '../../services/chatService';

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export const FraudShieldChat: React.FC = () => {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [riskData, setRiskData] = useState({
    score: 0,
    level: 'Safe',
    flaggedFeatures: [] as string[],
    reasoning: 'No conversation yet. Please start talking or paste a transcript.'
  });
  
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsRecording(false);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        setIsRecording(false);
      };
      
      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleRecording = () => {
    if (isRecording) {
      try {
        recognitionRef.current?.stop();
      } catch (e) {
        console.error(e);
      }
      setIsRecording(false);
    } else {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
          setIsRecording(true);
        } catch (e: any) {
          console.error("Failed to start speech recognition:", e);
          setIsRecording(false);
        }
      } else {
        alert('Web Speech API is not supported in this browser.');
      }
    }
  };

  const calculateRiskScore = async (transcript: string) => {
    try {
      const verdict = await scamService.analyzeText(transcript);
      const score = Math.round(verdict.risk_score * 100);
      let level = 'Safe';
      if (verdict.risk_band === 'high') level = 'High Scam Risk';
      else if (verdict.risk_band === 'needs_review') level = 'Needs Review';
      else level = 'Low Risk';

      setRiskData({
        score,
        level,
        flaggedFeatures: verdict.fired_features || [],
        reasoning: verdict.breakdown?.llm_analysis || `Analysis Stage: ${verdict.stage}. Fired indicators: ${verdict.fired_features.join(', ') || 'None'}`
      });
    } catch (error) {
      console.error('Failed to calculate risk score', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    
    const newMessages = [...messages, { role: 'user', content: userMessage }] as {role: 'user'|'assistant', content: string}[];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const fullTranscript = newMessages.map(m => `${m.role === 'user' ? 'Citizen' : 'AI'}: ${m.content}`).join('\n');
      calculateRiskScore(fullTranscript);

      try {
        const chatRes = await chatService.sendMessage({
          messages: newMessages.map(m => ({ role: m.role, content: m.content })),
          transcript: fullTranscript
        });
        setMessages([...newMessages, { role: 'assistant', content: chatRes.reply }]);
      } catch (chatErr) {
        console.error('Chat endpoint failed:', chatErr);
        const assistantMessage = `⚠️ The Raksha Grid AI chat service is currently unreachable. Please check backend connectivity. (Scam risk assessment remains available on the right panel)`;
        setMessages([...newMessages, { role: 'assistant', content: assistantMessage }]);
      }
    } catch (error) {
      console.error('Error handling send:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
      <div className="lg:col-span-2 glass-panel flex flex-col h-full rounded-2xl border border-white/5 bg-[#0A101F]/80 overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-white/5 bg-black/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm">Citizen Shield Assistant</h3>
              <p className="text-[10px] text-slate-400 font-mono">Real-time Call & Speech Interceptor</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] font-mono text-emerald-400">INTERCEPTOR ACTIVE</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
              <ShieldCheck className="w-12 h-12 mb-3 text-slate-600" />
              <p className="text-sm font-medium text-slate-400">No messages yet.</p>
              <p className="text-xs text-slate-500 max-w-xs mt-1">Speak or type a transcript below to evaluate scam risk instantly.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-cyan-400" />
                  </div>
                )}
                <div className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none shadow-lg'
                    : 'bg-black/60 border border-white/10 text-slate-200 rounded-bl-none font-mono'
                }`}>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-indigo-400" />
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-white/5 bg-black/40 flex items-center gap-2">
          <button
            onClick={toggleRecording}
            className={`p-3 rounded-xl border transition-all ${
              isRecording
                ? 'bg-rose-500/20 border-rose-500 text-rose-400 animate-pulse'
                : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
            }`}
            title={isRecording ? 'Stop Recording' : 'Start Voice Recording'}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type or speak suspicious caller transcript..."
            className="flex-1 bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="p-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-medium disabled:opacity-50 hover:opacity-90 transition-opacity shadow-lg shadow-cyan-500/20"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </div>
      </div>

      <div className="lg:col-span-1">
        <RiskScorePanel
          score={riskData.score}
          level={riskData.level}
          flaggedFeatures={riskData.flaggedFeatures}
          reasoning={riskData.reasoning}
        />
      </div>
    </div>
  );
};

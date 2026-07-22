import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Loader2, Bot, User, ShieldCheck } from 'lucide-react';
import { RiskScorePanel } from './RiskScorePanel';
import ReactMarkdown from 'react-markdown';

// Define SpeechRecognition interface for TypeScript
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
    flaggedFeatures: [],
    reasoning: 'No conversation yet. Please start talking.'
  });
  
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN'; // Default to Indian English

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
    // Scroll to bottom when messages change
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
          if (e.name === 'InvalidStateError') {
            // It's already started, let's just sync the state
            setIsRecording(true);
          } else {
            setIsRecording(false);
          }
        }
      } else {
        alert('Web Speech API is not supported in this browser.');
      }
    }
  };

  const calculateRiskScore = async (transcript: string) => {
    try {
      const res = await fetch('http://localhost:5000/api/fraud-shield/risk-score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript }),
      });
      const data = await res.json();
      if (data.success) {
        setRiskData(data.data);
      }
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
      // Create full transcript for risk score
      const fullTranscript = newMessages.map(m => `${m.role === 'user' ? 'Citizen' : 'AI'}: ${m.content}`).join('\n');
      
      // Fire risk score calculation in background
      calculateRiskScore(fullTranscript);

      // Call Chat API
      const res = await fetch('http://localhost:5000/api/fraud-shield/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, history: messages }),
      });

      const data = await res.json();
      
      if (data.success) {
        setMessages([...newMessages, { role: 'assistant', content: data.response }]);
        // Calculate risk again with AI response included
        calculateRiskScore(fullTranscript + `\nAI: ${data.response}`);
      } else {
        setMessages([...newMessages, { role: 'assistant', content: 'I am sorry, there was an error processing your request. Please try again.' }]);
      }
    } catch (error) {
      console.error('Chat error', error);
      setMessages([...newMessages, { role: 'assistant', content: 'Could not connect to the Citizen Shield server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 w-full max-w-7xl mx-auto min-h-[85vh] lg:h-[85vh]">
      {/* Risk Panel */}
      <div className="w-full lg:w-1/3 flex flex-col gap-6 overflow-y-auto pr-2 pb-2 custom-scrollbar">
        <RiskScorePanel {...riskData} />
        
        <div className="glass-panel p-6 rounded-2xl flex flex-col relative overflow-hidden bg-gradient-to-b from-blue-900/20 to-black/40 border border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.15)] mt-auto">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 pointer-events-none mix-blend-overlay"></div>
          <h3 className="text-lg font-black mb-4 flex items-center gap-2 uppercase tracking-wide text-white drop-shadow-md relative z-10">
            <ShieldCheck className="text-cyan-400 w-6 h-6" />
            Citizen Fraud Shield
          </h3>
          <p className="text-slate-300 text-sm leading-relaxed mb-6">
            This AI-powered interface helps citizens verify suspicious calls or messages in real-time. 
            Speak or type your concern, and the AI will cross-reference official I4C advisories.
          </p>
          <div className="bg-black/60 rounded-xl p-5 text-sm text-slate-200 border border-cyan-500/30 relative z-10 shadow-inner mt-2">
            <strong className="block mb-2 text-cyan-400 tracking-wider uppercase text-xs">Example Prompt:</strong>
            <span className="text-emerald-300 italic leading-relaxed block">"Someone claiming to be from CBI says my Aadhar is linked to money laundering"</span>
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="w-full lg:w-2/3 flex flex-col bg-black/40 backdrop-blur-xl rounded-2xl overflow-hidden border border-cyan-400/60 shadow-[0_0_40px_rgba(6,182,212,0.2)] relative">
        <div className="p-5 border-b border-cyan-500/40 bg-black/60 flex justify-between items-center backdrop-blur-md relative z-20 shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
          <h2 className="font-bold tracking-widest uppercase flex items-center gap-2 text-white">
            <div className="p-1.5 bg-cyan-500/20 rounded-lg border border-cyan-500/30">
              <Bot className="text-cyan-400 w-4 h-4" /> 
            </div>
            Raksha Grid Assistant
          </h2>
          <div className="text-[10px] font-bold px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30 uppercase tracking-widest flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Online
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center text-slate-500 text-center">
              <div>
                <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Hello! How can I help you today?<br/>Please describe the call or message you received.</p>
              </div>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-cyan-900/30 border border-cyan-500/30 flex items-center justify-center flex-shrink-0 shadow-[0_0_10px_rgba(34,211,238,0.2)]">
                  <Bot className="w-4 h-4 text-cyan-400" />
                </div>
              )}
              
              <div className={`max-w-[80%] rounded-2xl p-4 shadow-lg ${
                msg.role === 'user' 
                  ? 'bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-tr-sm border border-blue-500/50' 
                  : 'bg-black/60 text-slate-200 rounded-tl-sm border border-white/10 backdrop-blur-md'
              }`}>
                <div className="prose prose-sm prose-invert max-w-none text-[13px] leading-relaxed">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-slate-300" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4 justify-start">
               <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-blue-400" />
                </div>
                <div className="bg-slate-800 rounded-2xl rounded-tl-sm p-4 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
                  <span className="text-sm text-slate-400">Analyzing...</span>
                </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-black/60 border-t border-white/10 backdrop-blur-xl relative z-20">
          <div className="flex items-end gap-3">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-xl transition-all shadow-md ${
                isRecording 
                  ? 'bg-rose-600 hover:bg-rose-500 text-white animate-pulse shadow-rose-900/50 border border-rose-400/50' 
                  : 'bg-white/5 hover:bg-white/10 text-slate-400 border border-white/10'
              }`}
              title={isRecording ? 'Stop Recording' : 'Start Recording'}
            >
              {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
            
            <div className="flex-1 bg-black/40 border border-white/10 rounded-xl overflow-hidden focus-within:border-cyan-500/50 focus-within:shadow-[0_0_15px_rgba(34,211,238,0.15)] transition-all">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type or speak your concern here..."
                className="w-full bg-transparent border-none p-4 text-sm focus:ring-0 resize-none max-h-32 text-slate-200 placeholder:text-slate-600 font-mono"
                rows={1}
                style={{ minHeight: '52px' }}
              />
            </div>
            
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="p-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 border border-cyan-400/30 disabled:opacity-50 disabled:grayscale text-white transition-all shadow-[0_0_15px_rgba(34,211,238,0.3)] hover:scale-[1.02]"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

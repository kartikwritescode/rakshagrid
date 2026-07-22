import React, { useState, useEffect, useRef } from 'react';
import { supabase } from '../lib/supabase';
import { TableSkeleton } from '../components/Skeleton';
import { 
  MessageSquare, 
  Send, 
  Image as ImageIcon, 
  Search, 
  Smile, 
  Loader2, 
  User, 
  LogOut, 
  Maximize2,
  Lock,
  MessageCircle,
  Clock,
  ShieldCheck,
  ChevronDown,
  X
} from 'lucide-react';

interface ChatMessage {
  id: number;
  user_id: string;
  username: string;
  message: string;
  image_url?: string;
  created_at: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Auth states
  const [session, setSession] = useState<any>(null);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  // Chat inputs
  const [inputText, setInputText] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageName, setImageName] = useState('');
  const [uploadingImage, setUploadingImage] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // UI state
  const [enlargedImage, setEnlargedImage] = useState<string | null>(null);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  
  // Auto-scroll ref
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const emojis = ['🕵️', '🚨', '💻', '💸', '📱', '🏦', '🔒', '🔗', '🔥', '⚠️', '✅', '❌', '👍', '😮'];

  useEffect(() => {
    // 1. Auth Subscription
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event: string, currentSession: any) => {
      setSession(currentSession);
      if (currentSession?.user) {
        fetchMessages();
      } else {
        setLoading(false);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Set up real-time subscription when signed in
  useEffect(() => {
    if (!session?.user) return;

    const channel = supabase
      .channel('messages')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages' }, (payload: any) => {
        setMessages((prev) => {
          if (prev.some(m => m.id === payload.new.id)) return prev;
          return [...prev, payload.new];
        });
      })
      .subscribe();

    return () => {
      if (channel.unsubscribe) {
        channel.unsubscribe();
      } else {
        supabase.removeChannel(channel);
      }
    };
  }, [session]);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const { data, error: fetchErr } = await supabase
        .from('messages')
        .select('*')
        .order('created_at', { ascending: true })
        .limit(100);

      if (fetchErr) throw fetchErr;
      setMessages(data || []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to load chat messages.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !username.trim()) {
      setLoginError('Callsign and security email are required.');
      return;
    }

    setLoginLoading(true);
    setLoginError(null);

    try {
      // 1. Sign up user (includes username in metadata)
      const { data, error: signUpErr } = await supabase.auth.signUp({
        email: email.trim(),
        password: 'secure_password_123',
        options: {
          data: { username: username.trim() }
        }
      });

      // 2. If user already exists, sign them in
      if (signUpErr && signUpErr.message.includes('already registered')) {
        const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password: 'secure_password_123'
        });
        if (signInErr) throw signInErr;
        setSession(signInData.session);
      } else if (signUpErr) {
        throw signUpErr;
      } else {
        setSession(data.session);
      }
    } catch (err) {
      console.error(err);
      setLoginError((err as Error).message || 'Authentication failed.');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setMessages([]);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setImageFile(file);
      setImageName(file.name);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() && !imageFile) return;

    let imageUrl = '';
    const userId = session.user.id;
    const userCallsign = session.user.user_metadata?.username || session.user.email.split('@')[0];

    try {
      if (imageFile) {
        setUploadingImage(true);
        if (process.env.NEXT_PUBLIC_SUPABASE_URL) {
          // Real Supabase upload
          const fileExt = imageFile.name.split('.').pop();
          const fileName = `${Date.now()}_${Math.random().toString(36).substring(7)}.${fileExt}`;
          const { data, error: uploadErr } = await supabase.storage
            .from('chat_images')
            .upload(fileName, imageFile);

          if (uploadErr) throw uploadErr;
          
          const { data: publicData } = supabase.storage
            .from('chat_images')
            .getPublicUrl(fileName);
          imageUrl = publicData.publicUrl;
        } else {
          // Mock Upload: read as dataUrl for preview
          const reader = new FileReader();
          const promise = new Promise<string>((resolve) => {
            reader.onload = (e) => resolve(e.target?.result as string || '');
            reader.readAsDataURL(imageFile);
          });
          imageUrl = await promise;
        }
      }

      const { error: insertErr } = await supabase.from('messages').insert([
        {
          user_id: userId,
          username: userCallsign,
          message: inputText.trim(),
          image_url: imageUrl || undefined
        }
      ]).select();

      if (insertErr) throw insertErr;

      setInputText('');
      setImageFile(null);
      setImageName('');
      setShowEmojiPicker(false);
    } catch (err) {
      console.error(err);
      setError('Failed to deliver message.');
    } finally {
      setUploadingImage(false);
    }
  };

  const handleEmojiClick = (emoji: string) => {
    setInputText((prev) => prev + emoji);
  };

  // Search filter
  const filteredMessages = messages.filter(msg => 
    msg.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
    msg.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Callsign metadata
  const currentUsername = session?.user?.user_metadata?.username || session?.user?.email?.split('@')[0];

  return (
    <div className="space-y-6 h-[80vh] flex flex-col">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-2 bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            <MessageSquare className="w-8 h-8 text-indigo-500" />
            Cluster Chat Network
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time secure channels for forensic investigators sharing intelligence on active clusters.
          </p>
        </div>

        {session && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-slate-300 font-mono">Investigator: {currentUsername}</span>
            </div>
            <button
              onClick={handleSignOut}
              className="inline-flex items-center gap-1 px-3 py-1.5 border border-slate-800 hover:border-rose-500/20 text-slate-400 hover:text-rose-400 rounded-lg text-xs font-semibold hover:bg-rose-500/5 transition-all"
            >
              <LogOut className="w-3.5 h-3.5" />
              Disconnect
            </button>
          </div>
        )}
      </div>

      {/* Main Container */}
      <div className="glass-panel border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col flex-grow min-h-0 bg-slate-950/20">
        {!session ? (
          /* Authentication Screen */
          <div className="flex-grow flex items-center justify-center p-8 relative">
            {/* Security overlay details */}
            <div className="absolute right-6 top-6 text-[10px] text-slate-600 font-mono select-none pointer-events-none text-right">
              COMSEC PROTOCOL: LEVEL 4<br />
              PORT: SECURE SOCKET SHIELD
            </div>

            <div className="max-w-md w-full glass-panel border-slate-800/80 p-8 rounded-2xl space-y-6 relative overflow-hidden bg-slate-900/10">
              <div className="text-center space-y-2">
                <div className="mx-auto w-12 h-12 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex items-center justify-center">
                  <Lock className="w-6 h-6 text-indigo-400" />
                </div>
                <h2 className="text-lg font-bold text-white uppercase font-mono tracking-wider">
                  Investigator Clearance Check
                </h2>
                <p className="text-xs text-slate-400">
                  Register or join the secure network chat to collaborate on coordinates case files.
                </p>
              </div>

              {loginError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg text-xs font-medium">
                  {loginError}
                </div>
              )}

              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-400 uppercase font-mono">Investigator Callsign (Username)</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Agent_Rajesh"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-400 uppercase font-mono">Security Email Address</label>
                  <input
                    type="email"
                    required
                    placeholder="e.g. rajesh@fraudintel.gov"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loginLoading}
                  className="w-full inline-flex items-center justify-center gap-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/40 text-white rounded-lg text-xs font-semibold transition-all hover:shadow-lg hover:shadow-indigo-500/10"
                >
                  {loginLoading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Establishing SECURE Link...
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4" />
                      Join Chat Network
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        ) : (
          /* Active Chat Screen */
          <>
            {/* Top Toolbar: Search */}
            <div className="px-6 py-3 border-b border-slate-850 bg-slate-900/20 flex items-center justify-between flex-shrink-0">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono flex items-center gap-1.5">
                <MessageCircle className="w-3.5 h-3.5 text-indigo-400" />
                Live Syndicate Feed
              </span>

              <div className="relative w-48 sm:w-64">
                <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search messages..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg pl-8 pr-3 py-1.5 text-[11px] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 transition-colors"
                />
              </div>
            </div>

            {/* Message Stream */}
            <div className="flex-grow overflow-y-auto p-6 space-y-4">
              {loading ? (
                <div className="space-y-6">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-800 animate-pulse"></div>
                    <div className="h-10 bg-slate-900 rounded-lg w-1/3 animate-pulse"></div>
                  </div>
                  <div className="flex items-start gap-3 justify-end">
                    <div className="h-10 bg-indigo-950 rounded-lg w-1/4 animate-pulse"></div>
                    <div className="w-8 h-8 rounded-full bg-indigo-900 animate-pulse"></div>
                  </div>
                </div>
              ) : filteredMessages.length === 0 ? (
                <div className="flex flex-col items-center justify-center text-center h-full text-slate-500 space-y-2 py-12">
                  <MessageSquare className="w-10 h-10 text-slate-700 animate-bounce" />
                  <p className="text-xs">No intelligence reports logged in feed.</p>
                  <p className="text-[10px] text-slate-600 max-w-xs">Be the first to alert other investigators about new scam patterns.</p>
                </div>
              ) : (
                filteredMessages.map((msg) => {
                  const isOwn = msg.user_id === session.user.id;
                  const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

                  return (
                    <div 
                      key={msg.id} 
                      className={`flex gap-3 max-w-[85%] ${isOwn ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
                    >
                      {/* Avatar */}
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border ${
                        isOwn 
                          ? 'bg-indigo-600/10 border-indigo-500/20 text-indigo-400' 
                          : 'bg-slate-800 border-slate-700 text-slate-300'
                      }`}>
                        <User className="w-4.5 h-4.5" />
                      </div>

                      {/* Bubble content */}
                      <div className="space-y-1">
                        <div className={`flex items-center gap-2 text-[10px] font-mono ${isOwn ? 'justify-end' : ''}`}>
                          <span className="font-semibold text-slate-300">{msg.username}</span>
                          <span className="text-slate-500 flex items-center gap-1">
                            <Clock className="w-2.5 h-2.5" />
                            {time}
                          </span>
                        </div>

                        <div className={`p-3 rounded-xl border text-xs md:text-sm shadow-md leading-relaxed break-words relative overflow-hidden ${
                          isOwn
                            ? 'bg-indigo-600 border-indigo-500 text-white rounded-tr-none'
                            : 'bg-slate-900 border-slate-800 text-slate-200 rounded-tl-none'
                        }`}>
                          {msg.message && <p>{msg.message}</p>}

                          {/* Image inside bubble */}
                          {msg.image_url && (
                            <div className={`mt-2 rounded-lg border border-slate-800/40 overflow-hidden relative group max-w-xs cursor-pointer ${msg.message ? 'border-t' : ''}`}>
                              <img 
                                src={msg.image_url} 
                                alt="evidence upload" 
                                className="w-full max-h-48 object-cover group-hover:opacity-85 transition-opacity" 
                              />
                              <button
                                onClick={() => setEnlargedImage(msg.image_url || null)}
                                className="absolute bottom-2 right-2 p-1.5 bg-slate-950/80 hover:bg-slate-900 border border-slate-800/60 rounded-md text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                              >
                                <Maximize2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Typing, File Previews overlay */}
            {(imageName || uploadingImage) && (
              <div className="px-6 py-2 border-t border-slate-850 bg-slate-900/10 flex items-center justify-between text-xs font-mono flex-shrink-0">
                {uploadingImage ? (
                  <span className="text-indigo-400 flex items-center gap-1">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Uploading file payload...
                  </span>
                ) : (
                  <span className="text-emerald-400 flex items-center gap-1.5">
                    <ImageIcon className="w-3.5 h-3.5" />
                    Pending evidence: {imageName}
                  </span>
                )}
                {!uploadingImage && (
                  <button 
                    onClick={() => { setImageFile(null); setImageName(''); }} 
                    className="text-slate-500 hover:text-slate-300"
                  >
                    Remove
                  </button>
                )}
              </div>
            )}

            {/* Input Bar */}
            <div className="p-4 border-t border-slate-850 bg-slate-950/40 relative flex-shrink-0">
              {/* Emoji Picker Popover */}
              {showEmojiPicker && (
                <div className="absolute bottom-20 left-4 z-20 glass-panel border-slate-800 bg-slate-950 p-3 rounded-xl shadow-2xl max-w-xs animate-scaleIn">
                  <div className="grid grid-cols-7 gap-1.5">
                    {emojis.map((emoji) => (
                      <button
                        key={emoji}
                        type="button"
                        onClick={() => handleEmojiClick(emoji)}
                        className="w-7 h-7 text-sm hover:bg-slate-900 rounded-md flex items-center justify-center transition-colors"
                      >
                        {emoji}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <form onSubmit={handleSendMessage} className="flex items-center gap-3">
                {/* Emoji Picker Button */}
                <button
                  type="button"
                  onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                  className={`p-2 border rounded-lg text-slate-400 hover:text-slate-200 transition-all ${
                    showEmojiPicker 
                      ? 'bg-indigo-600/10 border-indigo-500/20 text-indigo-400' 
                      : 'border-slate-800 hover:bg-slate-900'
                  }`}
                  title="Insert Emoji"
                >
                  <Smile className="w-4.5 h-4.5" />
                </button>

                {/* File Upload Button */}
                <div className="relative">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    disabled={uploadingImage}
                    className="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10"
                  />
                  <button
                    type="button"
                    className="p-2 border border-slate-800 hover:bg-slate-900 rounded-lg text-slate-400 hover:text-slate-200 transition-all flex items-center justify-center"
                    title="Attach Image"
                  >
                    <ImageIcon className="w-4.5 h-4.5" />
                  </button>
                </div>

                {/* Input Text Field */}
                <input
                  type="text"
                  placeholder="Share case file details, phone links..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  className="flex-grow bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-xs md:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                />

                {/* Send Button */}
                <button
                  type="submit"
                  disabled={uploadingImage}
                  className="inline-flex items-center justify-center p-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/40 text-white rounded-lg text-xs font-semibold transition-all hover:shadow-lg hover:shadow-indigo-500/10"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </>
        )}
      </div>

      {/* Enlarged Image Viewer Overlay */}
      {enlargedImage && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 backdrop-blur-sm p-4 cursor-zoom-out animate-fadeIn"
          onClick={() => setEnlargedImage(null)}
        >
          <div className="relative max-w-4xl max-h-[85vh] overflow-hidden rounded-xl border border-slate-800 shadow-2xl bg-slate-900/20">
            <img 
              src={enlargedImage} 
              alt="enlarged preview" 
              className="max-w-full max-h-[85vh] object-contain" 
            />
            <button
              onClick={() => setEnlargedImage(null)}
              className="absolute top-4 right-4 p-2 bg-slate-950/80 border border-slate-800/60 text-white rounded-lg hover:bg-slate-900 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

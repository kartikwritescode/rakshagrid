import React, { useState } from 'react';
import { X, CheckCircle2, ShieldAlert, Upload, Loader2 } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface ReportCrimeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccessSubmit?: () => void;
}

export default function ReportCrimeModal({ isOpen, onClose, onSuccessSubmit }: ReportCrimeModalProps) {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form Fields
  const [victimName, setVictimName] = useState('');
  const [victimPhone, setVictimPhone] = useState('');
  const [victimEmail, setVictimEmail] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [country, setCountry] = useState('India');
  const [dateOfIncident, setDateOfIncident] = useState(new Date().toISOString().split('T')[0]);
  const [typeOfScam, setTypeOfScam] = useState('UPI Scam');
  const [scammerPhone, setScammerPhone] = useState('');
  const [scammerUpi, setScammerUpi] = useState('');
  const [scammerBank, setScammerBank] = useState('');
  const [amountLost, setAmountLost] = useState('');
  const [description, setDescription] = useState('');
  const [evidenceFile, setEvidenceFile] = useState<File | null>(null);
  const [evidenceFileName, setEvidenceFileName] = useState('');

  if (!isOpen) return null;

  // Extract browser fingerprint details for graph analysis
  const getBrowserFingerprint = () => {
    try {
      const ua = navigator.userAgent;
      const screenRes = `${window.screen.width}x${window.screen.height}`;
      const lang = navigator.language;
      const hashInput = `${ua}-${screenRes}-${lang}`;
      let hash = 0;
      for (let i = 0; i < hashInput.length; i++) {
        const char = hashInput.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return `dev_${Math.abs(hash).toString(16)}`;
    } catch {
      return `dev_${Math.floor(Math.random() * 100000000).toString(16)}`;
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setEvidenceFile(file);
      setEvidenceFileName(file.name);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!victimName.trim() || !victimPhone.trim() || !amountLost || !description.trim()) {
      setError('Please fill in all required fields (Victim Name, Phone, Amount Lost, Description).');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Handle File Upload (Real Supabase or Mock local name)
      let evidenceUrl = '';
      if (evidenceFile) {
        if (supabase && process.env.NEXT_PUBLIC_SUPABASE_URL) {
          const fileExt = evidenceFile.name.split('.').pop();
          const fileName = `${Date.now()}_${Math.random().toString(36).substring(7)}.${fileExt}`;
          const { data, error: uploadErr } = await supabase.storage
            .from('evidence')
            .upload(fileName, evidenceFile);
          
          if (uploadErr) {
            console.error('Supabase upload error:', uploadErr);
          } else if (data) {
            const { data: publicData } = supabase.storage
              .from('evidence')
              .getPublicUrl(fileName);
            evidenceUrl = publicData.publicUrl;
          }
        } else {
          // Mock Upload
          evidenceUrl = `/mock_uploads/evidence/${Date.now()}_${evidenceFile.name}`;
        }
      }

      // 2. Generate compatibility IDs
      const victimId = `VIC-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;
      const deviceFingerprint = getBrowserFingerprint();

      // 3. Post to MongoDB backend API
      const response = await fetch('http://localhost:5000/api/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          victimId,
          victimName,
          phoneNumber: scammerPhone.trim() || undefined,
          upiId: scammerUpi.trim() || undefined,
          bankAccount: scammerBank.trim() || undefined,
          deviceFingerprint,
          reportTimestamp: new Date(dateOfIncident).toISOString(),

          // Extended Fields
          victimPhone,
          victimEmail,
          city,
          state,
          country,
          dateOfIncident: new Date(dateOfIncident).toISOString(),
          typeOfScam,
          amountLost: Number(amountLost),
          description,
          evidenceUrl: evidenceUrl || undefined
        }),
      });

      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.message || 'Failed to submit report.');
      }

      // Success
      setSuccess(true);
      if (onSuccessSubmit) {
        onSuccessSubmit();
      }
      setTimeout(() => {
        // Auto-close after animation
        handleClose();
      }, 2500);

    } catch (err) {
      console.error(err);
      setError((err as Error).message || 'An error occurred during submission.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    // Reset state
    setSuccess(false);
    setError(null);
    setVictimName('');
    setVictimPhone('');
    setVictimEmail('');
    setCity('');
    setState('');
    setCountry('India');
    setDateOfIncident(new Date().toISOString().split('T')[0]);
    setTypeOfScam('UPI Scam');
    setScammerPhone('');
    setScammerUpi('');
    setScammerBank('');
    setAmountLost('');
    setDescription('');
    setEvidenceFile(null);
    setEvidenceFileName('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div 
        className="glass-panel border-slate-800 bg-slate-950/90 max-w-2xl w-full rounded-xl overflow-hidden shadow-2xl relative flex flex-col max-h-[90vh] transition-transform scale-100 duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Warning bar */}
        <div className="h-1 bg-gradient-to-r from-red-500 via-indigo-600 to-pink-500"></div>

        {/* Success State */}
        {success ? (
          <div className="p-12 flex flex-col items-center justify-center text-center space-y-6 flex-grow animate-scaleIn">
            <div className="relative">
              <CheckCircle2 className="w-20 h-20 text-emerald-500 animate-pulse" />
              <div className="absolute inset-0 w-20 h-20 bg-emerald-500/20 blur rounded-full -z-10 animate-ping"></div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-white font-mono uppercase tracking-wider">
                Report Logged Successfully
              </h2>
              <p className="text-xs text-slate-400 max-w-sm font-sans leading-relaxed">
                Incidents are parsed by the GraphEngine. Cross-victim shared details will automatically form a cluster profile.
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-indigo-500" />
                <h2 className="text-base font-bold text-white uppercase font-mono tracking-wider">
                  Report Cyber Incident
                </h2>
              </div>
              <button 
                onClick={handleClose} 
                className="text-slate-500 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-900/60 transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Form Scroll Area */}
            <form onSubmit={handleSubmit} className="flex-grow overflow-y-auto p-6 space-y-6">
              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400">
                  {error}
                </div>
              )}

              {/* 1. Victim Details */}
              <div className="space-y-4">
                <h3 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider font-mono border-b border-slate-800 pb-1">
                  Victim Profiling
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">Victim Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Ramesh Kumar"
                      value={victimName}
                      onChange={(e) => setVictimName(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">Phone Number *</label>
                    <input
                      type="tel"
                      required
                      placeholder="e.g. +91 98765 43210"
                      value={victimPhone}
                      onChange={(e) => setVictimPhone(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>
                  <div className="space-y-1 md:col-span-2">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">Email Address (Optional)</label>
                    <input
                      type="email"
                      placeholder="e.g. ramesh@example.com"
                      value={victimEmail}
                      onChange={(e) => setVictimEmail(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">City</label>
                    <input
                      type="text"
                      placeholder="e.g. Mumbai"
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">State</label>
                    <input
                      type="text"
                      placeholder="e.g. Maharashtra"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* 2. Scam/Incident Details */}
              <div className="space-y-4">
                <h3 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider font-mono border-b border-slate-800 pb-1">
                  Incident Telemetry
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">Date of Incident</label>
                    <input
                      type="date"
                      value={dateOfIncident}
                      onChange={(e) => setDateOfIncident(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors font-mono"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">Type of Scam</label>
                    <select
                      value={typeOfScam}
                      onChange={(e) => setTypeOfScam(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                    >
                      <option value="UPI Scam">UPI Scam</option>
                      <option value="Bank Fraud">Bank Fraud</option>
                      <option value="Fake Job">Fake Job</option>
                      <option value="OTP Scam">OTP Scam</option>
                      <option value="Loan Scam">Loan Scam</option>
                      <option value="Investment Scam">Investment Scam</option>
                      <option value="QR Scam">QR Scam</option>
                      <option value="Courier Scam">Courier Scam</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">Amount Lost (INR) *</label>
                    <input
                      type="number"
                      required
                      placeholder="e.g. 50000"
                      value={amountLost}
                      onChange={(e) => setAmountLost(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors font-mono"
                    />
                  </div>
                </div>
              </div>

              {/* 3. Scammer Details */}
              <div className="space-y-4">
                <h3 className="text-xs font-semibold text-rose-500 uppercase tracking-wider font-mono border-b border-slate-800 pb-1">
                  Accused Info (Graph linkage keys)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-rose-400 font-mono uppercase">Scammer Phone Number</label>
                    <input
                      type="tel"
                      placeholder="e.g. +91 99001 12233"
                      value={scammerPhone}
                      onChange={(e) => setScammerPhone(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500/50 transition-colors"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-rose-400 font-mono uppercase">Scammer UPI ID</label>
                    <input
                      type="text"
                      placeholder="e.g. fraudster@okaxis"
                      value={scammerUpi}
                      onChange={(e) => setScammerUpi(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500/50 transition-colors font-mono"
                    />
                  </div>
                  <div className="space-y-1 md:col-span-2">
                    <label className="text-[10px] text-rose-400 font-mono uppercase">Scammer Bank Account (Optional)</label>
                    <input
                      type="text"
                      placeholder="e.g. 501002345678 IFSC HDFC0000010"
                      value={scammerBank}
                      onChange={(e) => setScammerBank(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500/50 transition-colors font-mono"
                    />
                  </div>
                </div>
              </div>

              {/* 4. Description and Evidence */}
              <div className="space-y-4">
                <h3 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider font-mono border-b border-slate-800 pb-1">
                  Narrative & Evidence
                </h3>
                <div className="space-y-4">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase">Scam Narrative *</label>
                    <textarea
                      required
                      rows={3}
                      placeholder="Describe how the fraud occurred..."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                    />
                  </div>
                  
                  {/* File Upload Component */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-mono uppercase block">Upload Evidence (Images, PDF, Screenshots)</label>
                    <div className="border border-dashed border-slate-800 hover:border-indigo-500/40 bg-slate-900/20 rounded-xl p-6 transition-colors flex flex-col items-center justify-center gap-2 cursor-pointer relative">
                      <input
                        type="file"
                        accept="image/*,application/pdf"
                        onChange={handleFileChange}
                        className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                      />
                      <Upload className="w-8 h-8 text-slate-500" />
                      <div className="text-center">
                        <span className="text-xs text-indigo-400 font-semibold hover:underline">Click to upload file</span>
                        <p className="text-[10px] text-slate-500 mt-1">PNG, JPG, PDF up to 10MB</p>
                      </div>
                      {evidenceFileName && (
                        <div className="mt-2 text-xs font-semibold text-emerald-400 font-mono flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>{evidenceFileName}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-850 mt-6">
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-slate-200 rounded-lg text-xs font-semibold hover:bg-slate-900/60 transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/40 text-white rounded-lg text-xs font-semibold transition-all hover:shadow-lg hover:shadow-indigo-500/10"
                >
                  {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  Submit Case
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

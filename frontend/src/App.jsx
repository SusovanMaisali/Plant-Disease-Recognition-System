import React, { useState, useEffect, useRef } from 'react';
import { 
  Leaf, User, Mail, Phone, Lock, Eye, LogOut, Upload, Camera, 
  MapPin, CloudSun, AlertTriangle, MessageSquare, Play, Square,
  Download, Trash2, Globe, Settings, ShieldCheck, ChevronRight,
  TrendingUp, Sparkles, Languages, Check, RefreshCw, Send, Mic
} from 'lucide-react';

const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi (हिन्दी)' },
  { code: 'bn', name: 'Bengali (বাংলা)' },
  { code: 'te', name: 'Telugu (తెలుగు)' },
  { code: 'mr', name: 'Marathi (मराठी)' },
  { code: 'ta', name: 'Tamil (தமிழ்)' },
  { code: 'ur', name: 'Urdu (اردو)' },
  { code: 'gu', name: 'Gujarati (ગુજરાતી)' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ml', name: 'Malayalam (മലയാളം)' },
  { code: 'pb', name: 'Punjabi (ਪੰਜਾਬੀ)' },
  { code: 'es', name: 'Spanish (Español)' },
  { code: 'fr', name: 'French (Français)' }
];

export default function App() {
  // Auth State
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLogin, setIsLogin] = useState(true);
  const [authForm, setAuthForm] = useState({ name: '', mobile: '', email: '', captcha: '', otp: '' });
  const [captcha, setCaptcha] = useState({ num1: 0, num2: 0, sum: 0 });
  const [otpSent, setOtpSent] = useState(false);
  const [simulatedOtp, setSimulatedOtp] = useState('');
  const [authError, setAuthError] = useState('');
  
  // Dashboard Settings
  const [lang, setLang] = useState('en');
  const [minConfidence, setMinConfidence] = useState(50);
  const [showGradCam, setShowGradCam] = useState(true);
  const [showTop3, setShowTop3] = useState(true);
  const [useGemini, setUseGemini] = useState(true);
  const [showChatbot, setShowChatbot] = useState(true);

  // Live telemetry (Weather/Location)
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(true);

  // Diagnostic states
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [cameraActive, setCameraActive] = useState(false);
  const [diagResult, setDiagResult] = useState(null);
  const [diagLoading, setDiagLoading] = useState(false);
  const [diagError, setDiagError] = useState('');

  // History list
  const [history, setHistory] = useState([]);
  const [historySearch, setHistorySearch] = useState('');
  const [deletingIndex, setDeletingIndex] = useState(null);

  // Chatbot State
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'model', text: 'Hello! I am your CropSense Agronomist chatbot. Ask me any questions about plant health, pest control, or fertilizers.' }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  const [listening, setListening] = useState(false);

  // Translation mapping for headers
  const [translations, setTranslations] = useState({});

  // Audio elements
  const [audioPlaying, setAudioPlaying] = useState(false);
  const audioRef = useRef(null);
  const videoRef = useRef(null);

  // Load CAPTCHA
  const fetchCaptcha = async () => {
    try {
      const res = await fetch('/api/auth/captcha');
      const data = await res.json();
      setCaptcha(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (!user) {
      fetchCaptcha();
    }
  }, [user, isLogin]);

  // Load User History & Weather Telemetry
  useEffect(() => {
    if (user) {
      fetchHistory();
      fetchWeather();
    }
  }, [user]);

  // Language Change translations (simulated translation cache or API call)
  useEffect(() => {
    if (user && lang !== 'en' && diagResult) {
      translateDiagnosis();
    } else {
      setTranslations({});
    }
  }, [lang, diagResult]);

  const fetchWeather = async (coords = null) => {
    setWeatherLoading(true);
    try {
      let url = '/api/weather';
      if (coords) {
        url += `?lat=${coords.latitude}&lon=${coords.longitude}`;
      }
      const res = await fetch(url);
      const data = await res.json();
      setWeather(data);
    } catch (e) {
      console.error("Failed to load weather: ", e);
    } finally {
      setWeatherLoading(false);
    }
  };

  const requestGpsLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          fetchWeather({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude
          });
        },
        (err) => {
          console.warn("GPS location failed, fallback to IP:", err);
          fetchWeather();
        }
      );
    } else {
      fetchWeather();
    }
  };

  const fetchHistory = async () => {
    if (!user) return;
    try {
      const res = await fetch(`/api/history?mobile=${user.mobile}`);
      const data = await res.json();
      setHistory(data.history || []);
    } catch (e) {
      console.error(e);
    }
  };

  // Auth Operations
  const handleRequestOtp = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (parseInt(authForm.captcha) !== captcha.sum) {
      setAuthError('Incorrect CAPTCHA calculation.');
      fetchCaptcha();
      return;
    }
    try {
      const res = await fetch('/api/auth/send-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mobile: authForm.mobile })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'User not registered.');
      }
      const data = await res.json();
      setOtpSent(true);
      setSimulatedOtp(data.otp); // Simulated OTP returned in debug API
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch('/api/auth/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mobile: authForm.mobile, otp: authForm.otp })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Invalid OTP.');
      }
      const data = await res.json();
      localStorage.setItem('user', JSON.stringify(data.user));
      setUser(data.user);
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (parseInt(authForm.captcha) !== captcha.sum) {
      setAuthError('Incorrect CAPTCHA calculation.');
      fetchCaptcha();
      return;
    }
    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: authForm.name,
          mobile: authForm.mobile,
          email: authForm.email
        })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Signup failed.');
      }
      const data = await res.json();
      localStorage.setItem('user', JSON.stringify(data.user));
      setUser(data.user);
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('user');
    setUser(null);
    setOtpSent(false);
    setAuthForm({ name: '', mobile: '', email: '', captcha: '', otp: '' });
    setDiagResult(null);
    setPreviewUrl('');
    setTranslations({});
  };

  // Image Upload and Camera Capture
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDiagResult(null);
      setTranslations({});
    }
  };

  const triggerCamera = async () => {
    setCameraActive(true);
    setPreviewUrl('');
    setSelectedFile(null);
    setDiagResult(null);
    setTranslations({});
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (e) {
      console.error(e);
      setCameraActive(false);
      alert("Failed to access camera.");
    }
  };

  const capturePhoto = () => {
    const canvas = document.createElement('canvas');
    if (videoRef.current) {
      const video = videoRef.current;
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      canvas.toBlob((blob) => {
        const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
        stopCamera();
      }, "image/jpeg", 0.9);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  };

  // Diagnostic execution
  const runDiagnosis = async () => {
    if (!selectedFile) return;
    setDiagLoading(true);
    setDiagError('');
    setDiagResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('mobile', user.mobile);
    formData.append('use_gemini', useGemini ? 'true' : 'false');
    if (weather && weather.location) {
      formData.append('latitude', weather.location.latitude);
      formData.append('longitude', weather.location.longitude);
    }

    try {
      const res = await fetch('/api/diagnose', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.status === 'invalid_leaf') {
        setDiagError(data.message);
      } else if (data.status === 'success') {
        setDiagResult(data);
        fetchHistory(); // Refresh history panel
      } else {
        setDiagError("An unexpected error occurred during analysis.");
      }
    } catch (e) {
      setDiagError("Failed to connect to the server.");
    } finally {
      setDiagLoading(false);
    }
  };

  // Chat bot interaction
  const triggerChat = async (messageText = null) => {
    const textToSend = messageText || chatInput;
    if (!textToSend.trim()) return;

    setChatLoading(true);
    const newMsg = { role: 'user', text: textToSend };
    const updatedHistory = [...chatHistory, newMsg];
    setChatHistory(updatedHistory);
    if (!messageText) setChatInput('');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          history: chatHistory
        })
      });
      const data = await res.json();
      setChatHistory([...updatedHistory, { role: 'model', text: data.response }]);
    } catch (e) {
      setChatHistory([...updatedHistory, { role: 'model', text: "Error: Failed to fetch reply." }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Speech Recognition (Web Speech API)
  const handleStt = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech-to-text not supported in your browser.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setChatInput(text);
    };

    recognition.onerror = () => {
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.start();
  };

  // Voice Readout summary
  const playTts = async () => {
    if (!diagResult) return;
    if (audioPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      setAudioPlaying(false);
      return;
    }

    const recText = translations.treatment || diagResult.diagnosis.treatment || "";
    const voiceText = `Plant identified: ${translations.plant_name || diagResult.diagnosis.plant_name}. Disease: ${translations.disease_name || diagResult.diagnosis.disease_name}. Severity: ${diagResult.diagnosis.severity}. Recommendation: ${recText.slice(0, 150)}.`;

    try {
      const res = await fetch('/api/generate-tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: voiceText, lang: lang })
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.play();
      setAudioPlaying(true);
      audio.onended = () => setAudioPlaying(false);
    } catch (e) {
      alert("Failed to load voice synthesis.");
    }
  };

  // PDF Download Booklet
  const downloadPdf = async () => {
    if (!diagResult) return;
    try {
      const res = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plant_name: diagResult.diagnosis.plant_name,
          disease_name: diagResult.diagnosis.disease_name,
          cnn_confidence: diagResult.cnn_confidence,
          severity: diagResult.diagnosis.severity,
          diagnosis: diagResult.diagnosis,
          location: diagResult.location,
          weather: diagResult.weather,
          original_image: diagResult.original_image
        })
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `CropSense_Report_${diagResult.diagnosis.plant_name.replace(/\s+/g, '_')}.pdf`;
      link.click();
    } catch (e) {
      alert("Failed to generate PDF report booklet.");
    }
  };

  // Delete history item
  const handleDeleteHistory = async (item) => {
    try {
      const res = await fetch('/api/history/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mobile: user.mobile,
          date: item.Date,
          time: item.Time
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setHistory(data.history || []);
        setDeletingIndex(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Translation helpers
  const translateDiagnosis = async () => {
    if (!diagResult) return;
    const diag = diagResult.diagnosis;
    const keysToTranslate = {
      plant_name: diag.plant_name,
      disease_name: diag.disease_name,
      disease_pathogen: diag.disease_pathogen,
      symptoms: diag.symptoms,
      description: diag.description,
      treatment: diag.treatment,
      organic_treatment: diag.organic_treatment,
      chemical_treatment: diag.chemical_treatment,
    };

    const newTranslations = {};
    for (const [key, val] of Object.entries(keysToTranslate)) {
      if (!val) continue;
      try {
        const res = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: val, target: lang })
        });
        const data = await res.json();
        newTranslations[key] = data.translated;
      } catch (e) {
        newTranslations[key] = val;
      }
    }
    setTranslations(newTranslations);
  };

  // Filter history
  const filteredHistory = history.filter(item => {
    const q = historySearch.toLowerCase();
    return (
      item.Plant.toLowerCase().includes(q) ||
      item.Disease.toLowerCase().includes(q) ||
      item.City.toLowerCase().includes(q)
    );
  });

  // Welcome Screen
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden bg-cs-bg">
        {/* Visual Gradients */}
        <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-emerald-950/20 blur-[150px]"></div>
        <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-emerald-950/20 blur-[150px]"></div>

        <div className="w-full max-w-md glass-panel p-8 rounded-3xl animate-fade-in relative z-10">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-cs-mint/10 border border-cs-mint/35 text-cs-mint mb-4">
              <Leaf size={32} />
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">CropSense AI</h1>
            <p className="text-cs-muted text-sm max-w-xs mx-auto">
              Intelligent Crop Disease Detection & Farm Management Dashboard
            </p>
          </div>

          {authError && (
            <div className="mb-6 p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 text-sm flex items-start gap-2.5">
              <AlertTriangle size={18} className="mt-0.5 shrink-0" />
              <span>{authError}</span>
            </div>
          )}

          {isLogin ? (
            /* SIGN IN FORM */
            <form onSubmit={otpSent ? handleVerifyOtp : handleRequestOtp} className="space-y-5">
              <div className="text-sm font-semibold text-white border-b border-cs-border pb-2.5 mb-2 flex items-center gap-2">
                <Lock size={16} className="text-cs-mint" />
                <span>🔑 Farmer Sign In</span>
              </div>

              {!otpSent ? (
                /* SEND OTP STEP */
                <>
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-cs-muted">Mobile Number</label>
                    <div className="relative">
                      <Phone size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cs-muted" />
                      <input 
                        type="text" 
                        placeholder="e.g. 9876543210"
                        className="w-full pl-10 pr-4 py-3 rounded-xl bg-cs-cardlight border border-cs-border focus:outline-none focus:border-cs-mint transition text-white placeholder-emerald-900/60"
                        value={authForm.mobile}
                        onChange={(e) => setAuthForm({ ...authForm, mobile: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-cs-muted">CAPTCHA Challenge</label>
                      <div className="flex items-center justify-center py-2.5 rounded-xl bg-cs-cardlight/60 border border-cs-border select-none text-white font-mono text-sm tracking-wider">
                        {captcha.num1} + {captcha.num2} = ?
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-cs-muted">Your Answer</label>
                      <input 
                        type="number" 
                        placeholder="Sum result"
                        className="w-full px-4 py-2.5 rounded-xl bg-cs-cardlight border border-cs-border focus:outline-none focus:border-cs-mint transition text-white placeholder-emerald-900/60"
                        value={authForm.captcha}
                        onChange={(e) => setAuthForm({ ...authForm, captcha: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <button 
                    type="submit"
                    className="w-full py-3.5 rounded-xl bg-cs-mint hover:bg-cs-emerald text-cs-bg font-bold tracking-wide transition flex items-center justify-center gap-2 mt-2"
                  >
                    <span>Send Verification Code</span>
                    <ChevronRight size={18} />
                  </button>
                </>
              ) : (
                /* VERIFY OTP STEP */
                <>
                  <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-900/40 text-cs-muted text-xs leading-relaxed mb-4">
                    💬 Simulated SMS: A verification code has been dispatched. Enter <strong>{simulatedOtp}</strong> to authenticate.
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-cs-muted">Verification Code (OTP)</label>
                    <input 
                      type="text" 
                      placeholder="Enter 4-digit code"
                      maxLength={4}
                      className="w-full px-4 py-3 rounded-xl bg-cs-cardlight border border-cs-border focus:outline-none focus:border-cs-mint transition text-white text-center font-mono text-xl tracking-widest placeholder-emerald-900/60"
                      value={authForm.otp}
                      onChange={(e) => setAuthForm({ ...authForm, otp: e.target.value })}
                      required
                    />
                  </div>

                  <div className="flex gap-2">
                    <button 
                      type="button"
                      onClick={() => setOtpSent(false)}
                      className="w-1/3 py-3.5 rounded-xl border border-cs-border hover:bg-cs-cardlight text-cs-muted font-bold transition"
                    >
                      Back
                    </button>
                    <button 
                      type="submit"
                      className="w-2/3 py-3.5 rounded-xl bg-cs-mint hover:bg-cs-emerald text-cs-bg font-bold tracking-wide transition"
                    >
                      Verify & Login
                    </button>
                  </div>
                </>
              )}

              <div className="text-center pt-4 border-t border-cs-border text-xs text-cs-muted">
                Don't have an account?{' '}
                <button 
                  type="button" 
                  onClick={() => { setIsLogin(false); setAuthError(''); }}
                  className="text-cs-mint hover:underline font-semibold"
                >
                  Create one now
                </button>
              </div>
            </form>
          ) : (
            /* REGISTER ACCOUNT FORM */
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="text-sm font-semibold text-white border-b border-cs-border pb-2.5 mb-2 flex items-center gap-2">
                <User size={16} className="text-cs-mint" />
                <span>📝 Register New Farmer Account</span>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-cs-muted">Full Name</label>
                <div className="relative">
                  <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cs-muted" />
                  <input 
                    type="text" 
                    placeholder="e.g. John Doe"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-cs-cardlight border border-cs-border focus:outline-none focus:border-cs-mint transition text-white placeholder-emerald-900/60"
                    value={authForm.name}
                    onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-cs-muted">Mobile Number</label>
                <div className="relative">
                  <Phone size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cs-muted" />
                  <input 
                    type="text" 
                    placeholder="e.g. 9876543210"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-cs-cardlight border border-cs-border focus:outline-none focus:border-cs-mint transition text-white placeholder-emerald-900/60"
                    value={authForm.mobile}
                    onChange={(e) => setAuthForm({ ...authForm, mobile: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-cs-muted">Email ID</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cs-muted" />
                  <input 
                    type="email" 
                    placeholder="e.g. john@example.com"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-cs-cardlight border border-cs-border focus:outline-none focus:border-cs-mint transition text-white placeholder-emerald-900/60"
                    value={authForm.email}
                    onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-cs-muted">CAPTCHA</label>
                  <div className="flex items-center justify-center py-2.5 rounded-xl bg-cs-cardlight/60 border border-cs-border text-white font-mono text-sm">
                    {captcha.num1} + {captcha.num2} = ?
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-cs-muted">Answer</label>
                  <input 
                    type="number" 
                    placeholder="Result"
                    className="w-full px-4 py-2.5 rounded-xl bg-cs-cardlight border border-cs-border focus:outline-none focus:border-cs-mint transition text-white placeholder-emerald-900/60"
                    value={authForm.captcha}
                    onChange={(e) => setAuthForm({ ...authForm, captcha: e.target.value })}
                    required
                  />
                </div>
              </div>

              <button 
                type="submit"
                className="w-full py-3.5 rounded-xl bg-cs-mint hover:bg-cs-emerald text-cs-bg font-bold tracking-wide transition mt-2"
              >
                Register & Sign In
              </button>

              <div className="text-center pt-3 border-t border-cs-border text-xs text-cs-muted">
                Already registered?{' '}
                <button 
                  type="button" 
                  onClick={() => { setIsLogin(true); setAuthError(''); }}
                  className="text-cs-mint hover:underline font-semibold"
                >
                  Sign In here
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    );
  }

  // Dashboard Workspace
  return (
    <div className="min-h-screen flex flex-col md:flex-row relative bg-cs-bg">
      {/* Sidebar Navigation Panel */}
      <aside className="w-full md:w-80 shrink-0 border-b md:border-b-0 md:border-r border-cs-border bg-cs-card p-6 flex flex-col justify-between">
        <div className="space-y-8">
          {/* Brand Header */}
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cs-mint/15 border border-cs-mint/45 text-cs-mint">
              <Leaf size={24} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-wide">CropSense AI</h2>
              <p className="text-xs text-cs-mint font-medium">v3.0 Pro + Gemini</p>
            </div>
          </div>

          <div className="h-px bg-cs-border"></div>

          {/* Controls */}
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-bold text-cs-muted flex items-center gap-1.5">
                <Globe size={14} className="text-cs-mint" />
                <span>SELECT TELEMETRY LANGUAGE</span>
              </label>
              <select 
                className="w-full py-2.5 px-3.5 rounded-xl bg-cs-cardlight border border-cs-border text-white text-sm focus:outline-none focus:border-cs-mint cursor-pointer"
                value={lang}
                onChange={(e) => setLang(e.target.value)}
              >
                {SUPPORTED_LANGUAGES.map(sl => (
                  <option key={sl.code} value={sl.code}>{sl.name}</option>
                ))}
              </select>
            </div>

            {/* Config Sliders & Toggles */}
            <div className="space-y-4">
              <label className="text-xs font-bold text-cs-muted flex items-center gap-1.5">
                <Settings size={14} className="text-cs-mint" />
                <span>ADVANCED CLASSIFIER CONFIGS</span>
              </label>

              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-white">
                  <span>Min. CNN Confidence</span>
                  <span className="font-semibold text-cs-mint">{minConfidence}%</span>
                </div>
                <input 
                  type="range" 
                  min="20" 
                  max="90" 
                  className="w-full accent-cs-mint cursor-pointer"
                  value={minConfidence}
                  onChange={(e) => setMinConfidence(parseInt(e.target.value))}
                />
              </div>

              <div className="space-y-3.5 pt-2">
                <label className="flex items-center justify-between text-xs text-white cursor-pointer select-none">
                  <span>Show Grad-CAM Heatmap</span>
                  <input 
                    type="checkbox" 
                    checked={showGradCam} 
                    onChange={() => setShowGradCam(!showGradCam)} 
                    className="w-4 h-4 rounded border-cs-border text-cs-mint focus:ring-0 focus:ring-offset-0 accent-cs-mint"
                  />
                </label>

                <label className="flex items-center justify-between text-xs text-white cursor-pointer select-none">
                  <span>Show Top-3 CNN Predictions</span>
                  <input 
                    type="checkbox" 
                    checked={showTop3} 
                    onChange={() => setShowTop3(!showTop3)} 
                    className="w-4 h-4 rounded border-cs-border text-cs-mint focus:ring-0 focus:ring-offset-0 accent-cs-mint"
                  />
                </label>

                <label className="flex items-center justify-between text-xs text-white cursor-pointer select-none">
                  <span>Enable Gemini Vision Analysis</span>
                  <input 
                    type="checkbox" 
                    checked={useGemini} 
                    onChange={() => setUseGemini(!useGemini)} 
                    className="w-4 h-4 rounded border-cs-border text-cs-mint focus:ring-0 focus:ring-offset-0 accent-cs-mint"
                  />
                </label>

                <label className="flex items-center justify-between text-xs text-white cursor-pointer select-none">
                  <span>Show AI Farming Chatbot</span>
                  <input 
                    type="checkbox" 
                    checked={showChatbot} 
                    onChange={() => setShowChatbot(!showChatbot)} 
                    className="w-4 h-4 rounded border-cs-border text-cs-mint focus:ring-0 focus:ring-offset-0 accent-cs-mint"
                  />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* User Card */}
        <div className="mt-8 pt-4 border-t border-cs-border space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-cs-cardlight border border-cs-border flex items-center justify-center text-cs-mint text-sm font-bold">
              {user.name.slice(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-white truncate">{user.name}</p>
              <p className="text-xs text-cs-muted truncate">{user.email}</p>
            </div>
          </div>

          <button 
            onClick={handleSignOut}
            className="w-full py-2.5 rounded-xl border border-cs-border hover:bg-red-500/10 hover:border-red-500/30 text-cs-muted hover:text-red-400 text-xs font-semibold tracking-wide transition flex items-center justify-center gap-2"
          >
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Work Area */}
      <main className="flex-1 p-6 md:p-10 space-y-8 overflow-y-auto max-h-screen">
        {/* Hero Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-cs-border pb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Leaf Diagnostic Hub</h1>
            <p className="text-sm text-cs-muted">Crop pathology analysis, micro-climate insights, and agronomy advice</p>
          </div>

          {/* Quick Stats */}
          <div className="flex gap-4">
            <div className="px-4 py-2.5 rounded-xl bg-cs-card border border-cs-border text-center">
              <span className="text-xs text-cs-muted block mb-0.5">Scans Performed</span>
              <span className="text-lg font-bold text-cs-mint">{history.length}</span>
            </div>
            <div className="px-4 py-2.5 rounded-xl bg-cs-card border border-cs-border text-center">
              <span className="text-xs text-cs-muted block mb-0.5">Client Status</span>
              <span className="text-lg font-bold text-white flex items-center gap-1.5 justify-center">
                <ShieldCheck size={18} className="text-cs-mint" />
                <span>Active</span>
              </span>
            </div>
          </div>
        </div>

        {/* Upper Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Geolocation & Weather */}
          <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-white tracking-wide text-sm flex items-center gap-2">
                  <CloudSun size={18} className="text-cs-mint" />
                  <span>Climate Telemetry</span>
                </h3>
                <button 
                  onClick={requestGpsLocation}
                  className="p-2 rounded-lg bg-cs-cardlight border border-cs-border text-cs-mint hover:bg-cs-border transition text-xs font-semibold flex items-center gap-1"
                >
                  <MapPin size={12} />
                  <span>Use GPS</span>
                </button>
              </div>

              {weatherLoading ? (
                <div className="py-12 flex flex-col items-center justify-center gap-3 text-cs-muted text-sm">
                  <RefreshCw size={24} className="animate-spin text-cs-mint" />
                  <span>Syncing weather coordinates...</span>
                </div>
              ) : weather ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-xs text-cs-muted block uppercase tracking-wider font-bold">Detected Location</span>
                    <span className="text-base font-bold text-white">{weather.location.city}, {weather.location.country}</span>
                    <span className="text-xs text-cs-muted block mt-0.5">Coords: {weather.location.latitude?.toFixed(3)}, {weather.location.longitude?.toFixed(3)}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-xl bg-cs-cardlight/60 border border-cs-border/60">
                      <span className="text-xs text-cs-muted block">Temperature</span>
                      <span className="text-lg font-bold text-white">{weather.weather.temperature}°C</span>
                    </div>
                    <div className="p-3 rounded-xl bg-cs-cardlight/60 border border-cs-border/60">
                      <span className="text-xs text-cs-muted block">Humidity</span>
                      <span className="text-lg font-bold text-white">{weather.weather.humidity}%</span>
                    </div>
                    <div className="p-3 rounded-xl bg-cs-cardlight/60 border border-cs-border/60">
                      <span className="text-xs text-cs-muted block">Rainfall</span>
                      <span className="text-lg font-bold text-white">{weather.weather.precipitation || 0.0} mm</span>
                    </div>
                    <div className="p-3 rounded-xl bg-cs-cardlight/60 border border-cs-border/60">
                      <span className="text-xs text-cs-muted block">UV Index</span>
                      <span className="text-lg font-bold text-white">{weather.weather.uv_index || 0.0}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-cs-muted text-sm">
                  Weather telemetry unavailable.
                </div>
              )}
            </div>

            {weather && !weatherLoading && (
              <div className="mt-6 pt-4 border-t border-cs-border space-y-3.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-cs-muted font-semibold">LOCAL PATHOGEN RISK INDEX</span>
                  <span className={`font-bold px-2 py-0.5 rounded ${weather.risk_pct > 60 ? 'bg-red-500/10 text-red-400' : weather.risk_pct > 30 ? 'bg-amber-500/10 text-amber-400' : 'bg-cs-mint/10 text-cs-mint'}`}>
                    {weather.risk_pct.toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-cs-cardlight h-2 rounded-full overflow-hidden border border-cs-border">
                  <div 
                    className={`h-full rounded-full ${weather.risk_pct > 60 ? 'bg-red-500' : weather.risk_pct > 30 ? 'bg-amber-500' : 'bg-cs-mint'}`}
                    style={{ width: `${weather.risk_pct}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Diagnostics Upload File/Camera */}
          <div className="glass-panel p-6 rounded-2xl lg:col-span-2 space-y-4">
            <h3 className="font-bold text-white tracking-wide text-sm flex items-center gap-2">
              <Upload size={18} className="text-cs-mint" />
              <span>Specimen Upload & Leaf Validation</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Photo Input options */}
              <div className="space-y-4">
                {cameraActive ? (
                  <div className="relative aspect-video rounded-xl overflow-hidden border border-cs-border bg-black">
                    <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover"></video>
                    <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2 px-4">
                      <button 
                        onClick={capturePhoto}
                        className="py-2 px-4 rounded-lg bg-cs-mint text-cs-bg font-bold text-xs flex items-center gap-1.5 shadow"
                      >
                        <Camera size={14} />
                        <span>Capture Photo</span>
                      </button>
                      <button 
                        onClick={stopCamera}
                        className="py-2 px-4 rounded-lg bg-red-500 text-white font-bold text-xs flex items-center gap-1.5 shadow"
                      >
                        <Square size={14} />
                        <span>Cancel</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-cs-border hover:border-cs-mint/55 transition rounded-2xl p-6 flex flex-col items-center justify-center text-center group cursor-pointer aspect-video relative">
                    <input 
                      type="file" 
                      accept="image/*"
                      onChange={handleFileChange}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <Upload size={32} className="text-cs-muted group-hover:text-cs-mint transition mb-3" />
                    <p className="text-sm font-semibold text-white mb-1">Drag and drop file here</p>
                    <p className="text-xs text-cs-muted">or click to browse filesystem</p>
                  </div>
                )}

                <div className="flex gap-2">
                  <button 
                    onClick={triggerCamera}
                    disabled={cameraActive}
                    className="flex-1 py-3 px-4 rounded-xl bg-cs-cardlight hover:bg-cs-border border border-cs-border text-white text-xs font-bold transition flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <Camera size={16} className="text-cs-mint" />
                    <span>Open Device Camera</span>
                  </button>

                  <button 
                    onClick={runDiagnosis}
                    disabled={!selectedFile || diagLoading}
                    className="flex-1 py-3 px-4 rounded-xl bg-cs-mint hover:bg-cs-emerald text-cs-bg text-xs font-bold transition flex items-center justify-center gap-2 disabled:opacity-55"
                  >
                    {diagLoading ? (
                      <>
                        <RefreshCw size={16} className="animate-spin" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={16} />
                        <span>Analyze Leaf</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Photo Preview Pane */}
              <div className="rounded-2xl border border-cs-border bg-cs-cardlight/30 overflow-hidden flex flex-col items-center justify-center p-4 relative min-h-[160px] aspect-video">
                {previewUrl ? (
                  <img src={previewUrl} className="w-full h-full object-contain rounded-lg" alt="Specimen Preview" />
                ) : (
                  <div className="text-center space-y-1.5 p-4">
                    <p className="text-xs font-bold text-cs-mint tracking-widest uppercase">PREVIEW WORKSPACE</p>
                    <p className="text-xs text-cs-muted">No specimen image selected or captured yet.</p>
                  </div>
                )}
              </div>
            </div>

            {diagError && (
              <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 text-sm flex items-start gap-2.5">
                <AlertTriangle size={18} className="mt-0.5 shrink-0" />
                <div>
                  <h4 className="font-bold">Image Rejected</h4>
                  <p className="text-xs mt-0.5">{diagError}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Diagnosis Results Section */}
        {diagResult && (
          <div className="glass-panel p-6 md:p-8 rounded-2xl animate-fade-in space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-cs-border pb-4 gap-4">
              <div>
                <span className="text-xs text-cs-mint font-bold uppercase tracking-wider">AI PATHOLOGY TELEMETRY</span>
                <h2 className="text-2xl font-bold text-white mt-1">
                  {translations.plant_name || diagResult.diagnosis.plant_name} — {translations.disease_name || diagResult.diagnosis.disease_name}
                </h2>
                {diagResult.diagnosis.plant_scientific && (
                  <p className="text-xs text-cs-muted italic mt-0.5">Scientific Name: {translations.plant_scientific || diagResult.diagnosis.plant_scientific}</p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button 
                  onClick={playTts}
                  className={`py-2.5 px-4 rounded-xl text-xs font-bold transition flex items-center gap-1.5 border border-cs-border ${audioPlaying ? 'bg-amber-500 text-cs-bg border-amber-400' : 'bg-cs-cardlight text-white hover:bg-cs-border'}`}
                >
                  <Play size={14} />
                  <span>{audioPlaying ? 'Stop Readout' : 'Audio Readout'}</span>
                </button>
                <button 
                  onClick={downloadPdf}
                  className="py-2.5 px-4 rounded-xl bg-cs-cardlight border border-cs-border hover:bg-cs-border text-white text-xs font-bold transition flex items-center gap-1.5"
                >
                  <Download size={14} className="text-cs-mint" />
                  <span>Download PDF Booklet</span>
                </button>
              </div>
            </div>

            {/* Sub Diagnostics info */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-cs-cardlight/50 border border-cs-border">
                <span className="text-xs text-cs-muted block mb-0.5">Classification engine</span>
                <span className="text-sm font-bold text-white">CNN + Gemini Vision</span>
              </div>
              <div className="p-4 rounded-xl bg-cs-cardlight/50 border border-cs-border">
                <span className="text-xs text-cs-muted block mb-0.5">CNN Classifier Confidence</span>
                <span className="text-sm font-bold text-cs-mint">
                  {diagResult.cnn_confidence > 0 ? `${diagResult.cnn_confidence.toFixed(1)}%` : 'N/A (Zero-shot Gemini)'}
                </span>
              </div>
              <div className="p-4 rounded-xl bg-cs-cardlight/50 border border-cs-border">
                <span className="text-xs text-cs-muted block mb-0.5">Disease Severity</span>
                <span className={`text-sm font-bold ${diagResult.diagnosis.severity === 'Severe' ? 'text-red-400' : diagResult.diagnosis.severity === 'Moderate' ? 'text-amber-400' : 'text-cs-mint'}`}>
                  {diagResult.diagnosis.severity || 'Mild'}
                </span>
              </div>
              <div className="p-4 rounded-xl bg-cs-cardlight/50 border border-cs-border">
                <span className="text-xs text-cs-muted block mb-0.5">Image Quality Index</span>
                <span className="text-sm font-bold text-white">{diagResult.quality_score}% (Clear)</span>
              </div>
            </div>

            {/* Visual Heatmaps side by side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              <div className="rounded-xl border border-cs-border bg-cs-card overflow-hidden flex flex-col">
                <div className="py-2.5 px-4 bg-cs-cardlight border-b border-cs-border flex justify-between items-center">
                  <span className="text-xs font-bold text-white">Original Leaf Specimen</span>
                </div>
                <div className="p-4 flex items-center justify-center bg-black/20 aspect-video max-h-[300px]">
                  <img src={`data:image/jpeg;base64,${diagResult.original_image}`} className="max-h-full max-w-full object-contain rounded-lg" alt="Original Specimen" />
                </div>
              </div>

              {showGradCam && diagResult.heatmap && (
                <div className="rounded-xl border border-cs-border bg-cs-card overflow-hidden flex flex-col">
                  <div className="py-2.5 px-4 bg-cs-cardlight border-b border-cs-border flex justify-between items-center">
                    <span className="text-xs font-bold text-white">Grad-CAM Convolutional Heatmap</span>
                  </div>
                  <div className="p-4 flex items-center justify-center bg-black/20 aspect-video max-h-[300px]">
                    <img src={`data:image/jpeg;base64,${diagResult.heatmap}`} className="max-h-full max-w-full object-contain rounded-lg" alt="Gradcam Heatmap" />
                  </div>
                </div>
              )}
            </div>

            {/* Diagnostic Details: Tabs */}
            <div className="pt-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Symptoms & Pathogen Info */}
                <div className="glass-panel p-5 rounded-xl space-y-3.5 lg:col-span-2">
                  <div>
                    <h4 className="text-xs font-bold text-cs-mint tracking-wider uppercase">Causal Pathogen</h4>
                    <p className="text-sm text-white mt-1">{translations.disease_pathogen || diagResult.diagnosis.disease_pathogen || 'N/A'}</p>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-cs-mint tracking-wider uppercase">Symptoms Identified</h4>
                    <p className="text-sm text-white mt-1 leading-relaxed">{translations.symptoms || diagResult.diagnosis.symptoms || 'N/A'}</p>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-cs-mint tracking-wider uppercase">Organic & Cultural Treatment</h4>
                    <p className="text-sm text-white mt-1 leading-relaxed">{translations.organic_treatment || diagResult.diagnosis.organic_treatment || diagResult.diagnosis.treatment}</p>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-cs-mint tracking-wider uppercase">Chemical Spray Strategy</h4>
                    <p className="text-sm text-white mt-1 leading-relaxed">{translations.chemical_treatment || diagResult.diagnosis.chemical_treatment || 'N/A'}</p>
                  </div>
                </div>

                {/* Treatment Products */}
                <div className="glass-panel p-5 rounded-xl space-y-4">
                  <div className="border-b border-cs-border pb-2.5">
                    <h4 className="font-bold text-white text-sm">Recommended Supplies</h4>
                  </div>
                  {/* Medicine Product */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-cs-muted tracking-wider block">Recommended Medicine</span>
                    <div className="p-2.5 rounded-lg bg-cs-cardlight border border-cs-border">
                      <p className="text-sm font-bold text-cs-mint">{diagResult.diagnosis.medicine?.name || 'N/A'}</p>
                      <p className="text-xs text-cs-muted mt-0.5">Dose: {diagResult.diagnosis.medicine?.dose || 'N/A'}</p>
                    </div>
                  </div>
                  {/* Fertilizer Product */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] uppercase font-bold text-cs-muted tracking-wider block">Recommended Fertilizer</span>
                    <div className="p-2.5 rounded-lg bg-cs-cardlight border border-cs-border">
                      <p className="text-sm font-bold text-cs-mint">{diagResult.diagnosis.fertilizer?.name || 'N/A'}</p>
                      <p className="text-xs text-cs-muted mt-0.5">NPK Ratio: N:{diagResult.diagnosis.fertilizer?.npk_n} P:{diagResult.diagnosis.fertilizer?.npk_p} K:{diagResult.diagnosis.fertilizer?.npk_k}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Scan Registry & History Logs */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-cs-border pb-4">
            <div>
              <h3 className="font-bold text-white tracking-wide text-sm flex items-center gap-2">
                <TrendingUp size={18} className="text-cs-mint" />
                <span>Scan History Registry</span>
              </h3>
            </div>

            {/* Search */}
            <div className="w-full md:w-72">
              <input 
                type="text" 
                placeholder="Search history registry..."
                className="w-full py-2 px-3.5 rounded-xl bg-cs-cardlight border border-cs-border text-white text-xs focus:outline-none focus:border-cs-mint placeholder-emerald-900/60"
                value={historySearch}
                onChange={(e) => setHistorySearch(e.target.value)}
              />
            </div>
          </div>

          <div className="overflow-x-auto w-full">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-cs-border text-cs-muted font-semibold bg-cs-cardlight/30">
                  <th className="p-3">Date / Time</th>
                  <th className="p-3">Plant Type</th>
                  <th className="p-3">Diagnosis</th>
                  <th className="p-3">CNN Conf.</th>
                  <th className="p-3">Severity</th>
                  <th className="p-3">Climate Condition</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cs-border/60">
                {filteredHistory.length > 0 ? (
                  filteredHistory.map((item, idx) => (
                    <tr key={idx} className="hover:bg-cs-cardlight/20 transition">
                      <td className="p-3 font-mono text-[11px] text-white">
                        <div>{item.Date}</div>
                        <div className="text-cs-muted text-[10px] mt-0.5">{item.Time}</div>
                      </td>
                      <td className="p-3 font-semibold text-white">{item.Plant}</td>
                      <td className="p-3 text-cs-muted">{item.Disease}</td>
                      <td className="p-3 text-cs-mint font-bold">{item.CNN_Confidence}%</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${item.Severity === 'Severe' ? 'bg-red-500/15 text-red-400' : item.Severity === 'Moderate' ? 'bg-amber-500/15 text-amber-400' : 'bg-cs-mint/15 text-cs-mint'}`}>
                          {item.Severity}
                        </span>
                      </td>
                      <td className="p-3 text-cs-muted">
                        {item.Temperature}°C | {item.Humidity}% Hum
                      </td>
                      <td className="p-3 text-right">
                        {deletingIndex === idx ? (
                          <div className="inline-flex gap-2">
                            <button 
                              onClick={() => handleDeleteHistory(item)}
                              className="text-red-400 hover:text-red-500 font-bold px-2 py-1 bg-red-500/10 rounded border border-red-500/20"
                            >
                              Confirm
                            </button>
                            <button 
                              onClick={() => setDeletingIndex(null)}
                              className="text-cs-muted hover:text-white font-bold px-2 py-1"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <button 
                            onClick={() => setDeletingIndex(idx)}
                            className="p-2 text-cs-muted hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="p-8 text-center text-cs-muted">
                      No matching diagnostic scans found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Floating AI Chatbot Widget */}
      {showChatbot && (
        <div className="fixed bottom-6 right-6 w-96 max-h-[500px] h-[450px] glass-panel rounded-2xl flex flex-col overflow-hidden z-40 animate-fade-in shadow-2xl">
          <div className="py-3.5 px-4 bg-cs-cardlight border-b border-cs-border flex justify-between items-center">
            <div className="flex items-center gap-2">
              <MessageSquare size={16} className="text-cs-mint" />
              <span className="text-xs font-bold text-white tracking-wide">Agronomist Assistant</span>
            </div>
            {chatLoading && (
              <RefreshCw size={12} className="animate-spin text-cs-mint" />
            )}
          </div>

          {/* Chat Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3.5 text-xs">
            {chatHistory.map((h, i) => (
              <div key={i} className={`flex ${h.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl ${h.role === 'user' ? 'bg-cs-mint text-cs-bg font-medium rounded-tr-none' : 'bg-cs-cardlight/80 border border-cs-border text-white rounded-tl-none'} leading-relaxed`}>
                  {h.text}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-cs-cardlight/50 border border-cs-border/60 p-3 rounded-2xl rounded-tl-none text-cs-muted animate-pulse">
                  Assistant is typing...
                </div>
              </div>
            )}
          </div>

          {/* Quick chips suggestions */}
          {diagResult && (
            <div className="px-4 py-2 border-t border-cs-border/50 flex gap-1.5 overflow-x-auto shrink-0 bg-cs-card/30">
              <button 
                onClick={() => triggerChat(`How to prevent ${diagResult.diagnosis.disease_name} next season?`)}
                className="text-[10px] py-1 px-2.5 rounded-full bg-cs-cardlight border border-cs-border text-cs-muted hover:text-white shrink-0"
              >
                Prevention Tips
              </button>
              <button 
                onClick={() => triggerChat("What organic alternatives exist?")}
                className="text-[10px] py-1 px-2.5 rounded-full bg-cs-cardlight border border-cs-border text-cs-muted hover:text-white shrink-0"
              >
                Organic Options
              </button>
              <button 
                onClick={() => triggerChat("Is this safe to eat?")}
                className="text-[10px] py-1 px-2.5 rounded-full bg-cs-cardlight border border-cs-border text-cs-muted hover:text-white shrink-0"
              >
                Safety Notes
              </button>
            </div>
          )}

          {/* Chat Inputs */}
          <div className="p-3 bg-cs-card border-t border-cs-border flex gap-2 shrink-0">
            <button 
              onClick={handleStt}
              className={`p-2.5 rounded-xl border border-cs-border transition ${listening ? 'bg-red-500/20 border-red-500/40 text-red-400 animate-pulse' : 'bg-cs-cardlight text-cs-muted hover:text-white'}`}
            >
              <Mic size={16} />
            </button>
            <input 
              type="text" 
              placeholder="Ask about crop health..."
              className="flex-1 py-2.5 px-3.5 rounded-xl bg-cs-cardlight border border-cs-border text-white text-xs focus:outline-none focus:border-cs-mint placeholder-emerald-900/60"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') triggerChat(); }}
            />
            <button 
              onClick={() => triggerChat()}
              className="p-2.5 rounded-xl bg-cs-mint hover:bg-cs-emerald text-cs-bg transition"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

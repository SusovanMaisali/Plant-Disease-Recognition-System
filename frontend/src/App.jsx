import React, { useState, useEffect, useRef } from 'react';
import { 
  Leaf, User, Mail, Phone, Lock, LogOut, Upload, Camera, 
  MapPin, CloudSun, AlertTriangle, MessageSquare, Play, Square,
  Download, Trash2, Globe, Settings, ShieldCheck, ChevronRight,
  TrendingUp, Sparkles, Send, Mic, Sun, Moon, FileText, CheckCircle,
  BarChart2, HelpCircle, Thermometer, Droplets, CloudRain, Wind, 
  Compass, Gauge, Eye, Sunrise, Sunset, Activity, RefreshCw
} from 'lucide-react';

const SUPPORTED_LANGUAGES = [
  { code: 'en', flag: '🇬🇧', name: 'English' },
  { code: 'hi', flag: '🇮🇳', name: 'Hindi (हिन्दी)' },
  { code: 'bn', flag: '🇮🇳', name: 'Bengali (বাংলা)' },
  { code: 'es', flag: '🇪🇸', name: 'Spanish (Español)' },
  { code: 'fr', flag: '🇫🇷', name: 'French (Français)' },
  { code: 'de', flag: '🇩🇪', name: 'German (Deutsch)' },
  { code: 'it', flag: '🇮🇹', name: 'Italian (Italiano)' },
  { code: 'pt', flag: '🇵🇹', name: 'Portuguese (Português)' },
  { code: 'ru', flag: '🇷🇺', name: 'Russian (Русский)' },
  { code: 'zh-CN', flag: '🇨🇳', name: 'Chinese (简体中文)' },
  { code: 'ja', flag: '🇯🇵', name: 'Japanese (日本語)' },
  { code: 'ko', flag: '🇰🇷', name: 'Korean (한국어)' },
  { code: 'ar', flag: '🇸🇦', name: 'Arabic (العربية)' },
  { code: 'tr', flag: '🇹🇷', name: 'Turkish (Türkçe)' },
  { code: 'nl', flag: '🇳🇱', name: 'Dutch (Nederlands)' },
  { code: 'sv', flag: '🇸🇪', name: 'Swedish (Svenska)' },
  { code: 'no', flag: '🇳🇴', name: 'Norwegian (Norsk)' },
  { code: 'da', flag: '🇩🇰', name: 'Danish (Dansk)' },
  { code: 'pl', flag: '🇵🇱', name: 'Polish (Polski)' },
  { code: 'uk', flag: '🇺🇦', name: 'Ukrainian (Українська)' },
  { code: 'el', flag: '🇬🇷', name: 'Greek (Ελληνικά)' },
  { code: 'th', flag: '🇹🇭', name: 'Thai (ไทย)' },
  { code: 'vi', flag: '🇻🇳', name: 'Vietnamese (Tiếng Việt)' },
  { code: 'id', flag: '🇮🇩', name: 'Indonesian (Bahasa Indonesia)' },
  { code: 'ms', flag: '🇲🇾', name: 'Malay (Bahasa Melayu)' },
  { code: 'tl', flag: '🇵🇭', name: 'Filipino (Tagalog)' },
  { code: 'fa', flag: '🇮🇷', name: 'Persian (فارسی)' },
  { code: 'ur', flag: '🇵🇰', name: 'Urdu (اردو)' },
  { code: 'ta', flag: '🇮🇳', name: 'Tamil (தமிழ்)' },
  { code: 'te', flag: '🇮🇳', name: 'Telugu (తెలుగు)' },
  { code: 'kn', flag: '🇮🇳', name: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ml', flag: '🇮🇳', name: 'Malayalam (മലയാളം)' },
  { code: 'gu', flag: '🇮🇳', name: 'Gujarati (ગુજરાતી)' },
  { code: 'mr', flag: '🇮🇳', name: 'Marathi (मਰਾठी)' },
  { code: 'pa', flag: '🇮🇳', name: 'Punjabi (ਪੰਜਾਬੀ)' },
  { code: 'ro', flag: '🇷🇴', name: 'Romanian (Română)' },
  { code: 'hu', flag: '🇭🇺', name: 'Hungarian (Magyar)' },
  { code: 'cs', flag: '🇨🇿', name: 'Czech (Čeština)' },
  { code: 'ne', flag: '🇳🇵', name: 'Nepali (नेपाली)' },
  { code: 'si', flag: '🇱🇰', name: 'Sinhala (සිංහල)' },
  { code: 'sw', flag: '🇰🇪', name: 'Swahili (Kiswahili)' }
];

// Helper functions for safe UI numbers formatting
const formatNum = (val, dec = 0) => {
  const num = Number(val);
  return isNaN(num) ? '0' : num.toFixed(dec);
};

const formatCoord = (val, dec = 2) => {
  if (val === '' || val === null || val === undefined) return '0.00';
  const num = Number(val);
  return isNaN(num) ? '0.00' : num.toFixed(dec);
};

const getApiBase = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '');
  }
  const saved = localStorage.getItem('CUSTOM_API_BASE');
  if (saved) {
    return saved.replace(/\/$/, '');
  }
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return '';
  }
  return window.location.origin;
};

const API_BASE = getApiBase();

export default function App() {
  // Theme & Auth state
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState('diagnostics'); 
  const [isLogin, setIsLogin] = useState(true);
  const [authForm, setAuthForm] = useState({ name: '', mobile: '', email: '', captcha: '', otp: '' });
  const [captcha, setCaptcha] = useState({ num1: 0, num2: 0, sum: 0 });
  const [otpSent, setOtpSent] = useState(false);
  const [simulatedOtp, setSimulatedOtp] = useState('');
  const [authError, setAuthError] = useState('');
  const [connError, setConnError] = useState(false);
  const [showBaseInput, setShowBaseInput] = useState(false);
  const [customBase, setCustomBase] = useState(localStorage.getItem('CUSTOM_API_BASE') || '');

  const handleSaveCustomBase = (e) => {
    e.preventDefault();
    const cleanUrl = customBase.trim().replace(/\/$/, '');
    if (cleanUrl) {
      localStorage.setItem('CUSTOM_API_BASE', cleanUrl);
    } else {
      localStorage.removeItem('CUSTOM_API_BASE');
    }
    window.location.reload();
  };
  
  // Dashboard Settings
  const [lang, setLang] = useState('en');
  const [minConfidence, setMinConfidence] = useState(50);
  const [showGradCam, setShowGradCam] = useState(true);
  const [showTop3, setShowTop3] = useState(true);
  const [useGemini, setUseGemini] = useState(true);
  const [showChatbot, setShowChatbot] = useState(true);

  // Climate / Location telemetry
  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(true);
  const [locationQuery, setLocationQuery] = useState('');
  const [locationSuggestions, setLocationSuggestions] = useState([]);

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
  const [filterPlant, setFilterPlant] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [deletingIndex, setDeletingIndex] = useState(null);

  // Email Report Dialog
  const [emailReportOpen, setEmailReportOpen] = useState(false);
  const [emailInput, setEmailInput] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailMessage, setEmailMessage] = useState('');

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

  // Apply Theme class
  useEffect(() => {
    localStorage.setItem('theme', darkMode ? 'dark' : 'light');
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Load CAPTCHA
  const fetchCaptcha = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/auth/captcha`);
      if (!res.ok) throw new Error("Status " + res.status);
      const data = await res.json();
      setCaptcha(data);
      setConnError(false);
    } catch (e) {
      console.error(e);
      setConnError(true);
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
      const res = await fetch(`${API_BASE}${url}`);
      const data = await res.json();
      setWeather(data);
      if (data.location) {
        setLocationQuery(`${data.location.city || ''}, ${data.location.country || ''}`.trim());
      }
    } catch (e) {
      console.error("Failed to load weather: ", e);
    } finally {
      setWeatherLoading(false);
    }
  };

  const handleLocationSearch = async (val) => {
    setLocationQuery(val);
    if (val.length < 3) {
      setLocationSuggestions([]);
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/api/weather/suggest?query=${encodeURIComponent(val)}`);
      const data = await res.json();
      setLocationSuggestions(data.suggestions || []);
    } catch (e) {
      console.error(e);
    }
  };

  const selectSuggestion = (s) => {
    setLocationSuggestions([]);
    setLocationQuery(s.name);
    fetchWeather({
      latitude: s.latitude,
      longitude: s.longitude
    });
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
      const res = await fetch(`${API_BASE}/api/history?mobile=${user.mobile}`);
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
      const res = await fetch(`${API_BASE}/api/auth/send-otp`, {
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
      setSimulatedOtp(data.otp);
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/api/auth/verify-otp`, {
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
      const res = await fetch(`${API_BASE}/api/auth/signup`, {
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
    setActiveTab('diagnostics');
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
      const res = await fetch(`${API_BASE}/api/diagnose`, {
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
      const res = await fetch(`${API_BASE}/api/chat`, {
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
      const res = await fetch(`${API_BASE}/api/generate-tts`, {
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
      const res = await fetch(`${API_BASE}/api/generate-pdf`, {
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

  // Email report to farmer
  const emailReport = async () => {
    if (!emailInput.trim()) return;
    setEmailLoading(true);
    setEmailMessage('');
    try {
      const res = await fetch(`${API_BASE}/api/history/email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mobile: user.mobile,
          email: emailInput.trim(),
          name: user.name
        })
      });
      const data = await res.json();
      setEmailMessage(data.message);
    } catch (e) {
      setEmailMessage("Error compiling or dispatching report.");
    } finally {
      setEmailLoading(false);
    }
  };

  // Export File handlers
  const exportCsv = () => {
    if (history.length === 0) return;
    const headers = Object.keys(history[0]).join(",");
    const rows = history.map(row => 
      Object.values(row).map(val => `"${String(val).replace(/"/g, '""')}"`).join(",")
    );
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `cropsense_history_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportJson = () => {
    if (history.length === 0) return;
    const jsonStr = JSON.stringify(history, null, 2);
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(jsonStr);
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", `cropsense_history_${new Date().toISOString().slice(0,10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Delete history item
  const handleDeleteHistory = async (item) => {
    try {
      const res = await fetch(`${API_BASE}/api/history/delete`, {
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
        const res = await fetch(`${API_BASE}/api/translate`, {
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

  // Filter lists
  const uniquePlants = ['all', ...new Set(history.map(item => item.Plant))];
  const uniqueSeverities = ['all', ...new Set(history.map(item => item.Severity))];

  const filteredHistory = history.filter(item => {
    const q = historySearch.toLowerCase();
    const matchesSearch = item.Plant.toLowerCase().includes(q) ||
                          item.Disease.toLowerCase().includes(q) ||
                          item.City.toLowerCase().includes(q);
    const matchesPlant = filterPlant === 'all' || item.Plant === filterPlant;
    const matchesSeverity = filterSeverity === 'all' || item.Severity === filterSeverity;
    return matchesSearch && matchesPlant && matchesSeverity;
  });

  // Analytics Computation
  const getAnalyticsData = () => {
    if (history.length === 0) return null;

    const trend = {};
    history.forEach(item => {
      trend[item.Date] = (trend[item.Date] || 0) + 1;
    });
    const trendData = Object.entries(trend).map(([date, count]) => ({ date, count }));
    
    const crops = {};
    history.forEach(item => {
      crops[item.Plant] = (crops[item.Plant] || 0) + 1;
    });
    const cropData = Object.entries(crops).map(([name, count]) => ({ name, count }));

    const diseases = {};
    history.forEach(item => {
      diseases[item.Disease] = (diseases[item.Disease] || 0) + 1;
    });
    const diseaseData = Object.entries(diseases)
      .map(([name, count]) => ({ name, count }))
      .sort((a,b) => b.count - a.count)
      .slice(0, 5);

    const severityMap = { Excellent: 0, Mild: 0, Moderate: 0, Severe: 0 };
    history.forEach(item => {
      if (item.Severity in severityMap) {
        severityMap[item.Severity]++;
      }
    });

    return { trendData, cropData, diseaseData, severityMap };
  };

  const stats = getAnalyticsData();

  // Welcome Screen (Sign In / Register)
  if (!user) {
    return (
      <div className={`min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden transition-colors duration-300 ${darkMode ? 'bg-cs-bg text-cs-text' : 'bg-slate-50 text-slate-800'}`}>
        <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-emerald-950/20 blur-[150px]"></div>
        <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-emerald-950/20 blur-[150px]"></div>

        <div className={`w-full max-w-md p-8 rounded-3xl animate-fade-in relative z-10 transition-colors duration-300 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-xl'}`}>
          
          <div className="flex justify-between items-center mb-6">
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2.5 rounded-xl border transition ${darkMode ? 'border-cs-border hover:bg-cs-cardlight text-cs-mint' : 'border-slate-200 hover:bg-slate-100 text-emerald-600'}`}
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <div className="text-right text-[10px] uppercase font-bold tracking-widest text-cs-muted">
              SaaS Portal Active
            </div>
          </div>

          <div className="text-center mb-8">
            <div className={`inline-flex items-center justify-center p-3 rounded-2xl mb-4 ${darkMode ? 'bg-cs-mint/10 border border-cs-mint/35 text-cs-mint' : 'bg-emerald-50 border border-emerald-200 text-emerald-600'}`}>
              <Leaf size={32} />
            </div>
            <h1 className={`text-3xl font-extrabold tracking-tight mb-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>CropSense AI</h1>
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

          {connError && (
            <div className="mb-6 p-4 rounded-xl border border-amber-500/20 bg-amber-500/10 text-amber-400 text-xs space-y-2 animate-fade-in">
              <div className="flex items-start gap-2">
                <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                <span>Could not connect to the API backend server.</span>
              </div>
              {!showBaseInput ? (
                <button 
                  type="button"
                  onClick={() => setShowBaseInput(true)}
                  className="font-bold underline hover:text-white"
                >
                  Configure Backend URL manually
                </button>
              ) : (
                <form onSubmit={handleSaveCustomBase} className="space-y-2 pt-1.5">
                  <input 
                    type="text" 
                    placeholder="e.g. https://cropsense-ai-backend.onrender.com"
                    className="w-full px-3 py-1.5 rounded-lg border text-xs focus:outline-none bg-cs-cardlight border-cs-border text-white"
                    value={customBase}
                    onChange={(e) => setCustomBase(e.target.value)}
                  />
                  <div className="flex gap-2">
                    <button 
                      type="submit" 
                      className="px-3 py-1 rounded bg-cs-mint text-cs-bg font-bold text-[10px]"
                    >
                      Save & Reconnect
                    </button>
                    <button 
                      type="button" 
                      onClick={() => setShowBaseInput(false)}
                      className="px-3 py-1 rounded border border-cs-border text-cs-muted text-[10px]"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {isLogin ? (
            /* LOGIN */
            <form onSubmit={otpSent ? handleVerifyOtp : handleRequestOtp} className="space-y-5">
              <div className={`text-sm font-semibold border-b pb-2.5 mb-2 flex items-center gap-2 ${darkMode ? 'text-white border-cs-border' : 'text-slate-800 border-slate-100'}`}>
                <Lock size={16} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                <span>Farmer Sign In</span>
              </div>

              {!otpSent ? (
                <>
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-cs-muted">Mobile Number</label>
                    <div className="relative">
                      <Phone size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cs-muted" />
                      <input 
                        type="text" 
                        placeholder="e.g. 9876543210"
                        className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                        value={authForm.mobile}
                        onChange={(e) => setAuthForm({ ...authForm, mobile: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-cs-muted">CAPTCHA Challenge</label>
                      <div className={`flex items-center justify-center py-2.5 rounded-xl border select-none font-mono text-sm tracking-wider ${darkMode ? 'bg-cs-cardlight/60 border-cs-border text-white' : 'bg-slate-50 border-slate-200 text-slate-800'}`}>
                        {captcha.num1} + {captcha.num2} = ?
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold text-cs-muted">Your Answer</label>
                      <input 
                        type="number" 
                        placeholder="Sum"
                        className={`w-full px-4 py-2.5 rounded-xl border focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                        value={authForm.captcha}
                        onChange={(e) => setAuthForm({ ...authForm, captcha: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <button 
                    type="submit"
                    className={`w-full py-3.5 rounded-xl font-bold tracking-wide transition flex items-center justify-center gap-2 mt-2 ${darkMode ? 'bg-cs-mint hover:bg-cs-emerald text-cs-bg' : 'bg-emerald-600 hover:bg-emerald-700 text-white'}`}
                  >
                    <span>Send Verification Code</span>
                    <ChevronRight size={18} />
                  </button>
                </>
              ) : (
                <>
                  <div className={`p-3.5 rounded-xl border text-xs leading-relaxed mb-4 ${darkMode ? 'bg-emerald-950/20 border-emerald-900/40 text-cs-muted' : 'bg-emerald-50 border-emerald-100 text-slate-700'}`}>
                    💬 Simulated SMS: A verification code has been dispatched. Enter <strong>{simulatedOtp}</strong> to authenticate.
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-cs-muted">Verification Code (OTP)</label>
                    <input 
                      type="text" 
                      placeholder="4-digit code"
                      maxLength={4}
                      className={`w-full px-4 py-3 rounded-xl border focus:outline-none transition text-center font-mono text-xl tracking-widest ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                      value={authForm.otp}
                      onChange={(e) => setAuthForm({ ...authForm, otp: e.target.value })}
                      required
                    />
                  </div>

                  <div className="flex gap-2">
                    <button 
                      type="button"
                      onClick={() => setOtpSent(false)}
                      className={`w-1/3 py-3.5 rounded-xl border font-bold transition ${darkMode ? 'border-cs-border hover:bg-cs-cardlight text-cs-muted' : 'border-slate-200 hover:bg-slate-100 text-slate-600'}`}
                    >
                      Back
                    </button>
                    <button 
                      type="submit"
                      className={`w-2/3 py-3.5 rounded-xl font-bold tracking-wide transition ${darkMode ? 'bg-cs-mint hover:bg-cs-emerald text-cs-bg' : 'bg-emerald-600 hover:bg-emerald-700 text-white'}`}
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
                  className={`font-semibold hover:underline ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}
                >
                  Create one now
                </button>
              </div>
            </form>
          ) : (
            /* SIGN UP */
            <form onSubmit={handleSignup} className="space-y-4">
              <div className={`text-sm font-semibold border-b pb-2.5 mb-2 flex items-center gap-2 ${darkMode ? 'text-white border-cs-border' : 'text-slate-800 border-slate-100'}`}>
                <User size={16} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                <span>Register New Farmer Account</span>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-cs-muted">Full Name</label>
                <div className="relative">
                  <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-cs-muted" />
                  <input 
                    type="text" 
                    placeholder="e.g. John Doe"
                    className={`w-full pl-10 pr-4 py-2.5 rounded-xl border focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
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
                    className={`w-full pl-10 pr-4 py-2.5 rounded-xl border focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
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
                    className={`w-full pl-10 pr-4 py-2.5 rounded-xl border focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                    value={authForm.email}
                    onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-cs-muted">CAPTCHA</label>
                  <div className={`flex items-center justify-center py-2.5 rounded-xl border font-mono text-sm ${darkMode ? 'bg-cs-cardlight/60 border-cs-border text-white' : 'bg-slate-50 border-slate-200 text-slate-800'}`}>
                    {captcha.num1} + {captcha.num2} = ?
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-cs-muted">Answer</label>
                  <input 
                    type="number" 
                    placeholder="Result"
                    className={`w-full px-4 py-2.5 rounded-xl border focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                    value={authForm.captcha}
                    onChange={(e) => setAuthForm({ ...authForm, captcha: e.target.value })}
                    required
                  />
                </div>
              </div>

              <button 
                type="submit"
                className={`w-full py-3.5 rounded-xl font-bold tracking-wide transition mt-2 ${darkMode ? 'bg-cs-mint hover:bg-cs-emerald text-cs-bg' : 'bg-emerald-600 hover:bg-emerald-700 text-white'}`}
              >
                Register & Sign In
              </button>

              <div className="text-center pt-3 border-t border-cs-border text-xs text-cs-muted">
                Already registered?{' '}
                <button 
                  type="button" 
                  onClick={() => { setIsLogin(true); setAuthError(''); }}
                  className={`font-semibold hover:underline ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}
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
    <div className={`min-h-screen flex flex-col md:flex-row relative transition-colors duration-300 ${darkMode ? 'bg-cs-bg text-cs-text' : 'bg-slate-50 text-slate-800'}`}>
      
      {/* Sidebar Navigation Panel */}
      <aside className={`w-full md:w-80 shrink-0 border-b md:border-b-0 md:border-r p-6 flex flex-col justify-between transition-colors duration-300 ${darkMode ? 'bg-cs-card border-cs-border' : 'bg-white border-slate-200 shadow-md'}`}>
        <div className="space-y-8">
          {/* Brand Header */}
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl border transition ${darkMode ? 'bg-cs-mint/15 border-cs-mint/45 text-cs-mint' : 'bg-emerald-50 border-emerald-300 text-emerald-600'}`}>
              <Leaf size={24} />
            </div>
            <div>
              <h2 className={`text-lg font-bold tracking-wide ${darkMode ? 'text-white' : 'text-slate-900'}`}>CropSense AI</h2>
              <p className={`text-xs font-semibold ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>v3.0 Pro + Gemini</p>
            </div>
          </div>

          <div className={`h-px ${darkMode ? 'bg-cs-border' : 'bg-slate-100'}`}></div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            <button 
              onClick={() => setActiveTab('diagnostics')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                activeTab === 'diagnostics' 
                  ? (darkMode ? 'bg-cs-mint/15 text-cs-mint' : 'bg-emerald-50 text-emerald-700') 
                  : (darkMode ? 'text-cs-muted hover:bg-cs-cardlight hover:text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950')
              }`}
            >
              <Sparkles size={18} />
              <span>🌿 Diagnostics Workspace</span>
            </button>

            <button 
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                activeTab === 'analytics' 
                  ? (darkMode ? 'bg-cs-mint/15 text-cs-mint' : 'bg-emerald-50 text-emerald-700') 
                  : (darkMode ? 'text-cs-muted hover:bg-cs-cardlight hover:text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950')
              }`}
            >
              <BarChart2 size={18} />
              <span>📊 Analytics Dashboard</span>
            </button>

            <button 
              onClick={() => setActiveTab('climate')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                activeTab === 'climate' 
                  ? (darkMode ? 'bg-cs-mint/15 text-cs-mint' : 'bg-emerald-50 text-emerald-700') 
                  : (darkMode ? 'text-cs-muted hover:bg-cs-cardlight hover:text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950')
              }`}
            >
              <CloudSun size={18} />
              <span>🌦️ Weather & Risks</span>
            </button>

            <button 
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                activeTab === 'history' 
                  ? (darkMode ? 'bg-cs-mint/15 text-cs-mint' : 'bg-emerald-50 text-emerald-700') 
                  : (darkMode ? 'text-cs-muted hover:bg-cs-cardlight hover:text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950')
              }`}
            >
              <FileText size={18} />
              <span>📝 Scan History Log</span>
            </button>

            <button 
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                activeTab === 'settings' 
                  ? (darkMode ? 'bg-cs-mint/15 text-cs-mint' : 'bg-emerald-50 text-emerald-700') 
                  : (darkMode ? 'text-cs-muted hover:bg-cs-cardlight hover:text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950')
              }`}
            >
              <Settings size={18} />
              <span>⚙️ System Settings</span>
            </button>

            <button 
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                activeTab === 'profile' 
                  ? (darkMode ? 'bg-cs-mint/15 text-cs-mint' : 'bg-emerald-50 text-emerald-700') 
                  : (darkMode ? 'text-cs-muted hover:bg-cs-cardlight hover:text-white' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950')
              }`}
            >
              <User size={18} />
              <span>👤 Farmer Profile</span>
            </button>
          </nav>
        </div>

        {/* User Card */}
        <div className={`mt-8 pt-4 border-t space-y-4 ${darkMode ? 'border-cs-border' : 'border-slate-100'}`}>
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full border flex items-center justify-center font-bold ${darkMode ? 'bg-cs-cardlight border-cs-border text-cs-mint' : 'bg-emerald-50 border-emerald-200 text-emerald-600'}`}>
              {user.name.slice(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className={`text-sm font-semibold truncate ${darkMode ? 'text-white' : 'text-slate-900'}`}>{user.name}</p>
              <p className="text-xs text-cs-muted truncate">{user.mobile}</p>
            </div>
          </div>

          <button 
            onClick={handleSignOut}
            className={`w-full py-2.5 rounded-xl border text-xs font-semibold transition flex items-center justify-center gap-2 ${darkMode ? 'border-cs-border hover:bg-red-500/10 hover:border-red-500/30 text-cs-muted hover:text-red-400' : 'border-slate-200 hover:bg-red-500/5 hover:border-red-500/20 text-slate-600 hover:text-red-600'}`}
          >
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-10 space-y-8 overflow-y-auto max-h-screen">
        
        {/* Universal Top Header */}
        <div className={`flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b pb-6 ${darkMode ? 'border-cs-border' : 'border-slate-200'}`}>
          <div>
            <h1 className={`text-2xl md:text-3xl font-extrabold tracking-tight ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              {activeTab === 'diagnostics' && '🌿 Leaf Diagnostics Workspace'}
              {activeTab === 'analytics' && '📊 Performance Analytics Dashboard'}
              {activeTab === 'climate' && '🌦️ Weather & Micro-Climate Telemetry'}
              {activeTab === 'history' && '📝 History Scan Registry'}
              {activeTab === 'settings' && '⚙️ Advanced Configuration Panel'}
              {activeTab === 'profile' && '👤 Farmer Profile & Platform Tech'}
            </h1>
            <p className="text-xs md:text-sm text-cs-muted">
              {activeTab === 'diagnostics' && 'Upload crop specimen, review attention overlays, and stream chemical spray timings'}
              {activeTab === 'analytics' && 'Monitor category allocations, diagnostics trend metrics, and severity distributions'}
              {activeTab === 'climate' && 'IP geolocated climate readings, Open-Meteo variables, and local agricultural risks'}
              {activeTab === 'history' && 'Search records, download PDF reports, and export/email CSV databases'}
              {activeTab === 'settings' && 'Customize confidence thresholds, Grad-CAM toggle options, and select Dark/Light modes'}
              {activeTab === 'profile' && 'Review details of logged-in agronomist accounts and system frameworks'}
            </p>
          </div>

          {/* Quick Header Actions */}
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2.5 rounded-xl border transition ${darkMode ? 'border-cs-border bg-cs-cardlight text-cs-mint hover:bg-cs-border' : 'border-slate-200 bg-white text-emerald-600 hover:bg-slate-50'}`}
            >
              {darkMode ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <div className={`px-4 py-2.5 rounded-xl border text-xs font-bold flex items-center gap-1.5 ${darkMode ? 'bg-cs-card border-cs-border text-white' : 'bg-white border-slate-200 text-slate-800'}`}>
              <ShieldCheck size={16} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
              <span>SaaS Connected</span>
            </div>
          </div>
        </div>

        {/* ── TAB 1: DIAGNOSTICS WORKSPACE ── */}
        {activeTab === 'diagnostics' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Geolocation/Weather Summary */}
              <div className={`p-6 rounded-2xl flex flex-col justify-between ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className={`font-bold text-sm flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      <CloudSun size={18} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                      <span>Climate Readings</span>
                    </h3>
                  </div>

                  {weatherLoading ? (
                    <div className="py-12 flex flex-col items-center justify-center gap-3 text-cs-muted text-sm">
                      <RefreshCw size={24} className="animate-spin text-cs-mint" />
                      <span>Syncing climate coordinates...</span>
                    </div>
                  ) : weather ? (
                    <div className="space-y-4">
                      <div>
                        <span className="text-[10px] text-cs-muted block uppercase tracking-wider font-bold">Detected Location</span>
                        <span className={`text-base font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>{weather.location.city}, {weather.location.country}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-3.5">
                        <div className={`p-3 rounded-xl border ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                          <span className="text-[10px] text-cs-muted block">Temperature</span>
                          <span className={`text-base font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.temperature}°C</span>
                        </div>
                        <div className={`p-3 rounded-xl border ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                          <span className="text-[10px] text-cs-muted block">Humidity</span>
                          <span className={`text-base font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.humidity}%</span>
                        </div>
                      </div>
                      <div className="flex justify-between items-center text-xs border-t pt-3 border-cs-border/40">
                        <span className="text-cs-muted font-semibold">Local Pathogen Threat</span>
                        <span className={`font-bold px-2 py-0.5 rounded ${weather.risk_pct > 65 ? 'bg-red-500/10 text-red-400' : 'bg-cs-mint/10 text-cs-mint'}`}>
                          {formatNum(weather.risk_pct, 0)}%
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-cs-muted">Weather telemetry offline.</p>
                  )}
                </div>
              </div>

              {/* Leaf Specimen capture/upload */}
              <div className={`p-6 rounded-2xl lg:col-span-2 space-y-4 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                <h3 className={`font-bold text-sm flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  <Upload size={18} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                  <span>Specimen Upload & Validation</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-4">
                    {cameraActive ? (
                      <div className="relative aspect-video rounded-xl overflow-hidden border border-cs-border bg-black">
                        <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover"></video>
                        <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2 px-4">
                          <button 
                            onClick={capturePhoto}
                            className="py-2 px-4 rounded-lg bg-cs-mint text-cs-bg font-bold text-xs flex items-center gap-1.5"
                          >
                            <Camera size={14} />
                            <span>Capture</span>
                          </button>
                          <button 
                            onClick={stopCamera}
                            className="py-2 px-4 rounded-lg bg-red-500 text-white font-bold text-xs"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className={`border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center text-center group cursor-pointer aspect-video relative transition-colors ${darkMode ? 'border-cs-border hover:border-cs-mint/55' : 'border-slate-200 hover:border-emerald-600/50'}`}>
                        <input 
                          type="file" 
                          accept="image/*"
                          onChange={handleFileChange}
                          className="absolute inset-0 opacity-0 cursor-pointer"
                        />
                        <Upload size={32} className="text-cs-muted group-hover:text-cs-mint transition mb-3" />
                        <p className={`text-sm font-semibold mb-1 ${darkMode ? 'text-white' : 'text-slate-800'}`}>Drag and drop leaf here</p>
                        <p className="text-xs text-cs-muted">or browse files</p>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <button 
                        onClick={triggerCamera}
                        disabled={cameraActive}
                        className={`flex-1 py-3 px-4 rounded-xl border text-xs font-bold transition flex items-center justify-center gap-2 disabled:opacity-50 ${darkMode ? 'bg-cs-cardlight border-cs-border text-white hover:bg-cs-border' : 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100'}`}
                      >
                        <Camera size={16} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                        <span>Use Camera</span>
                      </button>

                      <button 
                        onClick={runDiagnosis}
                        disabled={!selectedFile || diagLoading}
                        className={`flex-1 py-3 px-4 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 disabled:opacity-50 ${darkMode ? 'bg-cs-mint hover:bg-cs-emerald text-cs-bg' : 'bg-emerald-600 hover:bg-emerald-700 text-white'}`}
                      >
                        {diagLoading ? (
                          <>
                            <RefreshCw size={16} className="animate-spin" />
                            <span>Inference Running...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles size={16} />
                            <span>Diagnose Specimen</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className={`rounded-2xl border overflow-hidden flex flex-col items-center justify-center p-4 relative min-h-[160px] aspect-video ${darkMode ? 'border-cs-border bg-cs-cardlight/30' : 'border-slate-200 bg-slate-100/50'}`}>
                    {previewUrl ? (
                      <img src={previewUrl} className="w-full h-full object-contain rounded-lg" alt="Specimen Preview" />
                    ) : (
                      <div className="text-center space-y-1.5 p-4">
                        <p className={`text-xs font-bold tracking-widest uppercase ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>PREVIEW WINDOW</p>
                        <p className="text-xs text-cs-muted">No crop leaf image selected.</p>
                      </div>
                    )}
                  </div>
                </div>

                {diagError && (
                  <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 text-sm flex items-start gap-2.5 animate-fade-in">
                    <AlertTriangle size={18} className="mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-bold">Image Validation Rejected</h4>
                      <p className="text-xs mt-0.5">{diagError}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Results Sheet */}
            {diagResult && (
              <div className={`p-6 md:p-8 rounded-2xl animate-fade-in space-y-6 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                <div className="flex flex-col md:flex-row md:items-center justify-between border-b pb-4 gap-4 border-cs-border/40">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-cs-mint">Dual AI Inference Verdict</span>
                    <h2 className={`text-2xl font-bold mt-1 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {translations.plant_name || diagResult.diagnosis.plant_name} — {translations.disease_name || diagResult.diagnosis.disease_name}
                    </h2>
                    {diagResult.diagnosis.plant_scientific && (
                      <p className="text-xs text-cs-muted italic mt-0.5">Scientific: {translations.plant_scientific || diagResult.diagnosis.plant_scientific}</p>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <button 
                      onClick={playTts}
                      className={`py-2.5 px-4 rounded-xl text-xs font-bold transition flex items-center gap-1.5 border ${audioPlaying ? 'bg-amber-500 text-cs-bg border-amber-400' : (darkMode ? 'bg-cs-cardlight border-cs-border text-white hover:bg-cs-border' : 'bg-slate-100 border-slate-200 text-slate-800 hover:bg-slate-200')}`}
                    >
                      <Play size={14} />
                      <span>{audioPlaying ? 'Pause Audio' : 'Speak Summary'}</span>
                    </button>
                    <button 
                      onClick={downloadPdf}
                      className={`py-2.5 px-4 rounded-xl border text-xs font-bold transition flex items-center gap-1.5 ${darkMode ? 'bg-cs-cardlight border-cs-border text-white hover:bg-cs-border' : 'bg-slate-100 border-slate-200 text-slate-800 hover:bg-slate-200'}`}
                    >
                      <Download size={14} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                      <span>Download PDF</span>
                    </button>
                  </div>
                </div>

                {/* Score Indicators */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className={`p-4 rounded-xl border ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                    <span className="text-[10px] text-cs-muted block mb-0.5">Dual-Engine Classification</span>
                    <span className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>CNN + Gemini Vision</span>
                  </div>
                  <div className={`p-4 rounded-xl border ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                    <span className="text-[10px] text-cs-muted block mb-0.5">CNN Conf. Score</span>
                    <span className={`text-sm font-bold ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>
                      {diagResult.cnn_confidence > 0 ? `${formatNum(diagResult.cnn_confidence, 1)}%` : 'Gemini Fallback'}
                    </span>
                  </div>
                  <div className={`p-4 rounded-xl border ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                    <span className="text-[10px] text-cs-muted block mb-0.5">Infection Severity</span>
                    <span className={`text-sm font-bold ${diagResult.diagnosis.severity === 'Severe' ? 'text-red-500' : diagResult.diagnosis.severity === 'Moderate' ? 'text-amber-500' : 'text-emerald-500'}`}>
                      {diagResult.diagnosis.severity || 'Mild'}
                    </span>
                  </div>
                  <div className={`p-4 rounded-xl border ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                    <span className="text-[10px] text-cs-muted block mb-0.5">Contrast Quality Index</span>
                    <span className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{diagResult.quality_score}% (Clear)</span>
                  </div>
                </div>

                {/* Imagery side by side */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                  <div className={`rounded-xl border overflow-hidden flex flex-col ${darkMode ? 'border-cs-border bg-cs-card' : 'border-slate-200 bg-white'}`}>
                    <div className={`py-2 px-4 border-b text-[10px] font-bold ${darkMode ? 'bg-cs-cardlight border-cs-border text-white' : 'bg-slate-50 border-slate-100 text-slate-700'}`}>
                      Original Specimen Frame
                    </div>
                    <div className="p-4 flex items-center justify-center bg-black/20 aspect-video max-h-[250px]">
                      <img src={`data:image/jpeg;base64,${diagResult.original_image}`} className="max-h-full max-w-full object-contain rounded-lg" alt="Original" />
                    </div>
                  </div>

                  {showGradCam && diagResult.heatmap && (
                    <div className={`rounded-xl border overflow-hidden flex flex-col ${darkMode ? 'border-cs-border bg-cs-card' : 'border-slate-200 bg-white'}`}>
                      <div className={`py-2 px-4 border-b text-[10px] font-bold ${darkMode ? 'bg-cs-cardlight border-cs-border text-white' : 'bg-slate-50 border-slate-100 text-slate-700'}`}>
                        Grad-CAM Attention Heatmap
                      </div>
                      <div className="p-4 flex items-center justify-center bg-black/20 aspect-video max-h-[250px]">
                        <img src={`data:image/jpeg;base64,${diagResult.heatmap}`} className="max-h-full max-w-full object-contain rounded-lg" alt="Gradcam" />
                      </div>
                    </div>
                  )}
                </div>

                {/* Treatment Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
                  <div className={`p-5 rounded-xl border lg:col-span-2 space-y-4 ${darkMode ? 'bg-cs-cardlight/30 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                    <div>
                      <h4 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>Causal Pathogen</h4>
                      <p className={`text-sm mt-1 font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{translations.disease_pathogen || diagResult.diagnosis.disease_pathogen || 'None (Healthy)'}</p>
                    </div>
                    <div>
                      <h4 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>Symptoms Identified</h4>
                      <p className="text-xs md:text-sm mt-1 leading-relaxed text-cs-muted">{translations.symptoms || diagResult.diagnosis.symptoms}</p>
                    </div>
                    <div>
                      <h4 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>Organic & Cultural Remedies</h4>
                      <p className="text-xs md:text-sm mt-1 leading-relaxed text-cs-muted">{translations.organic_treatment || diagResult.diagnosis.organic_treatment || diagResult.diagnosis.treatment}</p>
                    </div>
                    <div>
                      <h4 className={`text-xs font-bold uppercase tracking-wider ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>Chemical Controls</h4>
                      <p className="text-xs md:text-sm mt-1 leading-relaxed text-cs-muted">{translations.chemical_treatment || diagResult.diagnosis.chemical_treatment}</p>
                    </div>
                  </div>

                  <div className={`p-5 rounded-xl border space-y-4 ${darkMode ? 'bg-cs-cardlight/30 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                    <div className="border-b border-cs-border pb-2">
                      <h4 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>Product Recommendations</h4>
                    </div>
                    <div className="space-y-1">
                      <span className="text-[9px] uppercase font-bold text-cs-muted block">Recommended Fungicide</span>
                      <div className={`p-3 rounded-lg border ${darkMode ? 'bg-cs-cardlight border-cs-border' : 'bg-white border-slate-200'}`}>
                        <p className={`text-sm font-bold ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>{diagResult.diagnosis.medicine?.name || 'N/A'}</p>
                        <p className="text-[10px] text-cs-muted mt-0.5">Dose: {diagResult.diagnosis.medicine?.dose || 'N/A'}</p>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <span className="text-[9px] uppercase font-bold text-cs-muted block">Fertilizer Advice</span>
                      <div className={`p-3 rounded-lg border ${darkMode ? 'bg-cs-cardlight border-cs-border' : 'bg-white border-slate-200'}`}>
                        <p className={`text-sm font-bold ${darkMode ? 'text-cs-mint' : 'text-emerald-600'}`}>{diagResult.diagnosis.fertilizer?.name || 'N/A'}</p>
                        <p className="text-[10px] text-cs-muted mt-0.5">NPK Ratio: N:{diagResult.diagnosis.fertilizer?.npk_n} P:{diagResult.diagnosis.fertilizer?.npk_p} K:{diagResult.diagnosis.fertilizer?.npk_k}</p>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            )}
          </div>
        )}

        {/* ── TAB 2: ANALYTICS DASHBOARD ── */}
        {activeTab === 'analytics' && (
          <div className="space-y-6 animate-fade-in">
            {stats ? (
              <>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Daily Scan activity */}
                  <div className={`p-6 rounded-2xl ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                    <h3 className={`font-bold text-sm mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>📈 Diagnostic Scan Activity over Time</h3>
                    <div className="h-48 w-full flex items-end justify-between gap-1 pt-4 border-b border-cs-border/40 relative">
                      {stats.trendData.map((t, i) => {
                        const maxCount = Math.max(...stats.trendData.map(d => d.count));
                        const heightPct = maxCount > 0 ? (t.count / maxCount) * 100 : 0;
                        return (
                          <div key={i} className="flex-1 flex flex-col items-center group relative cursor-pointer">
                            <div className="text-[10px] text-cs-mint font-bold absolute bottom-full mb-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              {t.count} Scans
                            </div>
                            <div 
                              className="w-full bg-cs-mint/25 group-hover:bg-cs-mint border border-cs-mint/40 rounded-t transition-all duration-300"
                              style={{ height: `${Math.max(heightPct, 8)}%` }}
                            ></div>
                            <span className="text-[9px] text-cs-muted mt-2 rotate-45 origin-left truncate max-w-[40px] block">
                              {t.date.slice(0, 5)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Crop scan allocation */}
                  <div className={`p-6 rounded-2xl ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                    <h3 className={`font-bold text-sm mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>🌿 Plant Categories Monitored</h3>
                    <div className="space-y-3.5">
                      {stats.cropData.map((c, i) => {
                        const total = history.length;
                        const pct = total > 0 ? (c.count / total) * 100 : 0;
                        return (
                          <div key={i} className="space-y-1">
                            <div className="flex justify-between text-xs font-semibold">
                              <span className={darkMode ? 'text-white' : 'text-slate-800'}>{c.name}</span>
                              <span className="text-cs-muted">{c.count} scans ({formatNum(pct, 0)}%)</span>
                            </div>
                            <div className={`w-full h-2 rounded-full overflow-hidden border ${darkMode ? 'bg-cs-cardlight border-cs-border' : 'bg-slate-100 border-slate-200'}`}>
                              <div className="bg-cs-mint h-full rounded-full" style={{ width: `${pct}%` }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Infection prevalence */}
                  <div className={`p-6 rounded-2xl ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                    <h3 className={`font-bold text-sm mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>🐛 Prevalence of Leaf Infections</h3>
                    <div className="space-y-3.5">
                      {stats.diseaseData.map((d, i) => {
                        const maxCount = Math.max(...stats.diseaseData.map(x => x.count));
                        const pctOfMax = maxCount > 0 ? (d.count / maxCount) * 100 : 0;
                        return (
                          <div key={i} className="space-y-1">
                            <div className="flex justify-between text-xs font-semibold">
                              <span className={`truncate max-w-[200px] ${darkMode ? 'text-white' : 'text-slate-800'}`}>{d.name}</span>
                              <span className="text-cs-muted">{d.count} Cases</span>
                            </div>
                            <div className={`w-full h-2 rounded-full overflow-hidden border ${darkMode ? 'bg-cs-cardlight border-cs-border' : 'bg-slate-100 border-slate-200'}`}>
                              <div className="bg-amber-500 h-full rounded-full" style={{ width: `${pctOfMax}%` }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Diagnosed Severity count */}
                  <div className={`p-6 rounded-2xl ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                    <h3 className={`font-bold text-sm mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>🚨 Diagnosed Severity Distribution</h3>
                    <div className="grid grid-cols-4 gap-3.5 pt-4">
                      {Object.entries(stats.severityMap).map(([sev, count]) => {
                        const colors = {
                          Excellent: 'border-cs-mint/40 text-cs-mint bg-cs-mint/5',
                          Mild: 'border-yellow-500/40 text-yellow-500 bg-yellow-500/5',
                          Moderate: 'border-orange-500/40 text-orange-500 bg-orange-500/5',
                          Severe: 'border-red-500/40 text-red-500 bg-red-500/5'
                        };
                        return (
                          <div key={sev} className={`p-4 rounded-xl border text-center ${colors[sev] || 'border-cs-border'}`}>
                            <span className="text-[10px] font-bold block uppercase tracking-wider mb-1">{sev}</span>
                            <span className="text-2xl font-extrabold">{count}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                </div>

                {/* Geographical Map listing */}
                <div className={`p-6 rounded-2xl space-y-4 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                  <h3 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>🗺️ Geographical Scan Coordinates</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {history.filter(h => h.Latitude !== 0.0 && h.Latitude !== "").slice(0, 8).map((h, i) => (
                      <div key={i} className={`p-3.5 rounded-xl border text-xs flex items-center gap-2.5 ${darkMode ? 'bg-cs-cardlight border-cs-border' : 'bg-slate-50 border-slate-100 text-slate-800'}`}>
                        <MapPin size={16} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                        <div>
                          <p className="font-bold truncate">{h.City}</p>
                          <p className="text-[10px] text-cs-muted">{formatCoord(h.Latitude, 3)}, {formatCoord(h.Longitude, 3)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="py-20 text-center text-cs-muted">
                <BarChart2 size={48} className="mx-auto text-cs-border mb-4" />
                <h4 className="font-bold text-white text-base">No Statistics Available Yet</h4>
                <p className="text-xs text-cs-muted mt-1 max-w-xs mx-auto">Run crop disease scans in the Diagnostics tab to populate this dashboard.</p>
              </div>
            )}
          </div>
        )}

        {/* ── TAB 3: CLIMATE & WEATHER ── */}
        {activeTab === 'climate' && (
          <div className="space-y-6 animate-fade-in">
            {/* Location Search Bar */}
            <div className={`p-6 rounded-2xl space-y-4 relative z-20 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
              <h3 className={`font-bold text-sm flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                <MapPin size={18} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                <span>Search Location Telemetry</span>
              </h3>
              
              <div className="flex flex-col md:flex-row gap-2 relative">
                <input 
                  type="text" 
                  placeholder="Enter city or district name..."
                  className={`flex-1 py-3 px-4 rounded-xl border focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                  value={locationQuery}
                  onChange={(e) => handleLocationSearch(e.target.value)}
                />
                
                {locationSuggestions.length > 0 && (
                  <div className={`absolute top-full left-0 right-0 mt-1.5 rounded-xl border shadow-xl max-h-48 overflow-y-auto z-30 ${darkMode ? 'bg-cs-cardlight border-cs-border' : 'bg-white border-slate-200'}`}>
                    {locationSuggestions.map((s, i) => (
                      <button 
                        key={i}
                        onClick={() => selectSuggestion(s)}
                        className={`w-full text-left py-2.5 px-4 text-xs transition border-b border-cs-border/20 ${darkMode ? 'text-white hover:bg-cs-border/60' : 'text-slate-800 hover:bg-slate-100'}`}
                      >
                        {s.name}, {s.admin1 || ''} ({s.country})
                      </button>
                    ))}
                  </div>
                )}

                <button 
                  onClick={requestGpsLocation}
                  className={`py-3 px-6 rounded-xl border font-bold text-xs transition flex items-center justify-center gap-2 ${darkMode ? 'bg-cs-cardlight border-cs-border text-white hover:bg-cs-border' : 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100'}`}
                >
                  <MapPin size={14} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                  <span>GPS Geolocation</span>
                </button>
              </div>
            </div>

            {/* Detailed Weather Stats */}
            {weather ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Metrics Card */}
                  <div className={`p-6 rounded-2xl space-y-6 lg:col-span-2 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                    <h3 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>🌡️ Micro-Climate Variables</h3>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <Thermometer size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">Temperature</span>
                        <span className={`text-xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.temperature}°C</span>
                        <span className="text-[9px] text-cs-muted block">Feels like: {weather.weather.feels_like}°C</span>
                      </div>
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <CloudRain size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">Precipitation</span>
                        <span className={`text-xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.precipitation || 0.0} mm</span>
                        <span className="text-[9px] text-cs-muted block">Chance of Rain: {weather.weather.chance_of_rain}%</span>
                      </div>
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <Wind size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">Wind Speed</span>
                        <span className={`text-xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.wind_speed} km/h</span>
                        <span className="text-[9px] text-cs-muted block">Direction: {weather.weather.wind_direction}°</span>
                      </div>
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <Droplets size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">Humidity</span>
                        <span className={`text-xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.humidity}%</span>
                        <span className="text-[9px] text-cs-muted block">Pressure: {weather.weather.pressure} hPa</span>
                      </div>
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <Compass size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">UV Index</span>
                        <span className={`text-xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.uv_index || 0.0}</span>
                      </div>
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <Activity size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">US Air Quality</span>
                        <span className={`text-xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.aqi || 50} AQI</span>
                      </div>
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <Sunrise size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">Sunrise</span>
                        <span className={`text-sm font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.sunrise}</span>
                      </div>
                      <div className={`p-4 rounded-xl border text-center ${darkMode ? 'bg-cs-cardlight/60 border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
                        <Sunset size={20} className="mx-auto text-cs-mint mb-1" />
                        <span className="text-cs-muted text-[10px] block mb-1">Sunset</span>
                        <span className={`text-sm font-extrabold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{weather.weather.sunset}</span>
                      </div>
                    </div>
                  </div>

                  {/* Risk and warnings */}
                  <div className={`p-6 rounded-2xl space-y-4 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                    <h3 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>Advisory Risk Metrics</h3>
                    
                    <div className="space-y-3.5">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-cs-muted font-semibold">Climate Pathogen Threat</span>
                        <span className={`font-bold px-2 py-0.5 rounded ${weather.risk_pct > 65 ? 'bg-red-500/10 text-red-400' : 'bg-cs-mint/10 text-cs-mint'}`}>
                          {formatNum(weather.risk_pct, 0)}%
                        </span>
                      </div>
                      
                      <div className="w-full bg-cs-cardlight h-2 rounded-full overflow-hidden border border-cs-border">
                        <div 
                          className={`h-full rounded-full ${weather.risk_pct > 65 ? 'bg-red-500' : 'bg-cs-mint'}`}
                          style={{ width: `${weather.risk_pct}%` }}
                        ></div>
                      </div>

                      {weather.alerts && weather.alerts.length > 0 ? (
                        <div className="space-y-2 pt-2">
                          {weather.alerts.map((a, i) => (
                            <div key={i} className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs flex items-start gap-2">
                              <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                              <span>{a}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="p-3 rounded-lg bg-cs-mint/10 border border-cs-mint/20 text-cs-mint text-[11px] flex items-center gap-2">
                          <CheckCircle size={14} className="shrink-0" />
                          <span>No severe environment stress warnings for crops.</span>
                        </div>
                      )}
                    </div>
                  </div>

                </div>

                {/* Agricultural Advisories */}
                {weather.agri && (
                  <div className={`p-6 rounded-2xl space-y-4 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
                    <h3 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>🌾 Crop Management Advisory Recommendations</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className={`p-4 rounded-xl border space-y-1 ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100 text-slate-800'}`}>
                        <span className="text-[10px] text-cs-muted uppercase font-bold tracking-wider">Suitable Season Crops</span>
                        <p className="text-sm font-semibold">{weather.agri.suitable_crops}</p>
                      </div>
                      <div className={`p-4 rounded-xl border space-y-1 ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100 text-slate-800'}`}>
                        <span className="text-[10px] text-cs-muted uppercase font-bold tracking-wider">Irrigation Scheduling</span>
                        <p className="text-sm font-semibold">{weather.agri.irrigation}</p>
                      </div>
                      <div className={`p-4 rounded-xl border space-y-1 ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100 text-slate-800'}`}>
                        <span className="text-[10px] text-cs-muted uppercase font-bold tracking-wider">Fertilizer Suggestions</span>
                        <p className="text-sm font-semibold">{weather.agri.fertilizer}</p>
                      </div>
                      <div className={`p-4 rounded-xl border space-y-1 ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100 text-slate-800'}`}>
                        <span className="text-[10px] text-cs-muted uppercase font-bold tracking-wider">Chemical Spray Timing</span>
                        <p className="text-sm font-semibold">{weather.agri.spray_time}</p>
                      </div>
                      <div className={`p-4 rounded-xl border space-y-1 md:col-span-2 ${darkMode ? 'bg-cs-cardlight/50 border-cs-border' : 'bg-slate-50 border-slate-100 text-slate-800'}`}>
                        <span className="text-[10px] text-cs-muted uppercase font-bold tracking-wider">Seasonal stress warning</span>
                        <p className="text-sm font-semibold text-cs-muted">{weather.agri.seasonal_risk}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-center text-cs-muted text-sm animate-pulse">Coordinates telemetry loading...</p>
            )}
          </div>
        )}

        {/* ── TAB 4: SCAN HISTORY REGISTRY ── */}
        {activeTab === 'history' && (
          <div className="space-y-6 animate-fade-in">
            {/* Filter controls panel */}
            <div className={`p-6 rounded-2xl space-y-4 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h3 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>Filter History</h3>
                
                {/* Export / Email */}
                <div className="flex gap-2">
                  <button 
                    onClick={exportCsv}
                    disabled={history.length === 0}
                    className={`py-2 px-3.5 rounded-lg border text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-50 ${darkMode ? 'bg-cs-cardlight border-cs-border text-white hover:bg-cs-border' : 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100'}`}
                  >
                    <Download size={14} />
                    <span>CSV</span>
                  </button>
                  <button 
                    onClick={exportJson}
                    disabled={history.length === 0}
                    className={`py-2 px-3.5 rounded-lg border text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-50 ${darkMode ? 'bg-cs-cardlight border-cs-border text-white hover:bg-cs-border' : 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100'}`}
                  >
                    <Download size={14} />
                    <span>JSON</span>
                  </button>
                  <button 
                    onClick={() => { setEmailReportOpen(true); setEmailMessage(''); }}
                    disabled={history.length === 0}
                    className={`py-2 px-3.5 rounded-lg border text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-50 ${darkMode ? 'bg-cs-cardlight border-cs-border text-white hover:bg-cs-border' : 'bg-slate-50 border-slate-200 text-slate-800 hover:bg-slate-100'}`}
                  >
                    <Mail size={14} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
                    <span>Email report</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-cs-muted uppercase">Search Name</label>
                  <input 
                    type="text" 
                    placeholder="Search plant, disease, or city..."
                    className={`w-full py-2 px-3 rounded-lg border text-xs focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                    value={historySearch}
                    onChange={(e) => setHistorySearch(e.target.value)}
                  />
                </div>
                
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-cs-muted uppercase">Plant Category</label>
                  <select 
                    className={`w-full py-2 px-3 rounded-lg border text-xs focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border text-white' : 'bg-slate-50 border-slate-200 text-slate-800'}`}
                    value={filterPlant}
                    onChange={(e) => setFilterPlant(e.target.value)}
                  >
                    {uniquePlants.map(p => (
                      <option key={p} value={p}>{p === 'all' ? 'All Plants' : p}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-cs-muted uppercase">Severity</label>
                  <select 
                    className={`w-full py-2 px-3 rounded-lg border text-xs focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border text-white' : 'bg-slate-50 border-slate-200 text-slate-800'}`}
                    value={filterSeverity}
                    onChange={(e) => setFilterSeverity(e.target.value)}
                  >
                    {uniqueSeverities.map(s => (
                      <option key={s} value={s}>{s === 'all' ? 'All Severities' : s}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Email Dialog Modal */}
            {emailReportOpen && (
              <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50 px-4">
                <div className={`w-full max-w-sm p-6 rounded-2xl space-y-4 border ${darkMode ? 'bg-cs-card border-cs-border text-white shadow-2xl' : 'bg-white border-slate-200 text-slate-800 shadow-xl'}`}>
                  <h4 className="font-bold text-sm">Send Diagnosis History via Email</h4>
                  <div className="space-y-1.5">
                    <label className="text-xs text-cs-muted">Recipient Email Address</label>
                    <input 
                      type="email" 
                      placeholder="e.g. farmer@gmail.com"
                      className={`w-full px-3 py-2 rounded-lg border text-xs focus:outline-none ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-slate-50 border-slate-200 focus:border-emerald-600 text-slate-800'}`}
                      value={emailInput}
                      onChange={(e) => setEmailInput(e.target.value)}
                    />
                  </div>

                  {emailMessage && (
                    <p className="text-[10px] text-cs-mint leading-relaxed border border-cs-mint/20 p-2 rounded bg-cs-mint/5">{emailMessage}</p>
                  )}

                  <div className="flex gap-2 justify-end pt-2 text-xs">
                    <button 
                      onClick={() => setEmailReportOpen(false)}
                      className={`py-2 px-4 rounded-lg font-bold border ${darkMode ? 'border-cs-border hover:bg-cs-cardlight text-cs-muted' : 'border-slate-200 hover:bg-slate-55 text-slate-600'}`}
                    >
                      Close
                    </button>
                    <button 
                      onClick={emailReport}
                      disabled={emailLoading}
                      className={`py-2 px-4 rounded-lg font-bold text-cs-bg bg-cs-mint hover:bg-cs-emerald disabled:opacity-55`}
                    >
                      {emailLoading ? 'Sending...' : 'Send Email'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Scan history grid */}
            <div className={`p-6 rounded-2xl ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
              <div className="overflow-x-auto w-full">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className={`border-b text-cs-muted font-semibold ${darkMode ? 'border-cs-border bg-cs-cardlight/30' : 'border-slate-100 bg-slate-50'}`}>
                      <th className="p-3">Timestamp</th>
                      <th className="p-3">Plant Type</th>
                      <th className="p-3">Diagnosis</th>
                      <th className="p-3">CNN Conf.</th>
                      <th className="p-3">Severity</th>
                      <th className="p-3">Location Coordinates</th>
                      <th className="p-3 text-right">Delete</th>
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
                            {item.City || 'GPS Location'} ({formatCoord(item.Latitude, 2)}, {formatCoord(item.Longitude, 2)})
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
                                className={`p-2 rounded-lg transition ${darkMode ? 'text-cs-muted hover:text-red-400 hover:bg-red-500/10' : 'text-slate-500 hover:text-red-600 hover:bg-slate-100'}`}
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
                          No matching scans found in prediction registry logs.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ── TAB 5: SYSTEM SETTINGS ── */}
        {activeTab === 'settings' && (
          <div className={`p-6 rounded-2xl max-w-xl space-y-6 animate-fade-in ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
            <h3 className={`font-bold text-sm flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              <Settings size={18} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
              <span>Diagnostic Settings</span>
            </h3>

            <div className="space-y-6">
              {/* Slider */}
              <div className="space-y-2 border-b border-cs-border pb-4">
                <div className="flex justify-between text-xs font-semibold text-cs-muted">
                  <span>Minimum CNN Confidence Threshold</span>
                  <span className="text-cs-mint font-bold">{minConfidence}%</span>
                </div>
                <input 
                  type="range" 
                  min="20" 
                  max="90" 
                  className="w-full accent-cs-mint cursor-pointer"
                  value={minConfidence}
                  onChange={(e) => setMinConfidence(parseInt(e.target.value))}
                />
                <p className="text-[10px] text-cs-muted leading-relaxed">Predictions below this score will flag warning advisories to consult agronomists.</p>
              </div>

              {/* Toggles */}
              <div className="space-y-4 border-b border-cs-border pb-4 select-none">
                <label className="flex items-center justify-between text-xs text-white cursor-pointer">
                  <span className={darkMode ? 'text-white font-semibold' : 'text-slate-800 font-semibold'}>Generate Grad-CAM Attention Heatmap</span>
                  <input 
                    type="checkbox" 
                    checked={showGradCam} 
                    onChange={() => setShowGradCam(!showGradCam)} 
                    className="w-4.5 h-4.5 rounded text-cs-mint focus:ring-0 accent-cs-mint"
                  />
                </label>

                <label className="flex items-center justify-between text-xs text-white cursor-pointer">
                  <span className={darkMode ? 'text-white font-semibold' : 'text-slate-800 font-semibold'}>Show Top-3 CNN Alternatives</span>
                  <input 
                    type="checkbox" 
                    checked={showTop3} 
                    onChange={() => setShowTop3(!showTop3)} 
                    className="w-4.5 h-4.5 rounded text-cs-mint focus:ring-0 accent-cs-mint"
                  />
                </label>

                <label className="flex items-center justify-between text-xs text-white cursor-pointer">
                  <span className={darkMode ? 'text-white font-semibold' : 'text-slate-800 font-semibold'}>Enable Gemini Vision Diagnostics</span>
                  <input 
                    type="checkbox" 
                    checked={useGemini} 
                    onChange={() => setUseGemini(!useGemini)} 
                    className="w-4.5 h-4.5 rounded text-cs-mint focus:ring-0 accent-cs-mint"
                  />
                </label>

                <label className="flex items-center justify-between text-xs text-white cursor-pointer">
                  <span className={darkMode ? 'text-white font-semibold' : 'text-slate-800 font-semibold'}>Show Floating Agronomy Chatbot</span>
                  <input 
                    type="checkbox" 
                    checked={showChatbot} 
                    onChange={() => setShowChatbot(!showChatbot)} 
                    className="w-4.5 h-4.5 rounded text-cs-mint focus:ring-0 accent-cs-mint"
                  />
                </label>
              </div>

              {/* Languages Selection */}
              <div className="space-y-2 border-b border-cs-border pb-4">
                <span className="text-[10px] font-bold text-cs-muted uppercase flex items-center gap-1">
                  <Globe size={12} className="text-cs-mint" />
                  <span>Telemetry translation language</span>
                </span>
                <select 
                  className={`w-full py-2 px-3 rounded-lg border text-xs focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border text-white' : 'bg-slate-50 border-slate-200 text-slate-800'}`}
                  value={lang}
                  onChange={(e) => setLang(e.target.value)}
                >
                  {SUPPORTED_LANGUAGES.map(sl => (
                    <option key={sl.code} value={sl.code}>{sl.flag} {sl.name}</option>
                  ))}
                </select>
              </div>

              {/* Backend API Server URL Settings */}
              <div className="space-y-2 border-b border-cs-border pb-4">
                <span className="text-[10px] font-bold text-cs-muted uppercase flex items-center gap-1">
                  <Globe size={12} className="text-cs-mint" />
                  <span>Backend API Server URL</span>
                </span>
                <form onSubmit={handleSaveCustomBase} className="flex gap-2">
                  <input 
                    type="text" 
                    placeholder="Auto-detected (same origin)"
                    className={`flex-1 py-2 px-3 rounded-lg border text-xs focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border text-white' : 'bg-slate-50 border-slate-200 text-slate-800'}`}
                    value={customBase}
                    onChange={(e) => setCustomBase(e.target.value)}
                  />
                  <button 
                    type="submit"
                    className="py-2 px-4 rounded-lg bg-cs-mint text-cs-bg font-bold text-xs"
                  >
                    Save
                  </button>
                </form>
                <p className="text-[9px] text-cs-muted">Configure this only if your frontend and backend run on different domains.</p>
              </div>

              {/* Theme Settings */}
              <div className="space-y-3">
                <span className="text-[10px] font-bold text-cs-muted uppercase">Dashboard theme selector</span>
                <div className="flex gap-2">
                  <button 
                    onClick={() => setDarkMode(true)}
                    className={`flex-1 py-3.5 rounded-xl border font-bold text-xs flex items-center justify-center gap-2 transition ${darkMode ? 'bg-cs-mint text-cs-bg border-cs-mint' : 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-800'}`}
                  >
                    <Moon size={14} />
                    <span>Dark Theme</span>
                  </button>
                  <button 
                    onClick={() => setDarkMode(false)}
                    className={`flex-1 py-3.5 rounded-xl border font-bold text-xs flex items-center justify-center gap-2 transition ${!darkMode ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-cs-cardlight hover:bg-cs-border border-cs-border text-white'}`}
                  >
                    <Sun size={14} />
                    <span>Light Theme</span>
                  </button>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* ── TAB 6: FARMER PROFILE ── */}
        {activeTab === 'profile' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
            {/* User details */}
            <div className={`p-6 rounded-2xl space-y-4 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
              <h3 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>👤 Farmer Registration Details</h3>
              <div className="space-y-3.5">
                <div className="border-b border-cs-border/40 pb-2.5">
                  <span className="text-[10px] text-cs-muted block uppercase">Agronomist Name</span>
                  <span className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{user.name}</span>
                </div>
                <div className="border-b border-cs-border/40 pb-2.5">
                  <span className="text-[10px] text-cs-muted block uppercase">Registered Mobile No.</span>
                  <span className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{user.mobile}</span>
                </div>
                <div className="border-b border-cs-border/40 pb-2.5">
                  <span className="text-[10px] text-cs-muted block uppercase">Contact Email ID</span>
                  <span className={`text-sm font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{user.email}</span>
                </div>
              </div>
            </div>

            {/* Architecture stack list */}
            <div className={`p-6 rounded-2xl lg:col-span-2 space-y-4 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200 shadow-sm'}`}>
              <h3 className={`font-bold text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>🔬 Technology Stack Overview</h3>
              <p className="text-xs text-cs-muted leading-relaxed">
                CropSense AI leverages a dual-inference pipeline. Deep CNN structures analyze leaf spots locally in milliseconds. In parallel, Google Gemini multimodal models analyze symptoms to verify diagnostic accuracy and provide customized chemical recipes and fertilizer tips.
              </p>
              
              <div className="flex flex-wrap gap-2 pt-2">
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">🐍 Python 3.10</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">🧠 TensorFlow-CPU 2.16</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">🔮 Gemini 2.5 Flash</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">⚡ FastAPI REST APIs</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">⚛️ React 18 + Vite</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">🎨 Tailwind CSS</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">🗺️ Grad-CAM Heatmaps</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">📄 ReportLab PDF</span>
                <span className="px-3 py-1 bg-cs-mint/15 text-cs-mint border border-cs-mint/35 rounded-full text-xs font-semibold">🔊 Google Text-To-Speech</span>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Floating AI Chatbot Widget */}
      {showChatbot && (
        <div className={`fixed bottom-6 right-6 w-96 max-h-[480px] h-[440px] rounded-2xl flex flex-col overflow-hidden z-40 animate-fade-in shadow-2xl transition-colors duration-300 ${darkMode ? 'glass-panel' : 'bg-white border border-slate-200'}`}>
          <div className={`py-3.5 px-4 border-b flex justify-between items-center ${darkMode ? 'bg-cs-cardlight border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
            <div className="flex items-center gap-2">
              <MessageSquare size={16} className={darkMode ? 'text-cs-mint' : 'text-emerald-600'} />
              <span className={`text-xs font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>Agronomist Assistant</span>
            </div>
            {chatLoading && (
              <RefreshCw size={12} className="animate-spin text-cs-mint" />
            )}
          </div>

          {/* Chat Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3.5 text-xs">
            {chatHistory.map((h, i) => (
              <div key={i} className={`flex ${h.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl leading-relaxed ${h.role === 'user' ? (darkMode ? 'bg-cs-mint text-cs-bg font-medium rounded-tr-none' : 'bg-emerald-600 text-white font-medium rounded-tr-none') : (darkMode ? 'bg-cs-cardlight/80 border border-cs-border text-white rounded-tl-none' : 'bg-slate-100 border border-slate-200 text-slate-800 rounded-tl-none')}`}>
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
            <div className={`px-4 py-2 border-t flex gap-1.5 overflow-x-auto shrink-0 ${darkMode ? 'border-cs-border/50 bg-cs-card/30' : 'border-slate-100 bg-slate-50/50'}`}>
              <button 
                onClick={() => triggerChat(`How to prevent ${diagResult.diagnosis.disease_name} next season?`)}
                className={`text-[9px] py-1 px-2.5 rounded-full border transition ${darkMode ? 'bg-cs-cardlight border-cs-border text-cs-muted hover:text-white' : 'bg-white border-slate-200 text-slate-500 hover:text-slate-900'}`}
              >
                Prevention Tips
              </button>
              <button 
                onClick={() => triggerChat("What organic alternatives exist?")}
                className={`text-[9px] py-1 px-2.5 rounded-full border transition ${darkMode ? 'bg-cs-cardlight border-cs-border text-cs-muted hover:text-white' : 'bg-white border-slate-200 text-slate-500 hover:text-slate-900'}`}
              >
                Organic Options
              </button>
              <button 
                onClick={() => triggerChat("Is this safe to eat?")}
                className={`text-[9px] py-1 px-2.5 rounded-full border transition ${darkMode ? 'bg-cs-cardlight border-cs-border text-cs-muted hover:text-white' : 'bg-white border-slate-200 text-slate-500 hover:text-slate-900'}`}
              >
                Safety Notes
              </button>
            </div>
          )}

          {/* Chat Inputs */}
          <div className={`p-3 border-t flex gap-2 shrink-0 ${darkMode ? 'bg-cs-card border-cs-border' : 'bg-slate-50 border-slate-100'}`}>
            <button 
              onClick={handleStt}
              className={`p-2.5 rounded-xl border transition ${listening ? 'bg-red-500/20 border-red-500/40 text-red-400 animate-pulse' : (darkMode ? 'bg-cs-cardlight border-cs-border text-cs-muted hover:text-white' : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-100')}`}
            >
              <Mic size={16} />
            </button>
            <input 
              type="text" 
              placeholder="Ask about crop health..."
              className={`flex-1 py-2.5 px-3.5 rounded-xl border text-xs focus:outline-none transition ${darkMode ? 'bg-cs-cardlight border-cs-border focus:border-cs-mint text-white' : 'bg-white border-slate-200 focus:border-emerald-600 text-slate-800'}`}
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') triggerChat(); }}
            />
            <button 
              onClick={() => triggerChat()}
              className={`p-2.5 rounded-xl transition ${darkMode ? 'bg-cs-mint hover:bg-cs-emerald text-cs-bg' : 'bg-emerald-600 hover:bg-emerald-700 text-white'}`}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

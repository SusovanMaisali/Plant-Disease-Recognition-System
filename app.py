"""
CropSense AI v3.0 Pro — Gemini Vision + CNN
All 12 audit issues fixed:
  1. translate_text hoisted above cache functions
  2. get_gemini_client cached with @st.cache_resource
  3. Chat submit uses session_state submitted-flag to prevent duplicate messages
  4. Context vars stored in st.session_state, not checked via dir()
  5. predicted_class/input_tensor guarded with is_not_none checks
  6. gemini_data persisted in st.session_state across reruns
  7. Suggestion chips use real st.button calls
  8. gemini_analyze_leaf cache is language-agnostic; translation at render time
  9. PDF text sanitised (HTML tags stripped)
 10. check_repeat_alert normalises disease name before comparing
 11. Voice mp3 written to per-session tempfile (thread-safe)
 12. st.stop() replaced with early-return flag inside column scope
"""

import streamlit as st
import tensorflow as tf
import numpy as np
import pandas as pd
import cv2
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator
from datetime import datetime
import os, io, json, re, tempfile, html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER
import google.generativeai as genai

# ═══════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════
st.set_page_config(
    page_title="CropSense AI — Intelligent Crop Disease Detection",
    page_icon="🌿", layout="wide", initial_sidebar_state="expanded"
)

# Initialize Session State Auth Variables immediately
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_mobile = ""
    st.session_state.user_email = ""
    st.session_state.login_otp = ""
    st.session_state.login_otp_sent = False
    st.session_state.temp_mobile = ""

if "history" not in st.session_state:
    st.session_state.history = []

# ═══════════════════════════════════════════════════
# USER AUTHENTICATION & DATABASE HELPERS
# ═══════════════════════════════════════════════════
def load_and_migrate_history(csv_path: str) -> pd.DataFrame:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if not os.path.exists(csv_path):
        pd.DataFrame(columns=["Date", "Time", "Plant", "Disease", "CNN_Confidence", "Severity"]).to_csv(csv_path, index=False)
    try:
        history_df = pd.read_csv(csv_path)
    except Exception:
        history_df = pd.DataFrame(columns=["Date", "Time", "Plant", "Disease", "CNN_Confidence", "Severity"])
    
    if history_df.empty:
        history_df = pd.DataFrame(columns=["Date", "Time", "Plant", "Disease", "CNN_Confidence", "Severity"])
        return history_df

    # Standardize column names if needed
    rename_cols = {}
    if "Confidence" in history_df.columns and "CNN_Confidence" not in history_df.columns:
        rename_cols["Confidence"] = "CNN_Confidence"
    if rename_cols:
        history_df.rename(columns=rename_cols, inplace=True)
        
    # Ensure all required columns exist
    for col in ["Date", "Plant", "Disease", "CNN_Confidence", "Severity"]:
        if col not in history_df.columns:
            history_df[col] = ""

    # Migrate older Date formats to separate Date and Time
    if "Time" not in history_df.columns:
        times = []
        dates = []
        for _, row in history_df.iterrows():
            dt_str = str(row.get("Date", ""))
            if " " in dt_str:
                try:
                    dt = datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M")
                    dates.append(dt.strftime("%d-%m-%Y"))
                    times.append(dt.strftime("%H:%M:%S"))
                except ValueError:
                    try:
                        dt = datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")
                        dates.append(dt.strftime("%d-%m-%Y"))
                        times.append(dt.strftime("%H:%M:%S"))
                    except ValueError:
                        try:
                            parts = dt_str.split(' ')
                            dt_val = datetime.strptime(parts[0], "%Y-%m-%d")
                            dates.append(dt_val.strftime("%d-%m-%Y"))
                            times.append(parts[1] if len(parts) > 1 else "00:00:00")
                        except ValueError:
                            dates.append(dt_str)
                            times.append("00:00:00")
            else:
                try:
                    dt = datetime.strptime(dt_str.strip(), "%Y-%m-%d")
                    dates.append(dt.strftime("%d-%m-%Y"))
                    times.append("00:00:00")
                except ValueError:
                    try:
                        # Check if it is already in DD-MM-YYYY format
                        dt = datetime.strptime(dt_str.strip(), "%d-%m-%Y")
                        dates.append(dt.strftime("%d-%m-%Y"))
                        times.append("00:00:00")
                    except ValueError:
                        dates.append(dt_str)
                        times.append("00:00:00")
        
        history_df["Date"] = dates
        history_df.insert(1, "Time", times)
        history_df.to_csv(csv_path, index=False)
        
    cols_order = ["Date", "Time", "Plant", "Disease", "CNN_Confidence", "Severity"]
    history_df = history_df[[c for c in cols_order if c in history_df.columns]]
    return history_df

def load_users() -> dict:
    os.makedirs("history", exist_ok=True)
    users_file = "history/users.json"
    if not os.path.exists(users_file):
        with open(users_file, "w") as f:
            json.dump({}, f)
    try:
        with open(users_file, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict):
    os.makedirs("history", exist_ok=True)
    users_file = "history/users.json"
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

def render_auth_page():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px; margin-top: 32px;" class="cs-fadein">
        <h1 style="font-family:'Clash Display',sans-serif; font-size:clamp(32px, 5vw, 48px); color:var(--cs-white); margin-bottom: 8px;">🌿 CropSense AI</h1>
        <p style="color:var(--cs-mint); font-size:16px; font-family:'Satoshi',sans-serif; max-width:550px; margin: 0 auto;">Intelligent Crop Disease Detection & Farm Management Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown('<div class="cs-card cs-fadein">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab_login:
            st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
            mobile = st.text_input("Mobile Number", placeholder="e.g. 9876543210", key="login_mobile_input")
            
            if not st.session_state.login_otp_sent:
                if st.button("Request OTP Code", use_container_width=True, key="req_otp_btn"):
                    if not mobile.strip():
                        st.error("Please enter a valid mobile number")
                    else:
                        users = load_users()
                        if mobile.strip() in users:
                            import random
                            otp = f"{random.randint(1000, 9999)}"
                            st.session_state.login_otp = otp
                            st.session_state.login_otp_sent = True
                            st.session_state.temp_mobile = mobile.strip()
                            st.rerun()
                        else:
                            st.error("Mobile number is not registered. Please sign up first.")
            else:
                st.info(f"🔑 Demo OTP sent to {st.session_state.temp_mobile}: **{st.session_state.login_otp}**")
                otp_input = st.text_input("Enter 4-digit OTP", placeholder="Enter OTP code", key="login_otp_input")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Verify & Login", use_container_width=True, key="verify_btn"):
                        if otp_input.strip() == st.session_state.login_otp:
                            users = load_users()
                            user_data = users[st.session_state.temp_mobile]
                            
                            st.session_state.logged_in = True
                            st.session_state.user_name = user_data["name"]
                            st.session_state.user_mobile = user_data["mobile"]
                            st.session_state.user_email = user_data["email"]
                            
                            # Load user-specific history
                            csv_path = f"history/predictions_{st.session_state.user_mobile}.csv"
                            st.session_state.history = load_and_migrate_history(csv_path).to_dict(orient="records")
                            
                            # Reset OTP state
                            st.session_state.login_otp_sent = False
                            st.session_state.login_otp = ""
                            st.session_state.temp_mobile = ""
                            
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid OTP code. Please try again.")
                with col2:
                    if st.button("Cancel", use_container_width=True, key="cancel_otp_btn"):
                        st.session_state.login_otp_sent = False
                        st.session_state.login_otp = ""
                        st.session_state.temp_mobile = ""
                        st.rerun()
                        
        with tab_signup:
            st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
            name = st.text_input("Full Name", placeholder="e.g. John Doe", key="signup_name")
            signup_mobile = st.text_input("Mobile Number", placeholder="e.g. 9876543210", key="signup_mobile")
            email = st.text_input("Email Address", placeholder="e.g. john@example.com", key="signup_email")
            
            if st.button("Register & Login", use_container_width=True, key="register_btn"):
                if not name.strip() or not signup_mobile.strip() or not email.strip():
                    st.error("Please fill in all registration fields.")
                else:
                    users = load_users()
                    if signup_mobile.strip() in users:
                        st.error("This mobile number is already registered. Please login instead.")
                    else:
                        users[signup_mobile.strip()] = {
                            "name": name.strip(),
                            "mobile": signup_mobile.strip(),
                            "email": email.strip()
                        }
                        save_users(users)
                        
                        # Automatically login the user
                        st.session_state.logged_in = True
                        st.session_state.user_name = name.strip()
                        st.session_state.user_mobile = signup_mobile.strip()
                        st.session_state.user_email = email.strip()
                        
                        # Load user-specific history
                        csv_path = f"history/predictions_{st.session_state.user_mobile}.csv"
                        st.session_state.history = load_and_migrate_history(csv_path).to_dict(orient="records")
                        
                        st.success("Account created and logged in successfully!")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# FIX 1 — translate_text defined FIRST (before any @st.cache_data function that calls it)
# ═══════════════════════════════════════════════════
def translate_text(text: str, code: str) -> str:
    """Translate text to target language. Returns original on failure."""
    if code == "en" or not text:
        return text
    try:
        return GoogleTranslator(source='auto', target=code).translate(str(text))
    except Exception:
        return text

# ═══════════════════════════════════════════════════
# FIX 2 — Gemini client cached with @st.cache_resource (not called at module level)
# ═══════════════════════════════════════════════════
@st.cache_resource
def get_gemini_client():
    """Initialize Gemini client once per session, with graceful error."""
    key = ""
    try:
        if hasattr(st, "secrets"):
            key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    if not key:
        key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None, "GEMINI_API_KEY not found. Add it to .streamlit/secrets.toml"
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model, None
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════
# FIX 8 — gemini_analyze_leaf cached WITHOUT translation (avoids baking language into cache)
#         Translation applied at render time so language switching doesn't waste API quota
# ═══════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def gemini_analyze_leaf(image_bytes: bytes, cnn_disease: str, cnn_confidence: float) -> dict:
    """
    Universal leaf analysis via Gemini Vision.
    Returns raw English dict — translation happens at render time.
    Identifies any plant species and any disease beyond CNN's 38 PlantVillage classes.
    """
    gemini_model, err = get_gemini_client()
    if gemini_model is None:
        return {"error": err, "source": "gemini_unavailable"}

    img = Image.open(io.BytesIO(image_bytes))

    prompt = f"""You are an expert agricultural pathologist and botanist. Analyze this plant leaf image carefully.

CNN Model prediction: "{cnn_disease}" with {cnn_confidence:.1f}% confidence.

Your tasks:
1. Identify the PLANT TYPE (e.g., Tomato, Apple, Rice, Wheat, Mango, etc.)
2. Identify the DISEASE (or confirm healthy). Use the CNN prediction as a hint but rely on your own vision analysis. You can detect diseases NOT in the CNN model.
3. Provide complete agronomic advice.

Respond ONLY with a valid JSON object — no markdown, no extra text:
{{
  "plant_name": "Common name of the plant",
  "plant_scientific": "Scientific name",
  "disease_name": "Full disease name (or 'Healthy' if no disease)",
  "disease_pathogen": "Causal organism (fungus/bacteria/virus name)",
  "is_healthy": true,
  "severity": "Healthy",
  "confidence_note": "Brief note on how sure you are",
  "symptoms": "2-3 sentences describing visible symptoms in this image",
  "description": "Detailed disease description (3-4 sentences)",
  "treatment": "Step-by-step treatment plan",
  "prevention": "3-4 prevention measures",
  "medicine": {{
    "name": "Recommended fungicide/bactericide/pesticide name",
    "type": "Contact/Systemic/Biological",
    "active_ingredient": "Chemical name + concentration",
    "dose": "Amount per litre of water or per hectare",
    "frequency": "How often to apply",
    "method": "Application method",
    "preharvest_interval": "Days before harvest",
    "safety": "Safety precautions",
    "alternatives": ["Alternative 1", "Alternative 2"],
    "caution": "Important warning"
  }},
  "fertilizer": {{
    "name": "Recommended fertilizer name",
    "type": "Organic/Chemical/Bio",
    "npk_n": "Nitrogen value or N/A",
    "npk_p": "Phosphorus value or N/A",
    "npk_k": "Potassium value or N/A",
    "dose": "Application dose",
    "timing": "When to apply",
    "method": "How to apply",
    "benefits": "Why this fertilizer helps",
    "additional_supplement": "Any extra micronutrient or supplement",
    "tips": ["Tip 1", "Tip 2", "Tip 3"]
  }},
  "cnn_agreement": true,
  "cnn_note": "Brief comment on whether CNN result matches your analysis"
}}"""

    try:
        response = gemini_model.generate_content([prompt, img])
        raw = response.text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        data = json.loads(raw)
        data["source"] = "gemini"
        return data
    except json.JSONDecodeError as e:
        raw_preview = locals().get("raw", "")[:300]
        return {"error": f"JSON parse failed: {e}", "raw": raw_preview, "source": "parse_error"}
    except Exception as e:
        return {"error": str(e), "source": "gemini_error"}


def translate_gemini_data(data: dict, lang_code: str) -> dict:
    """
    FIX 8 continued — translate a Gemini result dict at render time.
    Called only when lang_code != 'en' so English users pay zero translation cost.
    """
    if lang_code == "en" or not data or "error" in data:
        return data
    translated = dict(data)
    for field in ["symptoms", "description", "treatment", "prevention", "confidence_note", "cnn_note"]:
        if translated.get(field):
            translated[field] = translate_text(translated[field], lang_code)
    if "medicine" in translated:
        med = dict(translated["medicine"])
        for f in ["dose", "frequency", "method", "safety", "caution", "type"]:
            if med.get(f):
                med[f] = translate_text(med[f], lang_code)
        translated["medicine"] = med
    if "fertilizer" in translated:
        fert = dict(translated["fertilizer"])
        for f in ["dose", "timing", "method", "benefits", "additional_supplement", "type"]:
            if fert.get(f):
                fert[f] = translate_text(fert[f], lang_code)
        translated["fertilizer"] = fert
    return translated


@st.cache_data(ttl=1800, show_spinner=False)
def gemini_chatbot_response(user_message: str, disease_context: str, plant_context: str,
                             confidence: float, severity: str, lang_code: str) -> str:
    """Context-aware farming chatbot powered by Gemini."""
    gemini_model, err = get_gemini_client()
    if gemini_model is None:
        return f"⚠️ Farming assistant unavailable: {err}"
    system_ctx = (
        f"You are an expert agricultural assistant in CropSense AI.\n"
        f"Current diagnosis context:\n"
        f"- Plant: {plant_context or 'Unknown'}\n"
        f"- Disease: {disease_context or 'Not yet diagnosed'}\n"
        f"- Confidence: {confidence:.0f}% | Severity: {severity}\n"
        f"Respond in language code '{lang_code}'. Be concise, practical, and farmer-friendly. "
        f"Do not use markdown headers. Max 150 words."
    )
    try:
        response = gemini_model.generate_content(f"{system_ctx}\n\nFarmer question: {user_message}")
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Assistant error: {str(e)[:100]}"


# ═══════════════════════════════════════════════════
# LANGUAGE MAP
# ═══════════════════════════════════════════════════
WORLD_LANGUAGES = {
    "🇬🇧 English": "en", "🇮🇳 Hindi": "hi", "🇧🇩 Bengali": "bn",
    "🇪🇸 Spanish": "es", "🇫🇷 French": "fr", "🇩🇪 German": "de",
    "🇮🇹 Italian": "it", "🇵🇹 Portuguese": "pt", "🇷🇺 Russian": "ru",
    "🇨🇳 Chinese (Simplified)": "zh-CN", "🇯🇵 Japanese": "ja",
    "🇰🇷 Korean": "ko", "🇸🇦 Arabic": "ar", "🇹🇷 Turkish": "tr",
    "🇳🇱 Dutch": "nl", "🇸🇪 Swedish": "sv", "🇳🇴 Norwegian": "no",
    "🇩🇰 Danish": "da", "🇵🇱 Polish": "pl", "🇺🇦 Ukrainian": "uk",
    "🇬🇷 Greek": "el", "🇹🇭 Thai": "th", "🇻🇳 Vietnamese": "vi",
    "🇮🇩 Indonesian": "id", "🇲🇾 Malay": "ms", "🇵🇭 Filipino": "tl",
    "🇮🇷 Persian": "fa", "🇵🇰 Urdu": "ur", "🇮🇳 Tamil": "ta",
    "🇮🇳 Telugu": "te", "🇮🇳 Kannada": "kn", "🇮🇳 Malayalam": "ml",
    "🇮🇳 Gujarati": "gu", "🇮🇳 Marathi": "mr", "🇮🇳 Punjabi": "pa",
    "🇷🇴 Romanian": "ro", "🇭🇺 Hungarian": "hu", "🇨🇿 Czech": "cs",
    "🇳🇵 Nepali": "ne", "🇱🇰 Sinhala": "si", "🇰🇪 Swahili": "sw",
}

def get_severity(confidence: float, is_healthy: bool):
    if is_healthy:
        return "Excellent", "#10b981", "🟢"
    if confidence >= 90:
        return "Severe", "#ef4444", "🔴"
    elif confidence >= 75:
        return "Moderate", "#f97316", "🟠"
    else:
        return "Mild", "#eab308", "🟡"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Satoshi:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Adaptive Layout Show/Hide Breakpoints */
.device-mobile, .device-tablet, .device-laptop, .device-desktop {
  display: none !important;
}
@media (max-width: 600px) {
  .device-mobile { display: block !important; }
}
@media (min-width: 601px) and (max-width: 960px) {
  .device-tablet { display: block !important; }
}
@media (min-width: 961px) and (max-width: 1280px) {
  .device-laptop { display: block !important; }
}
@media (min-width: 1281px) {
  .device-desktop { display: block !important; }
}
:root{--cs-void:#0c130c;--cs-deep:#111b11;--cs-forest:#0f3a1f;--cs-emerald:#065f46;--cs-jade:#10b981;--cs-mint:#34d399;--cs-lime:#a3e635;--cs-amber:#fbbf24;--cs-coral:#f97316;--cs-sky:#06b6d4;--cs-white:#f0fdf4;--cs-muted:rgba(240,253,244,0.55);--cs-border:rgba(52,211,153,0.15);--cs-glass:rgba(255,255,255,0.04);--radius-sm:10px;--radius-md:16px;--radius-lg:24px;--radius-xl:32px;--shadow-glow:0 0 40px rgba(16,185,129,0.15);--transition:all 0.3s cubic-bezier(0.4,0,0.2,1);}
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Satoshi','DM Sans',sans-serif;background:var(--cs-void)!important;color:var(--cs-white);}
.main{background:var(--cs-void)!important;}
.main .block-container{background:var(--cs-void)!important;padding-top:0!important;padding-bottom:3rem;max-width:1280px;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--cs-deep);}::-webkit-scrollbar-thumb{background:var(--cs-emerald);border-radius:99px;}
section[data-testid="stSidebar"]{background:var(--cs-void)!important;border-right:1px solid var(--cs-border)!important;}
section[data-testid="stSidebar"]>div{background:var(--cs-void)!important;padding-top:0!important;}
.stSelectbox>div>div,.stRadio>div,.stFileUploader>div{background:var(--cs-deep)!important;border-color:var(--cs-border)!important;color:var(--cs-white)!important;border-radius:var(--radius-md)!important;}
.stSelectbox label,.stRadio label,.stFileUploader label,.stCameraInput label{color:var(--cs-muted)!important;font-size:12px!important;font-weight:500!important;text-transform:uppercase!important;letter-spacing:0.08em!important;}
.stSelectbox [data-baseweb="select"]{background:rgba(16,185,129,0.08)!important;border:1px solid var(--cs-border)!important;border-radius:var(--radius-sm)!important;}
.stFileUploader>div{background:rgba(16,185,129,0.04)!important;border:1.5px dashed rgba(52,211,153,0.3)!important;border-radius:var(--radius-md)!important;}
.stButton>button{font-family:'Satoshi',sans-serif!important;background:linear-gradient(135deg,var(--cs-emerald),var(--cs-forest))!important;color:var(--cs-white)!important;border:1px solid rgba(52,211,153,0.3)!important;border-radius:var(--radius-md)!important;padding:12px 28px!important;font-size:14px!important;font-weight:600!important;width:100%!important;transition:var(--transition)!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(16,185,129,0.35)!important;}
audio{width:100%!important;border-radius:var(--radius-md)!important;filter:invert(1) hue-rotate(100deg) brightness(0.8);}
h1,h2,h3,h4{color:var(--cs-white)!important;font-family:'Clash Display',sans-serif!important;}
.stDataFrame{border-radius:var(--radius-md)!important;overflow:hidden!important;}
.stTextInput>div>div>input{background:rgba(16,185,129,0.06)!important;border:1px solid var(--cs-border)!important;border-radius:var(--radius-sm)!important;color:var(--cs-white)!important;}
.stTextInput>div>div>input:focus{border-color:var(--cs-jade)!important;box-shadow:0 0 0 2px rgba(16,185,129,0.2)!important;}
.cs-hero{position:relative;min-height:300px;display:flex;align-items:center;padding:48px 48px 44px;margin:0 0 28px;overflow:hidden;border-radius:0 0 var(--radius-xl) var(--radius-xl);background:linear-gradient(135deg,#020d08 0%,#051a0e 40%,#071f10 100%);}
.cs-hero-bg{position:absolute;inset:0;pointer-events:none;overflow:hidden;}
.cs-hero-orb1{position:absolute;width:500px;height:500px;top:-200px;right:-100px;border-radius:50%;background:radial-gradient(circle,rgba(16,185,129,0.12) 0%,transparent 70%);animation:orbFloat1 8s ease-in-out infinite;}
.cs-hero-orb2{position:absolute;width:300px;height:300px;bottom:-150px;left:10%;border-radius:50%;background:radial-gradient(circle,rgba(163,230,53,0.07) 0%,transparent 70%);animation:orbFloat2 10s ease-in-out infinite;}
.cs-hero-grid{position:absolute;inset:0;background-image:linear-gradient(rgba(52,211,153,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(52,211,153,0.04) 1px,transparent 1px);background-size:60px 60px;mask-image:radial-gradient(ellipse 70% 60% at 50% 50%,black,transparent);}
@keyframes orbFloat1{0%,100%{transform:translate(0,0) scale(1);}50%{transform:translate(-30px,20px) scale(1.05);}}
@keyframes orbFloat2{0%,100%{transform:translate(0,0);}50%{transform:translate(20px,-30px);}}
.cs-hero-content{position:relative;z-index:2;flex:1;}
.cs-hero-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(52,211,153,0.1);border:1px solid rgba(52,211,153,0.25);border-radius:999px;padding:6px 16px;font-size:11px;font-weight:600;color:var(--cs-mint);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:18px;backdrop-filter:blur(8px);}
.cs-hero-badge-dot{width:7px;height:7px;border-radius:50%;background:var(--cs-jade);box-shadow:0 0 8px var(--cs-jade);animation:pulseDot 2s ease-in-out infinite;}
@keyframes pulseDot{0%,100%{opacity:1;}50%{opacity:0.4;}}
.cs-hero-title{font-family:'Clash Display',sans-serif;font-size:clamp(28px,4vw,46px);font-weight:700;color:var(--cs-white);line-height:1.1;margin:0 0 14px;letter-spacing:-1px;}
.cs-hero-title .accent{color:var(--cs-mint);}.cs-hero-title .accent2{color:var(--cs-lime);}
.cs-hero-sub{font-size:14px;color:var(--cs-muted);line-height:1.7;max-width:480px;margin:0;}
.cs-hero-stats{position:absolute;right:48px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:12px;z-index:2;}
.cs-stat-pill{background:rgba(255,255,255,0.04);border:1px solid rgba(52,211,153,0.18);border-radius:var(--radius-md);padding:12px 18px;text-align:center;backdrop-filter:blur(12px);min-width:90px;transition:var(--transition);}
.cs-stat-val{font-family:'Clash Display',sans-serif;font-size:22px;font-weight:700;color:var(--cs-mint);display:block;line-height:1;}
.cs-stat-lab{font-size:10px;color:var(--cs-muted);text-transform:uppercase;letter-spacing:0.1em;display:block;margin-top:3px;}
.sb-brand{padding:24px 20px 18px;border-bottom:1px solid var(--cs-border);margin-bottom:8px;}
.sb-logo{display:flex;align-items:center;gap:12px;margin-bottom:12px;}
.sb-logo-icon{width:40px;height:40px;background:linear-gradient(135deg,var(--cs-jade),var(--cs-forest));border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 4px 16px rgba(16,185,129,0.3);}
.sb-logo-name{font-family:'Clash Display',sans-serif;font-size:17px;font-weight:700;color:var(--cs-white);}
.sb-logo-ver{font-size:10px;color:var(--cs-muted);background:rgba(52,211,153,0.12);border:1px solid rgba(52,211,153,0.2);border-radius:999px;padding:2px 8px;display:inline-block;margin-top:2px;}
.sb-status{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--cs-mint);font-weight:500;background:rgba(16,185,129,0.08);border:1px solid rgba(52,211,153,0.2);border-radius:999px;padding:5px 14px;}
.gemini-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(66,133,244,0.12);border:1px solid rgba(66,133,244,0.3);border-radius:999px;padding:4px 12px;font-size:11px;font-weight:600;color:#93c5fd;margin-bottom:12px;}
.gemini-plant-card{background:linear-gradient(135deg,rgba(66,133,244,0.08),rgba(139,92,246,0.08));border:1px solid rgba(66,133,244,0.2);border-radius:var(--radius-lg);padding:20px 24px;margin-bottom:16px;}
.gemini-plant-name{font-family:'Clash Display',sans-serif;font-size:22px;font-weight:700;color:var(--cs-white);margin:0 0 2px;}
.gemini-plant-sci{font-size:12px;color:rgba(147,197,253,0.8);font-style:italic;margin:0 0 10px;}
.gemini-agree{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;padding:3px 10px;border-radius:999px;}
.gemini-agree.yes{background:rgba(16,185,129,0.12);border:1px solid rgba(52,211,153,0.25);color:var(--cs-mint);}
.gemini-agree.no{background:rgba(249,115,22,0.12);border:1px solid rgba(249,115,22,0.25);color:#fb923c;}
.chat-wrap{background:rgba(255,255,255,0.025);border:1px solid var(--cs-border);border-radius:var(--radius-lg);padding:20px;margin-top:8px;max-height:420px;overflow-y:auto;}
.chat-msg-user{display:flex;justify-content:flex-end;margin-bottom:10px;}
.chat-msg-ai{display:flex;justify-content:flex-start;margin-bottom:10px;}
.chat-bubble-user{background:linear-gradient(135deg,var(--cs-emerald),var(--cs-forest));color:var(--cs-white);border-radius:16px 16px 4px 16px;padding:10px 14px;font-size:13px;max-width:80%;line-height:1.5;}
.chat-bubble-ai{background:rgba(255,255,255,0.05);border:1px solid var(--cs-border);color:var(--cs-white);border-radius:16px 16px 16px 4px;padding:10px 14px;font-size:13px;max-width:85%;line-height:1.6;}
.chat-bubble-ai .ai-label{font-size:10px;font-weight:700;color:var(--cs-mint);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;display:block;}
.cs-section{display:flex;align-items:center;gap:12px;margin:24px 0 16px;}
.cs-section-icon{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;}
.cs-section-icon.green{background:rgba(16,185,129,0.15);}.cs-section-icon.amber{background:rgba(245,158,11,0.15);}.cs-section-icon.sky{background:rgba(6,182,212,0.15);}.cs-section-icon.rose{background:rgba(244,63,94,0.15);}.cs-section-icon.violet{background:rgba(139,92,246,0.15);}.cs-section-icon.blue{background:rgba(66,133,244,0.15);}
.cs-section-title{font-family:'Clash Display',sans-serif;font-size:15px;font-weight:600;color:var(--cs-white);margin:0;}
.cs-section-sub{font-size:11px;color:var(--cs-muted);margin:1px 0 0;}
.cs-card{background:var(--cs-glass);border:1px solid var(--cs-border);border-radius:var(--radius-lg);padding:22px;transition:var(--transition);}
.cs-result{background:linear-gradient(135deg,rgba(6,31,16,0.9),rgba(11,23,14,0.95));border:1px solid rgba(52,211,153,0.2);border-radius:var(--radius-lg);padding:24px;position:relative;overflow:hidden;}
.cs-result.disease{background:linear-gradient(135deg,rgba(31,10,4,0.9),rgba(24,8,3,0.95));border-color:rgba(249,115,22,0.25);}
.cs-badge{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:5px 14px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;}
.cs-badge.healthy{background:rgba(16,185,129,0.15);border:1px solid rgba(52,211,153,0.35);color:var(--cs-mint);}
.cs-badge.disease-b{background:rgba(249,115,22,0.12);border:1px solid rgba(249,115,22,0.3);color:#fb923c;}
.cs-badge-dot{width:6px;height:6px;border-radius:50%;display:inline-block;}
.conf-wrap{margin:18px 0 0;}.conf-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}
.conf-label{font-size:12px;color:var(--cs-muted);font-weight:500;}.conf-val{font-family:'Clash Display',sans-serif;font-size:20px;font-weight:700;color:var(--cs-mint);}
.conf-track{height:8px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden;}
.conf-fill{height:100%;border-radius:999px;position:relative;overflow:hidden;}
.conf-fill::after{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent);animation:shimmer 2.5s infinite;}
@keyframes shimmer{to{left:200%;}}
.severity-badge{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;padding:5px 14px;border-radius:999px;margin-top:8px;}
.cs-info{background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-md);padding:16px 18px;height:100%;position:relative;overflow:hidden;}
.cs-info-accent{position:absolute;top:0;left:0;width:3px;height:100%;border-radius:2px 0 0 2px;}
.cs-info-tag{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;padding:3px 10px;border-radius:999px;display:inline-block;margin-bottom:8px;}
.tag-desc{background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.2);}
.tag-treat{background:rgba(16,185,129,0.12);color:var(--cs-mint);border:1px solid rgba(52,211,153,0.2);}
.tag-med{background:rgba(249,115,22,0.1);color:#fb923c;border:1px solid rgba(249,115,22,0.2);}
.tag-fert{background:rgba(245,158,11,0.1);color:var(--cs-amber);border:1px solid rgba(245,158,11,0.2);}
.cs-info-body{font-size:13px;color:rgba(240,253,244,0.75);line-height:1.7;margin:0;}
.cs-info-big{font-family:'Clash Display',sans-serif;font-size:17px;font-weight:600;color:var(--cs-white);margin:0;}
.detail-card{background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-lg);padding:22px 24px;transition:var(--transition);}
.detail-card-header{display:flex;align-items:center;gap:12px;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.07);}
.detail-card-icon{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}
.detail-card-title{font-family:'Clash Display',sans-serif;font-size:17px;font-weight:700;color:var(--cs-white);margin:0;}
.detail-card-subtitle{font-size:11px;color:var(--cs-muted);margin-top:2px;}
.detail-row{display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;}
.detail-row-icon{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;margin-top:1px;}
.detail-row-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:2px;}
.detail-row-val{font-size:13px;color:rgba(240,253,244,0.8);line-height:1.6;}
.detail-chip{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;margin:2px;}
.chip-warning{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.25);color:#fca5a5;}
.chip-info{background:rgba(6,182,212,0.12);border:1px solid rgba(6,182,212,0.25);color:#67e8f9;}
.detail-divider{height:1px;background:rgba(255,255,255,0.06);margin:12px 0;}
.npk-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px;}
.npk-box{text-align:center;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px 6px;}
.npk-val{font-family:'Clash Display',sans-serif;font-size:18px;font-weight:700;display:block;line-height:1;}
.npk-lab{font-size:9px;color:var(--cs-muted);text-transform:uppercase;letter-spacing:0.06em;display:block;margin-top:3px;}
.apply-step{display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;}
.apply-num{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;margin-top:1px;}
.apply-text{font-size:12px;color:rgba(240,253,244,0.75);line-height:1.6;}
.cs-error{display:flex;gap:14px;background:rgba(244,63,94,0.07);border:1px solid rgba(244,63,94,0.2);border-radius:var(--radius-md);padding:20px 22px;animation:fadeIn 0.4s ease;}
.cs-warn{background:rgba(245,158,11,0.07);border-color:rgba(245,158,11,0.2);}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
.cs-error-icon{font-size:24px;flex-shrink:0;}.cs-error-title{font-size:14px;font-weight:600;color:#fb7185;margin-bottom:5px;font-family:'Clash Display',sans-serif;}
.cs-warn .cs-error-title{color:var(--cs-amber);}.cs-error-body{font-size:12px;color:rgba(251,113,133,0.8);line-height:1.6;}.cs-warn .cs-error-body{color:rgba(251,191,36,0.75);}
.cs-tech-pill{display:inline-flex;align-items:center;gap:6px;background:rgba(52,211,153,0.07);border:1px solid rgba(52,211,153,0.18);color:rgba(240,253,244,0.75);border-radius:999px;padding:5px 14px;font-size:12px;font-weight:500;margin:4px;}
.cs-feat{background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:var(--radius-md);padding:16px;cursor:default;transition:var(--transition);}
.cs-feat:hover{background:rgba(52,211,153,0.07);border-color:rgba(52,211,153,0.2);transform:translateY(-3px);}
.cs-feat-emoji{font-size:22px;margin-bottom:6px;display:block;}.cs-feat-title{font-size:12px;font-weight:600;color:var(--cs-white);margin-bottom:2px;font-family:'Clash Display',sans-serif;}.cs-feat-desc{font-size:11px;color:var(--cs-muted);line-height:1.5;}
.cs-metric{background:rgba(255,255,255,0.03);border:1px solid var(--cs-border);border-radius:var(--radius-md);padding:16px 18px;text-align:center;transition:var(--transition);}
.cs-metric:hover{border-color:var(--cs-jade);background:rgba(16,185,129,0.06);}
.cs-metric-val{font-family:'Clash Display',sans-serif;font-size:28px;font-weight:700;color:var(--cs-mint);display:block;}
.cs-metric-lab{font-size:11px;color:var(--cs-muted);text-transform:uppercase;letter-spacing:0.08em;display:block;margin-top:3px;}
.cs-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:260px;background:rgba(255,255,255,0.02);border:1.5px dashed rgba(255,255,255,0.1);border-radius:var(--radius-lg);text-align:center;padding:36px;}
.cs-empty-icon{font-size:48px;opacity:0.2;margin-bottom:14px;}.cs-empty-title{font-size:14px;font-weight:600;color:rgba(240,253,244,0.3);margin-bottom:5px;}.cs-empty-sub{font-size:11px;color:rgba(240,253,244,0.15);}
.cs-voice-wrap{background:rgba(6,182,212,0.06);border:1px solid rgba(6,182,212,0.15);border-radius:var(--radius-md);padding:18px 22px;display:flex;align-items:center;gap:14px;}
.cs-voice-icon{width:42px;height:42px;background:rgba(6,182,212,0.15);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;}
.cs-voice-label{font-size:13px;font-weight:600;color:#22d3ee;font-family:'Clash Display',sans-serif;margin-bottom:1px;}.cs-voice-sub{font-size:11px;color:var(--cs-muted);}
.cs-about-hero{background:linear-gradient(135deg,rgba(6,95,70,0.25),rgba(16,185,129,0.08));border:1px solid rgba(52,211,153,0.15);border-radius:var(--radius-xl);padding:32px 36px;margin-bottom:22px;position:relative;overflow:hidden;}
.cs-divider{height:1px;background:linear-gradient(90deg,transparent,var(--cs-border),transparent);margin:8px 0;}
.cs-footer{text-align:center;padding:36px 0 14px;border-top:1px solid rgba(255,255,255,0.06);margin-top:44px;}
.cs-footer-logo{font-family:'Clash Display',sans-serif;font-size:14px;font-weight:700;color:rgba(240,253,244,0.3);}
.cs-footer-sub{font-size:11px;color:rgba(240,253,244,0.15);margin-top:5px;}
.quality-bar{height:6px;border-radius:999px;background:rgba(255,255,255,0.06);overflow:hidden;margin:6px 0 2px;}
.quality-fill{height:100%;border-radius:999px;}
.cs-alert-banner{display:flex;align-items:center;gap:10px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:var(--radius-md);padding:12px 18px;margin:10px 0;font-size:12px;color:var(--cs-amber);}
.top3-row{display:flex;align-items:center;gap:10px;margin-bottom:10px;padding:10px 14px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:10px;}
.top3-rank{font-family:'Clash Display',sans-serif;font-size:14px;font-weight:700;min-width:22px;}
.top3-name{flex:1;font-size:12px;color:var(--cs-white);font-weight:500;}
.top3-pct{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--cs-mint);font-weight:600;min-width:48px;text-align:right;}
.top3-bar-wrap{width:80px;height:5px;background:rgba(255,255,255,0.08);border-radius:99px;overflow:hidden;}
.top3-bar{height:100%;border-radius:99px;}
.cs-fadein{animation:fadeIn 0.6s ease both;}.symptoms-box{background:rgba(255,255,255,0.03);border-left:3px solid var(--cs-sky);border-radius:0 var(--radius-sm) var(--radius-sm) 0;padding:12px 16px;font-size:13px;color:var(--cs-muted);line-height:1.7;margin:10px 0;}
.chip-btn button{background:rgba(16,185,129,0.08)!important;border:1px solid rgba(52,211,153,0.2)!important;color:rgba(240,253,244,0.7)!important;border-radius:999px!important;padding:4px 12px!important;font-size:11px!important;width:auto!important;}
/* Mobile Portrait & Landscape (up to 768px) */
@media(max-width:768px){
  .cs-hero{padding:24px 16px;min-height:auto;border-radius:0 0 var(--radius-md) var(--radius-md);}
  .cs-hero-bg{display:none!important;} /* Hide heavy floating orbs and grids on mobile for clarity and performance */
  .cs-hero-title{font-size:24px;text-align:center;}
  .cs-hero-sub{text-align:center;font-size:12px;}
  .cs-hero-badge{margin:0 auto 14px;display:flex;justify-content:center;}
  .cs-hero-stats{position:static;flex-direction:row;transform:none;margin-top:20px;flex-wrap:wrap;gap:6px;justify-content:center;}
  .cs-stat-pill{padding:8px 12px;min-width:75px;}
  .cs-stat-val{font-size:18px;}
  .cs-about-hero{padding:20px 16px;border-radius:var(--radius-md);}
  .main .block-container{padding:0 0.75rem 2rem!important;}
  .cs-card, .cs-result, .detail-card{padding:16px;border-radius:var(--radius-md);}
  .cs-info{margin-bottom:10px;padding:12px 14px;}
  .cs-info-big{font-size:15px;}
  .cs-info-body{font-size:12px;line-height:1.6;}
  .detail-card-header{padding-bottom:10px;margin-bottom:12px;}
  .detail-card-icon{width:36px;height:36px;font-size:18px;border-radius:8px;}
  .detail-card-title{font-size:15px;}
  .npk-val{font-size:15px;}
  .npk-box{padding:6px 4px;}
  .stButton>button, .chip-btn button{
    min-height: 48px!important; /* Standard touch target height for mobile */
    font-size: 14px!important;
    display: flex!important;
    align-items: center!important;
    justify-content: center!important;
  }
}

/* Tablet Layouts (768px to 1024px) */
@media(min-width:769px) and (max-width:1024px){
  .cs-hero{padding:36px 36px 32px;}
  .cs-hero-title{font-size:32px;}
  .cs-hero-stats{right:36px;}
  .main .block-container{padding:0 1.5rem 3rem!important;}
  .cs-card, .cs-result, .detail-card{padding:20px;}
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════
# Desktop Hero Banner (Large Screens)
st.markdown("""
<div class="cs-hero cs-fadein device-desktop">
  <div class="cs-hero-bg">
    <div class="cs-hero-grid"></div>
    <div class="cs-hero-orb1"></div>
    <div class="cs-hero-orb2"></div>
  </div>
  <div class="cs-hero-content">
    <div class="cs-hero-badge"><span class="cs-hero-badge-dot"></span>AI System Active · Desktop Mode</div>
    <h1 class="cs-hero-title">Detect disease.<br><span class="accent">Save your crop.</span><br><span class="accent2">Any plant. Any disease.</span></h1>
    <p class="cs-hero-sub">Upload any leaf for instant AI-powered diagnosis. CNN for known diseases, Gemini Vision for any plant — with medicine, fertilizer, voice, PDF, and multilingual chat.</p>
  </div>
  <div class="cs-hero-stats">
    <div class="cs-stat-pill"><span class="cs-stat-val">Any</span><span class="cs-stat-lab">Plant</span></div>
    <div class="cs-stat-pill"><span class="cs-stat-val">∞</span><span class="cs-stat-lab">Diseases</span></div>
    <div class="cs-stat-pill"><span class="cs-stat-val">70+</span><span class="cs-stat-lab">Languages</span></div>
    <div class="cs-stat-pill"><span class="cs-stat-val">&lt;5s</span><span class="cs-stat-lab">Analysis</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# Laptop Hero Banner (Medium-Large Screens)
st.markdown("""
<div class="cs-hero cs-fadein device-laptop" style="padding: 40px; background: linear-gradient(135deg, #020d08 0%, #051a0e 100%);">
  <div class="cs-hero-bg">
    <div class="cs-hero-grid"></div>
  </div>
  <div class="cs-hero-content">
    <div class="cs-hero-badge" style="background: rgba(52,211,153,0.08);"><span class="cs-hero-badge-dot"></span>AI System Active · Laptop Mode</div>
    <h1 class="cs-hero-title" style="font-size: 38px;">Detect disease.<br><span class="accent">Save your crop.</span></h1>
    <p class="cs-hero-sub" style="font-size: 13px; max-width: 440px;">Upload any leaf for instant AI-powered diagnosis. CNN for known diseases, Gemini Vision for any plant.</p>
  </div>
  <div class="cs-hero-stats" style="right: 40px;">
    <div class="cs-stat-pill"><span class="cs-stat-val">Any</span><span class="cs-stat-lab">Plant</span></div>
    <div class="cs-stat-pill"><span class="cs-stat-val">∞</span><span class="cs-stat-lab">Diseases</span></div>
    <div class="cs-stat-pill"><span class="cs-stat-val">70+</span><span class="cs-stat-lab">Languages</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# Tablet Hero Banner (Medium Screens)
st.markdown("""
<div class="cs-hero cs-fadein device-tablet" style="padding: 32px; background: #051a0e; min-height: auto;">
  <div class="cs-hero-content">
    <div class="cs-hero-badge"><span class="cs-hero-badge-dot"></span>AI System Active · Tablet Mode</div>
    <h1 class="cs-hero-title" style="font-size: 32px; margin-bottom: 8px;">Detect disease. Save your crop.</h1>
    <p class="cs-hero-sub" style="font-size: 12px; max-width: 100%; margin-bottom: 20px;">AI-powered diagnosis for any plant disease. CNN classification + Gemini diagnostics.</p>
    <div style="display: flex; gap: 10px; margin-top: 14px;">
      <div class="cs-stat-pill" style="flex: 1; min-width: auto;"><span class="cs-stat-val" style="font-size: 18px;">Any</span><span class="cs-stat-lab">Plant</span></div>
      <div class="cs-stat-pill" style="flex: 1; min-width: auto;"><span class="cs-stat-val" style="font-size: 18px;">∞</span><span class="cs-stat-lab">Diseases</span></div>
      <div class="cs-stat-pill" style="flex: 1; min-width: auto;"><span class="cs-stat-val" style="font-size: 18px;">70+</span><span class="cs-stat-lab">Languages</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Mobile Hero Banner (Small Screens)
st.markdown("""
<div class="cs-hero cs-fadein device-mobile" style="padding: 24px 16px; background: #020d08; min-height: auto; border-radius: 0 0 16px 16px; text-align: center;">
  <div class="cs-hero-content">
    <div class="cs-hero-badge" style="margin: 0 auto 12px;"><span class="cs-hero-badge-dot"></span>AI System Active · Mobile</div>
    <h1 class="cs-hero-title" style="font-size: 24px; margin-bottom: 6px; line-height: 1.2;">Detect disease.<br><span class="accent" style="color: var(--cs-mint);">Save your crop.</span></h1>
    <p class="cs-hero-sub" style="font-size: 11px; max-width: 100%; line-height: 1.5; color: var(--cs-muted);">Upload a leaf photo for instant diagnosis & treatment advice.</p>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 16px;">
      <div class="cs-stat-pill" style="padding: 8px; min-width: auto;"><span class="cs-stat-val" style="font-size: 16px;">Any</span><span class="cs-stat-lab" style="font-size: 8px;">Plant</span></div>
      <div class="cs-stat-pill" style="padding: 8px; min-width: auto;"><span class="cs-stat-val" style="font-size: 16px;">∞</span><span class="cs-stat-lab" style="font-size: 8px;">Diseases</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    render_auth_page()
    st.markdown("""<div class="cs-footer cs-fadein" style="margin-top:40px; padding:20px 0; border-top:1px solid var(--cs-border); text-align:center;"><div class="cs-footer-logo" style="font-family:'Clash Display',sans-serif; font-weight:600; font-size:13px; color:var(--cs-mint);">🌿 CropSense AI v3.0 Pro</div><div class="cs-footer-sub" style="font-size:10px; color:var(--cs-muted); margin-top:4px;">TensorFlow · Gemini Vision · OpenCV · Grad-CAM · ReportLab · Streamlit · Empowering farmers worldwide</div></div>""", unsafe_allow_html=True)
    st.stop()

st.sidebar.markdown("""
<div class="sb-brand">
  <div class="sb-logo"><div class="sb-logo-icon">🌿</div><div><div class="sb-logo-name">CropSense AI</div><span class="sb-logo-ver">v3.0 Pro + Gemini</span></div></div>
  <div class="sb-status"><span style="width:7px;height:7px;border-radius:50%;background:#10b981;box-shadow:0 0 6px #10b981;flex-shrink:0;"></span>Gemini Vision Active</div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", ["🏠 Home", "📘 About", "📜 History"], label_visibility="collapsed")
st.sidebar.markdown('<div class="cs-divider" style="margin: 12px 0;"></div>', unsafe_allow_html=True)

# Expander for Translation Output
with st.sidebar.expander("🌍 Translate Language", expanded=True):
    language_label = st.selectbox("Translate Output To", list(WORLD_LANGUAGES.keys()), index=0, label_visibility="collapsed")
    lang_code = WORLD_LANGUAGES[language_label]

# Expander for Configuration Settings
with st.sidebar.expander("⚙️ Advanced Settings", expanded=False):
    conf_threshold = st.slider("Min. CNN Confidence %", min_value=20, max_value=90, value=50, step=5)
    show_heatmap = st.toggle("Show Grad-CAM Heatmap", value=True)
    show_top3    = st.toggle("Show Top-3 CNN Predictions", value=True)
    use_gemini   = st.toggle("Enable Gemini Vision Analysis", value=True)
    show_chatbot = st.toggle("Show AI Farming Chatbot", value=True)

st.sidebar.markdown('<div class="cs-divider" style="margin: 12px 0;"></div>', unsafe_allow_html=True)

_gemini_client, _gemini_err = get_gemini_client()
gemini_ok = _gemini_client is not None
if gemini_ok:
    st.sidebar.markdown('<div class="sb-status" style="margin:4px 0;">🔮 Gemini API connected</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<div style="font-size:11px;color:#fbbf24;padding:6px 10px;background:rgba(251,191,36,0.08);border-radius:8px;margin:4px 0;">⚠️ Gemini: {(_gemini_err or "")[:50]}</div>', unsafe_allow_html=True)

# Logged-in User Information & Logout Button
st.sidebar.markdown('<div class="cs-divider" style="margin: 12px 0;"></div>', unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid var(--cs-border);border-radius:12px;padding:12px;margin-bottom:12px;">
    <div style="font-size:11px;color:var(--cs-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Logged in as</div>
    <div style="font-family:'Clash Display',sans-serif;font-size:14px;font-weight:700;color:var(--cs-white);">{st.session_state.user_name}</div>
    <div style="font-size:11px;color:var(--cs-muted);">{st.session_state.user_email}</div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Sign Out", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_mobile = ""
    st.session_state.user_email = ""
    st.session_state.history = []
    st.rerun()

# ═══════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════
def is_leaf(img: np.ndarray):
    try:
        if len(img.shape) != 3: return False, 0.0
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, np.array([25, 20, 20]), np.array([100, 255, 255]))
        green_ratio = np.sum(mask > 0) / (img.shape[0] * img.shape[1])
        if green_ratio < 0.05: return False, green_ratio
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        if brightness < 20 or brightness > 245: return False, green_ratio
        return True, green_ratio
    except Exception:
        return False, 0.0

def image_quality_score(img_np: np.ndarray) -> int:
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    blur  = min(cv2.Laplacian(gray, cv2.CV_64F).var() / 5, 100)
    brite = max(0, 100 - abs(np.mean(gray) - 128) * 1.2)
    cont  = min(np.std(gray) * 2, 100)
    return int(blur * 0.4 + brite * 0.3 + cont * 0.3)

# FIX 10 — normalise disease name so repeat-alert fires even when Gemini varies capitalisation
def _norm_disease(name: str) -> str:
    return re.sub(r'[\s_]+', ' ', name.strip().lower())

def check_repeat_alert(history_df: pd.DataFrame, disease: str, window: int = 5):
    if len(history_df) < window: return None
    nd = _norm_disease(disease)
    recent = [_norm_disease(d) for d in history_df.tail(window)["Disease"].tolist()]
    count = recent.count(nd)
    if count >= 3:
        return f"'{disease}' detected {count}× in last {window} diagnoses. Consider consulting an agronomist."
    return None



if st.session_state.logged_in and not st.session_state.history:
    csv_path = f"history/predictions_{st.session_state.user_mobile}.csv"
    st.session_state.history = load_and_migrate_history(csv_path).to_dict(orient="records")

def generate_gradcam(model, img_array, class_idx):
    try:
        last_conv = next(
            (l.name for l in reversed(model.layers) if isinstance(l, tf.keras.layers.Conv2D)),
            None
        )
        if last_conv is None: return None
        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[model.get_layer(last_conv).output, model.output]
        )
        with tf.GradientTape() as tape:
            inp = tf.cast(img_array, tf.float32)
            conv_out, preds = grad_model(inp)
            loss = preds[:, class_idx]
        grads = tape.gradient(loss, conv_out)
        pooled = tf.reduce_mean(grads, axis=(0, 1, 2))
        heatmap = tf.squeeze(conv_out[0] @ pooled[..., tf.newaxis]).numpy()
        heatmap = np.maximum(heatmap, 0)
        if heatmap.max() > 0: heatmap /= heatmap.max()
        return heatmap
    except Exception:
        return None

def overlay_heatmap(original_img, heatmap, alpha=0.45):
    try:
        h, w = original_img.shape[:2]
        resized = cv2.resize(heatmap, (w, h))
        colored = (cm.jet(resized)[:, :, :3] * 255).astype(np.uint8)
        return (original_img * (1 - alpha) + colored * alpha).astype(np.uint8)
    except Exception:
        return original_img

def image_to_bytes(pil_image: Image.Image) -> bytes:
    buf = io.BytesIO()
    pil_image.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

# FIX 9 — strip any HTML tags from text before embedding in PDF
def _safe_text(t) -> str:
    if not t: return "N/A"
    return re.sub(r'<[^>]+>', '', str(t)).strip() or "N/A"

# ═══════════════════════════════════════════════════
# LOAD CNN MODEL  (non-fatal — Gemini handles fallback)
# ═══════════════════════════════════════════════════
@st.cache_resource
def load_ai_model():
    try:
        return tf.keras.models.load_model("model/best_plant_disease_model.keras"), None
    except Exception as e:
        return None, str(e)

model, model_err = load_ai_model()
if model is None:
    st.warning(f"⚠️ CNN model unavailable: {model_err}. Gemini Vision will handle all analysis.")

class_names: list[str] = []
try:
    with open("model/class_names.txt", "r") as f:
        class_names = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    if model is not None:
        st.warning("⚠️ class_names.txt not found. CNN class labels disabled.")

# ═══════════════════════════════════════════════════
# RENDER HELPERS
# ═══════════════════════════════════════════════════
def render_gemini_medicine(med: dict):
    alts_html = "".join(
        f'<span class="detail-chip chip-info">💊 {a}</span>' for a in med.get("alternatives", [])
    )
    st.markdown(f"""
    <div class="detail-card cs-fadein">
        <div class="detail-card-header">
            <div class="detail-card-icon" style="background:rgba(249,115,22,0.15);">💊</div>
            <div><div class="detail-card-title">{med.get('name','N/A')}</div>
            <div class="detail-card-subtitle">{med.get('type','')}</div></div>
            <div class="gemini-badge" style="margin-left:auto;margin-bottom:0;">🔮 Gemini</div>
        </div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(6,182,212,0.12);">🧪</div>
            <div><div class="detail-row-label" style="color:#22d3ee;">Active Ingredient</div>
            <div class="detail-row-val">{med.get('active_ingredient','N/A')}</div></div></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(16,185,129,0.12);">⚗️</div>
            <div><div class="detail-row-label" style="color:var(--cs-mint);">Dose</div>
            <div class="detail-row-val">{med.get('dose','N/A')}</div></div></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(163,230,53,0.12);">🔁</div>
            <div><div class="detail-row-label" style="color:var(--cs-lime);">Frequency</div>
            <div class="detail-row-val">{med.get('frequency','N/A')}</div></div></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(245,158,11,0.12);">🚿</div>
            <div><div class="detail-row-label" style="color:var(--cs-amber);">Application Method</div>
            <div class="detail-row-val">{med.get('method','N/A')}</div></div></div>
        <div class="detail-divider"></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(239,68,68,0.12);">⏰</div>
            <div><div class="detail-row-label" style="color:#fca5a5;">Pre-Harvest Interval</div>
            <div class="detail-row-val">{med.get('preharvest_interval','N/A')}</div></div></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(239,68,68,0.12);">🛡️</div>
            <div><div class="detail-row-label" style="color:#fca5a5;">Safety</div>
            <div class="detail-row-val">{med.get('safety','N/A')}</div></div></div>
        <div style="margin-top:4px;"><span class="detail-chip chip-warning">⚠ {med.get('caution','Follow label instructions.')}</span></div>
        {"<div style='margin-top:10px;'><div class='detail-row-label' style='color:var(--cs-muted);margin-bottom:6px;'>Alternatives</div>" + alts_html + "</div>" if alts_html else ""}
    </div>""", unsafe_allow_html=True)


def render_gemini_fertilizer(fert: dict):
    n, p, k = fert.get("npk_n","N/A"), fert.get("npk_p","N/A"), fert.get("npk_k","N/A")
    tips_html = "".join(
        f'<div class="apply-step"><div class="apply-num" style="background:rgba(163,230,53,0.15);color:var(--cs-lime);">{i+1}</div>'
        f'<div class="apply-text">{tip}</div></div>'
        for i, tip in enumerate(fert.get("tips", []))
    )
    st.markdown(f"""
    <div class="detail-card cs-fadein">
        <div class="detail-card-header">
            <div class="detail-card-icon" style="background:rgba(163,230,53,0.15);">🌱</div>
            <div><div class="detail-card-title">{fert.get('name','N/A')}</div>
            <div class="detail-card-subtitle">{fert.get('type','')}</div></div>
            <div class="gemini-badge" style="margin-left:auto;margin-bottom:0;">🔮 Gemini</div>
        </div>
        <div style="margin-bottom:14px;">
            <div class="detail-row-label" style="color:var(--cs-lime);margin-bottom:8px;">NPK Ratio</div>
            <div class="npk-grid">
                <div class="npk-box"><span class="npk-val" style="color:#34d399;">{n}</span><span class="npk-lab">N — Nitrogen</span></div>
                <div class="npk-box"><span class="npk-val" style="color:#fb923c;">{p}</span><span class="npk-lab">P — Phosphorus</span></div>
                <div class="npk-box"><span class="npk-val" style="color:#fbbf24;">{k}</span><span class="npk-lab">K — Potassium</span></div>
            </div>
        </div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(16,185,129,0.12);">⚖️</div>
            <div><div class="detail-row-label" style="color:var(--cs-mint);">Dose</div>
            <div class="detail-row-val">{fert.get('dose','N/A')}</div></div></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(245,158,11,0.12);">📅</div>
            <div><div class="detail-row-label" style="color:var(--cs-amber);">Timing</div>
            <div class="detail-row-val">{fert.get('timing','N/A')}</div></div></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(6,182,212,0.12);">🚜</div>
            <div><div class="detail-row-label" style="color:#22d3ee;">Method</div>
            <div class="detail-row-val">{fert.get('method','N/A')}</div></div></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(163,230,53,0.12);">✅</div>
            <div><div class="detail-row-label" style="color:var(--cs-lime);">Benefits</div>
            <div class="detail-row-val">{fert.get('benefits','N/A')}</div></div></div>
        <div class="detail-divider"></div>
        <div class="detail-row"><div class="detail-row-icon" style="background:rgba(139,92,246,0.12);">➕</div>
            <div><div class="detail-row-label" style="color:#c4b5fd;">Additional Supplement</div>
            <div class="detail-row-val">{fert.get('additional_supplement','N/A')}</div></div></div>
        {"<div style='margin-top:12px;'><div class='detail-row-label' style='color:var(--cs-muted);margin-bottom:8px;'>💡 Pro Tips</div>" + tips_html + "</div>" if tips_html else ""}
    </div>""", unsafe_allow_html=True)


def generate_pdf_report(disease: str, plant_name: str, confidence: float,
                         gemini_data: dict, severity_label: str) -> bytes:
    """FIX 9: _safe_text() strips HTML before writing to PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()
    story = []
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=22,
                              textColor=colors.HexColor('#065f46'), spaceAfter=4, fontName='Helvetica-Bold')
    sub_s   = ParagraphStyle('S', parent=styles['Normal'], fontSize=10,
                              textColor=colors.HexColor('#6b7280'), spaceAfter=16)
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=16,
                              textColor=colors.HexColor('#111827'), spaceBefore=10, spaceAfter=6)
    body_s  = ParagraphStyle('B', parent=styles['Normal'], fontSize=10,
                              textColor=colors.HexColor('#374151'), leading=15, spaceAfter=14)
    lbl_s   = ParagraphStyle('L', parent=styles['Normal'], fontSize=9,
                              textColor=colors.HexColor('#10b981'), fontName='Helvetica-Bold',
                              spaceAfter=4, spaceBefore=12)
    foot_s  = ParagraphStyle('F', parent=styles['Normal'], fontSize=8,
                              textColor=colors.HexColor('#9ca3af'), alignment=TA_CENTER)

    story.append(Paragraph("CropSense AI — Diagnosis Report", title_s))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')} · Powered by Gemini Vision + CNN", sub_s))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=20))
    story.append(Paragraph(f"{_safe_text(plant_name)} — {_safe_text(disease)}", h2_s))

    med  = gemini_data.get("medicine", {})
    fert = gemini_data.get("fertilizer", {})
    tbl_data = [
        ["Plant", _safe_text(plant_name)],
        ["Disease", _safe_text(disease)],
        ["CNN Confidence", f"{confidence:.1f}%"],
        ["Severity", severity_label],
        ["Pathogen", _safe_text(gemini_data.get("disease_pathogen","N/A"))],
        ["Medicine", _safe_text(med.get("name","N/A"))],
        ["Active Ingredient", _safe_text(med.get("active_ingredient","N/A"))],
        ["Dose", _safe_text(med.get("dose","N/A"))],
        ["Pre-Harvest Interval", _safe_text(med.get("preharvest_interval","N/A"))],
        ["Fertilizer", _safe_text(fert.get("name","N/A"))],
        ["NPK", f"N:{fert.get('npk_n','?')} P:{fert.get('npk_p','?')} K:{fert.get('npk_k','?')}"],
        ["Fertilizer Dose", _safe_text(fert.get("dose","N/A"))],
    ]
    tbl = Table(tbl_data, colWidths=[2.2*inch, 4.3*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR',(0,0),(0,-1),colors.HexColor('#065f46')),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#d1fae5')),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.white,colors.HexColor('#f9fafb')]),
        ('PADDING',(0,0),(-1,-1),8),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story += [tbl, Spacer(1, 16)]
    for label, val in [
        ("Symptoms",             gemini_data.get("symptoms")),
        ("Description",          gemini_data.get("description")),
        ("Treatment",            gemini_data.get("treatment")),
        ("Prevention",           gemini_data.get("prevention")),
        ("Safety Precautions",   med.get("safety")),
        ("Medicine Caution",     med.get("caution")),
        ("Fertilizer Benefits",  fert.get("benefits")),
        ("Additional Supplement",fert.get("additional_supplement")),
    ]:
        story.append(Paragraph(label.upper(), lbl_s))
        story.append(Paragraph(_safe_text(val), body_s))
    if fert.get("tips"):
        story.append(Paragraph("FERTILIZER TIPS", lbl_s))
        for i, tip in enumerate(fert["tips"]):
            story.append(Paragraph(f"{i+1}. {_safe_text(tip)}", body_s))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'),
                             spaceBefore=16, spaceAfter=10))
    story.append(Paragraph(
        "CropSense AI v3.0 Pro · Gemini Vision + CNN · For professional confirmation consult a certified agronomist.",
        foot_s))
    doc.build(story)
    buf.seek(0)
    return buf.read()


# ═══════════════════════════════════════════════════
# ABOUT PAGE
# ═══════════════════════════════════════════════════
if page == "📘 About":
    st.markdown("""
    <div class="cs-about-hero cs-fadein">
        <div style="font-family:'Clash Display',sans-serif;font-size:11px;text-transform:uppercase;letter-spacing:0.12em;color:var(--cs-mint);margin-bottom:10px;font-weight:600;">About the Platform</div>
        <h2 style="font-size:clamp(22px,4vw,34px);margin:0 0 12px;color:var(--cs-white);font-family:'Clash Display',sans-serif;font-weight:700;letter-spacing:-0.5px;">Intelligence at the root<br>of every harvest.</h2>
        <p style="font-size:13px;color:var(--cs-muted);line-height:1.8;max-width:600px;margin:0;">CropSense AI v3.0 Pro combines a CNN trained on 87,000+ plant images with Google Gemini Vision — enabling detection of <strong>any</strong> plant disease, not just PlantVillage classes. Gemini identifies the plant species, extends diagnoses beyond the CNN's scope, and powers the context-aware farming chatbot.</p>
    </div>""", unsafe_allow_html=True)
    col_a, col_b = st.columns([1.2,1], gap="large")
    with col_a:
        st.markdown("""<div class="cs-card cs-fadein"><div style="font-size:12px;font-weight:700;color:var(--cs-mint);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">🔬 Technology Stack</div><div><span class="cs-tech-pill">🐍 Python 3.10</span><span class="cs-tech-pill">🧠 TensorFlow 2.x</span><span class="cs-tech-pill">🔮 Gemini 2.5 Flash</span><span class="cs-tech-pill">📷 OpenCV</span><span class="cs-tech-pill">⚡ Streamlit</span><span class="cs-tech-pill">🌐 Deep Translator</span><span class="cs-tech-pill">🔊 gTTS</span><span class="cs-tech-pill">📊 Matplotlib</span><span class="cs-tech-pill">📄 ReportLab</span><span class="cs-tech-pill">🗺️ Grad-CAM</span></div></div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""<div class="cs-card cs-fadein" style="height:100%;"><div style="font-size:12px;font-weight:700;color:var(--cs-mint);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">🤖 AI Architecture</div><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;"><div style="text-align:center;background:rgba(16,185,129,0.08);border:1px solid rgba(52,211,153,0.15);border-radius:12px;padding:14px 8px;"><div style="font-family:'Clash Display',sans-serif;font-size:16px;font-weight:700;color:var(--cs-mint);">CNN</div><div style="font-size:10px;color:var(--cs-muted);text-transform:uppercase;">PlantVillage</div></div><div style="text-align:center;background:rgba(66,133,244,0.08);border:1px solid rgba(66,133,244,0.15);border-radius:12px;padding:14px 8px;"><div style="font-family:'Clash Display',sans-serif;font-size:16px;font-weight:700;color:#93c5fd;">Gemini</div><div style="font-size:10px;color:var(--cs-muted);text-transform:uppercase;">Vision AI</div></div><div style="text-align:center;background:rgba(163,230,53,0.08);border:1px solid rgba(163,230,53,0.15);border-radius:12px;padding:14px 8px;"><div style="font-family:'Clash Display',sans-serif;font-size:16px;font-weight:700;color:var(--cs-lime);">Any</div><div style="font-size:10px;color:var(--cs-muted);text-transform:uppercase;">Disease</div></div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="cs-section cs-fadein" style="margin-top:24px;"><div class="cs-section-icon green">✨</div><div><p class="cs-section-title">Key Features — v3.0 Pro + Gemini</p></div></div>""", unsafe_allow_html=True)
    feats = [("📸","Dual Input","Camera or file upload"),("🔮","Gemini Vision","Any plant identified"),("🛡️","Smart Validation","Rejects non-leaf images"),("🗺️","Grad-CAM","Visual AI heatmap"),("🏆","Top-3 CNN","Alternative diagnoses"),("🌍","70+ Languages","Multilingual output"),("🔊","Voice Output","TTS readout"),("📈","Severity Score","Mild / Moderate / Severe"),("📄","PDF Export","Full printable report"),("💊","Medicine Detail","Dose, safety, PHI"),("🌱","Fertilizer Detail","NPK, timing, tips"),("💬","AI Chatbot","Gemini farming assistant")]
    cols = st.columns(4)
    for i, (ico, title, desc) in enumerate(feats):
        with cols[i % 4]:
            st.markdown(f'<div class="cs-feat cs-fadein" style="margin-bottom:10px;"><span class="cs-feat-emoji">{ico}</span><div class="cs-feat-title">{title}</div><div class="cs-feat-desc">{desc}</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════
if page == "🏠 Home":

    # ── FIX 4 & 6: all cross-column context stored in session_state ──
    for key, default in [
        ("last_image_hash", None), ("gemini_data_raw", {}),
        ("final_disease", ""), ("plant_name", "Unknown Plant"),
        ("plant_sci", ""), ("is_healthy", False), ("severity_label", ""),
        ("severity_color", "#eab308"), ("severity_icon", "🟡"),
        ("cnn_confidence", 0.0), ("predicted_class", 0),
        ("description", ""), ("treatment", ""), ("prevention", ""),
        ("input_tensor", None), ("prediction", None), ("img_np_shape", None),
        ("prediction_time_date", ""), ("prediction_time_time", ""),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("""<div class="cs-section cs-fadein"><div class="cs-section-icon green">📷</div><div><p class="cs-section-title">Upload or Capture Leaf</p><p class="cs-section-sub">Select your preferred leaf photo source</p></div></div>""", unsafe_allow_html=True)
        image = None
        
        input_tab_file, input_tab_camera = st.tabs(["📁 Upload Image File", "📸 Use Camera Capture"])
        
        with input_tab_file:
            uploaded_file = st.file_uploader("Or drop your image here", type=["jpg","jpeg","png"], key="file_uploader_key", label_visibility="collapsed")
            if uploaded_file:
                image = Image.open(uploaded_file).convert("RGB")
                
        with input_tab_camera:
            camera_photo = st.camera_input("Point camera at leaf", key="camera_input_key", label_visibility="collapsed")
            if camera_photo:
                image = Image.open(camera_photo).convert("RGB")

        if image is not None:
            img_np_display = np.array(image)
            quality = image_quality_score(img_np_display)
            qcolor = "#10b981" if quality >= 70 else "#f59e0b" if quality >= 45 else "#ef4444"
            qlabel = "Good" if quality >= 70 else "Fair" if quality >= 45 else "Poor"
            st.markdown(f"""<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;"><span style="font-size:11px;color:var(--cs-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">Image Quality</span><span style="font-size:12px;font-weight:700;color:{qcolor};">{qlabel} · {quality}/100</span></div><div class="quality-bar"><div class="quality-fill" style="width:{quality}%;background:{qcolor};"></div></div></div>""", unsafe_allow_html=True)
            if quality < 45:
                st.markdown("""<div class="cs-error cs-warn" style="margin-bottom:12px;"><div class="cs-error-icon">📷</div><div><div class="cs-error-title">Low Image Quality</div><div class="cs-error-body">Image appears blurry or poorly lit. Use a clear, well-lit photo for best results.</div></div></div>""", unsafe_allow_html=True)
            st.image(image, caption="Input image", use_container_width=True)

    # ── FIX 12 — use a flag instead of st.stop() inside the column block ──
    analysis_blocked = False

    with right_col:
        st.markdown("""<div class="cs-section cs-fadein"><div class="cs-section-icon amber">🔬</div><div><p class="cs-section-title">AI Diagnosis</p><p class="cs-section-sub">CNN + Gemini Vision · Universal plant disease detection</p></div></div>""", unsafe_allow_html=True)

        if image is None:
            st.markdown("""<div class="cs-empty cs-fadein"><div class="cs-empty-icon">🌿</div><div class="cs-empty-title">Awaiting image input</div><div class="cs-empty-sub">Upload or capture any plant leaf to start analysis</div></div>""", unsafe_allow_html=True)
            analysis_blocked = True
        else:
            img_np = np.array(image)
            valid_leaf, _ = is_leaf(img_np)
            if not valid_leaf:
                st.markdown("""<div class="cs-error cs-fadein"><div class="cs-error-icon">⚠️</div><div><div class="cs-error-title">Invalid Image Detected</div><div class="cs-error-body">This doesn't appear to be a plant leaf. Please upload a clear leaf photo with visible green coloration.</div></div></div>""", unsafe_allow_html=True)
                analysis_blocked = True
            else:
                # Compute a lightweight hash to detect image changes
                img_hash = hash(img_np.tobytes())
                image_changed = (img_hash != st.session_state.last_image_hash)
                
                if image_changed:
                    # Capture unique real-time timestamp at the exact moment of prediction
                    pred_now = datetime.now()
                    st.session_state.prediction_time_date = pred_now.strftime("%d-%m-%Y")
                    st.session_state.prediction_time_time = pred_now.strftime("%H:%M:%S")

                # ── CNN PREDICTION ──
                cnn_disease = "Unknown"
                cnn_confidence = 0.0
                predicted_class = 0
                input_tensor = None
                prediction = None

                if model is not None and class_names:
                    resized = cv2.resize(img_np, (128, 128)) / 255.0
                    input_tensor = np.expand_dims(resized, axis=0)
                    with st.spinner("CNN analyzing…"):
                        prediction = model.predict(input_tensor, verbose=0)
                    predicted_class = int(np.argmax(prediction))
                    cnn_confidence  = float(np.max(prediction) * 100)
                    cnn_disease = class_names[predicted_class] if predicted_class < len(class_names) else "Unknown"

                is_healthy_cnn = "healthy" in cnn_disease.lower()

                # ── RUN GEMINI OR FALLBACK TO OFFLINE DATABASE ──
                if use_gemini and gemini_ok:
                    if image_changed:
                        img_bytes = image_to_bytes(image)
                        with st.spinner("🔮 Gemini Vision analyzing plant & disease…"):
                            raw_gemini = gemini_analyze_leaf(img_bytes, cnn_disease, cnn_confidence)
                        
                        # Fallback to offline database if Gemini failed with an error
                        if "error" in raw_gemini:
                            try:
                                from utils.offline_database import OFFLINE_DB
                                if cnn_disease in OFFLINE_DB:
                                    offline_data = dict(OFFLINE_DB[cnn_disease])
                                    offline_data["error"] = raw_gemini["error"]
                                    raw_gemini = offline_data
                            except Exception:
                                pass
                        
                        st.session_state.gemini_data_raw = raw_gemini
                        st.session_state.last_image_hash = img_hash
                    gemini_data_raw = st.session_state.gemini_data_raw
                else:
                    # ── OFFLINE DATABASE FALLBACK ──
                    offline_data = {}
                    try:
                        from utils.offline_database import OFFLINE_DB
                        if cnn_disease in OFFLINE_DB:
                            offline_data = OFFLINE_DB[cnn_disease]
                    except Exception:
                        pass
                    gemini_data_raw = offline_data
                    if image_changed:
                        st.session_state.gemini_data_raw = offline_data
                        st.session_state.last_image_hash = img_hash

                # FIX 8: translate at render time
                gemini_data = translate_gemini_data(gemini_data_raw, lang_code)

                # Determine final display values
                if gemini_data and ("error" not in gemini_data or "plant_name" in gemini_data):
                    plant_name    = gemini_data.get("plant_name", "Unknown Plant")
                    plant_sci     = gemini_data.get("plant_scientific", "")
                    final_disease = gemini_data.get("disease_name", cnn_disease)
                    is_healthy    = gemini_data.get("is_healthy", is_healthy_cnn)
                    severity_src  = gemini_data.get("severity", "")
                    cnn_agrees    = gemini_data.get("cnn_agreement", True)
                    symptoms_text = gemini_data.get("symptoms", "")
                    description   = gemini_data.get("description", "")
                    treatment     = gemini_data.get("treatment", "")
                    prevention    = gemini_data.get("prevention", "")
                else:
                    plant_name    = "Unknown Plant"
                    plant_sci     = ""
                    final_disease = cnn_disease.replace("___"," ").replace("_"," ")
                    is_healthy    = is_healthy_cnn
                    severity_src  = ""
                    cnn_agrees    = True
                    symptoms_text = ""
                    description   = translate_text("Consult local agricultural extension for detailed diagnosis.", lang_code)
                    treatment     = translate_text("Apply recommended fungicide. Consult agronomist.", lang_code)
                    prevention    = ""

                severity_label, severity_color, severity_icon = get_severity(
                    cnn_confidence if cnn_confidence > 0 else 75, is_healthy)
                if severity_src in ("Healthy","Mild","Moderate","Severe"):
                    severity_label = severity_src

                # FIX 4: persist context into session_state for chatbot / sections below
                st.session_state.update(dict(
                    final_disease=final_disease, plant_name=plant_name, plant_sci=plant_sci,
                    is_healthy=is_healthy, severity_label=severity_label,
                    severity_color=severity_color, severity_icon=severity_icon,
                    cnn_confidence=cnn_confidence, predicted_class=predicted_class,
                    description=description, treatment=treatment, prevention=prevention,
                    input_tensor=input_tensor, prediction=prediction,
                    img_np_shape=img_np.shape,
                ))
                st.session_state.img_np = img_np  # numpy arrays can't be serialised but fine within session

                # Save to history
                csv_path = f"history/predictions_{st.session_state.user_mobile}.csv"
                history_df = pd.DataFrame(st.session_state.history)
                alert_msg = check_repeat_alert(history_df, final_disease)
                if alert_msg:
                    st.markdown(f'<div class="cs-alert-banner">🔁 {alert_msg}</div>', unsafe_allow_html=True)
                if image_changed:  # only log new images, not reruns
                    new_entry = {
                        "Date": st.session_state.prediction_time_date or datetime.now().strftime("%d-%m-%Y"),
                        "Time": st.session_state.prediction_time_time or datetime.now().strftime("%H:%M:%S"),
                        "Plant": plant_name,
                        "Disease": final_disease,
                        "CNN_Confidence": round(cnn_confidence, 1),
                        "Severity": severity_label
                    }
                    st.session_state.history.append(new_entry)
                    # Write updated history back to CSV
                    pd.DataFrame(st.session_state.history).to_csv(csv_path, index=False)

                # ── GEMINI IDENTIFICATION CARD ──
                if gemini_data and "error" not in gemini_data:
                    agree_cls  = "yes" if cnn_agrees else "no"
                    agree_lbl  = "✓ CNN agrees" if cnn_agrees else "⚠ Differs from CNN"
                    agree_html = f'<span class="gemini-agree {agree_cls}">{agree_lbl}</span>' if model is not None else ""
                    st.markdown(f"""
                    <div class="gemini-plant-card cs-fadein">
                        <div class="gemini-badge">🔮 Gemini Vision Identification</div>
                        <div class="gemini-plant-name">{plant_name}</div>
                        <div class="gemini-plant-sci">{plant_sci}</div>
                        {agree_html}
                        {"<div class='symptoms-box'>" + symptoms_text + "</div>" if symptoms_text else ""}
                        {"<div style='font-size:11px;color:rgba(240,253,244,0.4);margin-top:8px;'>" + gemini_data.get('confidence_note','') + "</div>" if gemini_data.get('confidence_note') else ""}
                    </div>""", unsafe_allow_html=True)
                elif gemini_data.get("error"):
                    st.markdown(f"""<div class="cs-error cs-warn cs-fadein"><div class="cs-error-icon">🔮</div><div><div class="cs-error-title">Gemini Unavailable</div><div class="cs-error-body">{str(gemini_data.get('error',''))[:120]}. Using CNN result only.</div></div></div>""", unsafe_allow_html=True)

                # ── CNN RESULT CARD ──
                if model is not None and cnn_confidence > 0:
                    if cnn_confidence < conf_threshold:
                        st.markdown(f"""<div class="cs-error cs-warn cs-fadein"><div class="cs-error-icon">🔍</div><div><div class="cs-error-title">CNN Low Confidence ({cnn_confidence:.1f}%)</div><div class="cs-error-body">Gemini Vision result above is the primary diagnosis.</div></div></div>""", unsafe_allow_html=True)
                    else:
                        card_cls    = "cs-result" if is_healthy else "cs-result disease"
                        badge_cls   = "cs-badge healthy" if is_healthy else "cs-badge disease-b"
                        badge_color = "#10b981" if is_healthy else "#f97316"
                        badge_label = "✓ Healthy Plant" if is_healthy else "⚠ Disease Detected"
                        bar_grad    = "linear-gradient(90deg,#10b981,#34d399)" if is_healthy else "linear-gradient(90deg,#c2410c,#f97316)"
                        display_name = final_disease.replace("___"," · ").replace("_"," ")
                        st.markdown(f"""
                        <div class="{card_cls} cs-fadein" style="margin-top:14px;">
                            <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:8px;">
                                <div class="{badge_cls}"><span class="cs-badge-dot" style="background:{badge_color};box-shadow:0 0 6px {badge_color};"></span>{badge_label}</div>
                                <div class="severity-badge" style="background:{severity_color}22;border:1px solid {severity_color}55;color:{severity_color};">{severity_icon} {severity_label}</div>
                            </div>
                            <h2 style="font-family:'Clash Display',sans-serif;font-size:clamp(14px,2vw,20px);font-weight:700;color:var(--cs-white);margin:10px 0 4px;">{display_name}</h2>
                            <p style="font-size:11px;color:var(--cs-muted);margin:0;font-family:'JetBrains Mono',monospace;">CNN class_id:{predicted_class} · model:PlantVillage-CNN</p>
                            <div class="conf-wrap">
                                <div class="conf-row"><span class="conf-label">CNN Confidence</span><span class="conf-val">{cnn_confidence:.1f}%</span></div>
                                <div class="conf-track"><div class="conf-fill" style="width:{cnn_confidence:.1f}%;background:{bar_grad};"></div></div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                # ── TOP-3 CNN ──
                if show_top3 and prediction is not None and class_names:
                    top3_idx = np.argsort(prediction[0])[::-1][:3]
                    st.markdown("""<div class="cs-section" style="margin-top:20px;margin-bottom:10px;"><div class="cs-section-icon amber">🏆</div><div><p class="cs-section-title">Top-3 CNN Predictions</p></div></div>""", unsafe_allow_html=True)
                    for rank, idx in enumerate(top3_idx):
                        pct = float(prediction[0][idx] * 100)
                        nm  = class_names[idx].replace("___"," · ").replace("_"," ") if idx < len(class_names) else f"Class {idx}"
                        col_c = ["#10b981","#f59e0b","#6b7280"][rank]
                        st.markdown(f'<div class="top3-row"><span class="top3-rank" style="color:{col_c};">#{rank+1}</span><span class="top3-name">{nm}</span><div class="top3-bar-wrap"><div class="top3-bar" style="width:{pct:.1f}%;background:{col_c};"></div></div><span class="top3-pct">{pct:.1f}%</span></div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # Sections below columns — only render if image was valid
    # FIX 12: analysis_blocked flag replaces st.stop()
    # ════════════════════════════════════════════════
    if not analysis_blocked and image is not None:
        img_np   = st.session_state.get("img_np", None)
        it       = st.session_state.input_tensor
        pred     = st.session_state.prediction
        p_class  = st.session_state.predicted_class
        gd       = translate_gemini_data(st.session_state.gemini_data_raw, lang_code)
        dis      = st.session_state.final_disease
        sev      = st.session_state.severity_label
        sev_col  = st.session_state.severity_color
        sev_ico  = st.session_state.severity_icon
        desc     = st.session_state.description
        treat    = st.session_state.treatment
        prev     = st.session_state.prevention
        p_name   = st.session_state.plant_name
        conf     = st.session_state.cnn_confidence

        # ── DYNAMIC OUTPUT TABS ──
        st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
        
        tab_titles = ["🩺 Diagnosis & Heatmap"]
        has_med = gd and "medicine" in gd and "error" not in gd
        has_fert = gd and "fertilizer" in gd and "error" not in gd
        
        if has_med:
            tab_titles.append("💊 Medicine Details")
        if has_fert:
            tab_titles.append("🌱 Fertilizer Details")
        
        tab_titles.append("🤖 AI Assistant & Voice")
        
        tabs = st.tabs(tab_titles)
        
        # ── TAB 1: DIAGNOSIS & HEATMAP ──
        with tabs[0]:
            # Treatment Summary
            if dis or gd:
                st.markdown("""<div class="cs-section cs-fadein" style="margin-top:10px;"><div class="cs-section-icon rose">🩺</div><div><p class="cs-section-title">Diagnosis & Treatment Summary</p><p class="cs-section-sub">Overview of the crop health condition</p></div></div>""", unsafe_allow_html=True)
                pathogen = gd.get("disease_pathogen","N/A") if gd and "error" not in gd else "N/A"
                
                # Escape HTML characters and replace newlines with <br> to keep block tags single-line or valid HTML
                s_desc = html.escape(desc).replace('\n', '<br>')
                s_treat = html.escape(treat).replace('\n', '<br>')
                s_prev = html.escape(prev).replace('\n', '<br>')
                s_pathogen = html.escape(pathogen).replace('\n', '<br>')
                
                import textwrap
                summary_html = textwrap.dedent(f"""
<div class="device-desktop" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;">
<div class="cs-info"><div class="cs-info-accent" style="background:#22d3ee;"></div><span class="cs-info-tag tag-desc">📝 Description</span><p class="cs-info-body">{s_desc}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#10b981;"></div><span class="cs-info-tag tag-treat">💊 Treatment</span><p class="cs-info-body">{s_treat}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#fbbf24;"></div><span class="cs-info-tag tag-fert">🌿 Prevention</span><p class="cs-info-body">{s_prev}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#fb923c;"></div><span class="cs-info-tag tag-med">🦠 Pathogen</span><p class="cs-info-big">{s_pathogen}</p></div>
</div>
<div class="device-laptop">
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;">
<div class="cs-info"><div class="cs-info-accent" style="background:#22d3ee;"></div><span class="cs-info-tag tag-desc">📝 Description</span><p class="cs-info-body">{s_desc}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#10b981;"></div><span class="cs-info-tag tag-treat">💊 Treatment</span><p class="cs-info-body">{s_treat}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#fbbf24;"></div><span class="cs-info-tag tag-fert">🌿 Prevention</span><p class="cs-info-body">{s_prev}</p></div>
</div>
<div class="cs-info" style="width: 100%;"><div class="cs-info-accent" style="background:#fb923c;"></div><span class="cs-info-tag tag-med">🦠 Pathogen</span><p class="cs-info-big">{s_pathogen}</p></div>
</div>
<div class="device-tablet" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
<div class="cs-info"><div class="cs-info-accent" style="background:#22d3ee;"></div><span class="cs-info-tag tag-desc">📝 Description</span><p class="cs-info-body">{s_desc}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#10b981;"></div><span class="cs-info-tag tag-treat">💊 Treatment</span><p class="cs-info-body">{s_treat}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#fbbf24;"></div><span class="cs-info-tag tag-fert">🌿 Prevention</span><p class="cs-info-body">{s_prev}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#fb923c;"></div><span class="cs-info-tag tag-med">🦠 Pathogen</span><p class="cs-info-big">{s_pathogen}</p></div>
</div>
<div class="device-mobile" style="display: flex; flex-direction: column; gap: 10px;">
<div class="cs-info"><div class="cs-info-accent" style="background:#22d3ee;"></div><span class="cs-info-tag tag-desc">📝 Description</span><p class="cs-info-body" style="font-size:12px;">{s_desc}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#10b981;"></div><span class="cs-info-tag tag-treat">💊 Treatment</span><p class="cs-info-body" style="font-size:12px;">{s_treat}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#fbbf24;"></div><span class="cs-info-tag tag-fert">🌿 Prevention</span><p class="cs-info-body" style="font-size:12px;">{s_prev}</p></div>
<div class="cs-info"><div class="cs-info-accent" style="background:#fb923c;"></div><span class="cs-info-tag tag-med">🦠 Pathogen</span><p class="cs-info-big" style="font-size:14px;">{s_pathogen}</p></div>
</div>
                """).strip()
                st.markdown(summary_html, unsafe_allow_html=True)
                
            # Grad-CAM Heatmap
            if show_heatmap and model is not None and it is not None and pred is not None and img_np is not None:
                st.markdown("""<div class="cs-section cs-fadein" style="margin-top:28px;"><div class="cs-section-icon sky">🗺️</div><div><p class="cs-section-title">Grad-CAM Visual Explanation</p><p class="cs-section-sub">CNN attention map — shows where disease pattern was detected</p></div></div>""", unsafe_allow_html=True)
                heatmap = generate_gradcam(model, it, p_class)
                hm1, hm2 = st.columns(2, gap="medium")
                with hm1:
                    st.image(image, caption="Original", use_container_width=True)
                with hm2:
                    if heatmap is not None:
                        st.image(overlay_heatmap(img_np, heatmap), caption="Grad-CAM (red = high attention)", use_container_width=True)
                    else:
                        st.markdown('<div class="cs-empty" style="min-height:160px;"><div class="cs-empty-icon" style="font-size:32px;">🗺️</div><div class="cs-empty-title">Heatmap unavailable for this model</div></div>', unsafe_allow_html=True)

            # PDF Report Download
            st.markdown("""<div class="cs-section cs-fadein" style="margin-top:28px;"><div class="cs-section-icon amber">📄</div><div><p class="cs-section-title">Download Full Report</p><p class="cs-section-sub">PDF includes medicine, fertilizer NPK, safety & tips</p></div></div>""", unsafe_allow_html=True)
            try:
                pdf_bytes = generate_pdf_report(
                    disease=dis, plant_name=p_name, confidence=conf,
                    gemini_data=gd if gd and "error" not in gd else {},
                    severity_label=sev
                )
                st.download_button(
                    label="📄 Download PDF Report", data=pdf_bytes,
                    file_name=f"cropsense_{p_name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf", use_container_width=True
                )
            except Exception as e:
                st.markdown(f'<div class="cs-error cs-warn"><div class="cs-error-icon">⚠️</div><div><div class="cs-error-title">PDF Error</div><div class="cs-error-body">Results shown above. Failed: {str(e)[:80]}</div></div></div>', unsafe_allow_html=True)

        # ── TAB 2 (or 3): MEDICINE DETAILS ──
        next_tab_idx = 1
        if has_med:
            with tabs[next_tab_idx]:
                st.markdown("""<div class="cs-section cs-fadein" style="margin-top:10px;"><div class="cs-section-icon rose">💊</div><div><p class="cs-section-title">Medicine — Full Details</p><p class="cs-section-sub">Dose · Safety · Pre-harvest interval · Alternatives</p></div></div>""", unsafe_allow_html=True)
                render_gemini_medicine(gd["medicine"])
            next_tab_idx += 1
                
        # ── TAB 3 (or 2): FERTILIZER DETAILS ──
        if has_fert:
            with tabs[next_tab_idx]:
                st.markdown("""<div class="cs-section cs-fadein" style="margin-top:10px;"><div class="cs-section-icon violet">🌱</div><div><p class="cs-section-title">Fertilizer — Full Details</p><p class="cs-section-sub">NPK · Timing · Benefits · Pro tips</p></div></div>""", unsafe_allow_html=True)
                render_gemini_fertilizer(gd["fertilizer"])
            next_tab_idx += 1
            
        # ── TAB 4: CHAT & VOICE ──
        with tabs[next_tab_idx]:
            # Voice Summary
            voice_text = (
                f"Plant identified: {p_name}. Disease: {gd.get('disease_name', dis) if gd and 'error' not in gd else dis}. "
                f"Severity: {sev}. Treatment: {treat[:200]}. "
                f"Recommended medicine: {gd.get('medicine',{}).get('name','See details') if gd and 'error' not in gd else 'See details'}."
            )
            try:
                tts = gTTS(voice_text, lang='en')
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    tts.save(tmp.name)
                    tmp.seek(0)
                    audio_bytes = open(tmp.name, "rb").read()
                os.unlink(tmp.name)
                st.markdown("""<div class="cs-voice-wrap cs-fadein" style="margin-top:10px;"><div class="cs-voice-icon">🔊</div><div><div class="cs-voice-label">Voice Summary</div><div class="cs-voice-sub">AI diagnosis read aloud</div></div></div>""", unsafe_allow_html=True)
                st.audio(audio_bytes)
            except Exception as e:
                st.caption(f"ℹ️ Voice unavailable ({type(e).__name__})")
                
            # Chatbot
            if show_chatbot:
                st.markdown("""<div class="cs-section cs-fadein" style="margin-top:20px;"><div class="cs-section-icon blue">💬</div><div><p class="cs-section-title">AI Farming Assistant</p><p class="cs-section-sub">Powered by Gemini · Context-aware · Speaks your language</p></div></div>""", unsafe_allow_html=True)
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                if "chat_submitted" not in st.session_state:
                    st.session_state.chat_submitted = False
                    
                suggestions = [
                    f"What are early signs of {dis[:30]}?",
                    f"How to prevent {dis[:25]} next season?",
                    "Is this safe to eat after treatment?",
                    "What organic alternatives exist?",
                ]
                chip_cols = st.columns(len(suggestions))
                for i, (col_c, sugg) in enumerate(zip(chip_cols, suggestions)):
                    with col_c:
                        if st.button(sugg, key=f"chip_{i}", use_container_width=True):
                            st.session_state.chat_history.append({"role":"user","content":sugg})
                            with st.spinner("🔮 Thinking…"):
                                reply = gemini_chatbot_response(sugg, dis, p_name, conf, sev, lang_code)
                            st.session_state.chat_history.append({"role":"assistant","content":reply})
                            st.rerun()
                            
                if st.session_state.chat_history:
                    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
                    for msg in st.session_state.chat_history[-10:]:
                        if msg["role"] == "user":
                            st.markdown(f'<div class="chat-msg-user"><div class="chat-bubble-user">{html.escape(msg["content"])}</div></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="chat-msg-ai"><div class="chat-bubble-ai"><span class="ai-label">🔮 CropSense AI</span>{msg["content"]}</div></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                chat_col1, chat_col2 = st.columns([5, 1])
                with chat_col1:
                    user_input = st.text_input(
                        "Ask about your crop…",
                        placeholder=f"e.g. How do I treat {dis[:25]}?",
                        key="chat_input",
                        label_visibility="collapsed"
                    )
                with chat_col2:
                    send_clicked = st.button("Ask →", key="chat_send", use_container_width=True)
                    
                if send_clicked and user_input.strip() and not st.session_state.chat_submitted:
                    st.session_state.chat_submitted = True
                    st.session_state.chat_history.append({"role":"user","content":user_input.strip()})
                    with st.spinner("🔮 Gemini thinking…"):
                        reply = gemini_chatbot_response(
                            user_input.strip(), dis, p_name, conf, sev, lang_code)
                    st.session_state.chat_history.append({"role":"assistant","content":reply})
                    st.rerun()
                else:
                    st.session_state.chat_submitted = False
                    
                if st.session_state.chat_history:
                    if st.button("🗑 Clear chat", key="chat_clear"):
                        st.session_state.chat_history = []
                        st.rerun()

    elif show_chatbot and analysis_blocked:
        st.markdown("""<div class="cs-section cs-fadein" style="margin-top:32px;"><div class="cs-section-icon blue">💬</div><div><p class="cs-section-title">AI Farming Assistant</p></div></div>""", unsafe_allow_html=True)
        st.markdown('<div class="cs-empty" style="min-height:120px;"><div class="cs-empty-icon" style="font-size:32px;">💬</div><div class="cs-empty-title">Upload a leaf image to activate the chatbot</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
# HISTORY PAGE
# ═══════════════════════════════════════════════════
if page == "📜 History":
    st.markdown("""<div class="cs-section cs-fadein"><div class="cs-section-icon sky">📜</div><div><p class="cs-section-title">Prediction History & Analytics</p><p class="cs-section-sub">All diagnoses with plant identification, timestamp, and confidence</p></div></div>""", unsafe_allow_html=True)
    history_df = pd.DataFrame(st.session_state.history)
    if len(history_df) > 0:
        disease_col = "Disease" if "Disease" in history_df.columns else history_df.columns[1]
        conf_col    = next((c for c in ["CNN_Confidence","Confidence"] if c in history_df.columns), None)
        healthy_pct = round(len(history_df[history_df[disease_col].str.contains("healthy|Healthy",na=False)])/len(history_df)*100)
        avg_conf    = f"{history_df[conf_col].mean():.1f}%" if conf_col else "N/A"
        m1,m2,m3,m4 = st.columns(4)
        for col_m,(label,val) in zip([m1,m2,m3,m4],[("Total Diagnoses",str(len(history_df))),("Avg Confidence",avg_conf),("Unique Diseases",str(history_df[disease_col].nunique())),("Healthy Rate",f"{healthy_pct}%")]):
            with col_m:
                st.markdown(f'<div class="cs-metric cs-fadein"><span class="cs-metric-val">{val}</span><span class="cs-metric-lab">{label}</span></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        ch1, ch2 = st.columns(2, gap="large")
        with ch1:
            st.markdown("""<div class="cs-section" style="margin-top:0;"><div class="cs-section-icon amber">📊</div><div><p class="cs-section-title">Disease Frequency</p></div></div>""", unsafe_allow_html=True)
            top_diseases = history_df[disease_col].value_counts().head(8)
            fig, ax = plt.subplots(figsize=(6,3.5))
            fig.patch.set_facecolor('#0c130c'); ax.set_facecolor('#111b11')
            ax.barh([d[:28] for d in top_diseases.index], top_diseases.values,
                     color=['#10b981' if 'healthy' in d.lower() else '#f97316' for d in top_diseases.index],
                     edgecolor='none', height=0.65)
            ax.tick_params(colors='#9ca3af',labelsize=8)
            for sp in ax.spines.values(): sp.set_color('#1f2937')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.set_xlabel("Count",color='#9ca3af',fontsize=8); ax.invert_yaxis()
            plt.tight_layout(); st.pyplot(fig); plt.close()
        with ch2:
            if conf_col:
                st.markdown("""<div class="cs-section" style="margin-top:0;"><div class="cs-section-icon green">📈</div><div><p class="cs-section-title">Confidence Trend</p></div></div>""", unsafe_allow_html=True)
                fig2, ax2 = plt.subplots(figsize=(6,3.5))
                fig2.patch.set_facecolor('#0c130c'); ax2.set_facecolor('#111b11')
                confs = history_df[conf_col].tail(20).values
                ax2.plot(confs,color='#34d399',linewidth=2,marker='o',markersize=4,markerfacecolor='#10b981')
                ax2.fill_between(range(len(confs)),confs,alpha=0.15,color='#10b981')
                ax2.axhline(y=confs.mean(),color='#f59e0b',linewidth=1,linestyle='--',alpha=0.6)
                ax2.tick_params(colors='#9ca3af',labelsize=8)
                for sp in ax2.spines.values(): sp.set_color('#1f2937')
                ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
                ax2.set_ylabel("Confidence %",color='#9ca3af',fontsize=8)
                ax2.set_ylim(0,105); plt.tight_layout(); st.pyplot(fig2); plt.close()
        st.markdown("<br>", unsafe_allow_html=True)
        col_e, _ = st.columns([1,3])
        with col_e:
            st.download_button("📥 Export CSV", data=history_df.to_csv(index=False).encode(),
                file_name=f"cropsense_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        
        # Sort chronologically by converting Date + Time to sorting key
        try:
            temp_dt = pd.to_datetime(history_df["Date"] + " " + history_df["Time"], format="%d-%m-%Y %H:%M:%S")
            sorted_df = history_df.iloc[temp_dt.argsort()[::-1]]
        except Exception:
            sorted_df = history_df.iloc[::-1]
            
        st.dataframe(sorted_df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="cs-empty"><div class="cs-empty-icon">📋</div><div class="cs-empty-title">No history yet</div></div>', unsafe_allow_html=True)

st.markdown("""<div class="cs-footer cs-fadein"><div class="cs-footer-logo">🌿 CropSense AI v3.0 Pro</div><div class="cs-footer-sub">TensorFlow · Gemini Vision · OpenCV · Grad-CAM · ReportLab · Streamlit · Empowering farmers worldwide</div></div>""", unsafe_allow_html=True)
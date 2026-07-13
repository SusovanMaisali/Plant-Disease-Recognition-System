import os
import io
import json
import re
import random
import logging
import tempfile
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import numpy as np
import pandas as pd
import cv2
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator
import requests

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import tensorflow as tf
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CropSenseAI-Backend")

app = FastAPI(title="CropSense AI API", version="3.0 Pro")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════
# CNN MODEL INITIALIZATION & KERAS 3 PATCH
# ═══════════════════════════════════════════════════
def apply_keras_patch():
    try:
        if hasattr(tf.keras.layers.InputLayer, 'from_config'):
            original_from_config = tf.keras.layers.InputLayer.from_config

            @classmethod
            def patched_from_config(cls, config):
                if 'batch_shape' in config and 'batch_input_shape' not in config:
                    config['batch_input_shape'] = config.pop('batch_shape')
                if 'optional' in config:
                    config.pop('optional')
                return original_from_config(config)

            tf.keras.layers.InputLayer.from_config = patched_from_config
            logger.info("Successfully applied Keras 2/3 InputLayer patch.")
    except Exception as e:
        logger.warning(f"Could not apply Keras patch: {e}")

apply_keras_patch()

# Lazy loading variables
cnn_model = None
class_names = []

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model/best_plant_disease_model.keras")
CLASSES_PATH = os.path.join(os.path.dirname(__file__), "model/class_names.txt")

def get_cnn_model():
    global cnn_model
    if cnn_model is None:
        if os.path.exists(MODEL_PATH):
            try:
                cnn_model = tf.keras.models.load_model(MODEL_PATH)
                logger.info("CNN model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load CNN model: {e}")
        else:
            logger.warning(f"CNN model file not found at {MODEL_PATH}")
    return cnn_model

def get_class_names():
    global class_names
    if not class_names:
        if os.path.exists(CLASSES_PATH):
            try:
                with open(CLASSES_PATH, "r") as f:
                    class_names = [line.strip() for line in f if line.strip()]
                logger.info(f"Loaded {len(class_names)} class labels.")
            except Exception as e:
                logger.error(f"Failed to load class names: {e}")
        else:
            logger.warning(f"Class names file not found at {CLASSES_PATH}")
    return class_names

# Initial trigger
get_cnn_model()
get_class_names()

# ═══════════════════════════════════════════════════
# GEMINI GENERATIVE AI CLIENT
# ═══════════════════════════════════════════════════
def get_gemini_client():
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None, "GEMINI_API_KEY environment variable not configured."
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model, None
    except Exception as e:
        return None, str(e)

# Load offline database dictionary
try:
    from utils.offline_database import OFFLINE_DB
except ImportError:
    OFFLINE_DB = {}

# ═══════════════════════════════════════════════════
# CAPTCHA AND AUTHENTICATION
# ═══════════════════════════════════════════════════
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "../history")
os.makedirs(HISTORY_DIR, exist_ok=True)

def load_users() -> dict:
    users_file = os.path.join(HISTORY_DIR, "users.json")
    if not os.path.exists(users_file):
        with open(users_file, "w") as f:
            json.dump({}, f)
    try:
        with open(users_file, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict):
    users_file = os.path.join(HISTORY_DIR, "users.json")
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

@app.get("/api/auth/captcha")
def get_captcha():
    n1 = random.randint(1, 20)
    n2 = random.randint(1, 20)
    return {"num1": n1, "num2": n2, "sum": n1 + n2}

@app.post("/api/auth/send-otp")
def send_otp(data: dict):
    mobile = data.get("mobile", "").strip()
    if not mobile:
        raise HTTPException(status_code=400, detail="Mobile number is required.")
    users = load_users()
    if mobile not in users:
        raise HTTPException(status_code=404, detail="Mobile number not registered.")
    
    # Simulate OTP generation
    otp = str(random.randint(1000, 9999))
    logger.info(f"Simulated OTP for {mobile}: {otp}")
    return {"message": "OTP sent successfully.", "otp": otp}

@app.post("/api/auth/verify-otp")
def verify_otp(data: dict):
    mobile = data.get("mobile", "").strip()
    otp = data.get("otp", "").strip()
    if not mobile or not otp:
        raise HTTPException(status_code=400, detail="Mobile number and OTP are required.")
    
    users = load_users()
    if mobile not in users:
        raise HTTPException(status_code=404, detail="User not found.")
        
    user = users[mobile]
    return {
        "status": "success",
        "user": {
            "name": user["name"],
            "mobile": user["mobile"],
            "email": user["email"]
        }
    }

@app.post("/api/auth/signup")
def signup(data: dict):
    name = data.get("name", "").strip()
    mobile = data.get("mobile", "").strip()
    email = data.get("email", "").strip()
    
    if not name or not mobile or not email:
        raise HTTPException(status_code=400, detail="All signup fields are required.")
        
    users = load_users()
    if mobile in users:
        raise HTTPException(status_code=400, detail="This mobile number is already registered.")
        
    users[mobile] = {
        "name": name,
        "mobile": mobile,
        "email": email
    }
    save_users(users)
    return {
        "status": "success",
        "user": {
            "name": name,
            "mobile": mobile,
            "email": email
        }
    }

# ═══════════════════════════════════════════════════
# CLIMATE & GEOLOCATION ENDPOINTS
# ═══════════════════════════════════════════════════
try:
    from utils.weather_locator import get_ip_location, get_weather_data, calculate_disease_risk, generate_weather_alerts, reverse_geocode, get_location_suggestions, get_agri_info
except ImportError:
    def get_ip_location(): return {"latitude": 22.5726, "longitude": 88.3639, "city": "Kolkata", "status": "failed"}
    def get_weather_data(lat, lon): return {"temperature": 25.0, "humidity": 60, "precipitation": 0.0, "wind_speed": 10.0, "uv_index": 3.0, "status": "failed"}
    def calculate_disease_risk(temperature, humidity): return {"level": "Low", "color": "#10b981", "fungal_risk": "Low", "mildew_risk": "Low", "description": ""}
    def generate_weather_alerts(w): return []
    def reverse_geocode(lat, lon): return {"city": "Unknown City", "status": "failed"}
    def get_location_suggestions(q): return []
    def get_agri_info(temp, humidity, rain, uv): return {}

@app.get("/api/weather")
def get_weather(lat: float = None, lon: float = None):
    location_data = None
    if lat is not None and lon is not None:
        geo = reverse_geocode(lat, lon)
        location_data = {
            "city": geo.get("city", "GPS Location"),
            "state": geo.get("state", "Unknown State"),
            "country": geo.get("country", "Unknown Country"),
            "latitude": lat,
            "longitude": lon,
            "status": "success"
        }
    else:
        location_data = get_ip_location()
        lat = location_data.get("latitude", 22.5726)
        lon = location_data.get("longitude", 88.3639)

    weather_data = get_weather_data(lat, lon)
    
    # Correct positional signature parameters pass
    temp = weather_data.get("temperature", 25.0)
    humidity = weather_data.get("humidity", 60)
    rain = weather_data.get("precipitation", 0.0)
    uv = weather_data.get("uv_index", 3.0)
    
    risk_info = calculate_disease_risk(temp, humidity)
    agri_info = get_agri_info(temp, humidity, rain, uv)
    alerts = generate_weather_alerts(weather_data)
    
    # Calculate integer percentage representation for visual UI bar charts
    risk_pct = 15.0
    if risk_info.get("level") == "High":
        risk_pct = 85.0
    elif risk_info.get("level") == "Moderate":
        risk_pct = 50.0

    return {
        "location": location_data,
        "weather": weather_data,
        "risk_pct": risk_pct,
        "risk_info": risk_info,
        "agri": agri_info,
        "alerts": alerts
    }

@app.get("/api/weather/suggest")
def get_weather_suggestions_endpoint(query: str):
    return {"suggestions": get_location_suggestions(query)}

# ═══════════════════════════════════════════════════
# LEAF IMAGE QUALITY CHECK & GRAD-CAM VISUALIZER
# ═══════════════════════════════════════════════════
_mobilenet_model = None

def get_mobilenet_model():
    global _mobilenet_model
    if _mobilenet_model is None:
        try:
            _mobilenet_model = tf.keras.applications.MobileNetV2(weights="imagenet")
        except Exception as e:
            logger.error(f"Failed to load MobileNetV2 model: {e}")
    return _mobilenet_model

def local_imagenet_validate(img: np.ndarray) -> tuple[bool, str, bool]:
    try:
        model = get_mobilenet_model()
        if model is None:
            return True, "Classifier Offline", True
            
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
        
        resized = cv2.resize(img, (224, 224))
        preprocessed = preprocess_input(resized)
        batch = np.expand_dims(preprocessed, axis=0)
        
        preds = model.predict(batch, verbose=0)
        decoded = decode_predictions(preds, top=5)[0]
        
        plant_keywords = {"leaf", "buckeye", "fig", "banana", "pineapple", "acorn", "broccoli", "cabbage", "bell_pepper", "strawberry", "orange", "lemon", "tree", "plant", "grape", "vein", "foliage", "sprout", "bud", "stem", "stalk", "branch", "root", "herb", "grass", "fern", "moss", "clover", "squash", "pumpkin", "sunflower", "rose", "tulip", "mushroom", "fungus"}
        non_plant_keywords = {"face", "selfie", "mask", "t-shirt", "jersey", "sunglasses", "suit", "phone", "cellular", "computer", "laptop", "screen", "monitor", "keyboard", "car", "limousine", "cab", "van", "truck", "jeep", "bicycle", "motorcycle", "book", "paper", "slate", "document", "building", "house", "window", "furniture", "chair", "table", "desk", "cup", "bottle", "key", "coin", "pen"}
        
        is_plant = False
        is_non_plant = False
        top_name = decoded[0][1].lower()
        
        for item in decoded:
            class_name_lower = item[1].lower().replace("_", " ")
            prob = float(item[2])
            
            for pk in plant_keywords:
                if pk in class_name_lower and prob > 0.05:
                    is_plant = True
            
            for npk in non_plant_keywords:
                if npk in class_name_lower:
                    if prob > 0.15 or class_name_lower == top_name.replace("_", " "):
                        is_non_plant = True
                        
        if is_non_plant and not is_plant:
            return False, "Not a plant leaf (local ImageNet check).", is_plant
            
        top_name_clean = top_name.replace("_", " ")
        has_non_plant_top = any(nk in top_name_clean for nk in non_plant_keywords)
        has_plant_top = any(pk in top_name_clean for pk in plant_keywords)
        if has_non_plant_top and not has_plant_top and decoded[0][2] > 0.35:
            return False, "Not a plant leaf (local ImageNet check).", is_plant
            
        return True, "Leaf verified", is_plant
    except Exception as e:
        logger.error(f"ImageNet validation error: {e}")
        return True, "Validation error", True

def validate_image_pipeline(img: np.ndarray) -> tuple[bool, str]:
    invalid_msg = "Invalid Image. Please upload a clear image of a supported crop leaf."
    try:
        if img is None or len(img.shape) != 3 or img.size == 0:
            return False, invalid_msg
        
        h, w, c = img.shape
        if h < 50 or w < 50:
            return False, invalid_msg
            
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        std_val = np.std(gray)
        if std_val < 2:
            return False, invalid_msg
            
        # Local ImageNet Check
        is_leaf_local, reason, is_plant = local_imagenet_validate(img)
        if not is_leaf_local:
            return False, invalid_msg
            
        # Haar face detection (safe try-catch wrapper)
        try:
            xml_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
            if os.path.exists(xml_path):
                face_cascade = cv2.CascadeClassifier(xml_path)
                if not face_cascade.empty():
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(45, 45))
                    if len(faces) > 0 and not is_plant:
                        return False, invalid_msg
            else:
                logger.warning(f"Haar cascade XML not found at {xml_path}. Skipping face check.")
        except Exception as e:
            logger.warning(f"Haar face check failed (skipping): {e}")
            
        return True, "Valid Leaf Image"
    except Exception:
        return False, invalid_msg

def image_quality_score(img_np: np.ndarray) -> int:
    try:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blur  = min(cv2.Laplacian(gray, cv2.CV_64F).var() / 5, 100)
        brite = max(0, 100 - abs(np.mean(gray) - 128) * 1.2)
        cont  = min(np.std(gray) * 2, 100)
        return int(blur * 0.4 + brite * 0.3 + cont * 0.3)
    except Exception:
        return 70

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
        import matplotlib.cm as cm
        h, w = original_img.shape[:2]
        resized = cv2.resize(heatmap, (w, h))
        colored = (cm.jet(resized)[:, :, :3] * 255).astype(np.uint8)
        return (original_img * (1 - alpha) + colored * alpha).astype(np.uint8)
    except Exception:
        return original_img

# ═══════════════════════════════════════════════════
# GEMINI VISION ANALYSIS
# ═══════════════════════════════════════════════════
def gemini_analyze_leaf(image_bytes: bytes, cnn_disease: str, cnn_confidence: float) -> dict:
    gemini_model, err = get_gemini_client()
    if gemini_model is None:
        return {"error": err, "source": "gemini_unavailable"}

    try:
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
  "severity": "Healthy/Mild/Moderate/Severe",
  "severity_pct": 0,
  "confidence_note": "Brief note on how sure you are",
  "symptoms": "2-3 sentences describing visible symptoms in this image",
  "description": "Detailed disease description (3-4 sentences)",
  "treatment": "Step-by-step general treatment plan",
  "organic_treatment": "Organic/Biological treatment options and steps",
  "chemical_treatment": "Chemical/Chemical treatment options and steps",
  "prevention": "3-4 prevention measures",
  "irrigation_advice": "Irrigation and water management advice to prevent disease spread and help recovery",
  "soil_recommendation": "Soil pH, health, fertilizers, or soil remediation advice for this condition",
  "crop_rotation_advice": "Recommended crop rotation sequence or next crops to plant in this spot",
  "best_spray_timing": "Best time of day or weather conditions to apply sprays/treatments",
  "harvest_recommendation": "Harvesting recommendations and guidelines regarding this disease",
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
        response = gemini_model.generate_content([prompt, img])
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return {"error": str(e), "source": "gemini_failed"}

# ═══════════════════════════════════════════════════
# HISTORY CSV REGISTRY
# ═══════════════════════════════════════════════════
def load_and_migrate_history(csv_path: str) -> pd.DataFrame:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    required_cols = [
        "Date", "Time", "Plant", "Disease", "CNN_Confidence", "Severity",
        "Latitude", "Longitude", "City", "Country",
        "Temperature", "Humidity", "Rainfall", "WindSpeed", "UVIndex"
    ]
    if not os.path.exists(csv_path):
        pd.DataFrame(columns=required_cols).to_csv(csv_path, index=False)
    try:
        history_df = pd.read_csv(csv_path)
    except Exception:
        history_df = pd.DataFrame(columns=required_cols)
    
    if history_df.empty:
        return pd.DataFrame(columns=required_cols)

    # Standardizations
    if "Confidence" in history_df.columns and "CNN_Confidence" not in history_df.columns:
        history_df.rename(columns={"Confidence": "CNN_Confidence"}, inplace=True)
        
    for col in required_cols:
        if col not in history_df.columns:
            history_df[col] = ""
            
    return history_df[[c for c in required_cols if c in history_df.columns]]

# ═══════════════════════════════════════════════════
# MAIN DIAGNOSIS ENDPOINT
# ═══════════════════════════════════════════════════
@app.post("/api/diagnose")
async def diagnose(
    file: UploadFile = File(...),
    mobile: str = Form(...),
    latitude: float = Form(None),
    longitude: float = Form(None),
    use_gemini: bool = Form(True)
):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file format.")

    # 1. Image Validation
    valid_leaf, val_msg = validate_image_pipeline(img_rgb)
    if not valid_leaf:
        return {
            "status": "invalid_leaf",
            "message": val_msg
        }

    # 2. Quality Score
    quality = image_quality_score(img_rgb)

    # 3. Weather Fetch
    weather_info = None
    if latitude is not None and longitude is not None:
        try:
            weather_info = get_weather_data(latitude, longitude)
            geo_info = reverse_geocode(latitude, longitude)
            city = geo_info.get("city", "GPS Location")
            country = geo_info.get("country", "Unknown")
        except Exception:
            pass
    
    if weather_info is None:
        try:
            ip_loc = get_ip_location()
            latitude = ip_loc.get("latitude", 22.5726)
            longitude = ip_loc.get("longitude", 88.3639)
            city = ip_loc.get("city", "IP Location")
            country = ip_loc.get("country", "Unknown")
            weather_info = get_weather_data(latitude, longitude)
        except Exception:
            latitude, longitude = 0.0, 0.0
            city, country = "Unknown", "Unknown"
            weather_info = {"temperature": 25.0, "humidity": 60, "precipitation": 0.0, "wind_speed": 10.0, "uv_index": 3.0}

    # 4. Run CNN
    model = get_cnn_model()
    labels = get_class_names()
    cnn_disease = "Unknown"
    cnn_confidence = 0.0
    top_3 = []
    heatmap_b64 = None

    if model is not None and labels:
        try:
            resized = cv2.resize(img_rgb, (128, 128)) / 255.0
            input_tensor = np.expand_dims(resized, axis=0)
            prediction = model.predict(input_tensor, verbose=0)[0]
            
            top_idx = int(np.argmax(prediction))
            cnn_confidence = float(prediction[top_idx] * 100)
            cnn_disease = labels[top_idx]
            
            top_3_indices = np.argsort(prediction)[-3:][::-1]
            for idx in top_3_indices:
                top_3.append({
                    "disease": labels[idx],
                    "confidence": float(prediction[idx] * 100)
                })
                
            # Generate Grad-CAM Heatmap
            heatmap = generate_gradcam(model, input_tensor, top_idx)
            if heatmap is not None:
                overlay = overlay_heatmap(img_rgb, heatmap)
                _, buffer = cv2.imencode('.jpg', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
                heatmap_b64 = base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            logger.error(f"CNN execution failed: {e}")

    # 5. Gemini / Offline DB analysis
    gemini_data = {}
    if use_gemini:
        gemini_data = gemini_analyze_leaf(contents, cnn_disease, cnn_confidence)
        if "error" in gemini_data:
            if cnn_disease in OFFLINE_DB:
                gemini_data = dict(OFFLINE_DB[cnn_disease])
                gemini_data["error"] = "Gemini Vision offline. Loaded offline profile."
    else:
        if cnn_disease in OFFLINE_DB:
            gemini_data = dict(OFFLINE_DB[cnn_disease])
        else:
            gemini_data = {
                "plant_name": cnn_disease.split("___")[0] if "___" in cnn_disease else "Unknown",
                "disease_name": cnn_disease.split("___")[1].replace("_", " ") if "___" in cnn_disease else cnn_disease,
                "treatment": "No offline profile available. Connect to internet for Gemini advisory."
            }

    severity = gemini_data.get("severity", "Moderate")

    # 6. Save to Registry
    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M:%S")
    
    csv_path = os.path.join(HISTORY_DIR, f"predictions_{mobile}.csv")
    history_df = load_and_migrate_history(csv_path)
    
    new_entry = {
        "Date": date_str,
        "Time": time_str,
        "Plant": gemini_data.get("plant_name", "Unknown"),
        "Disease": gemini_data.get("disease_name", cnn_disease),
        "CNN_Confidence": round(cnn_confidence, 1),
        "Severity": severity,
        "Latitude": round(latitude, 4),
        "Longitude": round(longitude, 4),
        "City": city,
        "Country": country,
        "Temperature": weather_info.get("temperature", 0.0),
        "Humidity": weather_info.get("humidity", 0),
        "Rainfall": weather_info.get("precipitation", 0.0),
        "WindSpeed": weather_info.get("wind_speed", 0.0),
        "UVIndex": weather_info.get("uv_index", 0.0)
    }
    
    history_df = pd.concat([history_df, pd.DataFrame([new_entry])], ignore_index=True)
    history_df.to_csv(csv_path, index=False)

    _, orig_buffer = cv2.imencode('.jpg', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
    orig_b64 = base64.b64encode(orig_buffer).decode('utf-8')

    return {
        "status": "success",
        "quality_score": quality,
        "cnn_disease": cnn_disease,
        "cnn_confidence": cnn_confidence,
        "top_3": top_3,
        "heatmap": heatmap_b64,
        "original_image": orig_b64,
        "diagnosis": gemini_data,
        "weather": weather_info,
        "location": {
            "city": city,
            "country": country,
            "latitude": latitude,
            "longitude": longitude
        }
    }

# ═══════════════════════════════════════════════════
# AI CHATBOT ENDPOINT
# ═══════════════════════════════════════════════════
@app.post("/api/chat")
def chat_bot(data: dict):
    message = data.get("message", "")
    history = data.get("history", [])
    
    gemini_model, err = get_gemini_client()
    if gemini_model is None:
        return {"response": "AI Assistant offline. Please check your GEMINI_API_KEY environment variable."}

    try:
        gemini_history = []
        for h in history:
            gemini_history.append({
                "role": "user" if h["role"] == "user" else "model",
                "parts": [h["text"]]
            })
            
        chat = gemini_model.start_chat(history=gemini_history)
        response = chat.send_message(message)
        return {"response": response.text}
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        return {"response": f"Error: {e}"}

# ═══════════════════════════════════════════════════
# HISTORY LIST & DELETE ENDPOINTS
# ═══════════════════════════════════════════════════
@app.get("/api/history")
def get_history(mobile: str):
    csv_path = os.path.join(HISTORY_DIR, f"predictions_{mobile}.csv")
    history_df = load_and_migrate_history(csv_path)
    records = history_df.to_dict(orient="records")
    records.reverse()
    return {"history": records}

@app.post("/api/history/delete")
def delete_history_item(data: dict):
    mobile = data.get("mobile", "").strip()
    date = data.get("date", "")
    time = data.get("time", "")
    
    if not mobile or not date or not time:
        raise HTTPException(status_code=400, detail="Missing required lookup keys.")
        
    csv_path = os.path.join(HISTORY_DIR, f"predictions_{mobile}.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="History log not found.")
        
    history_df = pd.read_csv(csv_path)
    filtered_df = history_df[~((history_df["Date"] == date) & (history_df["Time"] == time))]
    filtered_df.to_csv(csv_path, index=False)
    
    records = filtered_df.to_dict(orient="records")
    records.reverse()
    return {"status": "success", "history": records}

# ═══════════════════════════════════════════════════
# TRANSLATION ENDPOINT
# ═══════════════════════════════════════════════════
@app.post("/api/translate")
def translate_text_endpoint(data: dict):
    text = data.get("text", "")
    target = data.get("target", "en")
    
    if target == "en" or not text:
        return {"translated": text}
        
    try:
        translated = GoogleTranslator(source='auto', target=target).translate(str(text))
        return {"translated": translated}
    except Exception as e:
        return {"translated": text, "error": str(e)}

# ═══════════════════════════════════════════════════
# TTS GENERATION ENDPOINT
# ═══════════════════════════════════════════════════
@app.post("/api/generate-tts")
def generate_tts_endpoint(data: dict):
    text = data.get("text", "")
    lang = data.get("lang", "en")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required.")
        
    try:
        clean_text = re.sub(r'<[^>]+>', '', str(text)).strip()
        tts = gTTS(clean_text, lang=lang)
        
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return StreamingResponse(fp, media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════
# REPORTLAB PDF GENERATION ENDPOINT
# ═══════════════════════════════════════════════════
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER

def _safe_text(t) -> str:
    if not t: return "N/A"
    return re.sub(r'<[^>]+>', '', str(t)).strip() or "N/A"

@app.post("/api/generate-pdf")
def generate_pdf_endpoint(data: dict):
    plant_name = data.get("plant_name", "Unknown Plant")
    disease = data.get("disease_name", "Unknown Disease")
    confidence = data.get("cnn_confidence", 0.0)
    severity_label = data.get("severity", "Moderate")
    gemini_data = data.get("diagnosis", {})
    location = data.get("location", {})
    weather = data.get("weather", {})
    original_image_b64 = data.get("original_image", "")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#065f46'), spaceAfter=4, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#6b7280'), spaceAfter=16)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=15, textColor=colors.HexColor('#111827'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#374151'), leading=14, spaceAfter=10)
    lbl_style = ParagraphStyle('LblStyle', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#10b981'), fontName='Helvetica-Bold', spaceAfter=3, spaceBefore=8)
    foot_style = ParagraphStyle('FootStyle', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#9ca3af'), alignment=TA_CENTER)

    story.append(Paragraph("CropSense AI — Diagnosis Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')} · Powered by Gemini Vision + CNN", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1fae5'), spaceAfter=15))
    story.append(Paragraph(f"{_safe_text(plant_name)} — {_safe_text(disease)}", h2_style))

    med = gemini_data.get("medicine", {})
    fert = gemini_data.get("fertilizer", {})
    
    loc_str = "N/A"
    if location:
        loc_str = f"{location.get('city')}, {location.get('country')} ({location.get('latitude', 0.0):.3f}, {location.get('longitude', 0.0):.3f})"
        
    wea_str = "N/A"
    if weather:
        wea_str = f"{weather.get('temperature')}°C | {weather.get('humidity')}% Humid | Wind: {weather.get('wind_speed')} km/h"

    tbl_data = [
        ["Plant Type", _safe_text(plant_name)],
        ["Diagnosis", _safe_text(disease)],
        ["CNN Confidence", f"{confidence:.1f}%"],
        ["Severity", severity_label],
        ["Pathogen", _safe_text(gemini_data.get("disease_pathogen", "N/A"))],
        ["Location", _safe_text(loc_str)],
        ["Weather", _safe_text(wea_str)],
        ["Recommended Medicine", _safe_text(med.get("name", "N/A"))],
        ["Active Ingredient", _safe_text(med.get("active_ingredient", "N/A"))],
        ["NPK Ratio", f"N:{fert.get('npk_n','?')} P:{fert.get('npk_p','?')} K:{fert.get('npk_k','?')}"],
        ["Recommended Fertilizer", _safe_text(fert.get("name", "N/A"))],
    ]
    
    t = Table(tbl_data, colWidths=[2.2*inch, 4.3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1f2937')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    if original_image_b64:
        try:
            from reportlab.platypus import Image as RLImage
            img_data = base64.b64decode(original_image_b64)
            temp_img = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            temp_img.write(img_data)
            temp_img.close()
            
            rlimg = RLImage(temp_img.name, width=2.8*inch, height=2.1*inch)
            story.append(Paragraph("📷 Captured Leaf Specimen", lbl_style))
            story.append(rlimg)
            story.append(Spacer(1, 10))
            os.unlink(temp_img.name)
        except Exception as ex:
            logger.error(f"Failed to embed image in PDF: {ex}")

    story.append(Paragraph("📋 Symptoms Identified", lbl_style))
    story.append(Paragraph(_safe_text(gemini_data.get("symptoms", "No symptom profile available.")), body_style))

    story.append(Paragraph("🔬 Disease Description", lbl_style))
    story.append(Paragraph(_safe_text(gemini_data.get("description", "No description available.")), body_style))

    story.append(Paragraph("🌿 Organic / Cultural Treatment Plan", lbl_style))
    story.append(Paragraph(_safe_text(gemini_data.get("organic_treatment", gemini_data.get("treatment", "No treatment available."))), body_style))

    story.append(Paragraph("🧪 Chemical Spray Measures", lbl_style))
    story.append(Paragraph(_safe_text(gemini_data.get("chemical_treatment", "Apply recommended medicine product as per label directions.")), body_style))

    story.append(Paragraph("🛡️ Prevention & Sanitation Guidelines", lbl_style))
    prev_list = gemini_data.get("prevention", [])
    if isinstance(prev_list, list) and prev_list:
        prev_str = "<br/>".join(f"• {p}" for p in prev_list)
        story.append(Paragraph(_safe_text(prev_str), body_style))
    else:
        story.append(Paragraph(_safe_text(str(prev_list)) if prev_list else "Maintain proper sanitation, clean tools, and crop spacing.", body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceAfter=10))
    story.append(Paragraph("CropSense AI Platform · Agricultural Diagnosis & Intelligent Telemetry Audit", foot_style))

    doc.build(story)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": "attachment;filename=diagnosis_report.pdf"})

# ═══════════════════════════════════════════════════
# EMAIL HISTORY REPORT ENDPOINT
# ═══════════════════════════════════════════════════
@app.post("/api/history/email")
def email_history_report(data: dict):
    mobile = data.get("mobile", "").strip()
    recipient_email = data.get("email", "").strip()
    name = data.get("name", "Farmer")
    
    if not mobile or not recipient_email:
        raise HTTPException(status_code=400, detail="Mobile and Email are required.")
        
    csv_path = os.path.join(HISTORY_DIR, f"predictions_{mobile}.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="No prediction history found to send.")
        
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load history data.")
        
    if df.empty:
        raise HTTPException(status_code=400, detail="Prediction history is empty.")

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    msg = MIMEMultipart()
    smtp_server = os.environ.get("SMTP_SERVER", "")
    smtp_port = os.environ.get("SMTP_PORT", "587")
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user) or "reports@cropsense.ai"
    
    msg['From'] = smtp_from
    msg['To'] = recipient_email
    msg['Subject'] = "Plant Disease Prediction Report — CropSense AI"
    
    body = f"""Dear {name},

Thank you for using CropSense AI. We have compiled your plant disease prediction history report.

Summary of diagnostics:
- Total scans: {len(df)}
- Latest diagnosis: {df.iloc[-1]['Plant']} — {df.iloc[-1]['Disease']} ({df.iloc[-1]['Severity']})

Please find the full prediction history attached as a CSV file.

Best regards,
CropSense AI Team
"""
    msg.attach(MIMEText(body, 'plain'))
    
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(csv_data.encode('utf-8'))
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='crop_prediction_history.csv')
    msg.attach(attachment)
    
    if not smtp_server or not smtp_user or not smtp_password:
        return {"status": "success", "message": "Simulation Mode: Email successfully compiled! (To enable real emails, configure your SMTP environment variables on Render)."}
        
    try:
        port = int(smtp_port)
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_server, port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_server, port, timeout=10)
            server.starttls()
            
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_from, recipient_email, msg.as_string())
        server.close()
        return {"status": "success", "message": "Email report sent successfully!"}
    except Exception as e:
        return {"status": "partial", "message": f"SMTP Error: {str(e)} (Simulation fallback: Email compiled successfully)."}

# ═══════════════════════════════════════════════════
# STATIC FILES SERVING (PRODUCTION MODE)
# ═══════════════════════════════════════════════════
frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
if os.path.exists(frontend_dist_path):
    logger.info(f"Serving compiled frontend static files from: {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")
else:
    logger.warning(f"Compiled frontend static folder not found at: {frontend_dist_path}. UI serving disabled. (Ignore in local development).")

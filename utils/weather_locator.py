import requests
import logging

logger = logging.getLogger("CropSenseAI")

WEATHER_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌧️"),
    53: ("Moderate Drizzle", "🌧️"),
    55: ("Dense Drizzle", "🌧️"),
    61: ("Slight Rain", "☔"),
    63: ("Moderate Rain", "☔"),
    65: ("Heavy Rain", "☔"),
    71: ("Slight Snow", "❄️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    80: ("Slight Rain Showers", "🌦️"),
    81: ("Moderate Rain Showers", "🌦️"),
    82: ("Violent Rain Showers", "🌦️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with Slight Hail", "⛈️"),
    99: ("Thunderstorm with Heavy Hail", "⛈️"),
}

def reverse_geocode(lat: float, lon: float) -> dict:
    """
    Performs reverse geocoding on coordinates using OpenStreetMap Nominatim API.
    Retrieves country, state, district, and city.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "CropSenseAI/3.0 (susovan670@gmail.com)"}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            address = data.get("address", {})
            city = address.get("city") or address.get("town") or address.get("village") or address.get("suburb") or "Unknown City"
            district = address.get("state_district") or address.get("county") or address.get("district") or address.get("city_district") or "Unknown District"
            state = address.get("state") or address.get("region") or "Unknown State"
            country = address.get("country") or "Unknown Country"
            return {
                "city": city,
                "district": district,
                "state": state,
                "country": country,
                "status": "success"
            }
    except Exception as e:
        logger.error(f"Reverse geocoding failed: {e}")
    return {
        "city": "GPS Location",
        "district": "Unknown District",
        "state": "Detected State",
        "country": "Detected Country",
        "status": "partial"
    }

def get_location_suggestions(query: str) -> list:
    """
    Fetches matching cities/regions autocomplete suggestions from Open-Meteo Geocoding Search API.
    """
    if not query or len(query.strip()) < 3:
        return []
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=8&language=en&format=json"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("results", [])
    except Exception as e:
        logger.error(f"Suggestions API failed: {e}")
    return []

def get_ip_location() -> dict:
    """
    Fallback method to fetch city, region, country, and coordinates via IP address.
    Uses free ip-api.com service.
    """
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return {
                    "city": data.get("city", "Unknown City"),
                    "district": "Unknown District",
                    "state": data.get("regionName", "Unknown State"),
                    "country": data.get("country", "Unknown Country"),
                    "latitude": data.get("lat", 0.0),
                    "longitude": data.get("lon", 0.0),
                    "status": "success"
                }
    except Exception as e:
        logger.error(f"IP Geolocation error: {e}")
    
    return {
        "city": "Kolkata",
        "district": "Kolkata District",
        "state": "West Bengal",
        "country": "India",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "status": "failed"
    }

def get_weather_data(lat: float, lon: float) -> dict:
    """
    Retrieves current weather details from Open-Meteo forecast API,
    and US Air Quality Index from Open-Meteo Air Quality API.
    """
    weather_info = {
        "temperature": 25.0,
        "feels_like": 25.0,
        "humidity": 60,
        "precipitation": 0.0,
        "chance_of_rain": 0,
        "wind_speed": 10.0,
        "wind_direction": 180,
        "pressure": 1013,
        "uv_index": 3.0,
        "visibility": 10000,
        "aqi": 50,
        "sunrise": "05:30 AM",
        "sunset": "06:30 PM",
        "weather_condition": "Clear Sky",
        "weather_icon": "☀️",
        "status": "failed"
    }
    
    # 1. Forecast variables
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,surface_pressure,uv_index,visibility,weather_code",
            "hourly": "precipitation_probability",
            "daily": "sunrise,sunset",
            "timezone": "auto"
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            curr = data.get("current", {})
            daily = data.get("daily", {})
            hourly = data.get("hourly", {})
            
            w_code = curr.get("weather_code", 0)
            cond, icon = WEATHER_CODES.get(w_code, ("Partly Cloudy", "⛅"))
            
            probs = hourly.get("precipitation_probability", [0])[:3]
            chance_of_rain = int(sum(probs) / len(probs)) if probs else 0
            
            sunrise_raw = daily.get("sunrise", ["06:00"])[0]
            sunset_raw = daily.get("sunset", ["18:00"])[0]
            sunrise = sunrise_raw.split("T")[-1] if "T" in sunrise_raw else sunrise_raw
            sunset = sunset_raw.split("T")[-1] if "T" in sunset_raw else sunset_raw
            
            weather_info.update({
                "temperature": curr.get("temperature_2m", 25.0),
                "feels_like": curr.get("apparent_temperature", 25.0),
                "humidity": curr.get("relative_humidity_2m", 60),
                "precipitation": curr.get("precipitation", 0.0),
                "chance_of_rain": chance_of_rain,
                "wind_speed": curr.get("wind_speed_10m", 10.0),
                "wind_direction": curr.get("wind_direction_10m", 180),
                "pressure": int(curr.get("surface_pressure", 1013)),
                "uv_index": curr.get("uv_index", 3.0),
                "visibility": curr.get("visibility", 10000),
                "sunrise": sunrise,
                "sunset": sunset,
                "weather_condition": cond,
                "weather_icon": icon,
                "status": "success"
            })
    except Exception as e:
        logger.error(f"Forecast fetch failed: {e}")
        
    # 2. Air quality
    try:
        aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        aqi_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "us_aqi"
        }
        res_aqi = requests.get(aqi_url, params=aqi_params, timeout=5)
        if res_aqi.status_code == 200:
            aqi_data = res_aqi.json()
            weather_info["aqi"] = int(aqi_data.get("current", {}).get("us_aqi", 50))
    except Exception as e:
        logger.error(f"AQI fetch failed: {e}")
        
    return weather_info

def calculate_disease_risk(temperature: float, humidity: int) -> dict:
    """
    Fallback support wrapper for disease risk calculations.
    """
    fungal_risk = "Low"
    if humidity > 80:
        if 20.0 <= temperature <= 30.0:
            fungal_risk = "High"
        else:
            fungal_risk = "Moderate"
    elif 65 <= humidity <= 80 and 18.0 <= temperature <= 32.0:
        fungal_risk = "Moderate"

    mildew_risk = "Low"
    if 20.0 <= temperature <= 32.0:
        if 50 <= humidity <= 70:
            mildew_risk = "High"
        else:
            mildew_risk = "Moderate"

    overall_level = "Low"
    color = "#10b981"
    if fungal_risk == "High" or mildew_risk == "High":
        overall_level = "High"
        color = "#ef4444"
    elif fungal_risk == "Moderate" or mildew_risk == "Moderate":
        overall_level = "Moderate"
        color = "#f97316"

    desc = f"Fungal pathogen risk is {fungal_risk} and mildew risk is {mildew_risk}."
    return {
        "level": overall_level,
        "color": color,
        "fungal_risk": fungal_risk,
        "mildew_risk": mildew_risk,
        "description": desc
    }

def get_agri_info(temp: float, humidity: int, rain: float, uvi: float) -> dict:
    """
    Calculates detailed agricultural advisory parameters based on current weather values.
    """
    risk_info = calculate_disease_risk(temp, humidity)
    
    # Seasonal risk profile
    if temp < 15.0:
        seasonal_risk = "Cold Stress, Early Blight & root moisture saturation risks."
    elif temp > 32.0:
        seasonal_risk = "Drought stress, fruit sunburn damage & spider mite propagation."
    else:
        seasonal_risk = "Powdery mildew, downy mildew, leaf spot & foliar rust outbreaks."
        
    # Crop matching
    if temp >= 24.0:
        suitable_crops = ["Rice (Paddy)", "Maize (Corn)", "Cotton", "Chili Pepper", "Tomato"]
    elif 15.0 <= temp < 24.0:
        suitable_crops = ["Wheat", "Potato", "Soybeans", "Cabbage", "Spinach"]
    else:
        suitable_crops = ["Barley", "Green Peas", "Radish", "Garlic", "Onions"]
        
    # Irrigation advice
    if rain > 1.5:
        irrigation = "🌧️ Suspended. Natural precipitation ({:.1f} mm) is sufficient. Skip irrigation.".format(rain)
    elif humidity > 85:
        irrigation = "💧 Reduced watering. High air humidity minimizes soil moisture evaporation."
    elif temp > 30.0:
        irrigation = "☀️ High rate watering. Thermal stress requires deep hydration cycles in early morning/evening."
    else:
        irrigation = "✅ Standard watering schedule. Maintain normal soil root-zone hydration levels."
        
    # NPK dynamic suggestions
    if temp > 28.0:
        fertilizer = "Formula N-P-K: 10-15-20. Enhance Potassium (K) ratio to maintain plant turgidity & mitigate thermal stress."
    elif temp < 15.0:
        fertilizer = "Formula N-P-K: 15-15-15. Focus on slow-release organic granules to prevent mineral leaching."
    else:
        fertilizer = "Formula N-P-K: 20-10-10. High Nitrogen (N) standard growth mix to accelerate stem & leaf vegetation."
        
    # Best spraying window
    if rain > 0.8:
        spray_time = "❌ DO NOT SPRAY. Active rain will wash fungicides/pesticides off the foliage immediately."
    elif temp > 32.0:
        spray_time = "❌ Avoid spraying. Heat induces immediate chemical evaporation and foliar burn. Spray after 5:30 PM."
    else:
        spray_time = "✅ Recommended. Spray before 9:30 AM or after 4:30 PM under calm winds."
        
    # Farm Advisory note
    if risk_info["level"] == "High":
        advisory = "Foliar pathogen risk is high. Inspect leaves for leaf spots daily. Apply prophylactic copper fungicide."
    else:
        advisory = "Maintain proper foliage pruning. Avoid overhead watering to limit leaf moisture duration."
        
    return {
        "risk_level": risk_info["level"],
        "risk_color": risk_info["color"],
        "seasonal_risk": seasonal_risk,
        "suitable_crops": ", ".join(suitable_crops),
        "irrigation": irrigation,
        "fertilizer": fertilizer,
        "spray_time": spray_time,
        "advisory": advisory
    }

def generate_weather_alerts(weather: dict) -> list:
    """
    Analyses weather conditions and flags emergency alerts.
    """
    alerts = []
    
    # Wind speed
    if weather.get("wind_speed", 0) > 25.0:
        alerts.append("⚠️ High Wind Speeds (>25 km/h): Risk of mechanical leaf damage and spray drift. Avoid spraying.")
    elif weather.get("wind_speed", 0) < 5.0:
        alerts.append("ℹ️ Calm winds: Perfect conditions for pesticide or foliar fertilizer spraying.")
        
    # Rain washing
    if weather.get("precipitation", 0) > 1.0:
        alerts.append("⚠️ Active rain detected: Treatments will be washed away. Postpone agricultural spray programs.")
        
    # UV index
    if weather.get("uv_index", 0) > 7.0:
        alerts.append("⚠️ Extreme UV Radiation Index: Plants are prone to sunburn and solar shock. Increase evening irrigation.")
        
    return alerts

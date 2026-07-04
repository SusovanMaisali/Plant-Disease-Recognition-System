import requests
import logging

logger = logging.getLogger("CropSenseAI")

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
                    "state": data.get("regionName", "Unknown State"),
                    "country": data.get("country", "Unknown Country"),
                    "latitude": data.get("lat", 0.0),
                    "longitude": data.get("lon", 0.0),
                    "status": "success"
                }
    except Exception as e:
        logger.error(f"IP Geolocation error: {e}")
    
    return {
        "city": "Unknown City",
        "state": "Unknown State",
        "country": "Unknown Country",
        "latitude": 0.0,
        "longitude": 0.0,
        "status": "failed"
    }

def get_weather_data(lat: float, lon: float) -> dict:
    """
    Retrieves current weather details from the free, keyless Open-Meteo API.
    Parameters: Temperature, Relative Humidity, Wind Speed, Rainfall (Precipitation), and UV Index.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index",
            "timezone": "auto"
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            return {
                "temperature": current.get("temperature_2m", 0.0),
                "humidity": current.get("relative_humidity_2m", 0),
                "precipitation": current.get("precipitation", 0.0),
                "wind_speed": current.get("wind_speed_10m", 0.0),
                "uv_index": current.get("uv_index", 0.0),
                "status": "success"
            }
    except Exception as e:
        logger.error(f"Weather API error: {e}")
    
    return {
        "temperature": 25.0,
        "humidity": 60,
        "precipitation": 0.0,
        "wind_speed": 10.0,
        "uv_index": 3.0,
        "status": "failed"
    }

def calculate_disease_risk(temperature: float, humidity: int) -> dict:
    """
    Calculates agricultural disease risk levels (Fungal/Bacterial/Mildew) based on weather factors.
    Returns level ('Low', 'Moderate', 'High') and a descriptive summary message.
    """
    # Fungal and bacterial pathogens thrive in warm, humid conditions
    fungal_risk = "Low"
    if humidity > 80:
        if 20.0 <= temperature <= 30.0:
            fungal_risk = "High"
        elif 15.0 <= temperature < 20.0 or 30.0 < temperature <= 35.0:
            fungal_risk = "Moderate"
    elif 65 <= humidity <= 80 and 18.0 <= temperature <= 32.0:
        fungal_risk = "Moderate"

    # Mildew (e.g. Powdery Mildew) can thrive in slightly lower humidity and moderate-high temperatures
    mildew_risk = "Low"
    if 20.0 <= temperature <= 32.0:
        if 50 <= humidity <= 70:
            mildew_risk = "High"
        elif 40 <= humidity < 50 or 70 < humidity <= 80:
            mildew_risk = "Moderate"

    # Combine into general agricultural risk
    overall_level = "Low"
    color = "#10b981"  # Emerald Green
    if fungal_risk == "High" or mildew_risk == "High":
        overall_level = "High"
        color = "#ef4444"  # Coral Red
    elif fungal_risk == "Moderate" or mildew_risk == "Moderate":
        overall_level = "Moderate"
        color = "#f97316"  # Orange

    desc = f"Fungal Pathogen Risk is {fungal_risk} and Powdery Mildew Risk is {mildew_risk}."
    
    return {
        "level": overall_level,
        "color": color,
        "fungal_risk": fungal_risk,
        "mildew_risk": mildew_risk,
        "description": desc
    }

def generate_weather_alerts(weather: dict) -> list:
    """
    Analyses wind speed, precipitation, and UV to yield actionable farming warnings.
    """
    alerts = []
    
    # Spraying warning for wind
    if weather.get("wind_speed", 0) > 25.0:
        alerts.append("⚠️ Wind speed is high (>25 km/h). Avoid chemical sprays now to prevent dangerous drift.")
    elif weather.get("wind_speed", 0) < 5.0:
        alerts.append("ℹ️ Wind is very calm. Excellent condition for chemical or foliar applications.")
        
    # Rain washing warning
    if weather.get("precipitation", 0) > 1.0:
        alerts.append("⚠️ Active rainfall detected. Postpone spray treatments as rainwater will wash them away.")
    elif weather.get("humidity", 0) > 85:
        alerts.append("ℹ️ High relative humidity may slow spray drying time. Allow extra time before rain.")

    # UV sun scorch alert
    if weather.get("uv_index", 0) > 7.0:
        alerts.append("⚠️ Extreme UV Index. Plants are prone to solar stress; ensure adequate morning/evening irrigation.")

    return alerts

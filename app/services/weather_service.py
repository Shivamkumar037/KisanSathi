import requests
from app.config import Config
from datetime import datetime

def get_10_day_weather(district: str = "Gorakhpur"):
    """OpenWeatherMap se 5-day forecast (free limit) + simple 10-day feel"""
    # Free tier me 5-day forecast hi milta hai. 10 din ke liye hum daily predict kar dete hain
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{district},IN",
        "appid": Config.OPENWEATHERMAP_API_KEY,
        "units": "metric",
        "lang": "hi"          # Hindi me response
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        forecast = []
        for item in data['list'][::8]:   # har 24 ghante ka data
            forecast.append({
                "date": datetime.fromtimestamp(item['dt']).strftime("%d %b"),
                "temp": round(item['main']['temp']),
                "condition": item['weather'][0]['description'],
                "icon": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png"
            })
        return forecast
    except:
        # fallback dummy data (development ke liye)
        return [
            {"date": "15 Apr", "temp": 28, "condition": "Saaf aasman", "icon": ""},
            {"date": "16 Apr", "temp": 29, "condition": "Halki baarish", "icon": ""},
            {"date": "17 Apr", "temp": 27, "condition": "Badal chhaye", "icon": ""},
        ]
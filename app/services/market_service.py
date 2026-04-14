import requests
from app.config import Config
from datetime import datetime

def get_market_rates(mandi: str = "Gorakhpur"):
    """
    Gorakhpur Mandi (UP) ke live-like rates
    Abhi static data (screenshot jaisa) — future mein real API (Agmarknet / e-NAM) add kar sakte hain
    """
    # Exact screenshot ke hisaab se data (14 April 2026)
    rates = [
        {
            "commodity": "Onion",
            "min": 1400,
            "max": 1850,
            "avg": 1600,
            "icon": "🧅"
        },
        {
            "commodity": "Potato",
            "min": 1300,
            "max": 1700,
            "avg": 1500,
            "icon": "🥔"
        },
        {
            "commodity": "Tomato",
            "min": 1800,
            "max": 2400,
            "avg": 2100,
            "icon": "🍅"
        },
        {
            "commodity": "Wheat",
            "min": 2000,
            "max": 2300,
            "avg": 2150,
            "icon": "🌾"
        },
        {
            "commodity": "Rice",
            "min": 3100,
            "max": 3500,
            "avg": 3300,
            "icon": "🍚"
        },
        {
            "commodity": "Sugar",
            "min": 3700,
            "max": 3800,
            "avg": 3750,
            "icon": "🍬"
        },
        {
            "commodity": "Maize",
            "min": 1300,
            "max": 1550,
            "avg": 1425,
            "icon": "🌽"
        }
    ]

    return {
        "mandi": f"{mandi} Mandi, UP",
        "updated": datetime.now().strftime("%d %b, %Y"),
        "rates": rates
    }


# Future real API integration ke liye placeholder (agar Agmarknet API mil jaaye)
def fetch_live_mandi_rates():
    """Yahan real API call daal sakte hain (abhi unused)"""
    try:
        # Example: response = requests.get("https://api.example.com/mandi?mandi=Gorakhpur")
        pass
    except:
        return get_market_rates()   # fallback to static
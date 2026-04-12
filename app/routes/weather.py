"""
Weather Routes
- GET /api/weather/current        - Current weather for location
- GET /api/weather/forecast       - 5-day forecast
"""

from flask import Blueprint, request, jsonify
import requests
import os

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    """Get current weather for a city/location"""
    city = request.args.get('city', 'Gorakhpur')
    state = request.args.get('state', 'Uttar Pradesh')
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')

    if not api_key:
        # Return mock data when API key not configured
        return jsonify({
            'success': True,
            'source': 'mock',
            'note': 'Configure OPENWEATHERMAP_API_KEY in .env for live data',
            'weather': {
                'city': city,
                'temperature': 28,
                'feels_like': 30,
                'condition': 'Sunny',
                'humidity': 65,
                'wind_speed': 12,
                'icon': '☀️',
                'forecast': [
                    {'day': 'Tue', 'temp': 18, 'icon': '🌤️'},
                    {'day': 'Wed', 'temp': 19, 'icon': '🌥️'},
                    {'day': 'Thu', 'temp': 17, 'icon': '🌦️'},
                ]
            }
        }), 200

    try:
        query = f"{city},{state},IN"
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': query,
            'appid': api_key,
            'units': 'metric',
            'lang': 'en'
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200:
            raise Exception(data.get('message', 'Weather API error'))

        icon_map = {
            '01': '☀️', '02': '🌤️', '03': '⛅', '04': '🌥️',
            '09': '🌧️', '10': '🌦️', '11': '⛈️', '13': '❄️', '50': '🌫️'
        }
        icon_code = data['weather'][0]['icon'][:2]
        emoji = icon_map.get(icon_code, '🌡️')

        return jsonify({
            'success': True,
            'source': 'openweathermap',
            'weather': {
                'city': data['name'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'condition': data['weather'][0]['description'].title(),
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'] * 3.6),  # m/s to km/h
                'icon': emoji,
                'forecast': []
            }
        }), 200

    except Exception as e:
        # API key invalid ya network issue — mock data return karo
        return jsonify({
            'success': True,
            'source': 'mock',
            'note': f'Live weather unavailable ({str(e)}). Configure valid OPENWEATHERMAP_API_KEY.',
            'weather': {
                'city': city,
                'temperature': 30,
                'feels_like': 33,
                'condition': 'Partly Cloudy',
                'humidity': 60,
                'wind_speed': 10,
                'icon': '🌤️',
                'forecast': [
                    {'day': 'Kal', 'temp': 28, 'icon': '🌤️'},
                    {'day': 'Parso', 'temp': 26, 'icon': '🌥️'},
                    {'day': 'Fir', 'temp': 25, 'icon': '🌦️'},
                ]
            }
        }), 200


@weather_bp.route('/forecast', methods=['GET'])
def get_forecast():
    """Get 5-day weather forecast"""
    city = request.args.get('city', 'Gorakhpur')
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')

    if not api_key:
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        icons = ['☀️', '🌤️', '🌥️', '🌦️', '⛈️']
        temps = [28, 26, 25, 22, 20]
        return jsonify({
            'success': True,
            'source': 'mock',
            'forecast': [
                {'day': days[i], 'temp': temps[i], 'icon': icons[i]}
                for i in range(5)
            ]
        }), 200

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {'q': f"{city},IN", 'appid': api_key, 'units': 'metric', 'cnt': 40}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        from collections import defaultdict
        daily = defaultdict(list)
        for item in data.get('list', []):
            day = item['dt_txt'][:10]
            daily[day].append(item['main']['temp'])

        forecast = []
        for day, temps in list(daily.items())[:5]:
            from datetime import datetime
            d = datetime.strptime(day, '%Y-%m-%d')
            forecast.append({
                'day': d.strftime('%a'),
                'date': day,
                'temp': round(sum(temps) / len(temps)),
                'min': round(min(temps)),
                'max': round(max(temps))
            })

        return jsonify({'success': True, 'forecast': forecast}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 503

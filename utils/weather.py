"""
Utility: Real-time weather fetching via OpenWeatherMap API
"""
import requests
from config import Config


def get_weather_data(location: str) -> dict:
    """Fetch current weather + 5-day forecast for a location."""
    api_key = Config.WEATHER_API_KEY
    base = Config.WEATHER_BASE_URL

    if not api_key or api_key == "your_openweather_key_here":
        # Return realistic mock data when API key not configured
        return _mock_weather(location)

    try:
        # Current weather
        curr_resp = requests.get(
            f"{base}/weather",
            params={"q": location, "appid": api_key, "units": "metric"},
            timeout=8,
        )
        curr_resp.raise_for_status()
        curr = curr_resp.json()

        # 5-day forecast
        fore_resp = requests.get(
            f"{base}/forecast",
            params={"q": location, "appid": api_key, "units": "metric", "cnt": 10},
            timeout=8,
        )
        fore_resp.raise_for_status()
        fore = fore_resp.json()

        daily = []
        seen = set()
        for item in fore.get("list", []):
            day = item["dt_txt"][:10]
            if day not in seen:
                seen.add(day)
                daily.append({
                    "date": day,
                    "temp_max": item["main"]["temp_max"],
                    "temp_min": item["main"]["temp_min"],
                    "humidity": item["main"]["humidity"],
                    "rain_mm": item.get("rain", {}).get("3h", 0),
                    "description": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                })

        return {
            "location": curr.get("name", location),
            "current": {
                "temperature": curr["main"]["temp"],
                "feels_like": curr["main"]["feels_like"],
                "humidity": curr["main"]["humidity"],
                "pressure": curr["main"]["pressure"],
                "wind_speed": curr["wind"]["speed"],
                "description": curr["weather"][0]["description"],
                "visibility": curr.get("visibility", 10000) / 1000,
                "uv_index": "N/A",
            },
            "forecast": daily[:5],
            "source": "OpenWeatherMap",
        }

    except Exception as e:
        return _mock_weather(location, error=str(e))


def _mock_weather(location: str, error: str = None) -> dict:
    """Mock weather data for demo/testing."""
    return {
        "location": location,
        "current": {
            "temperature": 28.5,
            "feels_like": 31.2,
            "humidity": 72,
            "pressure": 1013,
            "wind_speed": 3.4,
            "description": "partly cloudy",
            "visibility": 10.0,
            "uv_index": 7,
        },
        "forecast": [
            {"date": "2026-11-25", "temp_max": 30, "temp_min": 22, "humidity": 68,
             "rain_mm": 0, "description": "sunny", "wind_speed": 2.5},
            {"date": "2026-11-26", "temp_max": 29, "temp_min": 21, "humidity": 74,
             "rain_mm": 2.5, "description": "light rain", "wind_speed": 4.0},
            {"date": "2026-11-27", "temp_max": 27, "temp_min": 20, "humidity": 80,
             "rain_mm": 8.0, "description": "moderate rain", "wind_speed": 5.2},
            {"date": "2026-11-28", "temp_max": 31, "temp_min": 23, "humidity": 60,
             "rain_mm": 0, "description": "clear sky", "wind_speed": 2.0},
            {"date": "2026-11-29", "temp_max": 32, "temp_min": 24, "humidity": 58,
             "rain_mm": 0, "description": "sunny", "wind_speed": 1.8},
        ],
        "source": "Demo Data" if not error else f"Demo Data (API Error: {error})",
        "note": "Configure WEATHER_API_KEY in .env for live data",
    }

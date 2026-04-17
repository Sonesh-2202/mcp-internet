"""
Weather Tool - Get weather information using Open-Meteo API.

Open-Meteo is a free, open-source weather API that doesn't require an API key.
"""

import logging

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)

# Open-Meteo API endpoints
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Weather code descriptions
WEATHER_CODES = {
    0: "☀️ Clear sky",
    1: "🌤️ Mainly clear",
    2: "⛅ Partly cloudy",
    3: "☁️ Overcast",
    45: "🌫️ Foggy",
    48: "🌫️ Depositing rime fog",
    51: "🌧️ Light drizzle",
    53: "🌧️ Moderate drizzle",
    55: "🌧️ Dense drizzle",
    61: "🌧️ Slight rain",
    63: "🌧️ Moderate rain",
    65: "🌧️ Heavy rain",
    71: "🌨️ Slight snow",
    73: "🌨️ Moderate snow",
    75: "🌨️ Heavy snow",
    77: "🌨️ Snow grains",
    80: "🌦️ Slight rain showers",
    81: "🌦️ Moderate rain showers",
    82: "🌦️ Violent rain showers",
    85: "🌨️ Slight snow showers",
    86: "🌨️ Heavy snow showers",
    95: "⛈️ Thunderstorm",
    96: "⛈️ Thunderstorm with slight hail",
    99: "⛈️ Thunderstorm with heavy hail",
}


def get_weather_description(code: int) -> str:
    """Get human-readable weather description from code."""
    return WEATHER_CODES.get(code, f"🌡️ Weather code {code}")


def get_wind_direction(degrees: float) -> str:
    """Convert wind direction degrees to cardinal direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]


async def geocode_location(location: str) -> dict | None:
    """Convert location name to coordinates."""
    params = {"name": location, "count": 1, "language": "en", "format": "json"}
    url = f"{GEOCODING_URL}?name={location}&count=1&language=en&format=json"
    
    data = await fetch_json(url)
    if not data or "results" not in data or not data["results"]:
        return None
    
    result = data["results"][0]
    return {
        "name": result.get("name", location),
        "country": result.get("country", ""),
        "admin": result.get("admin1", ""),  # State/Province
        "lat": result["latitude"],
        "lon": result["longitude"],
        "timezone": result.get("timezone", "UTC"),
    }


async def get_weather(location: str) -> str:
    """
    Get current weather and forecast for a location.
    
    Args:
        location: City name, address, or place name
        
    Returns:
        Formatted weather report
    """
    if not location.strip():
        return "❌ Error: Please provide a location."
    
    # Geocode the location
    geo = await geocode_location(location)
    if not geo:
        return f"❌ Error: Unable to find location '{location}'. Please try a different city or be more specific."
    
    # Fetch weather data
    weather_url = (
        f"{WEATHER_URL}?"
        f"latitude={geo['lat']}&longitude={geo['lon']}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"weather_code,wind_speed_10m,wind_direction_10m"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max"
        f"&timezone={geo['timezone']}"
        f"&forecast_days=4"
    )
    
    weather_data = await fetch_json(weather_url)
    if not weather_data:
        return f"❌ Error: Unable to fetch weather data for {location}."
    
    try:
        current = weather_data["current"]
        daily = weather_data["daily"]
        
        # Format location name
        location_parts = [geo["name"]]
        if geo["admin"]:
            location_parts.append(geo["admin"])
        if geo["country"]:
            location_parts.append(geo["country"])
        location_display = ", ".join(location_parts)
        
        # Current weather
        weather_desc = get_weather_description(current["weather_code"])
        wind_dir = get_wind_direction(current["wind_direction_10m"])
        
        output = f"""🌍 **Weather for {location_display}**
{'=' * 50}

**Current Conditions**
{weather_desc}
🌡️ Temperature: {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)
💨 Wind: {current['wind_speed_10m']} km/h {wind_dir}
💧 Humidity: {current['relative_humidity_2m']}%

**3-Day Forecast**
"""
        
        # Daily forecast (skip today, show next 3 days)
        for i in range(1, min(4, len(daily["time"]))):
            date = daily["time"][i]
            code = daily["weather_code"][i]
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]
            precip = daily["precipitation_probability_max"][i]
            
            weather_emoji = get_weather_description(code).split()[0]
            output += f"\n📅 **{date}**: {weather_emoji} {min_temp}°C - {max_temp}°C"
            if precip > 0:
                output += f" | 🌧️ {precip}% rain"
        
        return output
        
    except KeyError as e:
        logger.error(f"Missing weather data key: {e}")
        return f"❌ Error: Incomplete weather data received. Please try again."
    except Exception as e:
        logger.error(f"Error processing weather data: {e}")
        return f"❌ Error: Unable to process weather data. Please try again."

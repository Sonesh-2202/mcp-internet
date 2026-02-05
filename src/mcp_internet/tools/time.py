"""
World Time Tool - Get current time for any timezone or city.

Uses WorldTimeAPI and Python's built-in timezone handling.
"""

import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, available_timezones

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)

# WorldTimeAPI endpoint
WORLDTIME_API = "https://worldtimeapi.org/api/timezone"

# Common city to timezone mappings
CITY_TIMEZONES = {
    "new york": "America/New_York",
    "nyc": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "tokyo": "Asia/Tokyo",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "hong kong": "Asia/Hong_Kong",
    "singapore": "Asia/Singapore",
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "dubai": "Asia/Dubai",
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "chennai": "Asia/Kolkata",
    "moscow": "Europe/Moscow",
    "toronto": "America/Toronto",
    "vancouver": "America/Vancouver",
    "seoul": "Asia/Seoul",
    "bangkok": "Asia/Bangkok",
    "jakarta": "Asia/Jakarta",
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "sao paulo": "America/Sao_Paulo",
    "mexico city": "America/Mexico_City",
    "amsterdam": "Europe/Amsterdam",
    "madrid": "Europe/Madrid",
    "rome": "Europe/Rome",
    "zurich": "Europe/Zurich",
    "istanbul": "Europe/Istanbul",
    "tel aviv": "Asia/Jerusalem",
    "jerusalem": "Asia/Jerusalem",
}


def find_timezone(location: str) -> str | None:
    """Find timezone for a location string."""
    location_lower = location.lower().strip()
    
    # Check city mappings first
    if location_lower in CITY_TIMEZONES:
        return CITY_TIMEZONES[location_lower]
    
    # Check if it's already a valid timezone
    if location in available_timezones():
        return location
    
    # Try to find partial matches in available timezones
    for tz in available_timezones():
        if location_lower in tz.lower():
            return tz
    
    return None


def format_time(dt: datetime, timezone_name: str) -> str:
    """Format datetime nicely."""
    # Get day of week
    day_name = dt.strftime("%A")
    date_str = dt.strftime("%B %d, %Y")
    time_str = dt.strftime("%I:%M:%S %p")
    
    # Calculate UTC offset
    offset = dt.strftime("%z")
    offset_formatted = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC"
    
    return f"""🕐 **Current Time**
{'=' * 40}

📍 **{timezone_name}**

📅 {day_name}, {date_str}
🕐 {time_str}
🌐 {offset_formatted}
"""


async def get_time_from_api(timezone_name: str) -> str | None:
    """Get time from WorldTimeAPI."""
    url = f"{WORLDTIME_API}/{timezone_name}"
    data = await fetch_json(url)
    
    if not data or "datetime" not in data:
        return None
    
    try:
        # Parse the datetime string
        dt_str = data["datetime"]
        # WorldTimeAPI returns ISO format with timezone
        dt = datetime.fromisoformat(dt_str)
        
        abbreviation = data.get("abbreviation", "")
        utc_offset = data.get("utc_offset", "")
        
        day_name = dt.strftime("%A")
        date_str = dt.strftime("%B %d, %Y")
        time_str = dt.strftime("%I:%M:%S %p")
        
        return f"""🕐 **Current Time**
{'=' * 40}

📍 **{timezone_name}**
   {abbreviation if abbreviation else ""}

📅 {day_name}, {date_str}
🕐 {time_str}
🌐 UTC{utc_offset}
"""
    except Exception as e:
        logger.error(f"Error parsing time API response: {e}")
        return None


async def get_current_time(location: str = "UTC") -> str:
    """
    Get current time for a timezone or city.
    
    Args:
        location: Timezone name (e.g., "America/New_York"), 
                  city name (e.g., "Tokyo"), or "UTC"
        
    Returns:
        Formatted current time
    """
    location = location.strip()
    if not location:
        location = "UTC"
    
    # Find the timezone
    timezone_name = find_timezone(location)
    
    if timezone_name:
        # Try API first for more accurate time
        api_result = await get_time_from_api(timezone_name)
        if api_result:
            return api_result
        
        # Fall back to local calculation
        try:
            tz = ZoneInfo(timezone_name)
            now = datetime.now(tz)
            return format_time(now, timezone_name)
        except Exception as e:
            logger.error(f"Error getting time for {timezone_name}: {e}")
    
    # If timezone not found, try API directly (might have different naming)
    api_result = await get_time_from_api(location)
    if api_result:
        return api_result
    
    # Provide helpful error
    return f"""❌ Unable to find timezone for: "{location}"

**Try one of these formats:**
• City name: "Tokyo", "New York", "London"
• Timezone: "America/New_York", "Europe/Paris", "Asia/Tokyo"
• "UTC" for Coordinated Universal Time

**Common cities:** New York, Los Angeles, London, Paris, Tokyo, Sydney, Mumbai, Dubai, Singapore
"""

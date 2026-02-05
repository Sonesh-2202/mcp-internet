"""
IP Tools - Get your public IP and geolocate IP addresses.

Uses free IP geolocation APIs (no API keys required).
"""

import logging

from ..utils.http_client import fetch_url, fetch_json

logger = logging.getLogger(__name__)


async def get_my_ip() -> str:
    """
    Get your public IP address.
    
    Returns:
        Your public IP address with location info
    """
    # Get IP address
    ip = await fetch_url("https://api.ipify.org")
    
    if not ip:
        # Fallback
        ip = await fetch_url("https://ifconfig.me/ip")
    
    if not ip:
        return "❌ Error: Unable to determine your public IP address."
    
    ip = ip.strip()
    
    # Get location info for this IP
    geo_data = await fetch_json(f"http://ip-api.com/json/{ip}")
    
    if geo_data and geo_data.get("status") == "success":
        country = geo_data.get("country", "Unknown")
        region = geo_data.get("regionName", "Unknown")
        city = geo_data.get("city", "Unknown")
        isp = geo_data.get("isp", "Unknown")
        
        return f"""🌐 **Your Public IP Address**
{'=' * 40}

📍 IP Address: {ip}

📌 Location:
   🏙️ City: {city}
   🗺️ Region: {region}
   🌍 Country: {country}
   
🔌 ISP: {isp}
"""
    else:
        return f"""🌐 **Your Public IP Address**
{'=' * 40}

📍 IP Address: {ip}
"""


async def geolocate_ip(ip: str) -> str:
    """
    Get geolocation information for an IP address.
    
    Args:
        ip: The IP address to look up (IPv4 or IPv6)
        
    Returns:
        Location and network information for the IP
    """
    if not ip.strip():
        return "❌ Error: Please provide an IP address."
    
    ip = ip.strip()
    
    # Validate IP format (basic check)
    if not any(c.isdigit() for c in ip):
        return "❌ Error: Invalid IP address format."
    
    # Use ip-api.com (free, no registration, 45 requests/minute)
    geo_data = await fetch_json(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
    
    if not geo_data:
        return f"❌ Error: Unable to look up IP address '{ip}'."
    
    if geo_data.get("status") == "fail":
        message = geo_data.get("message", "Unknown error")
        return f"❌ Error: {message}"
    
    # Extract data
    country = geo_data.get("country", "Unknown")
    country_code = geo_data.get("countryCode", "")
    region = geo_data.get("regionName", "Unknown")
    city = geo_data.get("city", "Unknown")
    zip_code = geo_data.get("zip", "")
    lat = geo_data.get("lat", 0)
    lon = geo_data.get("lon", 0)
    timezone = geo_data.get("timezone", "Unknown")
    isp = geo_data.get("isp", "Unknown")
    org = geo_data.get("org", "Unknown")
    as_info = geo_data.get("as", "Unknown")
    
    # Country flag emoji
    flag = ""
    if country_code:
        flag = "".join(chr(ord(c) + 127397) for c in country_code.upper())
    
    return f"""📍 **IP Geolocation: {ip}**
{'=' * 40}

🗺️ **Location**
   {flag} Country: {country}
   🏙️ City: {city}
   🗺️ Region: {region}
   📮 ZIP: {zip_code}
   📐 Coordinates: {lat}, {lon}
   🕐 Timezone: {timezone}

🔌 **Network**
   📡 ISP: {isp}
   🏢 Organization: {org}
   🌐 AS: {as_info}
"""

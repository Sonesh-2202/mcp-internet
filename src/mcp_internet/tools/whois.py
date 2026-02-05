"""
WHOIS Lookup Tool - Get domain registration information.

Uses free WHOIS APIs for domain lookups.
"""

import logging
import re
from urllib.parse import urlparse

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)


def extract_domain(input_str: str) -> str:
    """Extract clean domain from URL or domain string."""
    input_str = input_str.strip()
    
    # If it looks like a URL, parse it
    if "://" in input_str:
        parsed = urlparse(input_str)
        domain = parsed.netloc
    else:
        domain = input_str
    
    # Remove www. prefix
    if domain.startswith("www."):
        domain = domain[4:]
    
    # Remove port if present
    if ":" in domain:
        domain = domain.split(":")[0]
    
    # Remove path if accidentally included
    if "/" in domain:
        domain = domain.split("/")[0]
    
    return domain.lower()


async def whois_lookup(domain: str) -> str:
    """
    Look up WHOIS registration information for a domain.
    
    Args:
        domain: Domain name (e.g., 'example.com', 'github.com')
                Can also accept full URLs
        
    Returns:
        Domain registration information including registrar, dates, and nameservers
    """
    if not domain.strip():
        return "❌ Error: Please provide a domain name."
    
    domain = extract_domain(domain)
    
    # Basic domain validation
    if "." not in domain:
        return f"❌ Error: '{domain}' doesn't look like a valid domain name."
    
    # Use RDAP (Registration Data Access Protocol) - modern replacement for WHOIS
    # Try to find the appropriate RDAP server
    
    tld = domain.split(".")[-1].lower()
    
    # Common RDAP endpoints
    rdap_servers = {
        "com": "https://rdap.verisign.com/com/v1/domain/",
        "net": "https://rdap.verisign.com/net/v1/domain/",
        "org": "https://rdap.publicinterestregistry.org/rdap/domain/",
        "io": "https://rdap.nic.io/domain/",
        "dev": "https://rdap.nic.google/domain/",
        "app": "https://rdap.nic.google/domain/",
        "co": "https://rdap.nic.co/domain/",
    }
    
    rdap_url = rdap_servers.get(tld)
    
    if rdap_url:
        data = await fetch_json(f"{rdap_url}{domain}")
        
        if data and "errorCode" not in data:
            return format_rdap_response(domain, data)
    
    # Fallback to a WHOIS API service
    whois_api_url = f"https://whois.freeaiapi.xyz/?name={domain}"
    
    data = await fetch_json(whois_api_url)
    
    if data and data.get("status") == "success":
        return format_whois_api_response(domain, data.get("whois", {}))
    
    # If all else fails, return a basic message with alternative
    return f"""❌ Unable to perform WHOIS lookup for '{domain}'.

The domain may not exist, or the TLD (.{tld}) is not supported.

🔍 Try these alternatives:
   • https://whois.domaintools.com/{domain}
   • https://www.whois.com/whois/{domain}
   • https://lookup.icann.org/en/lookup?name={domain}
"""


def format_rdap_response(domain: str, data: dict) -> str:
    """Format RDAP response into readable output."""
    
    # Extract key information
    handle = data.get("handle", "N/A")
    status = data.get("status", [])
    
    # Get events (registration, expiration, etc.)
    events = {}
    for event in data.get("events", []):
        action = event.get("eventAction", "")
        date = event.get("eventDate", "")[:10] if event.get("eventDate") else "N/A"
        events[action] = date
    
    registration_date = events.get("registration", "N/A")
    expiration_date = events.get("expiration", "N/A")
    last_updated = events.get("last changed", events.get("last update", "N/A"))
    
    # Get nameservers
    nameservers = []
    for ns in data.get("nameservers", []):
        ns_name = ns.get("ldhName", "")
        if ns_name:
            nameservers.append(ns_name.lower())
    
    # Get registrar info
    registrar = "N/A"
    for entity in data.get("entities", []):
        roles = entity.get("roles", [])
        if "registrar" in roles:
            vcard = entity.get("vcardArray", [])
            if len(vcard) > 1:
                for item in vcard[1]:
                    if item[0] == "fn":
                        registrar = item[3]
                        break
    
    # Build status string
    status_emoji = "✅" if "active" in [s.lower() for s in status] else "⚠️"
    status_str = ", ".join(status[:3]) if status else "N/A"
    
    output = f"""🔍 **WHOIS Lookup: {domain}**
{'=' * 50}

{status_emoji} **Status**: {status_str}

📅 **Dates**
   📝 Registered: {registration_date}
   ⏰ Expires: {expiration_date}
   🔄 Last Updated: {last_updated}

🏢 **Registrar**: {registrar}
"""
    
    if nameservers:
        output += f"\n🌐 **Nameservers**\n"
        for ns in nameservers[:4]:
            output += f"   • {ns}\n"
    
    return output


def format_whois_api_response(domain: str, data: dict) -> str:
    """Format WHOIS API response into readable output."""
    
    registrar = data.get("registrar", "N/A")
    creation_date = data.get("creation_date", "N/A")
    expiration_date = data.get("expiration_date", "N/A")
    updated_date = data.get("updated_date", "N/A")
    nameservers = data.get("name_servers", [])
    status = data.get("status", [])
    
    if isinstance(status, str):
        status = [status]
    
    status_emoji = "✅" if any("active" in s.lower() for s in status) else "⚠️"
    status_str = ", ".join(status[:2]) if status else "N/A"
    
    output = f"""🔍 **WHOIS Lookup: {domain}**
{'=' * 50}

{status_emoji} **Status**: {status_str}

📅 **Dates**
   📝 Created: {creation_date}
   ⏰ Expires: {expiration_date}
   🔄 Updated: {updated_date}

🏢 **Registrar**: {registrar}
"""
    
    if nameservers:
        if isinstance(nameservers, str):
            nameservers = [nameservers]
        output += f"\n🌐 **Nameservers**\n"
        for ns in nameservers[:4]:
            output += f"   • {ns}\n"
    
    return output

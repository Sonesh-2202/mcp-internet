"""
QR Code Generator Tool - Create QR codes for URLs and text.

Uses free QR code generation APIs.
"""

import logging
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)


async def generate_qr(
    content: str,
    size: int = 200,
    format: str = "png"
) -> str:
    """
    Generate a QR code for text or URL.
    
    Args:
        content: The text, URL, or data to encode in the QR code
        size: Size in pixels (default: 200, range: 50-500)
        format: Image format - 'png' or 'svg' (default: 'png')
        
    Returns:
        URL to the generated QR code image
        
    Special formats supported:
        - URLs: https://example.com
        - WiFi: Use generate_wifi_qr() for WiFi credentials
        - Phone: tel:+1234567890
        - SMS: sms:+1234567890?body=Hello
        - Email: mailto:user@example.com
    """
    if not content.strip():
        return "❌ Error: Please provide content for the QR code."
    
    # Validate size
    size = max(50, min(size, 500))
    
    # Use QR Server API (free, no registration)
    encoded_content = quote(content)
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={encoded_content}"
    
    if format.lower() == "svg":
        qr_url += "&format=svg"
    
    return f"""🔲 **QR Code Generated**
{'=' * 40}

📝 Content: {content[:100]}{'...' if len(content) > 100 else ''}
📐 Size: {size}x{size} pixels

🖼️ QR Code URL:
{qr_url}

💡 Tip: Right-click the link and "Save As" to download the QR code.
"""


async def generate_wifi_qr(
    ssid: str,
    password: str,
    security: str = "WPA",
    hidden: bool = False
) -> str:
    """
    Generate a QR code for WiFi network credentials.
    
    Args:
        ssid: WiFi network name
        password: WiFi password
        security: Security type - 'WPA', 'WEP', or 'nopass' (default: 'WPA')
        hidden: Whether the network is hidden (default: False)
        
    Returns:
        URL to the generated QR code that can be scanned to connect to WiFi
    """
    if not ssid.strip():
        return "❌ Error: Please provide the WiFi network name (SSID)."
    
    # Validate security type
    security = security.upper()
    if security not in ["WPA", "WEP", "nopass"]:
        security = "WPA"
    
    # Build WiFi QR code content
    # Format: WIFI:T:WPA;S:ssid;P:password;H:true/false;;
    hidden_str = "true" if hidden else "false"
    
    # Escape special characters
    def escape_wifi(s):
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace('"', '\\"').replace(":", "\\:")
    
    wifi_content = f"WIFI:T:{security};S:{escape_wifi(ssid)};P:{escape_wifi(password)};H:{hidden_str};;"
    
    # Generate QR code
    encoded_content = quote(wifi_content)
    size = 250
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={encoded_content}"
    
    return f"""📶 **WiFi QR Code Generated**
{'=' * 40}

📡 Network: {ssid}
🔐 Security: {security}
👁️ Hidden: {'Yes' if hidden else 'No'}

🖼️ QR Code URL:
{qr_url}

📱 Scan this QR code with your phone camera to connect to the WiFi network automatically!

💡 Tip: Print this QR code and place it somewhere visible for guests.
"""


async def generate_vcard_qr(
    name: str,
    phone: str = "",
    email: str = "",
    organization: str = "",
    title: str = "",
    website: str = ""
) -> str:
    """
    Generate a QR code for a contact card (vCard).
    
    Args:
        name: Full name
        phone: Phone number
        email: Email address
        organization: Company/Organization name
        title: Job title
        website: Website URL
        
    Returns:
        URL to the generated QR code that adds contact info when scanned
    """
    if not name.strip():
        return "❌ Error: Please provide a name for the contact card."
    
    # Build vCard content
    vcard_parts = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{name}",
        f"FN:{name}",
    ]
    
    if phone:
        vcard_parts.append(f"TEL:{phone}")
    if email:
        vcard_parts.append(f"EMAIL:{email}")
    if organization:
        vcard_parts.append(f"ORG:{organization}")
    if title:
        vcard_parts.append(f"TITLE:{title}")
    if website:
        vcard_parts.append(f"URL:{website}")
    
    vcard_parts.append("END:VCARD")
    
    vcard_content = "\n".join(vcard_parts)
    
    # Generate QR code
    encoded_content = quote(vcard_content)
    size = 250
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={encoded_content}"
    
    return f"""👤 **Contact QR Code Generated**
{'=' * 40}

📝 Name: {name}
📱 Phone: {phone or 'N/A'}
📧 Email: {email or 'N/A'}
🏢 Organization: {organization or 'N/A'}
💼 Title: {title or 'N/A'}
🌐 Website: {website or 'N/A'}

🖼️ QR Code URL:
{qr_url}

📱 Scan this QR code to add the contact to your phone!
"""

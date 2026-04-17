"""
Translation Tool - Translate text between languages.

Uses Google Translate's free API endpoint (no API key required).
"""

import logging
import json
from urllib.parse import quote

from ..utils.http_client import fetch_url

logger = logging.getLogger(__name__)

# Common language codes
LANGUAGES = {
    "english": "en", "spanish": "es", "french": "fr", "german": "de",
    "italian": "it", "portuguese": "pt", "russian": "ru", "japanese": "ja",
    "korean": "ko", "chinese": "zh", "arabic": "ar", "hindi": "hi",
    "dutch": "nl", "polish": "pl", "turkish": "tr", "vietnamese": "vi",
    "thai": "th", "swedish": "sv", "danish": "da", "finnish": "fi",
    "norwegian": "no", "greek": "el", "hebrew": "he", "indonesian": "id",
    "malay": "ms", "filipino": "fil", "czech": "cs", "romanian": "ro",
    "hungarian": "hu", "ukrainian": "uk", "bengali": "bn", "tamil": "ta",
    "telugu": "te", "marathi": "mr", "gujarati": "gu", "urdu": "ur",
}


def get_language_code(lang: str) -> str:
    """Convert language name to code."""
    lang = lang.lower().strip()
    
    # Already a code?
    if len(lang) <= 3:
        return lang
    
    return LANGUAGES.get(lang, lang)


async def translate_text(
    text: str,
    to_language: str = "english",
    from_language: str = "auto"
) -> str:
    """
    Translate text between languages.
    
    Args:
        text: The text to translate
        to_language: Target language (name or code, e.g., 'spanish', 'es')
        from_language: Source language (default: 'auto' for auto-detect)
        
    Returns:
        Translated text with language information
    """
    if not text.strip():
        return "❌ Error: Please provide text to translate."
    
    # Get language codes
    to_code = get_language_code(to_language)
    from_code = get_language_code(from_language) if from_language != "auto" else "auto"
    
    # Use Google Translate API (unofficial but free)
    encoded_text = quote(text)
    
    # Try the unofficial Google Translate API
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={from_code}&tl={to_code}&dt=t&q={encoded_text}"
    
    response = await fetch_url(url)
    
    if not response:
        return "❌ Error: Unable to translate. Service may be temporarily unavailable."
    
    try:
        # Parse the response (it's a nested array)
        data = json.loads(response)
        
        # Extract translated text
        translated_parts = []
        for part in data[0]:
            if part[0]:
                translated_parts.append(part[0])
        
        translated_text = "".join(translated_parts)
        
        # Get detected source language
        detected_lang = data[2] if len(data) > 2 else from_code
        
        # Get full language names
        lang_names = {v: k.title() for k, v in LANGUAGES.items()}
        from_name = lang_names.get(detected_lang, detected_lang.upper())
        to_name = lang_names.get(to_code, to_code.upper())
        
        output = f"""🌐 **Translation**
{'=' * 40}

📝 **Original** ({from_name}):
{text}

✨ **Translated** ({to_name}):
{translated_text}
"""
        return output
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return "❌ Error: Unable to parse translation response."


async def detect_language(text: str) -> str:
    """
    Detect the language of a text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Detected language information
    """
    if not text.strip():
        return "❌ Error: Please provide text to analyze."
    
    encoded_text = quote(text[:200])  # Limit to 200 chars for detection
    
    # Use same API for detection
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={encoded_text}"
    
    response = await fetch_url(url)
    
    if not response:
        return "❌ Error: Unable to detect language."
    
    try:
        data = json.loads(response)
        
        detected_lang = data[2] if len(data) > 2 else "unknown"
        
        # Get full language name
        lang_names = {v: k.title() for k, v in LANGUAGES.items()}
        lang_name = lang_names.get(detected_lang, detected_lang.upper())
        
        return f"""🔍 **Language Detection**
{'=' * 40}

📝 Text: "{text[:100]}{'...' if len(text) > 100 else ''}"

🌐 Detected Language: **{lang_name}** ({detected_lang})
"""
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return "❌ Error: Unable to detect language."

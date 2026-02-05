"""
Dictionary/Definition Tool - Get definitions from Wikipedia API.

Uses Wikipedia's REST API to fetch article summaries and definitions.
Falls back to Free Dictionary API for word definitions.
"""

import logging
from urllib.parse import quote

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)

# API endpoints
WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary"
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en"


async def get_wikipedia_summary(term: str) -> str | None:
    """Get Wikipedia summary for a term."""
    encoded_term = quote(term.replace(" ", "_"))
    url = f"{WIKIPEDIA_API}/{encoded_term}"
    
    data = await fetch_json(url)
    if not data or "extract" not in data:
        return None
    
    title = data.get("title", term)
    description = data.get("description", "")
    extract = data.get("extract", "")
    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
    
    output = f"""📚 **{title}**"""
    if description:
        output += f"\n*{description}*"
    output += f"\n\n{extract}"
    if page_url:
        output += f"\n\n🔗 Read more: {page_url}"
    
    return output


async def get_dictionary_definition(word: str) -> str | None:
    """Get dictionary definition for a single word."""
    url = f"{DICTIONARY_API}/{quote(word.lower())}"
    
    data = await fetch_json(url)
    if not data or not isinstance(data, list):
        return None
    
    try:
        entry = data[0]
        word_text = entry.get("word", word)
        phonetic = entry.get("phonetic", "")
        
        output = f"📖 **{word_text}**"
        if phonetic:
            output += f" {phonetic}"
        output += "\n" + "=" * 40
        
        meanings = entry.get("meanings", [])
        for meaning in meanings[:3]:  # Limit to 3 parts of speech
            part_of_speech = meaning.get("partOfSpeech", "")
            definitions = meaning.get("definitions", [])
            
            output += f"\n\n**{part_of_speech.capitalize()}**"
            
            for i, defn in enumerate(definitions[:3], 1):  # Limit to 3 definitions
                definition = defn.get("definition", "")
                example = defn.get("example", "")
                
                output += f"\n{i}. {definition}"
                if example:
                    output += f"\n   *Example: \"{example}\"*"
            
            # Add synonyms if available
            synonyms = meaning.get("synonyms", [])[:5]
            if synonyms:
                output += f"\n   Synonyms: {', '.join(synonyms)}"
        
        return output
        
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing dictionary response: {e}")
        return None


async def get_definition(term: str) -> str:
    """
    Get definition or summary for a term.
    
    Tries Wikipedia first for topics/phrases, falls back to
    dictionary for single words.
    
    Args:
        term: The word or topic to look up
        
    Returns:
        Definition or summary
    """
    if not term.strip():
        return "❌ Error: Please provide a term to look up."
    
    term = term.strip()
    
    # Try Wikipedia first (good for topics, phrases, concepts)
    wiki_result = await get_wikipedia_summary(term)
    if wiki_result:
        return wiki_result
    
    # For single words, try dictionary
    if len(term.split()) == 1:
        dict_result = await get_dictionary_definition(term)
        if dict_result:
            return dict_result
    
    # If both fail, provide helpful message
    return f"""❌ No definition found for: "{term}"

Suggestions:
• Check the spelling
• Try a more common term
• For people or places, use their full proper name
• For technical terms, try including context (e.g., "Python programming language")
"""

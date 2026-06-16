"""
Domain-Specific Content Extractors — Structured data extraction from known websites.

Each extractor knows how to parse a specific domain's HTML and return structured
data (dicts/lists) that can be formatted into markdown tables or bullet points.

Registry pattern: domain substring → extractor function.
"""

import json
import logging
import re

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


# =============================================================================
# GENERIC STRUCTURED DATA EXTRACTION
# =============================================================================

def extract_json_ld(soup: BeautifulSoup) -> list[dict]:
    """Extract JSON-LD structured data (Schema.org) from the page."""
    results = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                results.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return results


def extract_opengraph(soup: BeautifulSoup) -> dict:
    """Extract OpenGraph meta tags."""
    og = {}
    for meta in soup.find_all("meta", property=re.compile(r"^og:")):
        key = meta.get("property", "").replace("og:", "")
        value = meta.get("content", "")
        if key and value:
            og[key] = value
    return og


def extract_html_tables(soup: BeautifulSoup, max_tables: int = 3, max_rows: int = 25) -> list[dict]:
    """
    Extract HTML tables and convert to structured data.
    
    Returns list of dicts with 'headers' and 'rows' keys.
    """
    tables = []
    for table in soup.find_all("table")[:max_tables]:
        # Extract headers
        headers = []
        thead = table.find("thead")
        if thead:
            for th in thead.find_all(["th", "td"]):
                headers.append(th.get_text(strip=True))
        
        if not headers:
            # Try first row
            first_row = table.find("tr")
            if first_row:
                for cell in first_row.find_all(["th", "td"]):
                    headers.append(cell.get_text(strip=True))
        
        if not headers:
            continue
        
        # Extract rows
        rows = []
        all_rows = table.find_all("tr")
        start_idx = 1 if headers else 0  # Skip header row
        
        for tr in all_rows[start_idx:max_rows + start_idx]:
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells and any(c.strip() for c in cells):
                rows.append(cells)
        
        if rows:
            tables.append({"headers": headers, "rows": rows})
    
    return tables


def tables_to_markdown(tables: list[dict]) -> str:
    """Convert extracted tables to markdown format."""
    output = ""
    for table in tables:
        headers = table["headers"]
        rows = table["rows"]
        
        if not headers or not rows:
            continue
        
        # Normalize row lengths to match headers
        num_cols = len(headers)
        
        # Header row
        output += "| " + " | ".join(h[:30] for h in headers) + " |\n"
        output += "| " + " | ".join("---" for _ in headers) + " |\n"
        
        for row in rows:
            # Pad or trim row to match header count
            padded = (row + [""] * num_cols)[:num_cols]
            output += "| " + " | ".join(c[:50] for c in padded) + " |\n"
        
        output += "\n"
    
    return output


# =============================================================================
# DOMAIN-SPECIFIC EXTRACTORS
# =============================================================================

def extract_wikipedia(soup: BeautifulSoup, url: str) -> dict:
    """Extract structured data from Wikipedia pages."""
    result = {"source": "Wikipedia", "type": "encyclopedia"}
    
    # Title
    title_elem = soup.find("h1", id="firstHeading")
    if title_elem:
        result["title"] = title_elem.get_text(strip=True)
    
    # Infobox
    infobox = soup.find("table", class_="infobox")
    if infobox:
        info_data = {}
        for row in infobox.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = th.get_text(strip=True)
                value = td.get_text(separator=" ", strip=True)
                if key and value and len(value) < 200:
                    info_data[key] = value
        if info_data:
            result["infobox"] = info_data
    
    # Lead paragraphs (summary)
    content_div = soup.find("div", class_="mw-parser-output")
    if content_div:
        paragraphs = []
        for p in content_div.find_all("p", recursive=False):
            text = p.get_text(strip=True)
            if text and len(text) > 50:
                paragraphs.append(text)
                if len(paragraphs) >= 3:
                    break
        if paragraphs:
            result["summary"] = "\n\n".join(paragraphs)
    
    return result


def extract_imdb(soup: BeautifulSoup, url: str) -> dict:
    """Extract movie/show data from IMDb pages."""
    result = {"source": "IMDb", "type": "entertainment"}
    
    # JSON-LD is the richest source on IMDb
    ld_data = extract_json_ld(soup)
    for item in ld_data:
        item_type = item.get("@type", "")
        if item_type in ("Movie", "TVSeries", "TVEpisode"):
            result["title"] = item.get("name", "")
            result["description"] = item.get("description", "")
            result["genre"] = item.get("genre", [])
            result["date_published"] = item.get("datePublished", "")
            result["content_rating"] = item.get("contentRating", "")
            
            rating = item.get("aggregateRating", {})
            if rating:
                result["imdb_rating"] = rating.get("ratingValue", "")
                result["vote_count"] = rating.get("ratingCount", "")
            
            director = item.get("director", [])
            if isinstance(director, list):
                result["director"] = [d.get("name", "") for d in director if isinstance(d, dict)]
            elif isinstance(director, dict):
                result["director"] = [director.get("name", "")]
            
            actors = item.get("actor", [])
            if isinstance(actors, list):
                result["cast"] = [a.get("name", "") for a in actors[:10] if isinstance(a, dict)]
            
            result["duration"] = item.get("duration", "")
            break
    
    # Fallback: parse title from the page
    if "title" not in result:
        title_elem = soup.find("h1")
        if title_elem:
            result["title"] = title_elem.get_text(strip=True)
    
    # For list pages (e.g., "Now Playing"), extract movie list
    if "/title/" not in url:
        movies = []
        for item_div in soup.find_all("div", class_=re.compile(r"lister-item|ipc-metadata-list-summary-item")):
            title_link = item_div.find("a")
            if title_link:
                movie_title = title_link.get_text(strip=True)
                if movie_title:
                    movies.append({"title": movie_title})
        
        if not movies:
            # Try structured list items
            for li in soup.select(".ipc-metadata-list-summary-item, .lister-item"):
                title_el = li.find(["h3", "a"])
                if title_el:
                    movies.append({"title": title_el.get_text(strip=True)})
        
        if movies:
            result["movies"] = movies[:20]
    
    return result


def extract_linkedin(soup: BeautifulSoup, url: str) -> dict:
    """Extract profile data from LinkedIn public profiles."""
    result = {"source": "LinkedIn", "type": "profile"}
    
    # JSON-LD (if available on public profiles)
    ld_data = extract_json_ld(soup)
    for item in ld_data:
        if item.get("@type") == "Person":
            result["name"] = item.get("name", "")
            result["job_title"] = item.get("jobTitle", "")
            result["description"] = item.get("description", "")
            address = item.get("address", {})
            if isinstance(address, dict):
                result["location"] = address.get("addressLocality", "")
            break
    
    # OpenGraph fallback
    og = extract_opengraph(soup)
    if og:
        if "title" in og and "name" not in result:
            result["name"] = og["title"].split(" - ")[0].split(" | ")[0].strip()
        if "description" in og and "description" not in result:
            result["description"] = og["description"]
    
    # Parse main content
    main = soup.find("main")
    if main:
        # Extract sections
        text_content = main.get_text(separator="\n", strip=True)
        
        # Try to extract experience, education, skills from section headers
        sections = {}
        current_section = "general"
        for line in text_content.split("\n"):
            line = line.strip()
            if not line:
                continue
            lower = line.lower()
            if lower in ("experience", "education", "skills", "about", "licenses & certifications"):
                current_section = lower
                sections[current_section] = []
            elif current_section in sections:
                sections[current_section].append(line)
        
        for section, lines in sections.items():
            if lines:
                result[section] = "\n".join(lines[:15])
    
    return result


def extract_generic(soup: BeautifulSoup, url: str) -> dict:
    """Generic extraction: tries JSON-LD, OpenGraph, tables, then main content."""
    result = {"source": url.split("/")[2] if "/" in url else url}
    
    # Title
    title = soup.find("title")
    if title:
        result["title"] = title.get_text(strip=True)
    
    # JSON-LD
    ld_data = extract_json_ld(soup)
    if ld_data:
        for item in ld_data[:3]:
            item_type = item.get("@type", "")
            if item_type:
                result["schema_type"] = item_type
                # Extract common fields
                for field in ["name", "description", "datePublished", "author", "headline"]:
                    if field in item:
                        val = item[field]
                        if isinstance(val, dict):
                            val = val.get("name", str(val))
                        elif isinstance(val, list):
                            val = ", ".join(v.get("name", str(v)) if isinstance(v, dict) else str(v) for v in val[:5])
                        result[field] = str(val)[:300]
                break
    
    # OpenGraph
    og = extract_opengraph(soup)
    if og:
        for key in ["title", "description", "site_name"]:
            if key in og and key not in result:
                result[key] = og[key]
    
    # Tables
    tables = extract_html_tables(soup)
    if tables:
        result["tables"] = tables
    
    return result


# =============================================================================
# EXTRACTOR REGISTRY
# =============================================================================

# Domain substring → extractor function
_EXTRACTORS = {
    "wikipedia.org": extract_wikipedia,
    "imdb.com": extract_imdb,
    "linkedin.com": extract_linkedin,
}


def get_extractor(url: str):
    """Get the appropriate extractor for a URL, falling back to generic."""
    url_lower = url.lower()
    for domain, extractor in _EXTRACTORS.items():
        if domain in url_lower:
            return extractor
    return extract_generic


def extract_structured_data(html: str, url: str) -> dict:
    """
    Parse HTML and extract structured data using the appropriate domain extractor.
    
    Args:
        html: Raw HTML content
        url: The URL the HTML was fetched from
        
    Returns:
        Dictionary with extracted structured data
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        extractor = get_extractor(url)
        return extractor(soup, url)
    except Exception as e:
        logger.error(f"Extraction error for {url}: {e}")
        return {"source": url, "error": str(e)}


def format_extracted_data(data: dict) -> str:
    """
    Format extracted structured data into readable markdown.
    
    Args:
        data: Extracted data dictionary
        
    Returns:
        Formatted markdown string
    """
    lines = []
    source = data.get("source", "Unknown")
    data_type = data.get("type", "")
    
    # Title
    title = data.get("title", data.get("name", ""))
    if title:
        lines.append(f"### {title}")
        lines.append(f"*Source: {source}*\n")
    else:
        lines.append(f"### Data from {source}\n")
    
    # Description/summary
    for field in ["description", "summary", "headline"]:
        if field in data:
            lines.append(data[field][:500])
            lines.append("")
            break
    
    # Infobox (Wikipedia)
    if "infobox" in data:
        lines.append("**Key Facts:**")
        for key, value in list(data["infobox"].items())[:15]:
            lines.append(f"- **{key}:** {value}")
        lines.append("")
    
    # Movie-specific fields
    if data_type == "entertainment":
        details = []
        if "genre" in data:
            genres = data["genre"] if isinstance(data["genre"], list) else [data["genre"]]
            details.append(f"- **Genre:** {', '.join(genres)}")
        if "imdb_rating" in data:
            details.append(f"- **IMDb Rating:** {data['imdb_rating']}/10 ({data.get('vote_count', 'N/A')} votes)")
        if "date_published" in data:
            details.append(f"- **Released:** {data['date_published']}")
        if "content_rating" in data:
            details.append(f"- **Rated:** {data['content_rating']}")
        if "duration" in data:
            details.append(f"- **Duration:** {data['duration']}")
        if "director" in data:
            details.append(f"- **Director:** {', '.join(data['director'])}")
        if "cast" in data:
            details.append(f"- **Cast:** {', '.join(data['cast'][:8])}")
        
        if details:
            lines.extend(details)
            lines.append("")
    
    # Movie list
    if "movies" in data:
        lines.append("**Movies:**\n")
        lines.append("| # | Title |")
        lines.append("| --- | --- |")
        for i, movie in enumerate(data["movies"][:20], 1):
            lines.append(f"| {i} | {movie.get('title', 'Unknown')} |")
        lines.append("")
    
    # Profile fields (LinkedIn)
    if data_type == "profile":
        if "job_title" in data:
            lines.append(f"- **Current Role:** {data['job_title']}")
        if "location" in data:
            lines.append(f"- **Location:** {data['location']}")
        
        for section in ["about", "experience", "education", "skills"]:
            if section in data:
                lines.append(f"\n**{section.title()}:**")
                content = data[section]
                if isinstance(content, str):
                    for line in content.split("\n")[:10]:
                        if line.strip():
                            lines.append(f"  - {line.strip()}")
        lines.append("")
    
    # Tables
    if "tables" in data:
        lines.append(tables_to_markdown(data["tables"]))
    
    return "\n".join(lines)

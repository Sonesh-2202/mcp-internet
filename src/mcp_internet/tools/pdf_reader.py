"""
PDF Reader Tool - Extract text from PDF URLs.

Uses pdfplumber or basic PDF parsing for text extraction.
"""

import logging
import io
import re

from ..utils.http_client import fetch_url

logger = logging.getLogger(__name__)


async def read_pdf(url: str, max_pages: int = 5, max_length: int = 5000) -> str:
    """
    Extract text content from a PDF URL.
    
    Args:
        url: URL of the PDF file
        max_pages: Maximum number of pages to extract (default: 5)
        max_length: Maximum characters to return (default: 5000)
        
    Returns:
        Extracted text from the PDF
    """
    if not url.strip():
        return "❌ Error: Please provide a PDF URL."
    
    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    # Validate URL looks like a PDF
    if not url.lower().endswith('.pdf') and 'pdf' not in url.lower():
        logger.warning(f"URL may not be a PDF: {url}")
    
    try:
        import httpx
        
        # Fetch PDF with binary mode
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            pdf_bytes = response.content
        
        if not pdf_bytes:
            return "❌ Error: Unable to download PDF."
        
        # Check if it's actually a PDF
        if not pdf_bytes[:5] == b'%PDF-':
            return "❌ Error: The URL does not point to a valid PDF file."
        
        try:
            # Try pdfplumber first
            import pdfplumber
            
            text_content = []
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                total_pages = len(pdf.pages)
                pages_to_read = min(max_pages, total_pages)
                
                for i in range(pages_to_read):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- Page {i+1} ---\n{text}")
            
            if not text_content:
                return "❌ Error: No text could be extracted from this PDF. It may contain only images."
            
            full_text = "\n\n".join(text_content)
            
            # Truncate if needed
            if len(full_text) > max_length:
                full_text = full_text[:max_length] + "\n\n[Content truncated...]"
            
            return f"""📄 **PDF Content**
🔗 {url}
📖 Pages: {pages_to_read}/{total_pages}
{'=' * 50}

{full_text}
"""
            
        except ImportError:
            # Fallback: Basic PDF text extraction without pdfplumber
            # Try to extract text using basic patterns
            text = pdf_bytes.decode('latin-1', errors='ignore')
            
            # Extract text between BT and ET markers (simplified)
            text_parts = re.findall(r'\((.*?)\)', text)
            extracted = ' '.join(text_parts)[:max_length]
            
            if len(extracted) < 100:
                return """❌ Error: Unable to extract text from this PDF.

💡 To enable full PDF support, install pdfplumber:
   pip install pdfplumber
"""
            
            return f"""📄 **PDF Content** (Basic extraction)
🔗 {url}
{'=' * 50}

{extracted}

💡 Note: For better PDF extraction, install pdfplumber:
   pip install pdfplumber
"""
        
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        return f"❌ Error: Unable to read PDF. {str(e)}"

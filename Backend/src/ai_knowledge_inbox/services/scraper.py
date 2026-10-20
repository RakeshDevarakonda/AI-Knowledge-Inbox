import re
import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException
from ai_knowledge_inbox.config import logger

async def _fetch_via_reader(url: str) -> dict | None:
    """
    Fallback reader service for websites protected by Cloudflare Turnstile,
    Akamai, or JavaScript anti-bot challenges (e.g. openai.com, medium.com).
    """
    reader_url = f"https://r.jina.ai/{url}"
    logger.info("Direct fetch blocked; attempting resilient reader fetch for: %s", url)
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(reader_url)
            if resp.status_code == 200 and resp.text.strip():
                full_text = resp.text
                title_match = re.search(r"^Title:\s*(.+)$", full_text, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else url
                
                if "Markdown Content:" in full_text:
                    body_text = full_text.split("Markdown Content:", 1)[1].strip()
                else:
                    body_text = full_text.strip()

                if len(body_text) > 40:
                    logger.info("Resilient reader successfully extracted %d chars for '%s'", len(body_text), title)
                    return {"title": title, "text": body_text}
    except Exception as e:
        logger.warning("Resilient reader fallback failed for %s: %s", url, e)
    return None

async def scrape_url(url: str) -> dict:
    """
    Fetches webpage content server-side, strips scripts, styles, and non-article elements,
    and returns the page title and clean text.
    Includes automated fallback for Cloudflare-protected sites like openai.com.
    """
    clean_url = url.strip()
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
    }

    html_content = ""
    is_blocked = False

    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(clean_url, headers=headers)
            
            # Check if site is blocking requests with anti-bot (e.g. Cloudflare 403/503)
            if response.status_code in (401, 403, 429, 503):
                logger.warning("Direct scrape returned HTTP %d for %s (Likely Cloudflare/anti-bot)", response.status_code, clean_url)
                is_blocked = True
            elif response.status_code >= 400:
                logger.warning("Scraper received error HTTP status %d for URL: %s", response.status_code, clean_url)
                is_blocked = True
            else:
                html_content = response.text
                
    except httpx.RequestError as exc:
        logger.warning("Scraper direct connection failed for URL %s: %s", clean_url, exc)
        is_blocked = True

    # If direct fetch was blocked by Cloudflare or failed, attempt resilient reader
    if is_blocked or not html_content:
        reader_result = await _fetch_via_reader(clean_url)
        if reader_result:
            return reader_result
        raise HTTPException(
            status_code=400,
            detail="Unable to fetch webpage. The site is unreachable or blocked requests. Please verify the URL."
        )

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Strip out non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside", "form"]):
        tag.extract()

    # Extract title
    title = soup.title.string.strip() if (soup.title and soup.title.string) else clean_url

    # Extract and clean plain text
    raw_text = soup.get_text(separator=" ", strip=True)
    
    # If content is empty (e.g. client-side JS app like OpenAI SPA), try resilient reader
    if not raw_text or len(raw_text) < 50:
        reader_result = await _fetch_via_reader(clean_url)
        if reader_result:
            return reader_result
        raise HTTPException(
            status_code=400, 
            detail="Could not extract readable text from this webpage."
        )

    logger.info("Successfully scraped %d characters from '%s' (%s)", len(raw_text), title, clean_url)
    return {
        "title": title,
        "text": raw_text
    }

"""
#Gyan Labs - Web Article & URL Document Scraper
===============================================
Fetches and sanitizes web content from URLs, stripping HTML tags,
extracting article headings, paragraphs, and canonical source metadata.
"""

from typing import List, Dict, Any, Optional
import urllib.request
import re
import html


class WebURLLoader:
    def __init__(self, timeout: int = 15, user_agent: Optional[str] = None):
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GyanLabsRAG/1.0"

    def clean_html(self, raw_html: str) -> str:
        """
        Strips scripts, styles, and tags, converting HTML to clean readable text.
        """
        # Remove script and style elements
        clean = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
        # Replace line breaks and paragraph tags with newlines
        clean = re.sub(r"<(br|p|div|h[1-6]|li)[^>]*>", "\n", clean, flags=re.IGNORECASE)
        # Strip all remaining HTML tags
        clean = re.sub(r"<[^>]+>", " ", clean)
        # Unescape HTML entities
        clean = html.unescape(clean)
        # Normalize whitespace and excessive newlines
        clean = re.sub(r"[ \t]+", " ", clean)
        clean = re.sub(r"\n\s*\n+", "\n\n", clean)
        return clean.strip()

    def load_url(self, url: str) -> Dict[str, Any]:
        """
        Fetches and extracts clean text and metadata from a given URL.
        """
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                raw_bytes = resp.read()
                raw_html = raw_bytes.decode(charset, errors="ignore")

                # Extract title tag if present
                title_match = re.search(r"<title>(.*?)</title>", raw_html, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else url

                clean_text = self.clean_html(raw_html)

                return {
                    "content": clean_text,
                    "metadata": {
                        "source": url,
                        "title": title,
                        "file_type": "web_url",
                        "content_length": len(clean_text)
                    }
                }
        except Exception as e:
            raise RuntimeError(f"Failed to fetch content from {url}: {e}")

    def load_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Fetches multiple URLs sequentially.
        """
        results = []
        for url in urls:
            url = url.strip()
            if not url:
                continue
            try:
                doc = self.load_url(url)
                results.append(doc)
            except Exception as e:
                print(f"Warning: Failed to load URL '{url}': {e}")
        return results

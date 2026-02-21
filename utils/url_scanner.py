
import urllib.request
import re


def fetch_url_text(url: str) -> str:
    """
    Fetch a webpage and extract clean text content.
    Uses only Python stdlib — no extra dependencies.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {"User-Agent": "Mozilla/5.0 (ContentGuard AI Moderation Bot)"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=10) as response:
        raw_html = response.read().decode("utf-8", errors="ignore")

    text = re.sub(r"<script[^>]*>.*?</script>", " ", raw_html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>",  " ", text,     flags=re.DOTALL)
    text = re.sub(r"<[^>]+>",                  " ", text)
    text = re.sub(r"\s+",                       " ", text).strip()

    return text[:5000]  

import html
import re
import time

import aiohttp

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CACHE_TTL = 6 * 60 * 60

_cache: dict = {"ts": 0.0, "data": {}}


def _clean_article(html_text: str) -> str:
    m = re.search(r"<article.*?</article>", html_text, re.S)
    body = m.group(0) if m else html_text
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", body, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"Posted.*?\d{4}(\s+\d+)*\s*\d*\s*$", "", text)
    return " ".join(text.split()).strip()


async def get_rendered_page_text(url: str, force: bool = False) -> str:
    global _cache
    now = time.time()
    if url in _cache["data"] and not force and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"][url]

    text = ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": USER_AGENT}, timeout=15) as resp:
                if resp.status == 200:
                    text = _clean_article(await resp.text())
    except (aiohttp.ClientError, TimeoutError):
        pass

    if text:
        _cache["data"][url] = text
        _cache["ts"] = now
    return text
import html
import re
import time

import aiohttp

GUKAR_URL = "https://man1jember.sch.id/gukar"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CACHE_TTL = 6 * 60 * 60

GUKAR_CATEGORIES = {
    "mipa": "PROFIL GURU MIPA",
    "ips": "PROFIL GURU IPS",
    "bahasa": "PROFIL GURU BAHASA",
    "agama": "PROFIL GURU AGAMA",
    "keterampilan": "PROFIL GURU KETERAMPILAN",
    "olahraga": "PROFIL GURU OLAH RAGA",
    "matematika": "PROFIL GURU MATEMATIKA",
    "bk": "PROFIL GURU BIMBINGAN KONSELING (BK)",
    "karyawan": "PROFIL KARYAWAN",
}

_cache: dict = {"ts": 0.0, "data": {}}


def _clean_title(raw: str) -> str:
    t = raw.replace("_", ".")
    t = re.sub(r"\.{2,}", ".", t)
    t = re.sub(r"-\s+", " ", t)
    t = t.replace("-", " ")
    t = html.unescape(t)
    t = re.sub(r"^[0-9.]+\.?", "", t)
    return " ".join(t.split())


def _parse_sections(html_text: str) -> dict[str, list[str]]:
    parts = re.split(r"(<h4[^>]*>.*?</h4>)", html_text, flags=re.S)
    sections: dict[str, list[str]] = {}
    current = None
    for part in parts:
        text = re.sub(r"<[^>]+>", "", part).strip()
        if part.startswith("<h4") and text.startswith("PROFIL"):
            current = text
            sections[current] = []
            continue
        if current:
            for name in re.findall(r'data-title="([^"]+)"', part):
                sections[current].append(_clean_title(name))
    return sections


async def get_gukar_sections(force: bool = False) -> dict[str, list[str]]:
    global _cache
    now = time.time()
    if not force and _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GUKAR_URL, headers={"User-Agent": USER_AGENT}, timeout=15) as resp:
                if resp.status != 200:
                    return _cache["data"]
                text = await resp.text()
    except (aiohttp.ClientError, TimeoutError):
        return _cache["data"]

    sections = _parse_sections(text)
    _cache = {"ts": now, "data": sections}
    return sections


async def get_gukar_category(key: str) -> tuple[str, list[str]] | None:
    target = GUKAR_CATEGORIES.get(key)
    if not target:
        return None
    sections = await get_gukar_sections()
    names = sections.get(target, [])
    return (target, names) if names else None
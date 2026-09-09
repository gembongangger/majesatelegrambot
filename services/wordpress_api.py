import html
import re

import aiohttp

from config import (
    API_BASE,
    API_FIELDS_CAT,
    API_FIELDS_PAGE,
    API_FIELDS_POST,
    BERITA_LIMIT,
    CACHE_TTL_SECONDS,
    PAGES,
)

_CACHE = {}


async def _get_json(url: str, params: dict, cache_key: str) -> list[dict] | None:
    now = __import__("time").time()
    if cache_key in _CACHE and now - _CACHE[cache_key]["ts"] < CACHE_TTL_SECONDS:
        return _CACHE[cache_key]["data"]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
    except (aiohttp.ClientError, TimeoutError, ValueError):
        return None

    _CACHE[cache_key] = {"ts": now, "data": data}
    return data


async def get_latest_posts(limit: int = BERITA_LIMIT):
    data = await _get_json(
        API_BASE + "/posts",
        {"per_page": limit, "_fields": API_FIELDS_POST},
        f"posts_{limit}",
    )
    if not data:
        return []
    return [
        {"id": p["id"], "title": _strip_html(p["title"]["rendered"]), "date": p["date"], "link": p["link"]}
        for p in data
    ]


async def get_posts_search(query: str, limit: int = 10):
    data = await _get_json(
        API_BASE + "/posts",
        {"search": query, "per_page": limit, "_fields": API_FIELDS_POST},
        f"search_{query.lower()}_{limit}",
    )
    if not data:
        return []
    return [
        {"id": p["id"], "title": _strip_html(p["title"]["rendered"]), "date": p["date"], "link": p["link"]}
        for p in data
    ]


async def get_posts_search_by_title(query: str, keyword: str, limit: int = 5):
    posts = await get_posts_search(query, limit * 2)
    kw = keyword.upper()
    return [p for p in posts if kw in p["title"].upper()][:limit]


async def _slug_to_category_id(slug: str) -> int | None:
    for cat in await get_categories():
        if cat["slug"] == slug:
            return cat["id"]
    return None


async def get_latest_posts_by_category(slug: str, limit: int = BERITA_LIMIT):
    cat_id = await _slug_to_category_id(slug)
    if cat_id is None:
        return []
    params = {"per_page": limit, "_fields": API_FIELDS_POST, "categories": cat_id}
    data = await _get_json(API_BASE + "/posts", params, f"posts_{slug}_{limit}")
    if not data:
        return []
    return [{"id": p["id"], "title": _strip_html(p["title"]["rendered"]), "date": p["date"], "link": p["link"]} for p in data]


def _strip_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(text).strip()


async def get_page(slug: str):
    data = await _get_json(
        API_BASE + "/pages",
        {"slug": slug, "_fields": API_FIELDS_PAGE},
        f"page_{slug}",
    )
    if not data:
        return None
    page = data[0]
    return {
        "title": _strip_html(page["title"]["rendered"]),
        "content": _clean_page_content(page["content"]["rendered"]),
        "link": page["link"],
        "downloads": _extract_downloads(page["content"]["rendered"]),
    }


def _clean_page_content(raw_html: str) -> str:
    text = _strip_html(raw_html)
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    lines = [ln for ln in lines if not ln.lower().startswith("download")]
    return "\n".join(lines).strip()


def _extract_downloads(raw_html: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for m in re.finditer(r"<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>", raw_html, re.S):
        label = _strip_html(m.group(2))
        if label.lower().startswith("download"):
            links.append((label, m.group(1)))
    return links


async def get_categories():
    data = await _get_json(API_BASE + "/categories", {"_fields": API_FIELDS_CAT}, "categories")
    if not data:
        return []
    return [{"id": c["id"], "name": c["name"], "slug": c["slug"]} for c in data]


def resolve_page_slug(key: str) -> str | None:
    return PAGES.get(key)
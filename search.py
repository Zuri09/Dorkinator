"""Brave Search API integration for Dorkinator's authorised AI workflow."""

from __future__ import annotations

import json
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


def extract_urls(payload: dict) -> list[str]:
    return [item["url"] for item in payload.get("web", {}).get("results", []) if isinstance(item.get("url"), str)]


def search_query(query: str, api_key: str, count: int) -> list[str]:
    url = f"{BRAVE_SEARCH_URL}?{urlencode({'q': query, 'count': count})}"
    request = Request(url, headers={"X-Subscription-Token": api_key, "Accept": "application/json"})
    with urlopen(request, timeout=20) as response:
        return extract_urls(json.load(response))


def search_searxng(query: str, base_url: str, count: int) -> list[str]:
    url = f"{base_url.rstrip('/')}/search?{urlencode({'q': query, 'format': 'json', 'categories': 'general'})}"
    with urlopen(url, timeout=20) as response:
        payload = json.load(response)
    return [item["url"] for item in payload.get("results", [])[:count] if isinstance(item.get("url"), str)]


def search_entries(entries: list[dict[str, str]], search, allowed) -> list[str]:
    urls, seen = [], set()
    for entry in entries:
        for url in search(entry["query"]):
            host = urlsplit(url).hostname
            if host and allowed(host) and url not in seen:
                urls.append(url)
                seen.add(url)
    return urls

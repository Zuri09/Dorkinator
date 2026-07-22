#!/usr/bin/env python3
"""Local, scope-bound AI triage for public URLs supplied by an authorised user."""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MAX_BYTES = 1_000_000
MAX_TEXT = 12_000


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def host_in_scope(host: str, scopes: list[str]) -> bool:
    host = host.lower().rstrip(".")
    return any(host == scope or host.endswith("." + scope) for scope in scopes)


def page_text(html: bytes) -> str:
    parser = TextExtractor()
    parser.feed(html.decode("utf-8", errors="replace"))
    return " ".join(" ".join(parser.parts).split())[:MAX_TEXT]


def fetch(url: str, scopes: list[str]) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or not host_in_scope(parsed.hostname, scopes):
        raise ValueError("URL is outside declared scope or does not use HTTP(S)")
    request = Request(url, headers={"User-Agent": "Dorkinator/2.0 authorised-triage"})
    try:
        with build_opener(NoRedirect).open(request, timeout=12) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "text/plain"}:
                raise ValueError(f"unsupported content type: {content_type}")
            return page_text(response.read(MAX_BYTES + 1))
    except HTTPError as error:
        if 300 <= error.code < 400:
            raise ValueError("redirect not followed; review its destination manually") from error
        raise ValueError(f"HTTP {error.code}") from error
    except URLError as error:
        raise ValueError(f"request failed: {error.reason}") from error


def ai_triage(url: str, text: str, model: str) -> dict:
    prompt = f"""You triage public web content for an authorised security assessment.
Return JSON only with keys: verdict (no_finding|possible_exposure|review_needed), summary,
evidence (array of short exact snippets from the supplied text), and next_step.
Do not invent facts. A possible secret or internal detail is not confirmed exposure.
URL: {url}\n\nSUPPLIED TEXT:\n{text}"""
    payload = json.dumps({"model": model, "stream": False, "format": "json", "messages": [{"role": "user", "content": prompt}]}).encode()
    request = Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=120) as response:
            content = json.load(response)["message"]["content"]
        result = json.loads(content)
    except (URLError, OSError, KeyError, json.JSONDecodeError) as error:
        return {"verdict": "review_needed", "summary": f"Local Ollama triage unavailable: {error}", "evidence": [], "next_step": "Confirm Ollama is running and the selected model is installed."}
    if result.get("verdict") not in {"no_finding", "possible_exposure", "review_needed"}:
        result["verdict"] = "review_needed"
    result["url"] = url
    return result


def triage_urls(urls: list[str], scopes: list[str], model: str, limit: int, output: Path) -> list[dict]:
    report = []
    for url in urls[:limit]:
        try:
            text = fetch(url, scopes)
            finding = ai_triage(url, text, model)
        except ValueError as error:
            finding = {"url": url, "verdict": "review_needed", "summary": str(error), "evidence": [], "next_step": "Check the approved scope and URL."}
        report.append(finding)
        print(f"{finding['verdict']}: {url}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def triage_url_file(url_file: str, scopes: list[str], model: str, limit: int, output: Path) -> list[dict]:
    urls = [line.strip() for line in Path(url_file).read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    return triage_urls(urls, scopes, model, limit, output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scope-bound local Ollama triage for approved public URLs.")
    parser.add_argument("urls", help="Newline-delimited URL file; only these URLs are requested")
    parser.add_argument("--scope", action="append", required=True, help="Allowed root domain; repeat for each approved scope")
    parser.add_argument("--model", default="qwen2.5:7b-instruct", help="Installed Ollama model (default: qwen2.5:7b-instruct)")
    parser.add_argument("--limit", type=int, default=20, help="Maximum URLs to request (default: 20)")
    parser.add_argument("--output", default="dorkinator-output/triage.json", help="JSON report path")
    parser.add_argument("--i-have-authorisation", action="store_true", help="Required acknowledgement before requests are sent")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.i_have_authorisation:
        print("error: pass --i-have-authorisation only for approved scope", file=sys.stderr)
        return 2
    scopes = [scope.lower().strip().removeprefix("*.").rstrip(".") for scope in args.scope]
    output = Path(args.output)
    report = triage_url_file(args.urls, scopes, args.model, args.limit, output)
    print(f"Saved {len(report)} triage records to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

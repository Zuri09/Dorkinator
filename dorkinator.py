#!/usr/bin/env python3
"""Dorkinator: build search-query collections for authorised reconnaissance."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

try:
    from colorama import Fore, Style, init
except ImportError:  # Colour is a convenience, never a reason the tool cannot run.
    class _Colour:
        def __getattr__(self, _name):
            return ""
    Fore = Style = _Colour()
    def init(**_kwargs):
        return None


init(autoreset=True)

DORKS = {
    "surface": [
        "site:{d}", "site:*.{d}", "(site:{d} OR site:api.{d} OR site:cdn.{d})",
        "site:{d} (ext:log OR ext:conf OR ext:ini OR ext:env OR ext:bak OR ext:backup OR ext:swp OR ext:old)",
        "site:{d} (ext:js OR ext:php OR ext:asp OR ext:aspx OR ext:jsp)",
        "site:{d} (ext:sql OR ext:db OR ext:sqlite OR ext:csv OR ext:xml)",
        "site:{d} (filetype:pdf OR filetype:xls OR filetype:ppt OR filetype:doc)",
    ],
    "cloud": [
        '(site:pastebin.com OR site:github.com) "{d}"', 'site:s3.amazonaws.com "{d}"',
        'site:blob.core.windows.net "{d}"', 'site:storage.googleapis.com "{d}"',
        'site:sharepoint.com "{d}"', 'site:onedrive.live.com "{d}"', 'site:dropbox.com/s "{d}"',
        'site:box.com/s "{d}"', 'site:openbugbounty.org inurl:reports intext:"{d}"',
    ],
    "api": [
        "site:{d} (inurl:/api/ OR inurl:/v1/ OR inurl:/v2/ OR inurl:/graphql)",
        "site:{d} (inurl:swagger OR inurl:apidocs OR inurl:api-explorer OR inurl:openapi.json)",
        "site:{d} (inurl:graphql OR filetype:gql OR filetype:graphql)",
        'site:{d} (intext:"api_key" OR intext:"token=" OR intext:"client_secret")',
    ],
    "exposure": [
        'site:{d} (intext:"BEGIN RSA PRIVATE KEY" OR intext:"PRIVATE KEY-----")',
        'site:{d} (intext:"AKIA" OR intext:"ASIA" OR intext:"aws_secret_access_key")',
        'site:{d} (intext:"xoxp-" OR intext:"xoxb-")',
        'site:{d} (filetype:doc OR filetype:docx OR filetype:xlsx OR filetype:pptx OR filetype:pdf) (intext:"confidential" OR intext:"internal use only" OR intext:"do not distribute")',
    ],
    "endpoints": [
        "site:{d} (inurl:upload OR inurl:file OR intext:\"choose file\")",
        "site:{d} (inurl:admin OR inurl:dashboard OR inurl:manage OR intitle:Admin)",
        "site:{d} (inurl:test OR inurl:dev OR inurl:staging OR inurl:qa OR inurl:sandbox)",
        "site:{d} (inurl:.git OR inurl:.svn OR inurl:jenkins OR inurl:gitlab OR inurl:bitbucket)",
        "site:{d} (inurl:?q= OR inurl:?search= OR inurl:?keyword= OR inurl:?lang=)",
        "site:{d} (inurl:?id= OR inurl:?cat= OR inurl:?action= OR inurl:?page=)",
        "site:{d} (inurl:?file= OR inurl:?include= OR inurl:?path= OR inurl:?doc=)",
        "site:{d} (inurl:?exec= OR inurl:?cmd= OR inurl:?run= OR inurl:?do=)",
        "site:{d} (inurl:?redirect= OR inurl:?url= OR inurl:?next= OR inurl:?return=)",
        'site:{d} (intitle:"Error" OR intitle:"Exception" OR intext:"Stack trace" OR intext:"Undefined index" OR intext:"SQL syntax")',
        'site:{d} (intext:"<!--" AND (intext:"TODO" OR intext:"FIXME" OR intext:"DEBUG"))',
        'site:{d} (inurl:"/wp-admin/" OR inurl:"/phpmyadmin/" OR inurl:"/xampp/" OR inurl:"/adminer.php")',
    ],
}

DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$", re.I)
ENGINES = {"google": "https://www.google.com/search?q={}", "bing": "https://www.bing.com/search?q={}"}


def normalise_domain(value: str) -> str:
    value = value.strip().lower().removeprefix("https://").removeprefix("http://").split("/", 1)[0]
    if not DOMAIN_RE.fullmatch(value):
        raise ValueError(f"Invalid domain: {value!r}")
    return value


def load_domains(target: str) -> list[str]:
    path = Path(target)
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else [target]
    domains, seen = [], set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        domain = normalise_domain(line)
        if domain not in seen:
            domains.append(domain)
            seen.add(domain)
    return domains


def make_entries(domain: str, engine: str) -> list[dict[str, str]]:
    entries = []
    for category, templates in DORKS.items():
        for template in templates:
            query = template.format(d=domain)
            entries.append({"domain": domain, "category": category, "query": query, "url": ENGINES[engine].format(quote(query))})
    return entries


def write_entries(entries: list[dict[str, str]], output: Path, export_format: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if export_format == "json":
        output.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    elif export_format == "csv":
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["domain", "category", "query", "url"])
            writer.writeheader(); writer.writerows(entries)
    else:
        output.write_text("\n".join(f"[{x['category']}] {x['query']}\n{x['url']}" for x in entries) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate search-query links for authorised reconnaissance.")
    parser.add_argument("target", nargs="?", help="A domain or a newline-delimited file of domains")
    parser.add_argument("-e", "--engine", choices=ENGINES, default="google", help="Search engine (default: google)")
    parser.add_argument("-f", "--format", choices=("txt", "json", "csv"), default="txt", help="Export format")
    parser.add_argument("-o", "--output-dir", default="dorkinator-output", help="Directory for exports")
    parser.add_argument("--ai", action="store_true", help="Searches and locally triages target-domain results; confirms you are authorised")
    parser.add_argument("--search-provider", choices=("auto", "brave", "searxng"), default="auto", help="Search backend for --ai (default: auto)")
    parser.add_argument("--searxng-url", default="http://127.0.0.1:8080", help="SearXNG base URL for --ai (default: http://127.0.0.1:8080)")
    parser.add_argument("--ai-model", default="qwen2.5:7b-instruct", help="Ollama model for --ai (default: qwen2.5:7b-instruct)")
    parser.add_argument("--ai-limit", type=int, default=20, help="Maximum URLs for --ai (default: 20)")
    parser.add_argument("--ai-results", type=int, default=5, help="Search results per query for --ai (1-20; default: 5)")
    parser.add_argument("--no-color", action="store_true", help="Disable terminal colour")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.no_color:
        global Fore, Style
        Fore = Style = type("Plain", (), {"__getattr__": lambda *_: ""})()
    if not args.target:
        print("error: target is required", file=sys.stderr)
        return 2
    if args.ai_limit < 1 or not 1 <= args.ai_results <= 20:
        print("error: --ai-limit must be at least 1 and --ai-results must be 1-20", file=sys.stderr); return 2
    try:
        domains = load_domains(args.target)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr); return 2
    brave_key = os.environ.get("BRAVE_SEARCH_API_KEY")
    if args.ai and args.search_provider == "brave" and not brave_key:
        print("error: Brave needs BRAVE_SEARCH_API_KEY.", file=sys.stderr); return 2
    print(f"{Fore.CYAN}DORKINATOR{Style.RESET_ALL}  engine={args.engine}  queries=all")
    output_dir = Path(args.output_dir)
    all_entries = []
    for domain in domains:
        entries = make_entries(domain, args.engine)
        all_entries.extend(entries)
        output = output_dir / f"{domain}_dorks.{args.format}"
        write_entries(entries, output, args.format)
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} {domain}: {len(entries)} queries → {output}")
    if args.ai:
        from search import search_entries, search_query, search_searxng
        from triage import host_in_scope, triage_urls
        if args.search_provider == "brave" or (args.search_provider == "auto" and brave_key):
            if not brave_key:
                print("error: Brave needs BRAVE_SEARCH_API_KEY.", file=sys.stderr); return 2
            search = lambda query: search_query(query, brave_key, args.ai_results)
            provider = "Brave"
        else:
            search = lambda query: search_searxng(query, args.searxng_url, args.ai_results)
            provider = f"SearXNG ({args.searxng_url})"
        try:
            urls = search_entries(all_entries, search, lambda host: host_in_scope(host, domains))
            report = triage_urls(urls, domains, args.ai_model, args.ai_limit, output_dir / "ai-triage.json")
        except OSError as error:
            print(f"error: {provider} search or triage failed: {error}", file=sys.stderr)
            if args.search_provider == "auto" and not brave_key:
                print("tip: start SearXNG locally, set BRAVE_SEARCH_API_KEY, or choose --search-provider brave.", file=sys.stderr)
            return 2
        possible = sum(item["verdict"] == "possible_exposure" for item in report)
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} AI triage complete: {len(urls)} in-scope result(s), {possible} possible exposure(s) → {output_dir / 'ai-triage.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

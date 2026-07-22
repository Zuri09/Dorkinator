# Dorkinator

An offline search-query collection generator for authorised reconnaissance, OSINT, and bug-bounty workflows.

It generates Google or Bing links for a supplied domain, groups them by purpose, and exports a reviewable collection. It does **not** send targets to a third party; opening a generated search link is the only network action.

## Quick start

```bash
git clone https://github.com/Zuri09/Dorkinator.git
cd Dorkinator
python3 -m pip install -r requirements.txt
python3 dorkinator.py example.com
```

`colorama` is optional—the tool still works without it, just without terminal colour.

## Useful commands

```bash
# Show the available query groups
python3 dorkinator.py --list-categories

# Create a focused JSON collection using Bing
python3 dorkinator.py example.com --engine bing --categories api,cloud --format json

# Process a newline-delimited scope file and write CSV files elsewhere
python3 dorkinator.py domains.txt --format csv --output-dir exports

# Use in CI/scripts without ANSI colour
python3 dorkinator.py example.com --no-color
```

Exports default to `dorkinator-output/<domain>_dorks.txt`. TXT includes each query and URL; JSON and CSV retain domain and category metadata.

## Browser workspace

Open [index.html](index.html) in a modern browser for a no-install visual workspace. It provides category selection, Google/Bing switching, direct result links, and TXT/JSON downloads. Everything runs locally in the browser.

## Included categories

- `surface` — indexed assets, files, and exposed technology hints
- `cloud` — public cloud, code-hosting, and sharing services
- `api` — API, GraphQL, OpenAPI, and documentation discovery
- `exposure` — public indicators that merit manual review
- `endpoints` — common application routes and error fingerprints

## Safety and responsible use

Only run queries for domains you own or are explicitly authorised to assess. Generated search results are leads, not findings: validate scope, impact, and permissions before interacting with any result.

## Tests

```bash
python3 -m unittest -v
```

## License

MIT. See [LICENSE](LICENSE).

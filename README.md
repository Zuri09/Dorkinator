<div align="center">

# DORKINATOR

### Offline search-query collections for authorised reconnaissance

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](#requirements)
[![License](https://img.shields.io/badge/License-MIT-22C55E)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-unittest-22C55E)](#verification)
[![Offline](https://img.shields.io/badge/Network-Offline%20generation-0EA5E9)](#privacy)

`Google + Bing` · `TXT + CSV + JSON` · `CLI + Browser workspace`

</div>

---

Dorkinator turns an approved domain into a focused collection of Google or Bing search links. It is designed for bug bounty, OSINT, and penetration-testing workflows where you need a repeatable, reviewable starting point.

> [!IMPORTANT]
> Use this tool only for domains you own or are explicitly authorised to assess. Generated results are leads, not findings—always validate scope, impact, and permissions.

## At a glance

| What you need | Dorkinator provides |
| --- | --- |
| Fast discovery | A complete query set for surface, cloud, API, exposure, and endpoint discovery |
| Repeatable output | Structured exports with the domain, category, query, and search URL |
| Automation | Script-friendly flags, scope-file support, deduplication, and no-colour mode |
| A visual workflow | A static, local browser workspace with filtering, copying, and downloads |
| Privacy | Query generation stays on your machine; only opening a result visits a search engine |

## Start here

### Requirements

- Python 3.9 or later
- `colorama` for optional terminal colour

```bash
git clone https://github.com/Zuri09/Dorkinator.git
cd Dorkinator
chmod +x install.sh
./install.sh
python3 dorkinator.py example.com
```

The export is written to `dorkinator-output/example.com_dorks.txt`.

### Want automated AI triage?

If Docker and Ollama are already installed, one command sets up the free local search and AI components:

```bash
./install.sh --ai
python3 dorkinator.py example.com --ai
```

`install.sh --ai` pulls the local Qwen model, creates a private SearXNG secret, and starts SearXNG only on `127.0.0.1:8080`. If Docker is unavailable, the script explains how to use the optional Brave API instead.

## Choose your workflow

<table>
<tr>
<td width="50%" valign="top">

### Command line

Best for a repeatable workflow, scope files, and automation.

```bash
python3 dorkinator.py example.com \
  --engine bing \
  --format json
```

</td>
<td width="50%" valign="top">

### Browser workspace

Best for quickly exploring one target visually.

Open [index.html](index.html) in a modern browser. It works locally with no install or backend.

</td>
</tr>
</table>

## CLI reference

```text
python3 dorkinator.py TARGET [OPTIONS]
```

| Option | Description |
| --- | --- |
| `TARGET` | A domain such as `example.com`, or a newline-delimited file of domains |
| `-e`, `--engine` | `google` (default) or `bing` |
| `-f`, `--format` | `txt` (default), `csv`, or `json` |
| `-o`, `--output-dir` | Export directory; defaults to `dorkinator-output` |
| `--ai` | Search results and locally triage target-domain pages with Ollama |
| `--search-provider` | `auto` (default), `searxng`, or `brave` |
| `--searxng-url` | Local or remote SearXNG URL; defaults to `http://127.0.0.1:8080` |
| `--ai-model` | Ollama model for AI triage; defaults to `qwen2.5:7b-instruct` |
| `--ai-limit` | Maximum URLs to triage; defaults to `20` |
| `--ai-results` | Results collected per generated query; defaults to `5` |
| `--no-color` | Disable ANSI terminal colour for scripts and CI |

### Examples

```bash
# Generate the complete collection using Bing
python3 dorkinator.py example.com --engine bing --format json

# Process a scope file and export each domain as CSV
python3 dorkinator.py domains.txt --format csv --output-dir exports

# Suitable for CI, pipes, and plain terminals
python3 dorkinator.py example.com --no-color
```

## Output formats

| Format | Best for | Contents |
| --- | --- | --- |
| TXT | Manual review | Category, query, and clickable search URL |
| CSV | Spreadsheets and tracking | One row per query with domain/category metadata |
| JSON | Integrations and scripts | Structured collection of all generated entries |

## Privacy

Dorkinator does not upload domains, retain targets, or call an API. The CLI writes local export files; the browser workspace generates collections in your browser. Opening a generated link is the point at which your browser contacts Google or Bing.

## Local AI triage

Triage reviews only search results whose host matches the target scope. It deliberately does not scrape Google/Bing, follow redirects, submit forms, or make a finding automatically. Ollama receives page text over `localhost` only.

### One-command AI triage

By default, Dorkinator uses a free local SearXNG instance when available, or Brave Search when `BRAVE_SEARCH_API_KEY` is set. It does not scrape search-engine pages. Run `./install.sh --ai` once to prepare the local option.

```bash
# Free option: start SearXNG locally, then run Dorkinator
python3 dorkinator.py example.com --ai
```

This generates the complete query set, searches each query, discards results outside `example.com` and its subdomains, then sends remaining public page text to local Qwen. The report is saved to `dorkinator-output/ai-triage.json` and labels each item as `no_finding`, `possible_exposure`, or `review_needed` for manual validation.

For SearXNG, run a self-hosted instance at `http://127.0.0.1:8080` (or pass `--searxng-url`). SearXNG documents a JSON `/search` API and supports container deployment. If you prefer Brave, set `BRAVE_SEARCH_API_KEY`; one target currently makes 36 API searches, so check your plan before running large scope files.

Use `--ai-limit` to cap requests or `--ai-model` to select another installed Ollama model:

```bash
python3 dorkinator.py example.com --ai --ai-limit 10 --ai-results 3
```

## License

Released under the [MIT License](LICENSE).

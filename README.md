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
| Fast discovery | Focused query groups for surface, cloud, API, exposure, and endpoint discovery |
| Repeatable output | Structured exports with the domain, category, query, and search URL |
| Automation | Script-friendly flags, scope-file support, deduplication, and no-colour mode |
| A visual workflow | A static, local browser workspace with filtering, copying, and downloads |
| Privacy | Query generation stays on your machine; only opening a result visits a search engine |

## Start in 60 seconds

### Requirements

- Python 3.9 or later
- `colorama` for optional terminal colour

```bash
git clone https://github.com/Zuri09/Dorkinator.git
cd Dorkinator
python3 -m pip install -r requirements.txt
python3 dorkinator.py example.com
```

The export is written to `dorkinator-output/example.com_dorks.txt`.

## Choose your workflow

<table>
<tr>
<td width="50%" valign="top">

### Command line

Best for a repeatable workflow, scope files, and automation.

```bash
python3 dorkinator.py example.com \
  --engine bing \
  --categories api,cloud \
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
| `-c`, `--categories` | Comma-separated groups, for example `api,cloud`; defaults to `all` |
| `-f`, `--format` | `txt` (default), `csv`, or `json` |
| `-o`, `--output-dir` | Export directory; defaults to `dorkinator-output` |
| `--list-categories` | List available query groups and exit |
| `--no-color` | Disable ANSI terminal colour for scripts and CI |

### Examples

```bash
# See the available query groups
python3 dorkinator.py --list-categories

# Create a focused collection using Bing
python3 dorkinator.py example.com --engine bing --categories api,cloud --format json

# Process a scope file and export each domain as CSV
python3 dorkinator.py domains.txt --format csv --output-dir exports

# Suitable for CI, pipes, and plain terminals
python3 dorkinator.py example.com --no-color
```

## Query categories

| Group | Focus |
| --- | --- |
| `surface` | Indexed assets, files, and technology hints |
| `cloud` | Public cloud, code-hosting, and sharing services |
| `api` | API, GraphQL, OpenAPI, and documentation discovery |
| `exposure` | Public indicators that merit manual review |
| `endpoints` | Common application routes and error fingerprints |

## Output formats

| Format | Best for | Contents |
| --- | --- | --- |
| TXT | Manual review | Category, query, and clickable search URL |
| CSV | Spreadsheets and tracking | One row per query with domain/category metadata |
| JSON | Integrations and scripts | Structured collection of all generated entries |

## Privacy

Dorkinator does not upload domains, retain targets, or call an API. The CLI writes local export files; the browser workspace generates collections in your browser. Opening a generated link is the point at which your browser contacts Google or Bing.

## Local AI triage

Triage reviews **only URLs you explicitly provide** and only when their host matches a declared scope. It deliberately does not scrape Google/Bing, follow redirects, submit forms, or make a finding automatically. Ollama receives page text over `localhost` only.

### The easy way: guided setup

First, create a file named `urls.txt` with one **approved, public** URL per line:

```text
https://app.example.com/status
https://docs.example.com/security
```

Then run one command. The wizard explains every field, checks that your URL file exists, and asks for confirmation before it sends any request:

```bash
python3 dorkinator.py triage --wizard
```

The default local model is `qwen2.5:7b-instruct`. The report is saved to `dorkinator-output/triage.json` and labels each item as `no_finding`, `possible_exposure`, or `review_needed`, with evidence for manual validation.

### Faster flag-based mode

```bash
python3 dorkinator.py triage urls.txt \
  --scope example.com \
  --i-have-authorisation
```

## Verification

```bash
python3 -m unittest -v
```

The test suite covers domain normalisation, scope-file deduplication, unsafe path rejection, and generated URL encoding.

## License

Released under the [MIT License](LICENSE).

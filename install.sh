#!/usr/bin/env sh
set -eu

AI_MODE=false
[ "${1:-}" = "--ai" ] && AI_MODE=true

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python 3.9+ and run this again." >&2
  exit 1
fi

echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt

if [ "$AI_MODE" = false ]; then
  echo "Ready. Generate links with: python3 dorkinator.py example.com"
  echo "For automated local AI triage, run: ./install.sh --ai"
  exit 0
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is required for AI mode. Install it from https://ollama.com, then rerun: ./install.sh --ai" >&2
  exit 1
fi

if ! ollama list 2>/dev/null | grep -q 'qwen2.5:7b-instruct'; then
  echo "Downloading local Qwen model (about 4.7 GB)..."
  ollama pull qwen2.5:7b-instruct
fi

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo "Qwen is ready. Docker is optional, but needed for free local search." >&2
  echo "Use Brave instead: export BRAVE_SEARCH_API_KEY=your-key" >&2
  exit 0
fi

if [ ! -f searxng/.env ]; then
  umask 077
  printf 'SEARXNG_SECRET=%s\n' "$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > searxng/.env
fi

echo "Starting free local SearXNG search at http://127.0.0.1:8080 ..."
docker compose -f searxng/compose.yml up -d
echo "AI mode is ready: python3 dorkinator.py example.com --ai"

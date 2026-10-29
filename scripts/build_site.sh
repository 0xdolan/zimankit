#!/usr/bin/env bash
# Build the website into _site/ (used by .github/workflows/pages.yml).
# Preview: scripts/build_site.sh && python3 -m http.server -d _site 8000
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_site.py

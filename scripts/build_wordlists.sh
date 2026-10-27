#!/usr/bin/env bash
# Build both wordlists end to end, logging to cache/build.log.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-.venv/bin/python}
mkdir -p cache
"$PY" run_pipeline.py "$@" 2>&1 | grep -v "No stemming for language" | tee cache/build.log
for lang in ckb kmr; do
  echo "== $lang"; wc -l "output/$lang/clean_wordlist_$lang.csv" "output/$lang/lemmas_$lang.csv"
done

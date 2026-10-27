#!/usr/bin/env bash
# Portable core of the zimankit rules with GNU sed/grep only.  Run: bash kurdish.sh
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
ZWNJ=$'‌'

normalize_ckb() { sed -e 's/ك/ک/g; s/[يى]/ی/g; s/ھ/ه/g; s/ة/ە/g' -e "s/ه${ZWNJ}/ە/g" -e 's/^ر/ڕ/; s/\([[:space:]]\)ر/\1ڕ/g'; }
normalize_kmr() { sed -e 's/[éèë]/ê/g; s/[íìï]/î/g; s/[úùü]/û/g; s/ı/i/g; s/ș/ş/g'; }
kmr_feat() {
  case "$1" in
    ekê) echo indef.obl.f ;; ekî) echo indef.obl.m ;; eke) echo indef.ezafe ;; ek) echo indef ;;
    ên) echo ezafe.pl ;; an) echo obl.pl ;; a) echo ezafe.f ;; ê) echo "ezafe.m|obl.f" ;; î) echo obl.m ;;
  esac
}

while IFS= read -r w; do
  [ -z "$w" ] && continue
  if printf '%s' "$w" | grep -qP '[\x{0600}-\x{06FF}]'; then
    n=$(printf '%s' "$w" | normalize_ckb)
    if [[ "$n" =~ ^(.+)(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$ ]]; then
      # strip the suffix chain from the right to get the shortest stem
      stem=$(printf '%s' "$n" | sed -E 's/(ەکان|ەکە|کان|کە)(مان|تان|یان|م|ت|ی)?$//')
      rest=${n#"$stem"}
      def=$(printf '%s' "$rest" | grep -oE '^(ەکان|ەکە|کان|کە)')
      clitic=${rest#"$def"}
      echo "ckb $w -> $n | stem=$stem def=$def clitic=${clitic:--}"
    else
      echo "ckb $w -> $n | stem=$n"
    fi
  else
    n=$(printf '%s' "$w" | normalize_kmr)
    low=$(printf '%s' "$n" | sed 's/.*/\L&/')
    suf=$(printf '%s' "$low" | grep -oE '(ekê|ekî|eke|ek|ên|an|a|ê|î)$' || true)
    if [ -n "$suf" ] && [ ${#low} -gt ${#suf} ]; then
      echo "kmr $w -> $n | stem=${low%"$suf"} suffix=$suf $(kmr_feat "$suf")"
    else
      echo "kmr $w -> $n | stem=$low"
    fi
  fi
done < "$here/inputs.txt"

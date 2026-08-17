#!/usr/bin/env bash
set -euo pipefail

full_pdf="${1:?full source PDF path required}"
out_pdf="${2:?fallback PDF path required}"
tmpd="$(mktemp -d /tmp/laavha_source_pages.XXXXXX)"
pdfseparate "$full_pdf" "$tmpd/page-%03d.pdf"
total="$(pdfinfo "$full_pdf" | awk '/^Pages:/{print $2}')"
if [ "$total" -le 60 ]; then
  cp "$full_pdf" "$out_pdf"
  exit 0
fi

parts=()
for n in $(seq 1 30); do parts+=("$tmpd/page-$(printf '%03d' "$n").pdf"); done
start=$((total - 29))
for n in $(seq "$start" "$total"); do parts+=("$tmpd/page-$(printf '%03d' "$n").pdf"); done
pdfunite "${parts[@]}" "$out_pdf"
printf 'Selected pages 1-30 and %s-%s from %s into %s\n' "$start" "$total" "$full_pdf" "$out_pdf"

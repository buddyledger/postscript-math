#!/bin/bash
# Builds doc/pst-numeric-doc.pdf with latex, dvips and ps2pdf.
# Needs TeX Live with PSTricks. Run from anywhere:
#   tools/make-doc.sh
# or, with Docker:
#   docker run --rm -v "$PWD:/pkg" texlive/texlive:latest bash /pkg/tools/make-doc.sh
#
# Copyright 2026 Buddy Ledger
# LaTeX Project Public License 1.3c or later, see LICENSE
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
export TEXINPUTS="$root/tex:$root/latex:$root/doc:"
export TEXPSHEADERS="$root/dvips:"
export DVIPSHEADERS="$root/dvips:"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cd "$work"
for pass in 1 2; do
  latex -interaction=nonstopmode -halt-on-error pst-numeric-doc.tex > latex.log 2>&1 \
    || { tail -30 latex.log; echo "latex failed"; exit 1; }
done
grep -i "warning" latex.log | grep -v "Font shape" || true
dvips -q pst-numeric-doc.dvi -o pst-numeric-doc.ps
ps2pdf -dNOSAFER pst-numeric-doc.ps pst-numeric-doc.pdf > gs.log 2>&1 || { cat gs.log; exit 1; }
if grep -q "Error" gs.log; then cat gs.log; exit 1; fi
cp pst-numeric-doc.pdf "$root/doc/"
echo "wrote doc/pst-numeric-doc.pdf ($(wc -c < pst-numeric-doc.pdf) bytes)"

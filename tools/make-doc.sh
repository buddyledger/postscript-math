#!/bin/bash
# Builds doc/pst-numeric-doc.pdf with latex, biber, makeindex, dvips and ps2pdf.
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
export BIBINPUTS="$root/doc:"
export TEXPSHEADERS="$root/dvips:"
export DVIPSHEADERS="$root/dvips:"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cd "$work"
run_latex() {
  latex -interaction=nonstopmode -halt-on-error pst-numeric-doc.tex > latex.log 2>&1 \
    || { tail -40 latex.log; echo "latex failed"; exit 1; }
}
run_latex
biber -q pst-numeric-doc > biber.log 2>&1 || { cat biber.log; echo "biber failed"; exit 1; }
makeindex -q pst-numeric-doc.idx
run_latex
run_latex
grep -iE "warning|undefined" pst-numeric-doc.log | grep -v "Font shape" || true
dvips -q pst-numeric-doc.dvi -o pst-numeric-doc.ps
ps2pdf pst-numeric-doc.ps pst-numeric-doc.pdf > gs.log 2>&1 || { cat gs.log; exit 1; }
if grep -q "Error" gs.log; then cat gs.log; exit 1; fi
cp pst-numeric-doc.pdf "$root/doc/"
echo "wrote doc/pst-numeric-doc.pdf ($(wc -c < pst-numeric-doc.pdf) bytes)"

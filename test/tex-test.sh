#!/bin/bash
# Tests the TeX interface of pst-numeric with latex, dvips and Ghostscript.
# Needs TeX Live with PSTricks. Run from anywhere:
#   test/tex-test.sh
# or, with Docker:
#   docker run --rm -v "$PWD:/pkg:ro" texlive/texlive:latest bash /pkg/test/tex-test.sh
#
# Copyright 2026 Buddy Ledger
# LaTeX Project Public License 1.3c or later, see LICENSE
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
export TEXINPUTS="$root/tex:$root/latex:$root/test:"
export TEXPSHEADERS="$root/dvips:"
export DVIPSHEADERS="$root/dvips:"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cd "$work"
fail=0

# name: latex, dvips, then Ghostscript to text; prints the text file's name
build() {
  latex -interaction=nonstopmode -halt-on-error "$1.tex" > "$1.latex.log" 2>&1 \
    || { tail -30 "$1.latex.log"; echo "FAIL $1: latex"; return 1; }
  dvips -q "$1.dvi" -o "$1.ps"
  gs -q -dNOPAUSE -dBATCH -dNOSAFER -sDEVICE=txtwrite -sOutputFile="$1.txt" "$1.ps" > "$1.gs.log" 2>&1 \
    || { cat "$1.gs.log"; echo "FAIL $1: Ghostscript"; return 1; }
  if grep -q "Error" "$1.gs.log"; then cat "$1.gs.log"; echo "FAIL $1: PostScript error"; return 1; fi
}
expect() { # file text
  if grep -qF -- "$2" "$1"; then echo "ok   $2"; else echo "FAIL $2 not found in $1"; fail=1; fi
}
headers() { # ps file -> names of the pst-numeric headers that dvips included
  grep -o "BeginProcSet: pst-numeric[a-z-]*\.pro" "$1" | sed 's/BeginProcSet: //' | tr '\n' ' '
}

echo "== every part, results printed by \\psNumericShow"
cp "$root/test/tex-test.tex" .
build tex-test || exit 1
for want in \
  "+1.41421356237309504880168872421e0" \
  "+2.7182818284590452354e0" \
  "+1.1826458156486142400e17" \
  "-2" \
  "[-2.0 1.0; 1.5 -0.5]" \
  "-5 + 10i" \
  "+1.4142135623730950488e0" \
  "7" \
  "[-1.0 - 2.0i, -1.0 + 2.0i]" \
  "-0.98803" \
  "text is kept" \
  "+1.7724538509055160273e0" \
  "+1.1490348493190048047e-1" \
  "3.16578 + 1.9596i" \
  "[0 - 1.0i, 0 + 1.0i]" \
  "[0.0, 1.0, 0.0, 1.0]" \
  "+9.7500210485177956586e-1"; do
  expect tex-test.txt "$want"
done
got="$(headers tex-test.ps)"
echo "headers: $got"
[ "$got" = "pst-numeric.pro pst-numeric-bignum.pro pst-numeric-trig.pro pst-numeric-matrix.pro pst-numeric-complex.pro pst-numeric-calc.pro pst-numeric-special.pro pst-numeric-tensor.pro " ] \
  || { echo "FAIL wrong headers"; fail=1; }

echo "== option special loads bignum too"
cat > special.tex <<'EOF'
\documentclass{article}
\usepackage[special]{pst-numeric}
\begin{document}
\begin{pspicture}(0,0)(8,0.4)\psNumericShow{0.5 erf}\end{pspicture}
\end{document}
EOF
build special || exit 1
expect special.txt "0.5205"
got="$(headers special.ps)"
echo "headers: $got"
[ "$got" = "pst-numeric.pro pst-numeric-bignum.pro pst-numeric-special.pro " ] || { echo "FAIL wrong headers"; fail=1; }

echo "== option calc loads matrix, complex, special and bignum too, but not trig"
cat > parts.tex <<'EOF'
\documentclass{article}
\usepackage[calc]{pst-numeric}
\begin{document}
\begin{pspicture}(0,0)(8,0.4)\psNumericShow{{ dup mul 2 sub } 0 2 froot}\end{pspicture}
\end{document}
EOF
build parts || exit 1
expect parts.txt "1.41421"
got="$(headers parts.ps)"
echo "headers: $got"
[ "$got" = "pst-numeric.pro pst-numeric-bignum.pro pst-numeric-matrix.pro pst-numeric-complex.pro pst-numeric-calc.pro pst-numeric-special.pro " ] \
  || { echo "FAIL wrong headers"; fail=1; }

echo "== \\pstNumericParts set before loading, without options"
# (PSTricks itself no longer loads in plain TeX, so this uses LaTeX too)
cat > parts2.tex <<'EOF'
\documentclass{article}
\def\pstNumericParts{bignum}
\usepackage{pst-numeric}
\begin{document}
\begin{pspicture}(0,0)(8,0.4)\psNumericShow{2 setbn sqrtbn}\end{pspicture}
\end{document}
EOF
build parts2 || exit 1
expect parts2.txt "+1.4142135623730950488e0"
got="$(headers parts2.ps)"
echo "headers: $got"
[ "$got" = "pst-numeric.pro pst-numeric-bignum.pro " ] || { echo "FAIL wrong headers"; fail=1; }

echo "== presentation: formats, matrices, tensors, regression"
cat > pres.tex <<'EOF'
\documentclass{article}
\usepackage{pst-numeric}
\psNumericDef{fit}{[1 2 3 4 5 6] [2.1 3.9 6.2 7.8 10.1 12.2] 1 regress}
\begin{document}
\begin{pspicture}(0,-6)(14,1)
\psNumericShow[numFormat=fixed,numDigits=3]{(2) setbn (3) setbn divbn}
\rput[l](4,0){\psNumericShow[numFormat=sci,numDigits=3,sciStyle=e]{(1.5e-12) setbn}}
\rput[l](8,0){\psNumericShow[numFormat=auto,numDecimal={,}]{[1.25 -0.5]}}
\rput[l](0,-1.5){\psNumericMatrix[label=A]{[[1 -2.5] [3 4]] mfromrows}}
\rput[l](5,-1.5){\psNumericMatrix{[[[1 2] [3 4]] [[5 6] [7 8]]] tensor}}
\rput[l](0,-4){\psNumericRegression[regShow=eq r2 dof]{fit}}
\rput[l](7,-4){\psNumericRegression[regShow=sxx xbar dropped ciw]{fit}}
\psset{xunit=0.3cm,yunit=0.2cm}
\rput(30,-20){\psNumericRegPlot{fit}{0}{7}\psNumericRegPlot[regPlot=pi]{fit}{0}{7}%
  \psNumericRegPlot[regPlot=data]{fit}{0}{0}}
\end{pspicture}
\end{document}
EOF
build pres || exit 1
for want in "0.667" "1.50e" "1,25" "0,5i" "2.5" "(2,:,:)" "y = " "2.02x" "0.9982" "dof = 4" "17.5" "mean x = 3.5" "dropped = 0"; do
  expect pres.txt "$want"
done

echo "== an unknown option is an error"
cat > badopt.tex <<'EOF'
\documentclass{article}
\usepackage[bogus]{pst-numeric}
\begin{document}x\end{document}
EOF
if latex -interaction=nonstopmode -halt-on-error badopt.tex > badopt.log 2>&1; then
  echo "FAIL the option bogus was accepted"; fail=1
else
  grep -q "Unknown option" badopt.log && echo "ok   option bogus rejected" || { echo "FAIL other error"; tail -20 badopt.log; fail=1; }
fi

echo "== an unknown part in \\pstNumericParts is an error"
cat > badpart.tex <<'EOF'
\documentclass{article}
\def\pstNumericParts{matrix,bogus}
\usepackage{pst-numeric}
\begin{document}x\end{document}
EOF
if latex -interaction=nonstopmode -halt-on-error badpart.tex > badpart.log 2>&1; then
  echo "FAIL the part bogus was accepted"; fail=1
else
  grep -q "unknown part .bogus" badpart.log && echo "ok   part bogus rejected" || { echo "FAIL other error"; tail -20 badpart.log; fail=1; }
fi

echo
if [ "$fail" = 0 ]; then echo "ALL TEX TESTS PASSED"; else echo "TEX TESTS FAILED"; exit 1; fi

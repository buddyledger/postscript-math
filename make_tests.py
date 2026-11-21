# Copyright 2026 Buddy Ledger
#
# This work may be distributed and/or modified under the
# conditions of the LaTeX Project Public License, either version 1.3c
# of this license or (at your option) any later version.
# The latest version of this license is in
#   https://www.latex-project.org/lppl.txt
# and version 1.3c or later is part of all distributions of LaTeX
# version 2008 or later.
#
# This work has the LPPL maintenance status `author-maintained'.
#
# The Current Maintainer of this work is Buddy Ledger.
#
# This work consists of the files listed in README.md.

"""Generate test_bignum.ps with reference values from Python's decimal module.

Usage:  python make_tests.py [output.ps]     (default: test_bignum.ps next to this file)

Add or change test cases below, rerun this script, then run
    runme.bat test_bignum.ps
Needs only the Python standard library.
"""
import math, sys
from pathlib import Path
from decimal import Decimal as D, Context, ROUND_HALF_UP, localcontext

HP = 100  # working precision for references

def pi_hp():
    with localcontext() as c:
        c.prec = HP + 10
        # Machin, independent of the PostScript code path only in implementation
        def atan_inv(k):
            x = D(1) / k; x2 = x * x; s = x; t = x; n = 1; sg = -1
            while True:
                t *= x2; term = t / (2 * n + 1)
                if term == 0 or abs(term) < D(10) ** (-(HP + 8)): break
                s += sg * term; sg = -sg; n += 1
            return s
        return +(16 * atan_inv(5) - 4 * atan_inv(239))

PI = pi_hp()

def sincos(x, which):
    with localcontext() as c:
        c.prec = HP + 10
        x = D(x)
        tp = 2 * PI
        r = x - tp * (x / tp).to_integral_value(rounding=ROUND_HALF_UP)
        if which == 'sin':
            t = r; s = r; i = 1
            while True:
                t = -t * r * r / ((2 * i) * (2 * i + 1))
                if t == 0 or abs(t) < D(10) ** (-(HP + 8)): break
                s += t; i += 1
        else:
            t = D(1); s = D(1); i = 1
            while True:
                t = -t * r * r / ((2 * i - 1) * (2 * i))
                if t == 0 or abs(t) < D(10) ** (-(HP + 8)): break
                s += t; i += 1
        return +s

def fmt(v, n):
    v = Context(prec=n, rounding=ROUND_HALF_UP).plus(D(v))
    if v == 0:
        return "+0." + "0" * (n - 1) + "e0"
    sign, digits, _ = v.as_tuple()
    ds = "".join(map(str, digits)).ljust(n, "0")[:n]
    return ("-" if sign else "+") + ds[0] + "." + ds[1:] + "e" + str(v.adjusted())

def rin(s, n):  # what setbn does to an input
    return Context(prec=n, rounding=ROUND_HALF_UP).plus(D(s))

lines = []
def out(s=""): lines.append(s)

def section(name, n):
    out(); out(f"({name}) bnt_section  {n} setbnsize")

def t(label, proc, expected):
    esc = label.replace("(", "\\(").replace(")", "\\)")
    out(f"({esc}) {{ {proc} }} ({expected}) check")

def ps(s):  # PostScript literal for a numeric string input
    return f"({s})"

# ---------------------------------------------------------------- setbn
n = 20
section("setbn / bncvs", n)
for s in ["509", "-0.00125", "123456789012345678901234", "0", "-0", "0.000",
          "99999999999999999999.5", "-1.5e-30", "+42", "1E5", ".5", "7.", "00012.3400"]:
    t(f"setbn {s}", f"{ps(s)} setbn", fmt(rin(s, n), n))
t("setbn integer 509", "509 setbn", fmt(509, n))
t("setbn real -0.00125", "-0.00125 setbn", fmt(D("-0.00125"), n))
t("setbn real 1e10", "1e10 setbn", fmt(D("1e10"), n))
t("setbn copies a bignum", "(3.5) setbn setbn", fmt(D("3.5"), n))
for bad in ["12x", "", "-", "1e", "1.2.3", "e5", "1e5-"]:
    t(f"setbn rejects ({bad})", f"{ps(bad)} setbn", "ERR:syntaxerror")
t("setbn leaves input string unchanged", "/bnt_s (12.5) def bnt_s setbn pop bnt_s", "12.5")
t("bncvr", "(1.5e3) setbn bncvr", "1500.0")

# ---------------------------------------------------------------- arithmetic
def binop(name, op, pairs):
    for a, b in pairs:
        ctx = Context(prec=n, rounding=ROUND_HALF_UP)
        A, B = rin(a, n), rin(b, n)
        if name == "divbn" and B == 0:
            exp = "ERR:undefinedresult"
        else:
            exp = fmt(getattr(ctx, op)(A, B), n)
        t(f"{a} {name} {b}", f"{ps(a)} setbn {ps(b)} setbn {name}", exp)

section("addbn / subbn", n)
binop("addbn", "add", [("509", "67"), ("67", "-509"), ("-50", "-602"), ("-507", "60"),
    ("50", "-60"), ("5", "-5"), ("1e10", "1"), ("1", "1e-10"), ("0.1", "0.2"),
    ("1e25", "-1"), ("1", "1e-25"), ("1", "-1e-25"), ("99999999999999999999", "1"),
    ("12345678901234567890", "0.5"), ("-12345678901234567890", "-0.5"),
    ("0", "-3.25"), ("0", "0"), ("1.000000000000000001", "-1")])
binop("subbn", "subtract", [("10", "3"), ("3", "10"), ("1", "1e-19"), ("-2.5", "-2.5"),
    ("1e-30", "1e-31"), ("0", "7")])
t("subbn leaves B unchanged", "/bnt_b 3 setbn def 10 setbn bnt_b subbn pop bnt_b", fmt(3, n))

section("mulbn / divbn", n)
binop("mulbn", "multiply", [("12", "34"), ("-12", "34"), ("-12", "-34"), ("0", "-5"),
    ("123456789.123456789", "987654321.987654321"), ("1e-200", "1e-200"),
    ("99999999999999999999", "99999999999999999999"), ("0.5", "0.5")])
binop("divbn", "divide", [("1", "3"), ("2", "3"), ("-1", "7"), ("22", "7"), ("1", "-8"),
    ("1e-30", "3e20"), ("0", "5"), ("1", "0"), ("100", "4"), ("1", "99999999999999999999")])

section("negbn absbn truncbn roundbn", n)
for s in ["3.5", "-3.5", "0"]:
    t(f"negbn {s}", f"{ps(s)} setbn negbn", fmt(-D(s), n))
    t(f"absbn {s}", f"{ps(s)} setbn absbn", fmt(abs(D(s)), n))
for s in ["12.5", "-12.5", "0.4", "-0.6", "7", "123456.789", "1e30", "2.5e-3"]:
    tr = D(s).to_integral_value(rounding="ROUND_DOWN")
    ro = D(s).to_integral_value(rounding=ROUND_HALF_UP)
    t(f"truncbn {s}", f"{ps(s)} setbn truncbn", fmt(tr, n))
    t(f"roundbn {s}", f"{ps(s)} setbn roundbn", fmt(ro, n))

section("comparisons", n)
pairs = [("2", "3"), ("3", "2"), ("2", "2"), ("-2", "-3"), ("-3", "-2"), ("0", "-0"),
         ("0", "1e-50"), ("-1e-50", "0"), ("1e5", "99999"), ("1.00000000000000000001", "1"),
         ("-5", "5"), ("123", "1.23e2")]
for a, b in pairs:
    A, B = rin(a, n), rin(b, n)
    c = (A > B) - (A < B)
    t(f"{a} cmpbn {b}", f"{ps(a)} setbn {ps(b)} setbn cmpbn", str(c))
    for op, f in [("eqbn", c == 0), ("nebn", c != 0), ("gtbn", c > 0), ("gebn", c >= 0),
                  ("ltbn", c < 0), ("lebn", c <= 0)]:
        t(f"{a} {op} {b}", f"{ps(a)} setbn {ps(b)} setbn {op}", "true" if f else "false")
for s, z in [("0", True), ("-0.000", True), ("1e-99", False)]:
    t(f"bniszero {s}", f"{ps(s)} setbn bniszero", "true" if z else "false")

section("transcendental", n)
t("pibn", "pibn", fmt(PI, n))
for s in ["1", "0.5", "-2", "4", "100", "1e6", "0", "3.14159", "-0.001", "1e-10"]:
    sv, cv = sincos(s, 'sin'), sincos(s, 'cos')
    t(f"sinbn {s}", f"{ps(s)} setbn sinbn", fmt(sv, n))
    t(f"cosbn {s}", f"{ps(s)} setbn cosbn", fmt(cv, n))
    with localcontext() as c:
        c.prec = HP
        t(f"tanbn {s}", f"{ps(s)} setbn tanbn", fmt(sv / cv, n))
with localcontext() as c:
    c.prec = HP
    for s in ["2", "10", "0.5", "1", "1e-30", "123.456", "1000", "9.99", "1e100", "2.718281828459045"]:
        t(f"lnbn {s}", f"{ps(s)} setbn lnbn", fmt(D(s).ln(), n))
        t(f"log10bn {s}", f"{ps(s)} setbn log10bn", fmt(D(s).log10(), n))
for bad in ["0", "-1"]:
    t(f"lnbn {bad} is an error", f"{ps(bad)} setbn lnbn", "ERR:rangecheck")
    t(f"log10bn {bad} is an error", f"{ps(bad)} setbn log10bn", "ERR:rangecheck")

for n2 in (5, 40):
    n = n2
    section(f"precision {n}", n)
    t("pibn", "pibn", fmt(PI, n))
    t("1 / 3", "1 setbn 3 setbn divbn", fmt(Context(prec=n, rounding=ROUND_HALF_UP).divide(D(1), D(3)), n))
    t("sinbn 1", "1 setbn sinbn", fmt(sincos("1", 'sin'), n))
    with localcontext() as c:
        c.prec = HP
        t("lnbn 2", "2 setbn lnbn", fmt(D(2).ln(), n))
    fact = math.factorial(30)
    t("30 factorial", "1 setbn 1 1 30 { setbn mulbn } for", fmt(fact, n))
n = 20

section("other", n)
t("typchk bignum", "1 setbn typchk", "bignumtype")
t("typchk matrix", "2 2 marray typchk", "matrixtype")
t("typchk integer", "5 typchk", "integertype")
t("typchk empty array", "[] typchk", "arraytype")
t("setbnsize rejects 0", "0 setbnsize", "ERR:rangecheck")
t("mergestr", "(ab) (cd) mergestr", "abcd")

# ---------------------------------------------------------------- Trig.ps / Matrix.ps
out(); out("(Trig.ps CORDIC - within 1e-5) bnt_section")
for x in [1, 0.5, -0.5, 2, -2, 4, -4, 6, 10, 0, 1.5707, -1.5707, 3.1415, 100, -100]:
    out(f"(corsin {x}) {{ {x} corsin }} {math.sin(x):.9f} approx")
    out(f"(corcos {x}) {{ {x} corcos }} {math.cos(x):.9f} approx")
    if abs(math.cos(x)) > 1e-3:
        out(f"(cortan {x}) {{ {x} cortan }} {math.tan(x):.9f} approx")
for x in [0.3, 1, -2.5]:
    out(f"(corcot {x}) {{ {x} corcot }} {1 / math.tan(x):.9f} approx")
    out(f"(corsec {x}) {{ {x} corsec }} {1 / math.cos(x):.9f} approx")
    out(f"(corcsc {x}) {{ {x} corcsc }} {1 / math.sin(x):.9f} approx")
for x, y in [(1, 1), (1, -1), (-1, 1), (-1, -1), (2, 1), (1, 3), (-3, 0.5), (5, 0),
             (1, 1000), (-1, -1000), (1000, 1), (0.001, 0.002), (-5, 0)]:
    out(f"(coratan {x} {y}) {{ {x} {y} coratan }} {math.atan(y / x):.9f} approx")
out(f"(coratan 0 1) {{ 0 1 coratan }} {math.pi / 2:.9f} approx")
out(f"(coratan 0 -2) {{ 0 -2 coratan }} {-math.pi / 2:.9f} approx")
t("coratan 0 0 is an error", "0 0 coratan", "ERR:undefinedresult")
for n_it in (8, 16):
    out(f"(cordicatan 1 1 {n_it} iterations, coarse) {{ 1 1 {n_it} cordicatan }} {math.pi / 4:.9f} approx_coarse")
t("cordiccossin returns a 2x1 matrix", "0 40 cordiccossin typchk", "matrixtype")
out(f"(cordiccossin works with mget) {{ 0.7 40 cordiccossin 2 1 mget }} {math.sin(0.7):.9f} approx")
out(); out("(Matrix.ps) bnt_section")
out("(mmul 2x2) { /bnt_M 2 2 marray def bnt_M 1 1 1 mput bnt_M 1 2 2 mput bnt_M 2 1 3 mput"
    " bnt_M 2 2 4 mput bnt_M bnt_M mmul dup 1 1 mget 4 string cvs exch dup 1 2 mget 4 string cvs"
    " exch dup 2 1 mget 4 string cvs exch 2 2 mget 4 string cvs"
    " ( ) exch mergestr mergestr ( ) exch mergestr mergestr ( ) exch mergestr mergestr } (7 10 15 22) check")

# ---------------------------------------------------------------- Matrix.ps v1.1
from fractions import Fraction as F

def mlit(rows):  # Python rows -> PostScript list of rows; strings stay decimal strings
    def el(x): return f"({x})" if isinstance(x, str) else str(x)
    return "[" + "".join("[" + " ".join(el(x) for x in r) + "]" for r in rows) + "]"

def fr(x): return F(D(x)) if isinstance(x, str) else F(x)

def mdet_exact(rows):
    a = [[fr(x) for x in r] for r in rows]; m = len(a); d = F(1)
    for c in range(m):
        p = next((r for r in range(c, m) if a[r][c] != 0), None)
        if p is None: return F(0)
        if p != c: a[c], a[p] = a[p], a[c]; d = -d
        d *= a[c][c]
        for r in range(c + 1, m):
            f = a[r][c] / a[c][c]
            a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return d

def msolve_exact(rows, rhs):  # exact X with rows * X = rhs, as rows of Fractions
    m = len(rows)
    a = [[fr(x) for x in r] + [fr(x) for x in b] for r, b in zip(rows, rhs)]
    for c in range(m):
        p = next(r for r in range(c, m) if a[r][c] != 0)
        a[c], a[p] = a[p], a[c]
        pv = a[c][c]; a[c] = [x / pv for x in a[c]]
        for r in range(m):
            if r != c and a[r][c] != 0:
                f = a[r][c]; a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return [r[m:] for r in a]

def ident(m): return [[1 if i == j else 0 for j in range(m)] for i in range(m)]

def fdec(q, digits):  # Fraction -> bncvs string
    with localcontext() as c:
        c.prec = HP
        return fmt(D(q.numerator) / D(q.denominator), digits)

def mbn(rows, digits): return "; ".join(" ".join(fdec(F(x), digits) for x in r) for r in rows)
def mflat(rows): return "[" + " ".join(f"{float(x):.9g}" for r in rows for x in r) + "]"

def ma(label, proc, rows):
    esc = label.replace("(", "\\(").replace(")", "\\)")
    out(f"({esc}) {{ {proc} }} {mflat(rows)} mapprox")

out(); out("(Matrix.ps building and arithmetic) bnt_section  10 setbnsize")
A2 = [[1, 2], [3, 4]]
t("mfromrows and bnt_mstr", f"{mlit(A2)} mfromrows bnt_mstr", "1 2; 3 4")
t("mfromrows stores columns", f"{mlit(A2)} mfromrows 2 1 mget", "3")
t("mfromrows typchk", f"{mlit(A2)} mfromrows typchk", "matrixtype")
t("mfromrows rejects ragged rows", "[[1 2][3]] mfromrows", "ERR:rangecheck")
t("mfromrows rejects an empty list", "[] mfromrows", "ERR:rangecheck")
t("mfromrows rejects a number", "5 mfromrows", "ERR:typecheck")
t("mtorows", f"{mlit(A2)} mfromrows mtorows 1 get 0 get", "3")
t("mcopy is independent", f"/bnt_M {mlit(A2)} mfromrows def bnt_M mcopy 1 1 99 mput bnt_M bnt_mstr", "1 2; 3 4")
t("midentity 3", "3 midentity bnt_mstr", "1 0 0; 0 1 0; 0 0 1")
t("mtranspose 2x3", "[[1 2 3][4 5 6]] mfromrows mtranspose bnt_mstr", "1 4; 2 5; 3 6")
t("madd", f"{mlit(A2)} mfromrows [[10 20][30 40]] mfromrows madd bnt_mstr", "11 22; 33 44")
t("msub", f"{mlit(A2)} mfromrows [[10 20][30 40]] mfromrows msub bnt_mstr", "-9 -18; -27 -36")
t("madd size mismatch", f"{mlit(A2)} mfromrows [[1 2 3]] mfromrows madd", "ERR:rangecheck")
t("msub size mismatch", f"{mlit(A2)} mfromrows [[1][2]] mfromrows msub", "ERR:rangecheck")
t("mscale by 3", f"{mlit(A2)} mfromrows 3 mscale bnt_mstr", "3 6; 9 12")
t("mmul 2x3 by 3x2", "[[1 2 3][4 5 6]] mfromrows [[7 8][9 10][11 12]] mfromrows mmul bnt_mstr", "58 64; 139 154")
t("mmul size mismatch gives Nan", "[[1 2 3]] mfromrows [[1 2]] mfromrows mmul", "Nan")
t("mmul by identity", f"{mlit(A2)} mfromrows 2 midentity mmul bnt_mstr", "1 2; 3 4")
D2 = [["0.1", "0.2"], ["0.3", "0.4"]]
t("decimal strings switch to bignums", f"{mlit(D2)} mfromrows [[1 1][1 1]] mfromrows madd bnt_mstr",
  mbn([[fr(a) + 1 for a in r] for r in D2], 10))
t("mscale by a decimal string", f"{mlit(A2)} mfromrows (0.5) mscale bnt_mstr", mbn([[F(x, 2) for x in r] for r in A2], 10))
# 1/3 is first rounded to 10 digits, 0.3333333333, so 3 times it is 0.9999999999
t("mscale by a bignum", f"{mlit(A2)} mfromrows 1 setbn 3 setbn divbn mscale bnt_mstr",
  mbn([[x * F(D("0.3333333333")) for x in r] for r in A2], 10))
t("mmul with decimals is exact", f"{mlit(D2)} mfromrows dup mmul bnt_mstr",
  mbn([[sum(fr(D2[i][k]) * fr(D2[k][j]) for k in range(2)) for j in range(2)] for i in range(2)], 10))

out(); out("(Matrix.ps determinant, inverse, solve - reals) bnt_section  20 setbnsize")
M3 = [[2, 1, 1], [1, 3, 2], [1, 0, 0]]
S3 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
R4 = [[4, -2, 1, 3], [3, 6, -4, 2], [2, 1, 8, -5], [1, -3, 2, 7]]
t("mdet 2x2 integers", f"{mlit(A2)} mfromrows mdet", "-2")
t("mdet 3x3 integers", f"{mlit(M3)} mfromrows mdet", str(mdet_exact(M3)))
t("mdet 4x4 integers", f"{mlit(R4)} mfromrows mdet", str(mdet_exact(R4)))
t("mdet 1x1", "[[5]] mfromrows mdet", "5")
t("mdet needs a row swap", "[[0 1][1 0]] mfromrows mdet", "-1")
t("mdet singular is 0", f"{mlit(S3)} mfromrows mdet", "0")
t("mdet non-square", "[[1 2 3][4 5 6]] mfromrows mdet", "ERR:rangecheck")
out("(mdet reals) { [[0.5 1][2 3]] mfromrows mdet } -0.5 approx")
ma("minv 2x2", f"{mlit(A2)} mfromrows minv", msolve_exact(A2, ident(2)))
ma("minv 3x3", f"{mlit(M3)} mfromrows minv", msolve_exact(M3, ident(3)))
ma("minv 4x4", f"{mlit(R4)} mfromrows minv", msolve_exact(R4, ident(4)))
ma("minv needs a row swap", "[[0 1][1 0]] mfromrows minv", [[0, 1], [1, 0]])
ma("A times minv A is the identity", f"{mlit(R4)} mfromrows dup minv mmul", ident(4))
t("minv singular", f"{mlit(S3)} mfromrows minv", "ERR:undefinedresult")
t("minv non-square", "[[1 2 3][4 5 6]] mfromrows minv", "ERR:rangecheck")
ma("msolve 2x2", f"{mlit(A2)} mfromrows [[5][6]] mfromrows msolve", msolve_exact(A2, [[5], [6]]))
ma("msolve 4x4", f"{mlit(R4)} mfromrows [[1][2][3][4]] mfromrows msolve", msolve_exact(R4, [[1], [2], [3], [4]]))
ma("msolve two right-hand sides", f"{mlit(M3)} mfromrows [[1 4][2 5][3 6]] mfromrows msolve",
   msolve_exact(M3, [[1, 4], [2, 5], [3, 6]]))
t("msolve singular", f"{mlit(S3)} mfromrows [[1][2][3]] mfromrows msolve", "ERR:undefinedresult")
t("msolve row mismatch", f"{mlit(A2)} mfromrows [[1][2][3]] mfromrows msolve", "ERR:rangecheck")
t("msolve leaves A unchanged", f"/bnt_M {mlit(A2)} mfromrows def bnt_M [[5][6]] mfromrows msolve pop bnt_M bnt_mstr", "1 2; 3 4")

out(); out("(Matrix.ps determinant, inverse, solve - bignums) bnt_section  20 setbnsize")
n = 20
def bnl(rows): return f"{mlit(rows)} mfromrows"
D3 = [["0.5", "1.25", "-2"], ["3.1", "0.2", "1"], ["-1", "4", "2.75"]]
B6 = [[(i * 37 + j * 91) % 1000 - 500 + (1999 if i == j else 0) for j in range(6)] for i in range(6)]
t("mdet decimals", f"{bnl(D2)} mdet bnt_str", fdec(mdet_exact(D2), n))
t("mdet 3x3 decimals", f"{bnl(D3)} mdet bnt_str", fdec(mdet_exact(D3), n))
t("mdet singular bignum is 0", f"{bnl(S3)} 1 setbn mscale mdet bnt_str", fdec(F(0), n))
t("mdet 6x6 integers as bignums", f"{bnl(B6)} 1 setbn mscale mdet bnt_str", fdec(mdet_exact(B6), n))
t("minv decimals", f"{bnl(D2)} minv bnt_mstr", mbn(msolve_exact(D2, ident(2)), n))
t("minv 3x3 decimals", f"{bnl(D3)} minv bnt_mstr", mbn(msolve_exact(D3, ident(3)), n))
t("minv singular bignum", f"{bnl(S3)} 1 setbn mscale minv", "ERR:undefinedresult")
t("msolve decimals", f"{bnl(D3)} [[(1)][(0.5)][(-2)]] mfromrows msolve bnt_mstr",
  mbn(msolve_exact(D3, [["1"], ["0.5"], ["-2"]]), n))
t("msolve integers with a decimal right-hand side", f"{bnl(M3)} [[(1)][2][3]] mfromrows msolve bnt_mstr",
  mbn(msolve_exact(M3, [[1], [2], [3]]), n))
t("minv with a tiny pivot", "[[(1e-30) 1][1 1]] mfromrows minv bnt_mstr",
  mbn(msolve_exact([["1e-30", 1], [1, 1]], ident(2)), n))

# ---------------------------------------------------------------- version 1.1 references
def hp():
    c = Context(prec=HP + 20, rounding=ROUND_HALF_UP)
    return c

def d_atan(x):
    with localcontext() as c:
        c.prec = HP + 20
        x = D(x); neg = x < 0; x = abs(x); inv = x > 1
        if inv: x = 1 / x
        for _ in range(4): x = x / (1 + (1 + x * x).sqrt())
        s = x; t = x; x2 = x * x; k = 1
        while True:
            t = -t * x2; term = t / (2 * k + 1)
            if abs(term) < D(10) ** (-(HP + 15)): break
            s += term; k += 1
        s *= 16
        if inv: s = PI / 2 - s
        return -s if neg else s

def d_asin(x):
    with localcontext() as c:
        c.prec = HP + 20
        x = D(x)
        if x == 1: return PI / 2
        if x == -1: return -PI / 2
        return d_atan(x / (1 - x * x).sqrt())

def d_acos(x):
    with localcontext() as c:
        c.prec = HP + 20
        return PI / 2 - d_asin(x)

def d_atan2(y, x):
    with localcontext() as c:
        c.prec = HP + 20
        y, x = D(y), D(x)
        if x == 0:
            return D(0) if y == 0 else (PI / 2 if y > 0 else -PI / 2)
        a = d_atan(y / x)
        if x < 0: a = a - PI if y < 0 else a + PI
        return a

def d_exp(x):
    with localcontext() as c:
        c.prec = HP + 20
        return D(x).exp()

def d_hyp(x, which):
    with localcontext() as c:
        c.prec = HP + 20
        e = D(x).exp(); ei = 1 / e
        return {'sinh': (e - ei) / 2, 'cosh': (e + ei) / 2, 'tanh': (e - ei) / (e + ei)}[which]

def d_sin(x): return sincos(x, 'sin')
def d_cos(x): return sincos(x, 'cos')

def cfmt(re, im, digits):  # what ccvs prints in bignum mode
    re_s = fmt(re, digits); im_s = fmt(abs(D(im)), digits)
    neg = D(im) < 0 or (D(im) == 0 and str(im).startswith("-"))
    return re_s + (" - " if neg else " + ") + im_s[1:] + "i"

n = 20
section("sqrtbn expbn powbn", n)
for x in ["2", "4", "0", "1e-51", "123456789", "0.0001", "99.99", "1e100", "0.5"]:
    with localcontext() as c:
        c.prec = HP
        t(f"sqrtbn {x}", f"{ps(x)} setbn sqrtbn", fmt(D(x).sqrt(), n))
t("sqrtbn -1 is an error", "-1 setbn sqrtbn", "ERR:rangecheck")
for x in ["0", "1", "-1", "100", "-100", "0.001", "-0.001", "1e-30", "50.5", "2302.585", "-700"]:
    t(f"expbn {x}", f"{ps(x)} setbn expbn", fmt(d_exp(x), n))
t("expbn 1e9 is out of range", "(1e9) setbn expbn", "ERR:rangecheck")
for x, y in [("2", "0.5"), ("2", "100"), ("-2", "3"), ("2", "-2"), ("1.5", "2.5"), ("10", "-20.5"),
             ("0", "0"), ("0", "5"), ("7", "0"), ("0.5", "-3"), ("1e10", "0.1"), ("3", "1e-5"),
             ("-1.5", "-3"), ("123.456", "7.89")]:
    with localcontext() as c:
        c.prec = HP
        X, Y = D(x), D(y)
        v = D(1) if (X == 0 and Y == 0) else X ** Y
    t(f"powbn {x} {y}", f"{ps(x)} setbn {ps(y)} setbn powbn", fmt(v, n))
t("powbn 0 -1", "0 setbn -1 setbn powbn", "ERR:undefinedresult")
t("powbn -2 0.5", "-2 setbn (0.5) setbn powbn", "ERR:rangecheck")

section("inverse trigonometric and hyperbolic", n)
for x in ["0", "1", "-1", "0.5", "-3", "1e20", "1e-20", "0.2", "2"]:
    t(f"atanbn {x}", f"{ps(x)} setbn atanbn", fmt(d_atan(x), n))
for x in ["0", "0.5", "-0.5", "1", "-1", "0.999", "1e-10"]:
    t(f"asinbn {x}", f"{ps(x)} setbn asinbn", fmt(d_asin(x), n))
for x in ["0", "0.5", "-0.5", "1", "-1", "0.9999999999", "1e-10"]:
    t(f"acosbn {x}", f"{ps(x)} setbn acosbn", fmt(d_acos(x), n))
t("asinbn 1.5 is an error", "(1.5) setbn asinbn", "ERR:rangecheck")
t("acosbn -2 is an error", "-2 setbn acosbn", "ERR:rangecheck")
for y, x in [("1", "-1"), ("-1", "-1"), ("0", "-1"), ("0", "0"), ("1", "0"), ("-1", "0"), ("3", "4"), ("-3", "4")]:
    t(f"atan2bn {y} {x}", f"{ps(y)} setbn {ps(x)} setbn atan2bn", fmt(d_atan2(y, x), n))
for x in ["0", "1", "-1", "1e-10", "0.5", "10", "-20", "50"]:
    for w in ("sinh", "cosh", "tanh"):
        t(f"{w}bn {x}", f"{ps(x)} setbn {w}bn", fmt(d_hyp(x, w), n))

section("factbn binombn", n)
for k in [0, 1, 5, 20, 30, 50]:
    t(f"factbn {k}", f"{k} factbn", fmt(math.factorial(k), n))
t("factbn -1", "-1 factbn", "ERR:rangecheck")
t("factbn 2.5", "2.5 factbn", "ERR:rangecheck")
for a, b in [(10, 3), (100, 50), (5, 7), (5, -1), (0, 0), (52, 5), (60, 30)]:
    t(f"binombn {a} {b}", f"{a} {b} binombn", fmt(math.comb(a, b) if 0 <= b <= a else 0, n))

# ---------------------------------------------------------------- Complex.ps
section("Complex.ps", n)
t("typchk complex", "[1 2] typchk", "complextype")
t("typchk bignum complex", "[1 setbn 2 setbn] typchk", "complextype")
t("typchk matrix still a matrix", "[[1 2][3 4]] mfromrows typchk", "matrixtype")
t("typchk list of bignums", "[1 setbn 2 setbn 3 setbn] typchk", "arraytype")
t("typchk bignum matrix", "[[(1) 2][3 4]] mfromrows 1 setbn mscale typchk", "matrixtype")
t("typchk decimal-string matrix", "[[(1) (2)][(3) (4)]] mfromrows typchk", "matrixtype")
t("cpx", "3 4 cpx ccvs", "3 + 4i")
t("cadd", "[1 2] [3 4] cadd ccvs", "4 + 6i")
t("csub", "[1 2] [3 4] csub ccvs", "-2 - 2i")
t("cmul", "[1 2] [3 4] cmul ccvs", "-5 + 10i")
t("cmul by a plain number", "[1 2] 3 cmul ccvs", "3 + 6i")
t("cdiv", "[1 2] [3 4] cdiv ccvs", "0.44 + 0.08i")
t("cdiv by 0", "[1 2] [0 0] cdiv", "ERR:undefinedresult")
t("cneg", "[1 -2] cneg ccvs", "-1 + 2i")
t("cconj", "[1 2] cconj ccvs", "1 - 2i")
t("cre cim", "[1 2] dup cre exch cim add", "3")
t("cabs", "[3 4] cabs", "5.0")
out(f"(carg -1) {{ [-1 0] carg }} {math.pi:.9f} approx")
out(f"(cexp i, real part) {{ [0 1] cexp cre }} {math.cos(1):.9f} approx")
t("csqrt -4", "[-4 0] csqrt ccvs", "0.0 + 2.0i")
t("csqrt 3+4i", "[3 4] csqrt ccvs", "2.0 + 1.0i")
t("csqrt 3-4i", "[3 -4] csqrt ccvs", "2.0 - 1.0i")
t("cpow i^2", "[0 1] 2 cpow ccvs", "-1 + 0i")
t("cpow (1+i)^-2", "[1 1] -2 cpow ccvs", "0.0 - 0.5i")
t("cln 0 is an error", "[0 0] cln", "ERR:rangecheck")
t("cpow 0^-1 is an error", "[0 0] -1 cpow", "ERR:undefinedresult")
def cdiv_d(a, b, c_, d_):
    with localcontext() as c:
        c.prec = HP
        den = c_ * c_ + d_ * d_
        return (a * c_ + b * d_) / den, (b * c_ - a * d_) / den
re_, im_ = cdiv_d(D(1), D(2), D(3), D(7))
t("cdiv bignums", "[(1) 2] [3 7] cdiv ccvs", cfmt(re_, im_, n))
with localcontext() as c:
    c.prec = HP + 10
    e1 = D(1).exp()
t("cexp bignums", "[(1) (2)] cexp ccvs", cfmt(e1 * d_cos("2"), e1 * d_sin("2"), n))
with localcontext() as c:
    c.prec = HP + 10
    l5 = D(25).ln() / 2
t("cln bignums", "[(3) (4)] cln ccvs", cfmt(l5, d_atan2("4", "3"), n))
with localcontext() as c:
    c.prec = HP + 10
    t("csqrt bignums", "[(-3) (4)] csqrt ccvs", cfmt(D(1), D(2), n))
    t("cabs bignums", "[(1) (1)] cabs bnt_str", fmt(D(2).sqrt(), n))
    t("carg bignums", "[(-1) (-1)] carg bnt_str", fmt(-3 * PI / 4, n))
    t("cpow i^i", "[(0) 1] [0 1] cpow ccvs", cfmt((-PI / 2).exp(), D(0), n))
    t("cpow (1+2i)^10", "[(1) 2] 10 cpow ccvs", cfmt(D(237), D(-3116), n))

# ---------------------------------------------------------------- Numeric.ps
section("Numeric.ps integers and roots", n)
for a, b in [(12, 345), (0, 5), (-12, 18), (17, 5), (0, 0)]:
    t(f"gcd {a} {b}", f"{a} {b} gcd", str(math.gcd(a, b)))
for a, b in [(12, 18), (4, 6), (0, 5), (-3, 7)]:
    t(f"lcm {a} {b}", f"{a} {b} lcm", str(abs(a * b) // math.gcd(a, b) if a and b else 0))
out("(froot x^2 - 2, reals) { { dup mul 2 sub } 0 2 froot } 1.414213562 approx")
out(f"(froot sin, reals) {{ {{ 57.29577951 mul sin }} 3 4 froot }} {math.pi:.9f} approx")
out("(froot root at 0, reals) { { dup dup dup mul mul exch sub } -0.5 0.3 froot } 0 approx")
t("froot needs a sign change", "{ dup mul 1 add } 0 2 froot", "ERR:rangecheck")
with localcontext() as c:
    c.prec = HP
    t("froot x^2 - 2, bignums", "{ dup mulbn 2 setbn subbn } (1) (2) froot bnt_str", fmt(D(2).sqrt(), n))
t("froot cos, bignums", "{ cosbn } (1) (2) froot bnt_str", fmt(PI / 2, n))
def newton_e3x():
    with localcontext() as c:
        c.prec = HP + 20
        x = D("0.6")
        for _ in range(60): x = x - (x.exp() - 3 * x) / (x.exp() - 3)
        return x
t("froot e^x = 3x, bignums", "{ dup expbn exch 3 setbn mulbn subbn } (0) (1) froot bnt_str", fmt(newton_e3x(), n))

out(); out("(Numeric.ps integration) bnt_section  12 setbnsize")
out("(fintegrate x^2, reals) { { dup mul } 0 1 fintegrate } 0.333333333 approx")
out("(fintegrate sin over 0..pi, reals) { { 57.29577951 mul sin } 0 3.14159265 fintegrate } 2 approx")
out("(fintegrate sqrt with a singular end, reals) { { sqrt } 0 1 fintegrate } 0.666666667 approx")
out("(fintegrate backwards, reals) { { dup mul } 1 0 fintegrate } -0.333333333 approx")
t("fintegrate x^2, bignums", "{ dup mulbn } (0) (1) fintegrate bnt_str", fmt(F(1, 3).numerator / D(3), 12))
with localcontext() as c:
    c.prec = HP
    t("fintegrate e^x, bignums", "{ expbn } (0) (1) fintegrate bnt_str", fmt(D(1).exp() - 1, 12))
t("fintegrate 1/(1+x^2), bignums", "{ 1 setbn exch dup mulbn 1 setbn addbn divbn } (0) (1) fintegrate bnt_str", fmt(PI / 4, 12))

section("Numeric.ps polynomials", n)
t("polyval", "[1 0 -2] 3 polyval", "7")
t("polyval at a complex x", "[1 0 -2] [0 1] polyval ccvs", "-3 + 0i")
t("polyval bignums", "[(0.1) (0.2) (0.3)] (0.5) polyval bnt_str", fmt(D("0.1") * D("0.25") + D("0.1") + D("0.3"), n))
t("polyder", "[1 2 3] polyder bnt_list", "2 2")
t("polyder of a constant", "[5] polyder bnt_list", "0")
t("polyadd", "[1 2 3] [1 1] polyadd bnt_list", "1 3 4")
t("polymul", "[1 2] [1 -2] polymul bnt_list", "1 0 -4")
t("polymul bignums", "[(0.5) 1] [(0.5) -1] polymul bnt_list", " ".join(fmt(D(v), n) for v in ["0.25", "0", "-1"]))
def roots_str(rs): return "; ".join(cfmt(r, i, n) for r, i in rs)
with localcontext() as c:
    c.prec = HP
    r2 = D(2).sqrt()
t("polyroots x^2 - 2", "[(1) 0 -2] polyroots bnt_clist", roots_str([(-r2, 0), (r2, 0)]))
t("polyroots (x-1)(x-2)(x-3)", "[(1) -6 11 -6] polyroots bnt_clist", roots_str([(1, 0), (2, 0), (3, 0)]))
t("polyroots x^2 + 1", "[(1) 0 1] polyroots bnt_clist", roots_str([(0, -1), (0, 1)]))
t("polyroots x^2 + 2x + 5", "[(1) 2 5] polyroots bnt_clist", roots_str([(-1, -2), (-1, 2)]))
t("polyroots x^4 - 1", "[(1) 0 0 0 -1] polyroots bnt_clist", roots_str([(-1, 0), (0, -1), (0, 1), (1, 0)]))
t("polyroots 2x^5 - ... (roots -2 -1 0.5 1 3)", "[(2) -3 -13 9 11 -6] polyroots bnt_clist",
  roots_str([(-2, 0), (-1, 0), (D("0.5"), 0), (1, 0), (3, 0)]))
t("polyroots skips leading zeros", "[0 (1) -2] polyroots bnt_clist", roots_str([(2, 0)]))
t("polyroots of a constant", "[5] polyroots length", "0")
t("polyroots of zero", "[0 0] polyroots", "ERR:rangecheck")
out("(polyroots reals) { [1 -6 11 -6] polyroots 2 get 0 get } 3 approx")
X5 = [0, 1, 2, 3, 4]; Y5 = ["1.1", "1.9", "5.2", "9.8", "17.1"]
def polyfit_exact(xs, ys, d):
    A = [[F(x) ** (d - j) for j in range(d + 1)] for x in xs]
    AtA = [[sum(A[r][i] * A[r][j] for r in range(len(xs))) for j in range(d + 1)] for i in range(d + 1)]
    Atb = [[sum(A[r][i] * fr(ys[r]) for r in range(len(xs)))] for i in range(d + 1)]
    return [row[0] for row in msolve_exact(AtA, Atb)]
pf = polyfit_exact(X5, Y5, 2)
t("polyfit degree 2, bignums", f"{mlit([X5])} 0 get {mlit([Y5])} 0 get 2 polyfit bnt_list", " ".join(fdec(q, n) for q in pf))
out("(polyfit degree 1, reals) { [0 1 2 3] [1 3 5 7] 1 polyfit 0 get } 2 approx")
t("polyfit too few points", "[1 2] [3 4] 2 polyfit", "ERR:rangecheck")

section("Matrix.ps least squares and eigenvalues", n)
LA = [[1, 1], [1, 2], [1, 3], [1, 4]]; LB = [["6"], ["5"], ["7"], ["10"]]
def lstsq_exact(A, B):
    m_ = len(A); k_ = len(A[0])
    AtA = [[sum(F(A[r][i]) * F(A[r][j]) for r in range(m_)) for j in range(k_)] for i in range(k_)]
    Atb = [[sum(F(A[r][i]) * fr(B[r][c]) for r in range(m_)) for c in range(len(B[0]))] for i in range(k_)]
    return msolve_exact(AtA, Atb)
t("mlstsq line fit, bignums", f"{bnl(LA)} {bnl(LB)} mlstsq bnt_mstr",
  mbn(lstsq_exact(LA, LB), n))
ma("mlstsq line fit, reals", f"{mlit(LA)} mfromrows [[6][5][7][10]] mfromrows mlstsq", lstsq_exact(LA, [[6], [5], [7], [10]]))
ma("mlstsq square system", f"{mlit(R4)} mfromrows [[1][2][3][4]] mfromrows mlstsq", msolve_exact(R4, [[1], [2], [3], [4]]))
t("mlstsq dependent columns", "[[1 2][2 4][3 6]] mfromrows [[1][2][3]] mfromrows mlstsq", "ERR:undefinedresult")
t("mlstsq more columns than rows", "[[1 2 3][4 5 6]] mfromrows [[1][2]] mfromrows mlstsq", "ERR:rangecheck")

def sym_eigs(Mrows):
    # roots of det(M - x I) by bisection at high precision
    nn = len(Mrows)
    def det(x):
        a = [[D(Mrows[i][j]) - (x if i == j else 0) for j in range(nn)] for i in range(nn)]
        dd = D(1)
        for c_ in range(nn):
            p = max(range(c_, nn), key=lambda r: abs(a[r][c_]))
            if a[p][c_] == 0: return D(0)
            if p != c_: a[c_], a[p] = a[p], a[c_]; dd = -dd
            dd *= a[c_][c_]
            for r in range(c_ + 1, nn):
                f = a[r][c_] / a[c_][c_]
                a[r] = [x1 - f * y1 for x1, y1 in zip(a[r], a[c_])]
        return dd
    with localcontext() as c:
        c.prec = HP + 20
        bound = 1 + max(sum(abs(D(v)) for v in r) for r in Mrows)
        grid = [-bound + (2 * bound) * D(i) / 4000 for i in range(4001)]
        roots = []
        for lo, hi in zip(grid, grid[1:]):
            flo, fhi = det(lo), det(hi)
            if flo == 0: roots.append(lo); continue
            if flo * fhi < 0:
                for _ in range(400):
                    mid = (lo + hi) / 2; fm = det(mid)
                    if (fm < 0) == (flo < 0): lo, flo = mid, fm
                    else: hi = mid
                roots.append((lo + hi) / 2)
        return sorted(roots)
E3 = [[4, 1, 2], [1, 3, 0], [2, 0, 5]]
t("meigsym 2x2 values, bignums", f"{bnl([[2, 1], [1, 2]])} 1 setbn mscale meigsym pop bnt_list", " ".join(fmt(v, n) for v in [1, 3]))
with localcontext() as c:
    c.prec = HP
    h = 1 / D(2).sqrt()
t("meigsym 2x2 vectors, bignums", f"{bnl([[2, 1], [1, 2]])} 1 setbn mscale meigsym exch pop bnt_mstr",
  f"{fmt(h, n)} {fmt(h, n)}; {fmt(-h, n)} {fmt(h, n)}")
t("meigsym 3x3 values, bignums", f"{bnl(E3)} 1 setbn mscale meigsym pop bnt_list", " ".join(fmt(v, n) for v in sym_eigs(E3)))
ev3 = sym_eigs(E3)
out(f"(meigsym 3x3 smallest value, reals) {{ {mlit(E3)} mfromrows meigsym pop 0 get }} {float(ev3[0]):.9f} approx")
out(f"(meigsym 3x3: A v = lambda v, reals) {{ {mlit(E3)} mfromrows dup meigsym /bnt_V exch def 2 get /bnt_l exch def"
    " bnt_V mmul 2 get /bnt_c exch def"
    " 0 0 1 2 { /bnt_i exch def bnt_c bnt_i get bnt_V 2 get bnt_i get bnt_l mul sub abs 2 copy lt { exch } if pop } for } 0 approx")
t("meigsym non-symmetric", "[[1 2][3 4]] mfromrows meigsym", "ERR:rangecheck")
t("meigsym non-square", "[[1 2 3][4 5 6]] mfromrows meigsym", "ERR:rangecheck")

header = r"""%!PS
% test_bignum.ps - regression tests for the postscript-math library
% Generated by make_tests.py - edit that file, not this one.
%
% Copyright 2026 Buddy Ledger
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License, either version 1.3c
% of this license or (at your option) any later version.
% The latest version of this license is in
%   https://www.latex-project.org/lppl.txt
% and version 1.3c or later is part of all distributions of LaTeX
% version 2008 or later.
%
% This work has the LPPL maintenance status `author-maintained'.
%
% The Current Maintainer of this work is Buddy Ledger.
%
% This work consists of the files listed in README.md.
%
% Run from this folder:   runme.bat test_bignum.ps
%   (or: gswin64c -q -dNODISPLAY -dNOSAFER -dBATCH test_bignum.ps)
% Expected values were generated with Python's decimal module (100-digit
% references, rounded half away from zero).  Prints failures and a summary.

(Load.ps) run

/bnt_pass 0 def /bnt_fail 0 def /bnt_verbose false def
/bnt_section { (== ) print = } def
/bnt_str {
	dup typchk (bignumtype) eq { bncvs }{
	dup typchk (complextype) eq { ccvs }{
	dup type /stringtype eq { }{ 80 string cvs } ifelse } ifelse } ifelse
} def
/bnt_list { () exch { bnt_str exch dup length 0 gt { ( ) mergestr } if exch mergestr } forall } def
/bnt_clist { () exch { ccvs exch dup length 0 gt { (; ) mergestr } if exch mergestr } forall } def
/bnt_result { % label got ok
	{ /bnt_pass bnt_pass 1 add def bnt_verbose { (ok   ) print pop = }{ pop pop } ifelse }
	{ /bnt_fail bnt_fail 1 add def (FAIL ) print exch print (: got ) print = (       expected ) print bnt_exp = } ifelse
} def
/check { % (label) {proc} (expected)
	/bnt_exp exch def /bnt_proc exch def /bnt_lab exch def
	/bnt_proc load stopped { clear (ERR:) $error /errorname get 40 string cvs mergestr }{ bnt_str } ifelse
	count 1 ne { count 1 sub { exch pop } repeat (EXTRA ITEMS LEFT ON STACK) mergestr } if
	dup bnt_exp eq
	bnt_lab 3 1 roll
	bnt_result
} def
/bnt_approx { % (label) {proc} expected tolerance
	/bnt_tol exch def /bnt_exp exch def /bnt_proc exch def /bnt_lab exch def
	/bnt_proc load stopped { clear (ERR:) $error /errorname get 40 string cvs mergestr false }{
		dup type /realtype eq 1 index type /integertype eq or
		{ dup bnt_exp sub abs bnt_tol le }{ false } ifelse } ifelse
	bnt_lab 3 1 roll
	exch dup type /stringtype ne { 40 string cvs } if exch
	bnt_result
} def
/approx { 1e-5 bnt_approx } def         % reals within 1e-5
/approx_coarse { 1e-2 bnt_approx } def  % reals within 1e-2 (few iterations)
/bnt_mstr { % M -> (a b; c d)
	mtorows () exch {
		exch dup length 0 gt { (; ) mergestr } if exch
		() exch { bnt_str exch dup length 0 gt { ( ) mergestr } if exch mergestr } forall
		mergestr
	} forall
} def
/bnt_mok { % [flat values] -> bool   (each within 1e-4 of bnt_exp)
	/bnt_g exch def
	bnt_g length bnt_exp length eq dup {
		0 1 bnt_g length 1 sub { /bnt_k exch def
			bnt_g bnt_k get bnt_exp bnt_k get sub abs 1e-4 le and } for
	} if
} def
/mapprox { % (label) {proc} [expected, row by row]   (each within 1e-4)
	/bnt_exp exch def /bnt_proc exch def /bnt_lab exch def
	/bnt_proc load stopped { clear (ERR:) $error /errorname get 40 string cvs mergestr false }{
		dup typchk (matrixtype) eq {
			dup mtorows [ exch { aload pop } forall ] bnt_mok exch bnt_mstr exch
		}{ bnt_str false } ifelse
	} ifelse
	count 2 ne { pop count 1 sub { exch pop } repeat (EXTRA ITEMS LEFT ON STACK) mergestr false } if
	bnt_lab 3 1 roll
	bnt_result
} def
"""
footer = r"""
() =
bnt_pass =only ( passed, ) print bnt_fail =only ( failed) =
bnt_fail 0 gt { (TESTS FAILED) = } { (ALL TESTS PASSED) = } ifelse
"""
# Write the file directly (not via shell redirection: Windows PowerShell 5.1's
# ">" writes UTF-16, which Ghostscript cannot read).
target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("test_bignum.ps")
with open(target, "w", encoding="ascii", newline="\n") as f:
    f.write(header + "\n".join(lines) + "\n" + footer + "\n")
print(f"wrote {target} ({sum(l.endswith((' check', ' approx', ' approx_coarse', ' mapprox')) for l in lines)} tests)")

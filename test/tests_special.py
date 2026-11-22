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

# Tests of the version 1.4 additions to Special.ps (distributions, more
# special functions) and bignumlibrary.ps (powmodbn, isprime, factor).
# Run by make_tests.py in its namespace (t, ra, bna, section, D, F, fmt,
# spouge_lgamma, d_gamma, PI_HP, d_besselj, ...). References come from
# methods other than the PostScript code: power series instead of continued
# fractions, Spouge's formula instead of Stirling's series, quadrature for
# K_n, exact fractions for the discrete distributions, Python integers for
# the number theory.

import functools
from fractions import Fraction as _Fr

_P = 90                                  # working digits of the references

@functools.lru_cache(maxsize=None)
def _lg(x):                              # ln Gamma(x), x > 0
    return +spouge_lgamma(D(x))

def _gam(x):
    with localcontext() as c:
        c.prec = _P
        return _lg(str(x)).exp()

def _beta(a, b):
    with localcontext() as c:
        c.prec = _P
        return (_lg(str(a)) + _lg(str(b)) - _lg(str(D(a) + D(b)))).exp()

def _pi():
    with localcontext() as c:
        c.prec = _P
        return +PI_HP()

def _bern(m):                            # B_0 .. B_m as Fractions (Akiyama-Tanigawa)
    a = [_Fr(0)] * (m + 1); out_ = []
    for k in range(m + 1):
        a[k] = _Fr(1, k + 1)
        for j in range(k, 0, -1):
            a[j - 1] = j * (a[j - 1] - a[j])
        out_.append(a[0])
    return out_
_B = _bern(80)

def _cot(x):
    with localcontext() as c:
        c.prec = _P + 10
        s = d_sin_hp(x); co = d_sin_hp(x + _pi() / 2)
        return co / s

def _psi(x):                             # digamma by recurrence and the asymptotic series
    with localcontext() as c:
        c.prec = _P
        x = D(x)
        if x < 0:
            return _psi(1 - x) - _pi() * _cot(_pi() * x)
        acc = D(0)
        while x < 60:
            acc -= 1 / x; x += 1
        s = x.ln() - 1 / (2 * x)
        for k in range(1, 40):
            b = _B[2 * k]
            s -= D(b.numerator) / D(b.denominator) / (2 * k) / x ** (2 * k)
        return s + acc

def _gser(a, x):                         # P(a,x) by its series of positive terms
    with localcontext() as c:
        c.prec = 160
        a = D(a); x = D(x)
        if x == 0: return D(0)
        term = D(1); s = D(1); k = 0
        while True:
            k += 1; term = term * x / (a + k); s += term
            if term < s * D(10) ** -150: break
        lg = _lg(str(a)) + a.ln()                  # ln Gamma(a+1)
        return (a * x.ln() - x - lg).exp() * s

def _gq(a, x):
    with localcontext() as c:
        c.prec = 160
        return 1 - _gser(a, x)

def _bser(x, a, b):                      # I_x(a,b) by the hypergeometric series (x <= 1/2)
    with localcontext() as c:
        c.prec = 160
        x = D(x); a = D(a); b = D(b)
        if x == 0: return D(0)
        s = D(0); poch = D(1); k = 0; fact = D(1)
        while True:
            term = poch / fact * x ** k / (a + k)
            s += term
            if k > 5 and abs(term) < D(10) ** -150: break
            poch *= (1 - b + k); k += 1; fact *= k
            if k > 20000: break
        B = (_lg(str(a)) + _lg(str(b)) - _lg(str(a + b))).exp()
        return x ** a * s / B

def _binc(x, a, b):
    with localcontext() as c:
        c.prec = 160
        x = D(x)
        if x <= D("0.5"): return _bser(x, a, b)
        return 1 - _bser(1 - x, b, a)

def _tcdf(tt, nu):
    with localcontext() as c:
        c.prec = 160
        tt = D(tt); nu = D(nu)
        if tt == 0: return D("0.5")
        tail = _binc(nu / (nu + tt * tt), nu / 2, D("0.5")) / 2
        return tail if tt < 0 else 1 - tail

def _tpdf(tt, nu):
    with localcontext() as c:
        c.prec = _P
        tt = D(tt); nu = D(nu)
        return (_lg(str((nu + 1) / 2)) - _lg(str(nu / 2))).exp() / (nu * _pi()).sqrt() * \
               (-(nu + 1) / 2 * (1 + tt * tt / nu).ln()).exp()

def _newton(F, f, p, x, lo=None, hi=None, it=60):
    with localcontext() as c:
        c.prec = _P
        p = D(p); x = D(x)
        for _ in range(it):
            dx = (F(x) - p) / f(x)
            xn = x - dx
            if lo is not None and xn <= lo: xn = (x + lo) / 2
            if hi is not None and xn >= hi: xn = (x + hi) / 2
            if abs(xn - x) < abs(xn) * D(10) ** -60: return xn
            x = xn
        return x

def _chi2pdf(x, k):
    with localcontext() as c:
        c.prec = _P
        x = D(x); k = D(k); h = k / 2
        return ((h - 1) * x.ln() - x / 2 - h * D(2).ln() - _lg(str(h))).exp()

def _fpdf(x, d1, d2):
    with localcontext() as c:
        c.prec = _P
        x = D(x); d1 = D(d1); d2 = D(d2)
        u = d1 * x
        return ((d1 * u.ln() + d2 * d2.ln() - (d1 + d2) * (u + d2).ln()) / 2 - x.ln()).exp() / _beta(d1 / 2, d2 / 2)

def _fcdf(x, d1, d2):
    with localcontext() as c:
        c.prec = 160
        x = D(x); d1 = D(d1); d2 = D(d2)
        return _binc(d1 * x / (d1 * x + d2), d1 / 2, d2 / 2)

def _iser(nn, x):                        # I_n(x) by its series
    with localcontext() as c:
        c.prec = 120
        x = abs(D(x)); h = x / 2
        tm = h ** nn / math.factorial(nn); s = tm; k = 0
        while True:
            k += 1; tm = tm * h * h / (k * (k + nn)); s += tm
            if tm < s * D(10) ** -110: break
        return s

def _cosh(x):
    with localcontext() as c:
        c.prec = 120
        e = D(x).exp(); return (e + 1 / e) / 2

def _kquad(nn, x):                       # K_n(x) = int_0^inf e^(-x cosh t) cosh(n t) dt, trapezoid rule
    with localcontext() as c:
        c.prec = 120
        x = D(x); h = D("0.01"); s = D(0); k = 0
        while True:
            tt = h * k
            ch = _cosh(tt)
            v = (-x * ch).exp() * _cosh(nn * tt)
            s += v / 2 if k == 0 else v
            if k > 10 and v < s * D(10) ** -70: break
            k += 1
        return s * h

def _euler():
    return -_psi(1)

def _yser(nn, x):                        # Y_n(x) by its series at high precision
    with localcontext() as c:
        c.prec = 160
        x = D(x); h = x / 2; h2 = h * h; g2 = 2 * _euler()
        s1 = D(0)
        for k in range(nn):
            s1 += D(math.factorial(nn - k - 1)) / math.factorial(k) * h2 ** k
        s1 = -s1 / h ** nn
        s2 = 2 * h.ln() * d_besselj(nn, x)
        Hk = D(0); Hnk = sum((D(1) / j for j in range(1, nn + 1)), D(0))
        tm = D(1) / math.factorial(nn); s3 = (Hk + Hnk - g2) * tm; k = 0
        while True:
            k += 1; Hk += D(1) / k; Hnk += D(1) / (nn + k)
            tm = -tm * h2 / (k * (nn + k)); dl = (Hk + Hnk - g2) * tm; s3 += dl
            if k > x and abs(dl) < D(10) ** -150: break
        s3 = -s3 * h ** nn
        return (s1 + s2 + s3) / _pi()

def _fx(v, nd):                          # bncvs of an exact integer: all its digits
    return fmt(v, max(nd, len(str(abs(v)))))

def _bnl(vs, nd): return " ".join(_fx(v, nd) for v in vs)

# ================================================================ Special.ps 1.4
n = 20
section("Special.ps 1.4 digamma, beta, binomial coefficients", n)
out("countdictstack /spt_ds exch def")      # dictionaries open before these tests
for x in ["0.5", "1", "2", "10.5", "1e-3", "-0.5", "-2.3", "100", "3.75"]:
    bna(f"digamma {x}", f"({x}) digamma", _psi(x), 18)
ra("digamma 1 (real)", "1 digamma", float(_psi(1)))
t("digamma 0 is an error", "0 digamma", "ERR:undefinedresult")
t("digamma -2 is an error", "(-2) digamma", "ERR:undefinedresult")
for a_, b_ in [("0.5", "0.5"), ("2", "3"), ("1.5", "2.5"), ("0.3", "0.7"), ("10", "20")]:
    bna(f"betafn {a_} {b_}", f"({a_}) ({b_}) betafn", _beta(a_, b_), 18)
with localcontext() as c:
    c.prec = _P
    # B(-0.5, 2) = Gamma(-1/2) Gamma(2) / Gamma(3/2), Gamma(-1/2) = -2 sqrt(pi)
    bna("betafn -0.5 2", "(-0.5) (2) betafn", D(-2) * _pi().sqrt() / (_pi().sqrt() / 2), 18)
    bna("lnbeta 100 200", "(100) (200) lnbeta", _lg("100") + _lg("200") - _lg("300"), 18)
    bna("lnbeta 0.5 0.5 = ln pi", "(0.5) (0.5) lnbeta", _pi().ln(), 18)
ra("betafn 2 3 (real)", "2 3 betafn", 1 / 12)
t("betafn 0 1 is an error", "0 1 betafn", "ERR:undefinedresult")
t("betafn -1.5 1.5 is 0", "(-1.5) (1.5) betafn bnt_str", fmt(0, n))
for nn, kk in [(100, 50), (10, 3), (50, 0), (1000, 3), (5, 7), (5, -1), (-3, 2), (-4, 3), (60, 30)]:
    t(f"choose {nn} {kk}", f"({nn}) ({kk}) choose bnt_str", _fx(math.comb(nn, kk) if nn >= 0 and kk >= 0 else
      (0 if kk < 0 else (-1) ** kk * math.comb(kk - nn - 1, kk)), n))
BIG = 123456789012345678901234567890
t("choose of a 30-digit integer", f"({BIG}) 2 choose bnt_str", _fx(BIG * (BIG - 1) // 2, n))
t("choose 10 3 (real)", "10 3 choose", "120.0")
with localcontext() as c:
    c.prec = _P
    t("choose 2.5 2", "(2.5) 2 choose bnt_str", fmt(D("1.875"), n))
    bna("choose 5.5 2.5", "(5.5) (2.5) choose", _gam("6.5") / (_gam("3.5") * _gam("4")), 18)
    bna("choose 0.5 3", "(0.5) 3 choose", D("0.5") * D("-0.5") * D("-1.5") / 6, 18)
t("choose -1 0.5 is an error", "(-1) (0.5) choose", "ERR:undefinedresult")

section("Special.ps 1.4 incomplete gamma and beta", n)
for a_, x_ in [("2", "1"), ("0.5", "0.3"), ("5", "10"), ("10", "5"), ("3.5", "4.5"), ("1", "50"), ("100", "90"), ("2.7", "0.01")]:
    bna(f"gammainc {a_} {x_}", f"({a_}) ({x_}) gammainc", _gser(a_, x_), 18)
    bna(f"gammaincc {a_} {x_}", f"({a_}) ({x_}) gammaincc", _gq(a_, x_), 17)
ra("gammainc 3 5 (real)", "3 5 gammainc", float(_gser(3, 5)))
t("gammainc a = 0 is an error", "0 1 gammainc", "ERR:rangecheck")
t("gammaincc x < 0 is an error", "1 -1 gammaincc", "ERR:rangecheck")
t("gammainc x = 0", "(2) 0 gammainc bnt_str", fmt(0, n))
for x_, a_, b_ in [("0.3", "2", "3"), ("0.9", "2", "3"), ("0.5", "0.5", "0.5"), ("0.1", "10", "1.5"), ("0.99", "5", "5"), ("0.45", "50", "60"), ("1e-5", "0.5", "3")]:
    bna(f"betainc {x_} {a_} {b_}", f"({x_}) ({a_}) ({b_}) betainc", _binc(x_, a_, b_), 18)
ra("betainc 0.4 2 2 (real)", "0.4 2 2 betainc", float(_binc("0.4", 2, 2)))
t("betainc x > 1 is an error", "1.5 2 2 betainc", "ERR:rangecheck")
t("betainc b = 0 is an error", "0.5 2 0 betainc", "ERR:rangecheck")
t("betainc at 1", "(1) 2 3 betainc bnt_str", fmt(1, n))

section("Special.ps 1.4 Bessel I K Y", n)
for nn, x_ in [(0, "1"), (1, "1"), (3, "-2"), (2, "10"), (0, "0.001"), (5, "30")]:
    v = _iser(nn, x_)
    if D(x_) < 0 and nn % 2: v = -v
    bna(f"besseli {nn} {x_}", f"{nn} ({x_}) besseli", v, 18)
for nn, x_ in [(0, "1"), (1, "2"), (2, "0.5"), (0, "50"), (3, "20"), (5, "1"), (1, "40")]:
    bna(f"besselk {nn} {x_}", f"{nn} ({x_}) besselk", _kquad(nn, x_), 18)
for nn, x_ in [(0, "1"), (1, "1"), (3, "20"), (0, "50"), (2, "0.1"), (10, "7.5"), (1, "45")]:
    bna(f"bessely {nn} {x_}", f"{nn} ({x_}) bessely", _yser(nn, x_), 17)
bna("bessely -3 2", "-3 (2) bessely", -_yser(3, "2"), 18)
ra("besselk 1 2.5 (real)", "1 2.5 besselk", float(_kquad(1, "2.5")))
ra("bessely 0 1 (real)", "0 1 bessely", float(_yser(0, "1")))
t("besselk at 0 is an error", "0 0 besselk", "ERR:undefinedresult")
t("bessely of a negative x is an error", "0 -1 bessely", "ERR:rangecheck")
t("besseli with a real order is an error", "0.5 1 besseli", "ERR:typecheck")
t("besseli 2 0", "2 (0) besseli bnt_str", fmt(0, n))

section("Special.ps 1.4 t chi-squared F", n)
for tt, nu in [("2", "5"), ("-3", "3"), ("0.5", "1"), ("1", "2"), ("-1.5", "2.5"), ("10", "4")]:
    bna(f"tcdf {tt} {nu}", f"({tt}) ({nu}) tcdf", _tcdf(tt, nu), 18)
for tt, nu in [("1", "3"), ("0", "1"), ("2.5", "7")]:
    bna(f"tpdf {tt} {nu}", f"({tt}) ({nu}) tpdf", _tpdf(tt, nu), 18)
with localcontext() as c:
    c.prec = _P
    bna("tinv 0.975 10", "(0.975) 10 tinv", _newton(lambda x: _tcdf(x, 10), lambda x: _tpdf(x, 10), "0.975", "2.2"), 18)
    bna("tinv 0.95 1 (closed form)", "(0.95) 1 tinv", -_cot(_pi() * D("0.95")), 18)
    bna("tinv 0.001 2 (closed form)", "(0.001) 2 tinv", (2 * D("0.001") - 1) / (2 * D("0.001") * D("0.999")).sqrt(), 18)
    bna("tinv 1e-6 4", "(1e-6) 4 tinv", _newton(lambda x: _tcdf(x, 4), lambda x: _tpdf(x, 4), "1e-6", "-30", None, 0), 17)
ra("tinv 0.975 10 (real)", "0.975 10 tinv", 2.2281388519862744, "1e-4")
ra("tcdf 2 5 (real)", "2 5 tcdf", float(_tcdf(2, 5)))
t("tinv 0.5 is 0", "(0.5) 3 tinv bnt_str", fmt(0, n))
t("tinv 1 is an error", "1 3 tinv", "ERR:rangecheck")
t("tcdf nu = 0 is an error", "1 0 tcdf", "ERR:rangecheck")
for x_, k_ in [("3.84", "1"), ("10", "5"), ("0.5", "3"), ("50", "40")]:
    bna(f"chi2cdf {x_} {k_}", f"({x_}) ({k_}) chi2cdf", _gser(D(k_) / 2, D(x_) / 2), 18)
for x_, k_ in [("0.5", "4"), ("3", "1"), ("7.5", "5.5")]:
    bna(f"chi2pdf {x_} {k_}", f"({x_}) ({k_}) chi2pdf", _chi2pdf(x_, k_), 18)
t("chi2pdf 0 2", "(0) 2 chi2pdf bnt_str", fmt(D("0.5"), n))
t("chi2pdf 0 1 is an error", "0 1 chi2pdf", "ERR:undefinedresult")
with localcontext() as c:
    c.prec = _P
    bna("chi2inv 0.95 3", "(0.95) 3 chi2inv", _newton(lambda x: _gser(D("1.5"), x / 2), lambda x: _chi2pdf(x, 3), "0.95", "7.8", D(0)), 18)
    bna("chi2inv 0.05 10", "(0.05) 10 chi2inv", _newton(lambda x: _gser(D(5), x / 2), lambda x: _chi2pdf(x, 10), "0.05", "3.9", D(0)), 18)
ra("chi2inv 0.99 2 (real)", "0.99 2 chi2inv", -2 * math.log(0.01), "1e-4")
for x_, a_, b_ in [("2", "3", "7"), ("0.5", "10", "4"), ("5", "1", "1")]:
    bna(f"fcdf {x_} {a_} {b_}", f"({x_}) ({a_}) ({b_}) fcdf", _fcdf(x_, a_, b_), 18)
bna("fpdf 2 3 7", "(2) 3 7 fpdf", _fpdf("2", 3, 7), 18)
with localcontext() as c:
    c.prec = _P
    bna("finv 0.95 3 7", "(0.95) 3 7 finv", _newton(lambda x: _fcdf(x, 3, 7), lambda x: _fpdf(x, 3, 7), "0.95", "4.3", D(0)), 18)
ra("finv 0.5 2 2 (real)", "0.5 2 2 finv", 1.0, "1e-4")
with localcontext() as c:
    c.prec = _P
    ra("finv 0.05 5 10 (real)", "0.05 5 10 finv", float(_newton(lambda x: _fcdf(x, 5, 10), lambda x: _fpdf(x, 5, 10), "0.05", "0.2", D(0))), "1e-5")
    ra("tinv 1e-6 4 (real)", "1e-6 4 tinv", float(_newton(lambda x: _tcdf(x, 4), lambda x: _tpdf(x, 4), "1e-6", "-30", None, 0)), "1e-3")
    ra("tinv 0.3 3.5 (real)", "0.3 3.5 tinv", float(_newton(lambda x: _tcdf(x, "3.5"), lambda x: _tpdf(x, "3.5"), "0.3", "-0.5")), "1e-5")
    ra("chi2inv 0.05 10 (real)", "0.05 10 chi2inv", float(_newton(lambda x: _gser(D(5), x / 2), lambda x: _chi2pdf(x, 10), "0.05", "3.9", D(0))), "1e-4")
t("chi2inv 1.5 3 (real) is an error", "1.5 3 chi2inv", "ERR:rangecheck")
t("finv d1 = 0 is an error", "0.5 0 2 finv", "ERR:rangecheck")
ra("fcdf 2 3 7 (real)", "2 3 7 fcdf", float(_fcdf("2", 3, 7)))
ra("fpdf 2 3 7 (real)", "2 3 7 fpdf", float(_fpdf("2", 3, 7)))
ra("chi2cdf 10 5 (real)", "10 5 chi2cdf", float(_gser(D("2.5"), 5)))
ra("chi2pdf 3 1 (real)", "3 1 chi2pdf", float(_chi2pdf("3", 1)))
ra("tpdf 2.5 7 (real)", "2.5 7 tpdf", float(_tpdf("2.5", 7)))
ra("tcdf -1.5 2.5 (real)", "-1.5 2.5 tcdf", float(_tcdf("-1.5", "2.5")))
t("tcdf nu = 0 (real) is an error", "1 0 tcdf", "ERR:rangecheck")
t("fpdf 0 1 1 (real) is an error", "0 1 1 fpdf", "ERR:undefinedresult")

section("Special.ps 1.4 exponential binomial Poisson", n)
with localcontext() as c:
    c.prec = _P
    bna("exppdf 1 2", "(1) 2 exppdf", 2 * D(-2).exp(), 18)
    bna("expcdf 1e-10 1 (small)", "(1e-10) 1 expcdf", 1 - D("-1e-10").exp(), 18)
    bna("expinv 0.5 2", "(0.5) 2 expinv", D(2).ln() / 2, 18)
    bna("expinv 1e-30 1 (small)", "(1e-30) 1 expinv", -(1 - D("1e-30")).ln(), 18)
t("exppdf x < 0", "(-1) 2 exppdf bnt_str", fmt(0, n))
t("exppdf lambda = 0 is an error", "1 0 exppdf", "ERR:rangecheck")
ra("expcdf 2 0.5 (real)", "2 0.5 expcdf", 1 - math.exp(-1))
ra("exppdf 1 2 (real)", "1 2 exppdf", 2 * math.exp(-2))
ra("expinv 0.5 2 (real)", "0.5 2 expinv", math.log(2) / 2)
t("expinv 1 2 (real) is an error", "1 2 expinv", "ERR:rangecheck")
def _bpmf(k, nn, p): return math.comb(nn, k) * p ** k * (1 - p) ** (nn - k)
def _fdec(q, nd):
    with localcontext() as c:
        c.prec = _P
        return D(q.numerator) / D(q.denominator)
P3 = _Fr(3, 10)
for k_ in [0, 3, 10]:
    bna(f"binompdf {k_} 10 0.3", f"{k_} 10 (0.3) binompdf", _fdec(_bpmf(k_, 10, P3), n), 18)
for k_ in [0, 3, 9]:
    bna(f"binomcdf {k_} 10 0.3", f"{k_} 10 (0.3) binomcdf", _fdec(sum(_bpmf(j, 10, P3) for j in range(k_ + 1)), n), 18)
bna("binomcdf 40 100 0.5", "40 100 (0.5) binomcdf", _fdec(sum(_bpmf(j, 100, _Fr(1, 2)) for j in range(41)), n), 18)
t("binomcdf k >= n", "(12) 10 (0.3) binomcdf bnt_str", fmt(1, n))
t("binompdf of a non-integer k is an error", "1.5 10 0.3 binompdf", "ERR:rangecheck")
def _bquant(q, nn, p):
    s = _Fr(0)
    for k in range(nn + 1):
        s += _bpmf(k, nn, p)
        if s >= q: return k
for q_ in ["0.5", "0.05", "0.99"]:
    t(f"binominv {q_} 10 0.3", f"({q_}) 10 (0.3) binominv", str(_bquant(_Fr(q_), 10, P3)))
t("binominv 0.5 20 0.5 (real)", "0.5 20 0.5 binominv", str(_bquant(_Fr(1, 2), 20, _Fr(1, 2))))
def _ppmf(k, lam):
    with localcontext() as c:
        c.prec = _P
        lam = D(lam); return (-lam).exp() * lam ** k / math.factorial(k)
for k_, l_ in [(2, "3"), (0, "0.5"), (10, "2.5"), (30, "25")]:
    bna(f"poissonpdf {k_} {l_}", f"{k_} ({l_}) poissonpdf", _ppmf(k_, l_), 18)
for k_, l_ in [(2, "3"), (10, "2.5"), (30, "25")]:
    with localcontext() as c:
        c.prec = _P
        bna(f"poissoncdf {k_} {l_}", f"{k_} ({l_}) poissoncdf", sum((_ppmf(j, l_) for j in range(k_ + 1)), D(0)), 18)
def _pquant(q, lam):
    with localcontext() as c:
        c.prec = _P
        s = D(0); k = 0
        while True:
            s += _ppmf(k, lam)
            if s >= D(q): return k
            k += 1
for q_, l_ in [("0.9", "3"), ("0.5", "10"), ("0.001", "2")]:
    t(f"poissoninv {q_} {l_}", f"({q_}) ({l_}) poissoninv", str(_pquant(q_, l_)))
t("poissoninv 0.5 10 (real)", "0.5 10 poissoninv", str(_pquant("0.5", "10")))
t("binominv 0.99 10 0.3 (real)", "0.99 10 0.3 binominv", str(_bquant(_Fr(99, 100), 10, P3)))
t("poissonpdf lambda = 0 is an error", "1 0 poissonpdf", "ERR:rangecheck")
t("poissoncdf k < 0", "(-1) 2 poissoncdf bnt_str", fmt(0, n))

n = 40
section("Special.ps 1.4 precision 40", n)
bna("digamma 0.25", "(0.25) digamma", _psi("0.25"), 38)
bna("gammaincc 3 7", "(3) (7) gammaincc", _gq(3, 7), 37)
bna("betainc 0.3 2.5 4", "(0.3) (2.5) (4) betainc", _binc("0.3", "2.5", 4), 38)
bna("besselk 1 3", "1 (3) besselk", _kquad(1, "3"), 38)
bna("bessely 2 5", "2 (5) bessely", _yser(2, "5"), 37)
bna("tcdf -2.5 6", "(-2.5) 6 tcdf", _tcdf("-2.5", 6), 38)
n = 20

# ================================================================ bignumlibrary.ps 1.4
section("bignumlibrary.ps 1.4 powmodbn isprime factor", n)
for a_, b_, m_ in [(2, 100, 1000000007), (3, 200, 1000000000000000003), (-7, 3, 10), (123456789, 0, 97),
                   (5, 117, 19), (10, 30, 7), ("98765432109876543210987654321", 12345, "1000000000000000000000000057")]:
    v = pow(int(a_), int(b_), int(m_))
    t(f"powmodbn {a_} {b_} {m_}", f"({a_}) ({b_}) ({m_}) powmodbn bnt_str", _fx(v, n))
t("powmodbn m = 0 is an error", "2 3 0 powmodbn", "ERR:rangecheck")
t("powmodbn b < 0 is an error", "2 -3 5 powmodbn", "ERR:rangecheck")
def _isp(m):
    if m < 2: return False
    if m % 2 == 0: return m == 2
    f = 3
    while f * f <= m:
        if m % f == 0: return False
        f += 2
    return True
for v in [0, 1, 2, 97, 91, 561, 7919, 2147483647, 1000003 * 1000033]:
    t(f"isprime {v}", f"{v} isprime", "true" if _isp(v) else "false")
for v, ok in [((1 << 61) - 1, True), ((1 << 89) - 1, True), ((1 << 127) - 1, True), ((1 << 67) - 1, False),
              (3215031751, False), (3825123056546413051, False), (318665857834031151167461, False),
              (3317044064679887385961981, False), (100000000000000000039, True), (-7, False)]:
    t(f"isprime {v}", f"({v}) isprime", "true" if ok else "false")
t("isprime of a fraction is an error", "2.5 isprime", "ERR:rangecheck")
def _fac(m):
    out_ = []; f = 2
    while f * f <= m:
        while m % f == 0: out_.append(f); m //= f
        f += 1
    if m > 1: out_.append(m)
    return out_
for v in [360, 1, 97, 2147483647, 1024, 999999937 * 2]:
    t(f"factor {v}", f"{v} factor bnt_list", " ".join(map(str, _fac(v))))
for v in [600851475143, 123456789012345678901234567890, 100003 * 1000003]:
    t(f"factor {v}", f"({v}) factor bnt_list", _bnl(_fac(v), n))
t("factor 2^64+1 (Pollard rho)", f"({(1 << 64) + 1}) factor bnt_list", _bnl([274177, 67280421310721], n))
t("factor 0 is an error", "0 factor", "ERR:rangecheck")
t("factor -6 is an error", "-6 factor", "ERR:rangecheck")

# errors must close the dictionaries of the procedure that raises them
t("setbn of a bad string closes its dictionary", "countdictstack mark (1x2) { setbn } stopped pop cleartomark countdictstack sub", "0")
t("divbn by 0 closes its dictionary", "countdictstack mark 1 setbn 0 setbn { divbn } stopped pop cleartomark countdictstack sub", "0")
t("choose of a bad string is a syntaxerror", "(1x2) 2 choose", "ERR:syntaxerror")
t("no dictionaries left open by the error tests of 1.4", "countdictstack spt_ds sub", "0")

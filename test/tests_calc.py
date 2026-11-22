# Tests of the version 1.4 additions to Numeric.ps: statistics, regression,
# random numbers, Gauss-Legendre. Run by make_tests.py in its namespace.
import math as _m

def _q(x): return F(D(x)) if isinstance(x, str) else F(x)
def _dec(q):
    with localcontext() as c:
        c.prec = HP
        return D(q.numerator) / D(q.denominator)
def _dsqrt(q):
    with localcontext() as c:
        c.prec = HP
        return (D(q.numerator) / D(q.denominator)).sqrt()
def _ps(xs): return "[" + " ".join(str(x) if not isinstance(x, str) else f"({x})" for x in xs) + "]"

# ---------------------------------------------------------------- statistics
section("Numeric.ps 1.4 statistics", n)
# Earlier error tests of setbn leave its local dictionary open, and it has a
# /mode of its own; so the tests of mode fetch it from tx@NumericDict.
MODE = "tx@NumericDict /mode get exec"
S8 = [2, 4, 4, 4, 5, 5, 7, 9]
t("listmin", "[5 3 8 -2 7] listmin", "-2")
t("listmax", "[5 3 8 -2 7] listmax", "8")
t("listsum", f"{_ps(S8)} listsum", "40")
t("listsum of nothing", "[] listsum", "0")
t("listmin of nothing", "[] listmin", "ERR:rangecheck")
t("listmin bignums", "[(0.3) (0.1) (0.2)] listmin bnt_str", fdec(F(1, 10), n))
t("listmax bignums", "[(0.3) (0.1) (0.2)] listmax bnt_str", fdec(F(3, 10), n))
t("listsum bignums", "[(0.1) (0.2) (0.3)] listsum bnt_str", fdec(F(6, 10), n))
t("mode", f"[3 1 3 2 2] {MODE}", "2")
t("mode one value", f"[5] {MODE}", "5")
t("mode all different", f"[3 1 2] {MODE}", "1")
t("mode of S8", f"{_ps(S8)} {MODE}", "4")
t("mode bignums", f"[(0.5) (0.25) (0.5)] {MODE} bnt_str", fdec(F(1, 2), n))
t("mode of nothing", f"[] {MODE}", "ERR:rangecheck")
ra("wmean", "[1 2 3] [1 1 2] wmean", 2.25)
t("wmean bignums", "[(0.1) (0.2)] [1 3] wmean bnt_str", fdec(F(175, 1000), n))
t("wmean lengths differ", "[1 2 3] [1 1] wmean", "ERR:rangecheck")
t("wmean weights add to 0", "[1 2] [1 -1] wmean", "ERR:undefinedresult")

def _skew_kurt(xs):
    xs = [_q(x) for x in xs]; k = len(xs); mu = sum(xs) / k
    m2 = sum((x - mu) ** 2 for x in xs); m3 = sum((x - mu) ** 3 for x in xs); m4 = sum((x - mu) ** 4 for x in xs)
    s2 = m2 / (k - 1)
    with localcontext() as c:
        c.prec = HP
        s2d = _dec(s2)
        g1 = _dec(m3) / (s2d * s2d.sqrt()) * k / ((k - 1) * (k - 2))
        g2 = _dec(m4 / (s2 * s2)) * k * (k + 1) / ((k - 1) * (k - 2) * (k - 3)) - D(3 * (k - 1) ** 2) / ((k - 2) * (k - 3))
    return g1, g2
g1, g2 = _skew_kurt(S8)
ra("skewness", f"{_ps(S8)} skewness", float(g1))
ra("kurtosis", f"{_ps(S8)} kurtosis", float(g2))
SK = ["0.5", "1.25", "0.75", "3", "2.5", "0.125"]
g1, g2 = _skew_kurt(SK)
bna("skewness bignums", f"{_ps(SK)} skewness", g1, 18)
bna("kurtosis bignums", f"{_ps(SK)} kurtosis", g2, 18)
t("skewness of 2 values", "[1 2] skewness", "ERR:rangecheck")
t("kurtosis of 3 values", "[1 2 3] kurtosis", "ERR:rangecheck")
t("skewness of a constant", "[5 5 5] skewness", "ERR:undefinedresult")
t("skewness symmetric", "[1 2 3 4 5] skewness", "0.0")

def _quant(xs, p):
    s = sorted(_q(x) for x in xs); h = (len(s) - 1) * _q(p); lo = int(h)
    return s[lo] if lo == len(s) - 1 else s[lo] + (h - lo) * (s[lo + 1] - s[lo])
Q6 = [7, 1, 3, 10, 4, 2]
for p in ["0", "0.25", "0.5", "0.9", "1"]:
    ra(f"quantile {p}", f"{_ps(Q6)} {p} quantile", float(_quant(Q6, p)))
t("quantile 0.5 is the median", f"{_ps(Q6)} 0.5 quantile {_ps(Q6)} median eq", "true")
t("quantile bignums", f"{_ps(['0.7', '0.1', '0.3', '1.0', '0.4'])} (0.3) quantile bnt_str",
  fdec(_quant(['0.7', '0.1', '0.3', '1.0', '0.4'], '0.3'), n))
t("quantile one value", "[4] 0.3 quantile", "4")
t("quantile p < 0", f"{_ps(Q6)} -0.1 quantile", "ERR:rangecheck")
t("quantile p > 1", f"{_ps(Q6)} 1.5 quantile", "ERR:rangecheck")
t("quantile of nothing", "[] 0.5 quantile", "ERR:rangecheck")
t("histogram", "[1 2 3 4 5 9] 0 10 5 histogram bnt_list", "1 2 2 0 1")
t("histogram last bin closed", "[0 5 10 10] 0 10 2 histogram bnt_list", "1 3")
t("histogram outside ignored", "[-1 11 5 4.99] 0 10 2 histogram bnt_list", "1 1")
t("histogram bignums", "[(0.1) (0.5) (0.9) (0.49999999999)] (0) (1) 2 histogram bnt_list", "2 2")
t("histogram k = 0", "[1 2] 0 10 0 histogram", "ERR:rangecheck")
t("histogram k not an integer", "[1 2] 0 10 2.5 histogram", "ERR:rangecheck")
t("histogram a = b", "[1 2] 3 3 2 histogram", "ERR:rangecheck")

# ---------------------------------------------------------------- regression references
def _solve(Mx, v):  # exact Gauss-Jordan
    k = len(v); A = [row[:] + [v[i]] for i, row in enumerate(Mx)]
    for c in range(k):
        p = next(r for r in range(c, k) if A[r][c] != 0); A[c], A[p] = A[p], A[c]
        for r in range(k):
            if r != c and A[r][c] != 0:
                f = A[r][c] / A[c][c]; A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [A[i][k] / A[i][i] for i in range(k)]
def _inv(Mx):
    k = len(Mx); cols = [_solve(Mx, [F(int(i == j)) for i in range(k)]) for j in range(k)]
    return [[cols[j][i] for j in range(k)] for i in range(k)]

def wls(B, Y, W=None):
    """B rows of basis values, Y values, W weights (Fractions) -> dict of exact statistics."""
    nn = len(Y); k = len(B[0]); W = W or [F(1)] * nn
    XtX = [[sum(W[r] * B[r][i] * B[r][j] for r in range(nn)) for j in range(k)] for i in range(k)]
    Xty = [sum(W[r] * B[r][i] * Y[r] for r in range(nn)) for i in range(k)]
    c = _solve(XtX, Xty); P = _inv(XtX)
    fit = [sum(c[i] * B[r][i] for i in range(k)) for r in range(nn)]
    res = [Y[r] - fit[r] for r in range(nn)]
    sse = sum(W[r] * res[r] ** 2 for r in range(nn)); dof = nn - k
    s2 = sse / dof
    ybar = sum(W[r] * Y[r] for r in range(nn)) / sum(W)
    sst = sum(W[r] * (Y[r] - ybar) ** 2 for r in range(nn))
    ssr = sum(W[r] * (fit[r] - ybar) ** 2 for r in range(nn))
    h = [W[r] * sum(B[r][i] * P[i][j] * B[r][j] for i in range(k) for j in range(k)) for r in range(nn)]
    return dict(c=c, P=P, fit=fit, res=res, sse=sse, dof=dof, s2=s2, sst=sst, ssr=ssr, h=h, W=W, k=k, n=nn)
def quad(P, b): return sum(b[i] * P[i][j] * b[j] for i in range(len(b)) for j in range(len(b)))

def _tcdf(x, nu):  # Student's t, integer nu (Abramowitz-Stegun 26.7.3/4)
    th = _m.atan(abs(x) / _m.sqrt(nu)); c, s = _m.cos(th), _m.sin(th)
    if nu % 2:
        tot = 0.0
        if nu >= 3:
            term = c; tot = c
            for j in range(1, (nu - 3) // 2 + 1):
                term *= c * c * 2 * j / (2 * j + 1); tot += term
        a = 2 / _m.pi * (th + s * tot)
    else:
        term = 1.0; tot = 1.0
        for j in range(1, nu // 2):
            term *= c * c * (2 * j - 1) / (2 * j); tot += term
        a = s * tot
    return 0.5 + a / 2 if x >= 0 else 0.5 - a / 2
def tq(p, nu):
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if _tcdf(mid, nu) < p: lo = mid
        else: hi = mid
    return (lo + hi) / 2

# ---------------------------------------------------------------- straight line (GLLSR example)
section("Numeric.ps 1.4 regression", n)
X1 = [1, 2, 3, 4, 5, 6, 7, 8]
Y1 = ["2.3", "4.1", "6.4", "7.7", "10.2", "12.1", "13.8", "16.3"]
B1 = [[F(1), F(x)] for x in X1]; YQ1 = [_q(y) for y in Y1]
r1 = wls(B1, YQ1)
L1 = f"{_ps(X1)} [{' '.join(Y1)}]"
R1 = f"{L1} 1 regress"
t1 = tq(0.975, 6)
s1 = float(r1["s2"]) ** 0.5
la("linear coef", f"{R1} /coef get", [float(v) for v in r1["c"]])
la("linear se", f"{R1} /se get", [(float(r1['s2'] * r1['P'][i][i])) ** 0.5 for i in range(2)])
la("linear cov", f"{R1} /cov get", [float(r1["s2"] * r1["P"][i][j]) for j in range(2) for i in range(2)])
ra("linear r2", f"{R1} /r2 get", float(1 - r1["sse"] / r1["sst"]))
ra("linear adjr2", f"{R1} /adjr2 get", float(1 - r1["sse"] / r1["sst"] * F(7, 6)))
ra("linear s", f"{R1} /s get", s1)
ra("linear sse", f"{R1} /sse get", float(r1["sse"]), "1e-4")
ra("linear sst", f"{R1} /sst get", float(r1["sst"]), "1e-3")
ra("linear ssr", f"{R1} /ssr get", float(r1["ssr"]), "1e-3")
t("linear n", f"{R1} /n get", "8")
t("linear k", f"{R1} /k get", "2")
t("linear dof", f"{R1} /dof get", "6")
ra("linear tval", f"{R1} /tval get", t1, "1e-4")
ra("linear level", f"{R1} /level get", 0.95)
la("linear fitted", f"{R1} /fitted get", [float(v) for v in r1["fit"]])
la("linear resid", f"{R1} /resid get", [float(v) for v in r1["res"]])
la("linear stdresid", f"{R1} /stdresid get",
   [float(r1["res"][i]) / (s1 * (1 - float(r1["h"][i])) ** 0.5) for i in range(8)])
# the textbook formulas for a straight line (GLLSR, Devore)
xb = sum(F(x) for x in X1) / 8; sxx = sum((F(x) - xb) ** 2 for x in X1)
for x0 in [F(9, 2), F(10)]:
    y0 = r1["c"][0] + r1["c"][1] * x0
    ci = t1 * s1 * float(F(1, 8) + (x0 - xb) ** 2 / sxx) ** 0.5
    pi = t1 * s1 * float(1 + F(1, 8) + (x0 - xb) ** 2 / sxx) ** 0.5
    ra(f"GLLSR example regeval at {float(x0)}", f"{R1} {float(x0)} regeval", float(y0))
    la(f"GLLSR example regci at {float(x0)}", f"{R1} {float(x0)} regci", [float(y0) - ci, float(y0) + ci])
    la(f"GLLSR example regpi at {float(x0)}", f"{R1} {float(x0)} regpi", [float(y0) - pi, float(y0) + pi])
la("linreg is 1 regress", f"{L1} linreg /coef get", [float(v) for v in r1["c"]])
t("model of linreg", f"{L1} linreg /model get", "1")
t("model /linear is 1", f"{L1} /linear regress /model get", "1")
t("intercept null", f"{L1} linreg /intercept get null eq", "true")
t("weights null", f"{L1} linreg /weights get null eq", "true")
t("x kept as given", f"{L1} linreg /x get bnt_list", " ".join(map(str, X1)))
t("y kept as given", f"{L1} linreg /y get 1 get", "4.1")
t("params of a polynomial", f"{L1} linreg /params get /coef get length", "2")
la("level 0.99", f"{L1} << /model 1 /level 0.99 >> regress /tval get", [tq(0.995, 6)])

# ---------------------------------------------------------------- quadratic, own basis, weights, intercept
X2 = [0, 1, 2, 3, 4, 5, 6]; Y2 = ["1.2", "1.9", "4.1", "7.8", "13.2", "20.5", "28.9"]
B2 = [[F(1), F(x), F(x) ** 2] for x in X2]; r2_ = wls(B2, [_q(y) for y in Y2])
R2 = f"{_ps(X2)} [{' '.join(Y2)}] 2 regress"
s2r = float(r2_["s2"]) ** 0.5; t2 = tq(0.975, 4)
la("quadratic coef", f"{R2} /coef get", [float(v) for v in r2_["c"]])
la("quadratic se", f"{R2} /se get", [float(r2_["s2"] * r2_["P"][i][i]) ** 0.5 for i in range(3)])
ra("quadratic r2", f"{R2} /r2 get", float(1 - r2_["sse"] / r2_["sst"]))
b0 = [F(1), F(5, 2), F(25, 4)]; y0 = float(sum(c * b for c, b in zip(r2_["c"], b0)))
w0 = t2 * s2r * float(1 + quad(r2_["P"], b0)) ** 0.5
la("quadratic regpi at 2.5 (general formula)", f"{R2} 2.5 regpi", [y0 - w0, y0 + w0])
w0 = t2 * s2r * float(quad(r2_["P"], b0)) ** 0.5
la("quadratic regci at 2.5", f"{R2} 2.5 regci", [y0 - w0, y0 + w0])
la("quadratic stdresid", f"{R2} /stdresid get",
   [float(r2_["res"][i]) / (s2r * (1 - float(r2_["h"][i])) ** 0.5) for i in range(7)])

BP = "{ dup dup mul 2 array astore }"
X3 = [1, 2, 3, 4, 5]; Y3 = ["1.1", "3.9", "9.2", "15.8", "25.1"]
r3 = wls([[F(x), F(x) ** 2] for x in X3], [_q(y) for y in Y3])
R3 = f"{_ps(X3)} [{' '.join(Y3)}] {BP} regress"
la("own basis x, x^2 coef", f"{R3} /coef get", [float(v) for v in r3["c"]])
la("own basis se", f"{R3} /se get", [float(r3["s2"] * r3["P"][i][i]) ** 0.5 for i in range(2)])
ra("own basis regeval", f"{R3} 2.5 regeval", float(r3["c"][0] * F(5, 2) + r3["c"][1] * F(25, 4)))
t("own basis model", f"{R3} /model get", "basis")
t("own basis kept", f"{R3} /basis get xcheck", "true")
t("own basis in a dict", f"{_ps(X3)} [{' '.join(Y3)}] << /model {BP} >> regress /k get", "2")

W4 = [1, 2, 1, 2, 4, 1, 1, 3]
r4 = wls(B1, YQ1, [F(w) for w in W4])
R4 = f"{L1} << /model 1 /weights {_ps(W4)} >> regress"
la("weighted coef", f"{R4} /coef get", [float(v) for v in r4["c"]])
la("weighted se", f"{R4} /se get", [float(r4["s2"] * r4["P"][i][i]) ** 0.5 for i in range(2)])
ra("weighted s", f"{R4} /s get", float(r4["s2"]) ** 0.5)
ra("weighted r2", f"{R4} /r2 get", float(1 - r4["sse"] / r4["sst"]))
la("weighted stdresid", f"{R4} /stdresid get",
   [float(W4[i]) ** 0.5 * float(r4["res"][i]) / (float(r4["s2"]) ** 0.5 * (1 - float(r4["h"][i])) ** 0.5) for i in range(8)])
t("weights kept", f"{R4} /weights get length", "8")

r5 = wls([[F(x)] for x in X1], [y - 1 for y in YQ1])
R5 = f"{L1} << /model 1 /intercept 1 >> regress"
la("intercept 1: coef", f"{R5} /coef get", [1.0, float(r5["c"][0])])
la("intercept 1: se", f"{R5} /se get", [0.0, float(r5["s2"] * r5["P"][0][0]) ** 0.5])
t("intercept 1: dof", f"{R5} /dof get", "7")
t("intercept 1: k", f"{R5} /k get", "1")
t("intercept kept", f"{R5} /intercept get", "1")
ra("intercept 1: regeval at 0", f"{R5} 0 regeval", 1.0)
y0 = 1 + float(r5["c"][0]) * 4; w0 = tq(0.975, 7) * float(r5["s2"]) ** 0.5 * float(1 + 16 * r5["P"][0][0]) ** 0.5
la("intercept 1: regpi at 4", f"{R5} 4 regpi", [y0 - w0, y0 + w0])
r6 = wls([[F(x), F(x) ** 2] for x in X2], [_q(y) - F(1) for y in Y2])
la("quadratic through (0, 1)", f"{_ps(X2)} [{' '.join(Y2)}] << /model 2 /intercept 1 >> regress /coef get",
   [1.0] + [float(v) for v in r6["c"]])

# ---------------------------------------------------------------- transforms
def tfit(xs, ys, fx, fy, deg=1):
    B = [[F(fx(x)) ** j for j in range(deg + 1)] for x in xs]
    return wls(B, [F(fy(y)) for y in ys])
XT = [1, 2, 3, 4, 5, 6]
YPW = [2.1, 5.5, 10.6, 15.8, 22.6, 29.1]
rp = tfit(XT, YPW, _m.log, _m.log)
RP = f"{_ps(XT)} {_ps(YPW)} /power regress"
la("power coef (ln a, b)", f"{RP} /coef get", [float(v) for v in rp["c"]])
ra("power a", f"{RP} /params get /a get", _m.exp(float(rp["c"][0])))
ra("power b", f"{RP} /params get /b get", float(rp["c"][1]))
ra("power regeval at 3.5", f"{RP} 3.5 regeval", _m.exp(float(rp["c"][0])) * 3.5 ** float(rp["c"][1]), "1e-4")
ra("power r2 (of ln y)", f"{RP} /r2 get", float(1 - rp["sse"] / rp["sst"]))
b0 = [F(1), F(_m.log(3.5))]; yl = float(sum(c * b for c, b in zip(rp["c"], b0)))
w0 = tq(0.975, 4) * float(rp["s2"]) ** 0.5 * float(1 + quad(rp["P"], b0)) ** 0.5
la("power regpi transformed back", f"{RP} 3.5 regpi", [_m.exp(yl - w0), _m.exp(yl + w0)])
t("power model", f"{RP} /model get", "power")
YEX = [2.7, 7.6, 19.8, 55.1, 147.0, 405.0]
re_ = tfit(XT, YEX, float, _m.log)
REX = f"{_ps(XT)} {_ps(YEX)} /exp regress"
ra("exp a", f"{REX} /params get /a get", _m.exp(float(re_["c"][0])), "1e-4")
ra("exp b", f"{REX} /params get /b get", float(re_["c"][1]))
ra("exp regeval at 2.5", f"{REX} 2.5 regeval", _m.exp(float(re_["c"][0]) + 2.5 * float(re_["c"][1])), "1e-4")
YLG = [1.1, 2.9, 4.1, 4.8, 5.6, 6.1]
rl = tfit(XT, YLG, lambda x: _m.log10(x), float)
la("log10 coef", f"{_ps(XT)} {_ps(YLG)} /log10 regress /coef get", [float(v) for v in rl["c"]])
la("log10 params", f"{_ps(XT)} {_ps(YLG)} /log10 regress /params get dup /a get exch /b get 2 array astore",
   [float(v) for v in rl["c"]])
rn = tfit(XT, YLG, _m.log, float)
la("ln coef", f"{_ps(XT)} {_ps(YLG)} /ln regress /coef get", [float(v) for v in rn["c"]])
ra("ln regeval at 10", f"{_ps(XT)} {_ps(YLG)} /ln regress 10 regeval", float(rn["c"][0]) + float(rn["c"][1]) * _m.log(10))
YRC = [5.1, 3.4, 2.9, 2.7, 2.6, 2.45]
rr = tfit(XT, YRC, lambda x: 1 / x, float)
la("recip coef", f"{_ps(XT)} {_ps(YRC)} /recip regress /coef get", [float(v) for v in rr["c"]])
XG = [-1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3]
YG = [round(3 * _m.exp(-(x - 1) ** 2 / (2 * 0.8 ** 2)) * (1 + 0.01 * ((i * 7) % 5 - 2)), 4) for i, x in enumerate(XG)]
rg = tfit(XG, YG, float, _m.log, 2)
c0, c1, c2 = (float(v) for v in rg["c"])
sg2 = -1 / (2 * c2)
RG = f"{_ps(XG)} {_ps(YG)} /gauss regress"
ra("gauss sigma", f"{RG} /params get /sigma get", sg2 ** 0.5, "1e-4")
ra("gauss mu", f"{RG} /params get /mu get", c1 * sg2, "1e-4")
ra("gauss A", f"{RG} /params get /A get", _m.exp(c0 - c1 * c1 / (4 * c2)), "1e-4")
ra("gauss regeval at 1.2", f"{RG} 1.2 regeval", _m.exp(c0 + 1.2 * c1 + 1.44 * c2), "1e-4")
t("gauss k", f"{RG} /k get", "3")

# ---------------------------------------------------------------- errors
t("power with x = 0", "[0 1 2] [1 2 3] /power regress", "ERR:rangecheck")
t("exp with y < 0", "[0 1 2] [1 -2 3] /exp regress", "ERR:rangecheck")
t("log10 with x < 0", "[-1 1 2] [1 2 3] /log10 regress", "ERR:rangecheck")
t("recip with x = 0", "[0 1 2] [1 2 3] /recip regress", "ERR:rangecheck")
t("gauss with y = 0", "[0 1 2 3] [1 0 3 1] /gauss regress", "ERR:rangecheck")
t("gauss opening upwards", "[0 1 2 3] [4 1 1 4] /gauss regress", "ERR:undefinedresult")
t("no degrees of freedom", "[1 2] [1 2] 1 regress", "ERR:rangecheck")
t("negative degree", "[1 2 3] [1 2 3] -1 regress", "ERR:rangecheck")
t("unknown model", "[1 2 3] [1 2 3] /cubic regress", "ERR:rangecheck")
t("model a string", "[1 2 3] [1 2 3] (1) regress", "ERR:typecheck")
t("dict without model", "[1 2 3] [1 2 3] << /level 0.9 >> regress", "ERR:typecheck")
t("lengths differ", "[1 2 3] [1 2] 1 regress", "ERR:rangecheck")
t("weight 0", "[1 2 3] [1 2 4] << /model 1 /weights [1 0 1] >> regress", "ERR:rangecheck")
t("weights too few", "[1 2 3] [1 2 4] << /model 1 /weights [1 1] >> regress", "ERR:rangecheck")
t("level 1", "[1 2 3] [1 2 4] << /model 1 /level 1 >> regress", "ERR:rangecheck")
t("intercept with own basis", f"[1 2 3] [1 2 4] << /model {BP} /intercept 0 >> regress", "ERR:rangecheck")
t("intercept leaves nothing to fit", "[1 2 3] [1 2 4] << /model 0 /intercept 0 >> regress", "ERR:rangecheck")
t("dependent columns", "[1 1 1] [1 2 3] 1 regress", "ERR:undefinedresult")
t("basis not a list", "[1 2 3] [1 2 4] { } regress", "ERR:typecheck")
t("basis of unequal lengths", "[1 2 3 4] [1 2 4 5] { dup 2 gt { 1 2 array astore }{ 1 array astore } ifelse } regress", "ERR:rangecheck")
t("error leaves the operands", "{ [1 2] [1 2] 1 regress } stopped pop pop length exch length add", "4")
t("errors keep the dictionary stack", "countdictstack { [0 1 2] [1 2 3] /power regress } stopped pop pop pop pop "
  "{ [1 1 1] [1 2 3] 1 regress } stopped pop pop pop pop { [1 2] [1 2] 1 regress } stopped pop pop pop pop "
  "countdictstack exch sub", "0")
t("regeval power at x < 0", f"{RP} -1 regeval", "ERR:rangecheck")
t("regeval error keeps the dictionary stack", f"countdictstack {{ {RP} -1 regeval }} stopped pop pop pop countdictstack exch sub", "0")
t("regeval of a number", "3 4 regeval", "ERR:typecheck")

# ---------------------------------------------------------------- bignums
XB = ["1", "2", "3", "4", "5"]; YB = ["2.1", "3.9", "6.2", "7.8", "10.1"]
rb = wls([[F(1), _q(x)] for x in XB], [_q(y) for y in YB])
RB = f"{_ps(XB)} {_ps(YB)} 1 regress"
t("bignum line coef", f"{RB} /coef get bnt_list", " ".join(fdec(v, n) for v in rb["c"]))
bna("bignum line se of the slope", f"{RB} /se get 1 get", _dsqrt(rb["s2"] * rb["P"][1][1]), 18)
bna("bignum line s", f"{RB} /s get", _dsqrt(rb["s2"]), 18)
t("bignum line sse", f"{RB} /sse get bnt_str", fdec(rb["sse"], n))
bna("bignum line r2", f"{RB} /r2 get", _dec(1 - rb["sse"] / rb["sst"]), 18)
t("bignum line regeval", f"{RB} (2.5) regeval bnt_str", fdec(rb["c"][0] + rb["c"][1] * F(5, 2), n))
y0 = rb["c"][0] + rb["c"][1] * F(5, 2)
with localcontext() as c:
    c.prec = HP
    hw = D(repr(tq(0.975, 3))) * _dsqrt(rb["s2"] * (1 + quad(rb["P"], [F(1), F(5, 2)])))
    t("bignum line regpi", f"{RB} (2.5) regpi 0 get typchk", "bignumtype")
    bna("bignum line regpi upper", f"{RB} (2.5) regpi 1 get", _dec(y0) + hw, 5)
rq = wls([[F(1), _q(x), _q(x) ** 2] for x in XB], [_q(y) for y in YB])
t("bignum quadratic coef", f"{_ps(XB)} {_ps(YB)} 2 regress /coef get bnt_list", " ".join(fdec(v, n) for v in rq["c"]))
rwb = wls([[F(1), _q(x)] for x in XB], [_q(y) for y in YB], [F(1), F(2), F(3), F(2), F(1)])
t("bignum weighted coef", f"{_ps(XB)} {_ps(YB)} << /model 1 /weights [1 2 3 2 1] >> regress /coef get bnt_list",
  " ".join(fdec(v, n) for v in rwb["c"]))
t("bignum intercept coef", f"{_ps(XB)} {_ps(YB)} << /model 1 /intercept (0) >> regress /coef get 1 get bnt_str",
  fdec(sum(_q(x) * _q(y) for x, y in zip(XB, YB)) / sum(_q(x) ** 2 for x in XB), n))
t("bignum mode from the intercept", "[1 2 3] [2 4 7] << /model 1 /intercept (0) >> regress /coef get 1 get typchk", "bignumtype")
with localcontext() as c:
    c.prec = HP
    lx = [D(x).ln() for x in XB]; ly = [D(y).ln() for y in YB]
    mx = sum(lx) / 5; my = sum(ly) / 5
    bb = sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
    aa = (my - bb * mx).exp()
bna("bignum power a", f"{_ps(XB)} {_ps(YB)} /power regress /params get /a get", aa, 17)
bna("bignum power b", f"{_ps(XB)} {_ps(YB)} /power regress /params get /b get", bb, 17)

# ---------------------------------------------------------------- random numbers, Gauss-Legendre
section("Numeric.ps 1.4 random numbers, Gauss-Legendre", n)
t("rngseed repeats", "7 rngseed rnguniform 7 rngseed rnguniform eq", "true")
t("different seeds differ", "7 rngseed rnguniform 8 rngseed rnguniform ne", "true")
ra("first value after 0 rngseed", "0 rngseed rnguniform", 16807 / 2147483647, "1e-9")
t("Park-Miller check: state 1043618065 after 10000 steps", "0 rngseed 10000 { rnguniform pop } repeat n_rngs", "1043618065")
t("rnguniform in (0, 1)", "1 rngseed true 1000 { rnguniform dup 0 gt exch 1 lt and and } repeat", "true")
t("rngnormal mean near 0", "3 rngseed 0 1000 { rngnormal add } repeat 1000 div abs 0.1 lt", "true")
t("rngnormal variance near 1", "3 rngseed 0 1000 { rngnormal dup mul add } repeat 1000 div 1 sub abs 0.15 lt", "true")
t("rngseed of a real", "1.5 rngseed", "ERR:typecheck")
ra("fgauss x^3 with 2 nodes", "{ dup dup mul mul } 0 1 2 fgauss", 0.25)
ra("fgauss x^5 with 3 nodes", "{ dup dup mul dup mul mul } 0 1 3 fgauss", 1 / 6)
ra("fgauss e^x with 5 nodes", "{ 2.718281828 exch exp } 0 1 5 fgauss", _m.e - 1)
ra("fgauss sin on [0, pi], 10 nodes", "{ 57.29577951 mul sin } 0 3.14159265 10 fgauss", 2.0)
ra("fgauss 1 node is the midpoint rule", "{ dup mul } 0 2 1 fgauss", 2.0)
ra("fgauss reversed limits", "{ dup mul } 1 0 3 fgauss", -1 / 3)
bna("fgauss bignums x^5, 3 nodes", "{ dup dup mulbn dup mulbn mulbn } (0) (1) 3 fgauss", D(1) / D(6), 18)
with localcontext() as c:
    c.prec = HP
    bna("fgauss bignums e^x, 12 nodes", "{ expbn } (0) (1) 12 fgauss", D(1).exp() - 1, 18)
t("fgauss n = 0", "{ } 0 1 0 fgauss", "ERR:rangecheck")
t("fgauss n not an integer", "{ } 0 1 2.5 fgauss", "ERR:rangecheck")

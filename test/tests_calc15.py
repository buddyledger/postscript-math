# Tests of the version 1.5 additions: what pst-fit needs from regress
# (centring, custom transforms, dropping points, tval, statistics of the
# data, evaluation in the space of the fit) and setbnx. Run by
# make_tests.py in its namespace, after tests_calc.py (whose helpers wls,
# tq, quad, _q and _ps it uses).
import math as _m

section("Numeric.ps 1.5 regression for pst-fit", n)

# ---------------------------------------------------------------- centring: pst-fit's precision test
XP = list(range(293, 303))
YP = ["1.3", "3.1", "7.2", "12.5", "20.1", "28.4", "40.2", "51.0", "65.3", "79.6"]
LP = f"{_ps(XP)} [{' '.join(YP)}]"
for d in (2, 4):
    rp_ = wls([[F(x) ** j for j in range(d + 1)] for x in XP], [_q(y) for y in YP])
    RPd = f"{LP} {d} regress"
    ra(f"far from 0, degree {d}: r2", f"{RPd} /r2 get", float(1 - rp_["sse"] / rp_["sst"]))
    ra(f"far from 0, degree {d}: s", f"{RPd} /s get", float(rp_["s2"]) ** 0.5, "1e-4")
    for x in (293, 297.5, 302):
        yx = float(sum(c * F(x) ** j for j, c in enumerate(rp_["c"])))
        ra(f"far from 0, degree {d}: regeval at {x}", f"{RPd} {x} regeval", yx, "2e-3")
    b0 = [F(297.5) ** j for j in range(d + 1)]
    y0 = float(sum(c * b for c, b in zip(rp_["c"], b0)))
    w0 = tq(0.975, 10 - d - 1) * float(rp_["s2"]) ** 0.5 * float(quad(rp_["P"], b0)) ** 0.5
    ra(f"far from 0, degree {d}: regci at 297.5, low", f"{RPd} 297.5 regci 0 get", y0 - w0, "2e-3")
    ra(f"far from 0, degree {d}: regpi at 297.5, high", f"{RPd} 297.5 regpi 1 get",
       y0 + tq(0.975, 10 - d - 1) * float(rp_["s2"]) ** 0.5 * float(1 + quad(rp_["P"], b0)) ** 0.5, "2e-3")
    ra(f"far from 0, degree {d}: stdresid 1", f"{RPd} /stdresid get 0 get",
       float(rp_["res"][0]) / (float(rp_["s2"]) ** 0.5 * float(1 - rp_["h"][0]) ** 0.5), "1e-3")
rp2 = wls([[F(x) ** j for j in range(3)] for x in XP], [_q(y) for y in YP])
ra("far from 0, degree 2: c0 to 6 digits", f"{LP} 2 regress /coef get 0 get", float(rp2["c"][0]), "0.1")
ra("far from 0, degree 2: c2", f"{LP} 2 regress /coef get 2 get", float(rp2["c"][2]), "1e-4")
bna("far from 0, degree 2 with bignums: c0", f"{LP} << /model 2 /bignum true >> regress /coef get 0 get",
    _dec(rp2["c"][0]), 15)
bna("far from 0, degree 2 with bignums: c1", f"{LP} << /model 2 /bignum true >> regress /coef get 1 get",
    _dec(rp2["c"][1]), 15)
XGF = [998, 999, 1000, 1001, 1002]
YGF = [round(4 * _m.exp(-(x - 1000) ** 2 / 2) + 1, 4) for x in XGF]
RGF = f"{_ps(XGF)} {_ps(YGF)} << /model /gauss /yoffset 1 >> regress /params get"
ra("gauss far from 0: mu", f"{RGF} /mu get", 1000.0, "1e-3")
ra("gauss far from 0: sigma", f"{RGF} /sigma get", 1.0, "1e-3")
ra("gauss far from 0: A", f"{RGF} /A get", 4.0, "1e-3")

# ---------------------------------------------------------------- statistics of the data
XS = [1, 2, 3, 4, 5, 6]; YS = ["2.1", "3.9", "6.2", "7.8", "10.1", "12.2"]
LS = f"{_ps(XS)} [{' '.join(YS)}]"
xq = [F(x) for x in XS]; yq = [_q(y) for y in YS]
xb = sum(xq) / 6; yb = sum(yq) / 6
ra("xbar", f"{LS} linreg /xbar get", float(xb))
ra("ybar", f"{LS} linreg /ybar get", float(yb))
ra("sxx", f"{LS} linreg /sxx get", float(sum((x - xb) ** 2 for x in xq)))
ra("syy", f"{LS} linreg /syy get", float(sum((y - yb) ** 2 for y in yq)), "1e-4")
ra("sxy", f"{LS} linreg /sxy get", float(sum((x - xb) * (y - yb) for x, y in zip(xq, yq))), "1e-4")
ra("weighted xbar", f"{LS} << /model 1 /weights [1 1 1 1 1 5] >> regress /xbar get", (15 + 30) / 10)
ra("xbar of /power is the mean of ln x", f"{LS} /power regress /xbar get", sum(_m.log(x) for x in XS) / 6)
t("dropped 0", f"{LS} linreg /dropped get", "0")
la("xused", f"{LS} linreg /xused get", [1, 2, 3, 4, 5, 6])

# ---------------------------------------------------------------- dropping points
XD = [0, 1, 2, 3, 4, -1]; YD = [5, 2.1, 8.3, 17.9, 33.0, 4]
RD = f"{_ps(XD)} {_ps(YD)} << /model /power /drop true >> regress"
rd = wls([[F(1), F(_m.log(x))] for x in XD if x > 0], [F(_m.log(y)) for x, y in zip(XD, YD) if x > 0])
t("drop: dropped", f"{RD} /dropped get", "2")
la("drop: xused", f"{RD} /xused get", [1, 2, 3, 4])
la("drop: yused", f"{RD} /yused get", [2.1, 8.3, 17.9, 33.0])
la("drop: coef of the rest", f"{RD} /coef get", [float(v) for v in rd["c"]])
t("drop: n", f"{RD} /n get", "4")
t("drop: fitted has n values", f"{RD} /fitted get length", "4")
t("drop: a failing xtrans", "[0 1 2 3] [1 2 3 4] << /model 1 /xtrans { ln } /drop true >> regress /dropped get", "1")
t("drop: all points", "[0 -1] [1 2] << /model /ln /drop true >> regress", "ERR:rangecheck")
t("without drop: rangecheck", f"{_ps(XD)} {_ps(YD)} /power regress", "ERR:rangecheck")
t("drop does not excuse a weight 0", "[1 2 3] [1 2 4] << /model 1 /drop true /weights [1 0 1] >> regress", "ERR:rangecheck")

# ---------------------------------------------------------------- custom transforms
XC = [1, 4, 9, 16, 25]; YC = [3.1, 4.9, 7.2, 8.8, 11.1]
rc = wls([[F(1), F(_m.sqrt(x))] for x in XC], [F(y) for y in YC])
RC = f"{_ps(XC)} {_ps(YC)} << /model 1 /xtrans {{ sqrt }} >> regress"
la("xtrans sqrt: coef", f"{RC} /coef get", [float(v) for v in rc["c"]])
ra("xtrans sqrt: regeval at 36", f"{RC} 36 regeval", float(rc["c"][0] + 6 * rc["c"][1]), "1e-4")
RE1 = f"{_ps(XT)} {_ps(YEX)} << /model 1 /ytrans {{ ln }} /yback {{ 2.718281828 exch exp }} >> regress"
ra("ytrans ln, yback exp = /exp: regeval at 2.5", f"{RE1} 2.5 regeval",
   _m.exp(float(re_["c"][0]) + 2.5 * float(re_["c"][1])), "1e-3")
la("ytrans ln, yback exp = /exp: coef", f"{RE1} /coef get", [float(v) for v in re_["c"]])
t("ytrans ln: regpi transformed back is positive", f"{RE1} 2.5 regpi 0 get 0 gt", "true")
t("xtrans with a transform model", "[1 2 3] [1 2 3] << /model /power /xtrans { } >> regress", "ERR:rangecheck")
t("xtrans with a basis", "[1 2 3] [1 2 3] << /model { 1 array astore } /xtrans { } >> regress", "ERR:rangecheck")
t("ytrans without yback", "[1 2 3] [1 2 3] << /model 1 /ytrans { } >> regress", "ERR:rangecheck")
t("yback without ytrans", "[1 2 3] [1 2 3] << /model 1 /yback { } >> regress", "ERR:rangecheck")
t("xtrans not a procedure", "[1 2 3] [1 2 3] << /model 1 /xtrans 5 >> regress", "ERR:typecheck")
t("drop not a boolean", "[1 2 3] [1 2 4] << /model 1 /drop 1 >> regress", "ERR:typecheck")

# ---------------------------------------------------------------- t value
t("tval given", "[1 2 3 4 5] [2 4 5 4 6] << /model 1 /tval 3 >> regress /tval get", "3")
rt = wls([[F(1), F(x)] for x in range(1, 6)], [F(y) for y in (2, 4, 5, 4, 6)])
b0 = [F(1), F(3)]; w0 = 3 * float(rt["s2"]) ** 0.5 * float(quad(rt["P"], b0)) ** 0.5
la("tval given: regci", "[1 2 3 4 5] [2 4 5 4 6] << /model 1 /tval 3 >> regress 3 regci",
   [float(sum(c * b for c, b in zip(rt["c"], b0))) - w0, float(sum(c * b for c, b in zip(rt["c"], b0))) + w0])
bna("bignum mode: t value from reals", "[1 2 3 4] [3 5 7 10] << /model 1 /bignum true >> regress /tval get",
    D(str(round(tq(0.975, 2), 5))), 5)
t("bignum mode: tval is a bignum", "[1 2 3 4] [3 5 7 10] << /model 1 /bignum true >> regress /tval get typchk", "bignumtype")
t("bignum forced: coef are bignums", "[1 2 3 4] [3 5 7 10] << /model 1 /bignum true >> regress /coef get 1 get typchk", "bignumtype")

# ---------------------------------------------------------------- the space of the fit
RT = f"{_ps(XT)} {_ps(YPW)} /power regress"
ra("regevalt: c0 + c1 X", f"{RT} 0.6931472 regevalt", float(rp["c"][0]) + 0.6931472 * float(rp["c"][1]))
b0 = [F(1), F(0.6931472)]; yl = float(sum(c * b for c, b in zip(rp["c"], b0)))
w0 = tq(0.975, 4) * float(rp["s2"]) ** 0.5 * float(quad(rp["P"], b0)) ** 0.5
la("regcit: not transformed back", f"{RT} 0.6931472 regcit", [yl - w0, yl + w0])
w1 = tq(0.975, 4) * float(rp["s2"]) ** 0.5 * float(1 + quad(rp["P"], b0)) ** 0.5
la("regpit", f"{RT} 0.6931472 regpit", [yl - w1, yl + w1])
t("regevalt takes X <= 0", f"{RT} -1 regevalt type", "realtype")
t("regevalt leaves out yoffset",
  f"{_ps(XT)} {_ps(YKO)} << /model /power /yoffset 5 >> regress dup 0 regevalt exch /coef get 0 get sub abs 1e-5 lt", "true")

# ---------------------------------------------------------------- setbnx and /exact
n = 30
section("setbnx", n)
t("setbnx 0.1", "0.1 setbnx bncvs", "+1.00000001490116119384765625000e-1")
t("setbnx -2.5", "-2.5 setbnx bncvs", "-2.50000000000000000000000000000e0")
t("setbnx 1e-30", "1e-30 setbnx bncvs", "+1.00000000317107685097105134714e-30")
t("setbnx 0.0", "0.0 setbnx bncvs", "+0.00000000000000000000000000000e0")
t("setbnx of an integer", "7 setbnx bncvs", "+7.00000000000000000000000000000e0")
t("setbnx of a string", "(0.1) setbnx bncvs", "+1.00000000000000000000000000000e-1")
t("/exact: data with all their binary digits",
  "[1 2] [0.1 0.2] << /model 1 /bignum true /exact true /intercept 0 >> regress /coef get 1 get bncvs",
  "+1.00000001490116119384765625000e-1")
t("without /exact: the 6 digits of cvs",
  "[1 2] [0.1 0.2] << /model 1 /bignum true /intercept 0 >> regress /coef get 1 get bncvs",
  "+1.00000000000000000000000000000e-1")
n = 20

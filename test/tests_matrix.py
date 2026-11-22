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

# Tests of the matrix procedures of version 1.4 (mkron, mdiag, mpow, mchol,
# mqr, msvd, msingular, mpinv, mnull, meigsymv, meigvec, mexp). Run by
# make_tests.py in its namespace.

# PostScript helpers: the largest |difference| of two matrices, the largest
# |element|, and the residual of eigenpairs, all as bignums (elements of
# either kind are read with setbn)
out(r"""
/tm_mdiff { 4 dict begin mtorows /tm_b exch def mtorows /tm_a exch def
	0 setbn 0 1 tm_a length 1 sub { /tm_i exch def 0 1 tm_a 0 get length 1 sub { /tm_j exch def
		tm_a tm_i get tm_j get setbn tm_b tm_i get tm_j get setbn subbn absbn
		2 copy gtbn { pop }{ exch pop } ifelse } for } for end } def
/tm_mmax { 0 setbn exch { { setbn absbn 2 copy gtbn { pop }{ exch pop } ifelse } forall } forall } def
/tm_le { setbn lebn } def   % bn (tol) -> bool
/tm_eigres { % A [[z v] ...] -> largest |(A v - z v)_i| and ||v| - 1| over all pairs
	8 dict begin /tm_P exch def mtorows /tm_A exch def
	0 setbn tm_P { aload pop /tm_v exch def aload pop setbn /tm_zi exch def setbn /tm_zr exch def
		0 setbn tm_v { aload pop setbn dup mulbn exch setbn dup mulbn addbn addbn } forall
		sqrtbn 1 setbn subbn absbn 2 copy gtbn { pop }{ exch pop } ifelse
		0 1 tm_A length 1 sub { /tm_i exch def
			0 setbn 0 setbn
			0 1 tm_v length 1 sub { /tm_j exch def
				tm_A tm_i get tm_j get setbn /tm_a exch def
				tm_v tm_j get aload pop setbn tm_a mulbn 3 -1 roll addbn
				3 1 roll setbn tm_a mulbn addbn exch
			} for
			tm_v tm_i get aload pop setbn /tm_wi exch def setbn /tm_wr exch def
			tm_zr tm_wi mulbn tm_zi tm_wr mulbn addbn subbn absbn exch
			tm_zr tm_wr mulbn tm_zi tm_wi mulbn subbn subbn absbn
			addbn 2 copy gtbn { pop }{ exch pop } ifelse
		} for
	} forall
	end } def
""")

def ffl(rows): return [float(x) for r in rows for x in r]
def fmatmul(a, b): return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def ftr(a): return [list(r) for r in zip(*a)]
def finv(a):  # exact inverse with Fractions (Gauss-Jordan)
    k = len(a); w = [[F(x) for x in r] + [F(int(i == j)) for j in range(k)] for i, r in enumerate(a)]
    for c in range(k):
        p = next(r for r in range(c, k) if w[r][c] != 0); w[c], w[p] = w[p], w[c]
        pv = w[c][c]; w[c] = [x / pv for x in w[c]]
        for r in range(k):
            if r != c and w[r][c] != 0:
                f = w[r][c]; w[r] = [x - f * y for x, y in zip(w[r], w[c])]
    return [r[k:] for r in w]

TOL = "1e-26"   # for invariants at 30 digits

# ---------------------------------------------------------------- reals
section("Matrix.ps 1.4: Kronecker product, diagonal, powers", 30)
KA = [[1, 2], [3, 4]]; KB = [[0, 1], [1, 0]]
kron = [[KA[i // 2][j // 2] * KB[i % 2][j % 2] for j in range(4)] for i in range(4)]
t("mkron 2x2 (x) 2x2", f"{mlit(KA)} mfromrows {mlit(KB)} mfromrows mkron bnt_mstr", "; ".join(" ".join(map(str, r)) for r in kron))
t("mkron 1x2 (x) 2x1", "[[1 2]] mfromrows [[3][4]] mfromrows mkron bnt_mstr", "3 6; 4 8")
t("mkron decimals", "[[(0.5)]] mfromrows [[2 (0.1)]] mfromrows mkron bnt_mstr", f"{fmt(1, 30)} {fmt('0.05', 30)}")
t("mdiag list", "[1 2 3] mdiag bnt_mstr", "1 0 0; 0 2 0; 0 0 3")
t("mdiag of a matrix", "[[1 2 3][4 5 6]] mfromrows mdiag bnt_list", "1 5")
t("mdiag of bignums", "[(1.5) (2)] mdiag mdiag bnt_list", "1.5 2")
t("mdiag of a non-array", "5 mdiag", "ERR:typecheck")
t("mdiag of []", "[] mdiag", "ERR:rangecheck")
P3 = fmatmul(fmatmul(KA, KA), KA)
t("mpow 3", f"{mlit(KA)} mfromrows 3 mpow bnt_mstr", "; ".join(" ".join(map(str, r)) for r in P3))
t("mpow 0 is the identity", f"{mlit(KA)} mfromrows 0 mpow bnt_mstr", "1 0; 0 1")
t("mpow 1", f"{mlit(KA)} mfromrows 1 mpow bnt_mstr", "1 2; 3 4")
F10 = [[1, 1], [1, 0]]
fib = [[1, 0], [0, 1]]
for _ in range(30): fib = fmatmul(fib, F10)
t("mpow 30 of the Fibonacci matrix", f"{mlit(F10)} mfromrows 30 mpow bnt_mstr", "; ".join(" ".join(map(str, r)) for r in fib))
inv2 = finv(KA); inv2sq = fmatmul(inv2, inv2)
ma("mpow -2, reals", f"{mlit(KA)} mfromrows -2 mpow", inv2sq)
t("mpow -2, bignums", f"{bnl([['1', 2], [3, 4]])} -2 mpow bnt_mstr", mbn(inv2sq, 30))
t("mpow of a singular matrix to -1", "[[1 2][2 4]] mfromrows -1 mpow", "ERR:undefinedresult")
t("mpow with a real exponent", f"{mlit(KA)} mfromrows 1.5 mpow", "ERR:typecheck")
t("mpow of a non-square matrix", "[[1 2 3][4 5 6]] mfromrows 2 mpow", "ERR:rangecheck")

section("Matrix.ps 1.4: Cholesky and QR", 30)
C2 = [[4, 2], [2, 3]]
ma("mchol 2x2", f"{mlit(C2)} mfromrows mchol", [[2, 0], [1, 2 ** 0.5]])
C3 = [[25, 15, -5], [15, 18, 0], [-5, 0, 11]]
t("mchol 3x3 with an integer factor", f"{mlit(C3)} mfromrows mchol bnt_mstr", "5.0 0 0; 3.0 3.0 0; -1.0 1.0 3.0")
with localcontext() as c:
    c.prec = HP
    r2 = D(2).sqrt()
bna("mchol bignums: l22 = sqrt 2", f"{bnl([['4', 2], [2, 3]])} mchol 2 2 mget", r2, 28)
SPD = [["2.5", 1, "0.5"], [1, 3, "-0.25"], ["0.5", "-0.25", 4]]
t("mchol bignums: L L^T = A", f"{bnl(SPD)} dup mchol dup mtranspose mmul tm_mdiff ({TOL}) tm_le", "true")
t("mchol of an indefinite matrix", "[[1 2][2 1]] mfromrows mchol", "ERR:rangecheck")
t("mchol of a non-symmetric matrix", "[[2 1][0 2]] mfromrows mchol", "ERR:rangecheck")
t("mchol of a non-square matrix", "[[1 2 3][4 5 6]] mfromrows mchol", "ERR:rangecheck")

QA = [[1, 2], [3, 4], [5, 6]]
def fqr(a):  # classical Gram-Schmidt in floats, for the reference
    cols = ftr(a); qs = []; R = [[0.0] * len(cols) for _ in cols]
    for j, v in enumerate(cols):
        v = [float(x) for x in v]
        for i, q in enumerate(qs):
            R[i][j] = sum(x * y for x, y in zip(q, v)); v = [x - R[i][j] * y for x, y in zip(v, q)]
        R[j][j] = sum(x * x for x in v) ** 0.5; qs.append([x / R[j][j] for x in v])
    return ftr(qs), R
Qr, Rr = fqr(QA)
ma("mqr 3x2: Q", f"{mlit(QA)} mfromrows mqr pop", Qr)
ma("mqr 3x2: R", f"{mlit(QA)} mfromrows mqr exch pop", Rr)
ma("mqr reals: Q R = A", f"{mlit(QA)} mfromrows mqr mmul", QA)
ma("mqr square: Q^T Q = I", "[[2 -1 0][-1 2 -1][0 -1 2]] mfromrows mqr pop dup mtranspose exch mmul", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
QB = [["0.1", "0.2", "0.3"], ["1.5", "-2", "0.25"], ["3", "1", "-1"], ["0.5", "0.5", "7"]]
t("mqr bignums: Q R = A", f"{bnl(QB)} dup mqr mmul tm_mdiff ({TOL}) tm_le", "true")
t("mqr bignums: Q^T Q = I", f"{bnl(QB)} mqr pop dup mtranspose exch mmul 3 midentity tm_mdiff ({TOL}) tm_le", "true")
t("mqr bignums: R upper triangular, positive diagonal",
  f"{bnl(QB)} mqr exch pop dup 2 1 mget bniszero 1 index 3 1 mget bniszero and 1 index 3 2 mget bniszero and"
  " exch mdiag { bn_isneg not and } forall", "true")
t("mqr of a wide matrix", "[[1 2 3][4 5 6]] mfromrows mqr", "ERR:rangecheck")
t("mqr of dependent columns", "[[1 2][2 4][3 6]] mfromrows mqr", "ERR:undefinedresult")

section("Matrix.ps 1.4: singular values, pseudo-inverse, null space", 30)
SA = [[3, 0], [4, 5]]
la("msingular 2x2", f"{mlit(SA)} mfromrows msingular", [45 ** 0.5, 5 ** 0.5])
with localcontext() as c:
    c.prec = HP
    s1, s2 = D(45).sqrt(), D(5).sqrt()
bna("msingular bignums: 3 sqrt 5", f"{bnl([['3', 0], [4, 5]])} msingular 0 get", s1, 28)
bna("msingular bignums: sqrt 5", f"{bnl([['3', 0], [4, 5]])} msingular 1 get", s2, 28)
S34 = [[1, 2, 3, 4], [2, 0, 1, -1], [0, 1, 1, 2]]
AtA = fmatmul(S34, ftr(S34))   # 3x3: the singular values are the roots of its eigenvalues
sv = [e.sqrt() for e in reversed(sym_eigs(AtA))]
la("msingular 3x4 (wide)", f"{mlit(S34)} mfromrows msingular", [float(x) for x in sv])
bna("msingular 4x3 bignums, largest", f"{bnl(ftr(S34))} 1 setbn mscale msingular 0 get", sv[0], 26)
bna("msingular 4x3 bignums, smallest", f"{bnl(ftr(S34))} 1 setbn mscale msingular 2 get", sv[2], 26)
ma("msvd reals: U diag(S) V^T = A", f"{mlit(S34)} mfromrows msvd mtranspose exch mdiag exch mmul mmul", S34)
ma("msvd reals: U^T U = I (wide)", f"{mlit(S34)} mfromrows msvd pop pop dup mtranspose exch mmul", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
ma("msvd reals: V^T V = I (wide)", f"{mlit(S34)} mfromrows msvd exch pop exch pop dup mtranspose exch mmul", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
SB = [["0.5", "1", "-2"], ["3", "0.25", "1"], ["1", "1", "1"], ["2", "-1", "0.5"]]
t("msvd bignums: U diag(S) V^T = A", f"{bnl(SB)} dup msvd mtranspose exch mdiag exch mmul mmul tm_mdiff ({TOL}) tm_le", "true")
t("msvd bignums: V^T V = I", f"{bnl(SB)} msvd exch pop exch pop dup mtranspose exch mmul 3 midentity tm_mdiff ({TOL}) tm_le", "true")
t("msvd rank 1: second singular value 0", "[[1 2][2 4]] mfromrows msingular 1 get", "0")
t("msvd rank 1, bignums: U still orthonormal",
  f"{bnl([['1', 2], [2, 4]])} msvd pop pop dup mtranspose exch mmul 2 midentity tm_mdiff ({TOL}) tm_le", "true")
t("msvd of the zero matrix", "[[0 0][0 0]] mfromrows msingular bnt_list", "0 0")
PA = [[1, 2], [3, 4], [5, 7]]
pinv = fmatmul(finv(fmatmul(ftr(PA), PA)), ftr(PA))
ma("mpinv full column rank = (A^T A)^-1 A^T", f"{mlit(PA)} mfromrows mpinv", pinv)
t("mpinv bignums, full column rank", f"{bnl([['1', 2], [3, 4], [5, 7]])} mpinv {bnl([[str(Context(prec=40).divide(D(x.numerator), D(x.denominator))) for x in r] for r in pinv])} tm_mdiff ({TOL}) tm_le", "true")
ma("mpinv rank 1: A / 25", "[[1 2][2 4]] mfromrows mpinv", [[0.04, 0.08], [0.08, 0.16]])
t("mpinv bignums rank 1: A A+ A = A", f"{bnl([['1', 2], [2, 4], [3, 6]])} dup dup mpinv mmul 1 index mmul tm_mdiff ({TOL}) tm_le", "true")
ma("mpinv of a square invertible matrix is the inverse", f"{mlit(KA)} mfromrows mpinv", finv(KA))
ma("mpinv wide", "[[1 0 1][0 1 1]] mfromrows mpinv", fmatmul(ftr([[1, 0, 1], [0, 1, 1]]), finv(fmatmul([[1, 0, 1], [0, 1, 1]], ftr([[1, 0, 1], [0, 1, 1]])))))
ma("mpinv of the zero matrix", "[[0 0 0][0 0 0]] mfromrows mpinv", [[0, 0], [0, 0], [0, 0]])
NA = [[1, 2, 3], [4, 5, 6]]
nv = [1, -2, 1]; nn6 = 6 ** 0.5
la("mnull 2x3: +-(1, -2, 1)/sqrt 6, squared", f"{mlit(NA)} mfromrows mnull mtorows {{ 0 get dup mul }} forall 3 array astore", [x * x / 6 for x in nv])
ma("mnull 2x3: A N = 0", f"{mlit(NA)} mfromrows dup mnull mmul", [[0], [0]])
t("mnull of an invertible matrix is []", f"{mlit(KA)} mfromrows mnull length", "0")
t("mnull of rank 1 3x3 has 2 columns", "[[1 2 3][2 4 6][3 6 9]] mfromrows mnull msize exch pop", "2")
t("mnull bignums: A N = 0", f"{bnl([['1', 2, 3], [2, 4, 6], [1, 1, 1]])} dup mnull mmul tm_mmax ({TOL}) tm_le", "true")
t("mnull bignums: N^T N = I", f"{bnl([['1', 2, 3, 4], [2, 4, 6, 8]])} mnull dup mtranspose exch mmul 3 midentity tm_mdiff ({TOL}) tm_le", "true")
t("mnull of the zero matrix is everything", "[[0 0][0 0]] mfromrows mnull bnt_mstr", "1 0; 0 1")

section("Matrix.ps 1.4: eigenvectors", 30)
t("meigsymv is meigsym", "[[2 1][1 2]] mfromrows meigsymv pop bnt_list", "1.0 3.0")
la("meigvec 2x2 values and vectors", "[[2 1][1 2]] mfromrows meigvec",
   [1, 0, 2 ** -0.5, 0, -(2 ** -0.5), 0, 3, 0, 2 ** -0.5, 0, 2 ** -0.5, 0])
la("meigvec rotation: complex vectors", "[[0 -1][1 0]] mfromrows meigvec",
   [0, -1, 2 ** -0.5, 0, 0, 2 ** -0.5, 0, 1, 2 ** -0.5, 0, 0, -(2 ** -0.5)])
t("meigvec non-symmetric 3x3, reals: residual", "[[1 1 0][0 1 1][1 0 1]] mfromrows dup meigvec tm_eigres (1e-4) tm_le", "true")
t("meigvec 4x4 reals: residual", "[[4 1 0 2][1 3 1 0][0 2 5 1][1 0 1 2]] mfromrows dup meigvec tm_eigres (1e-4) tm_le", "true")
t("meigvec bignums, 3x3 complex pair: residual", f"{bnl([['1', 1, 0], [0, 1, 1], [1, 0, 1]])} dup meigvec tm_eigres (1e-24) tm_le", "true")
t("meigvec bignums, symmetric 3x3: residual", f"{bnl(E3)} 1 setbn mscale dup meigvec tm_eigres (1e-24) tm_le", "true")
t("meigvec repeated eigenvalue: orthogonal vectors",
  "[[2 0][0 2]] mfromrows meigvec dup 0 get 1 get exch 1 get 1 get /tm_v2 exch def /tm_v1 exch def 0 0 1 1 { dup tm_v1 exch get 0 get exch tm_v2 exch get 0 get mul add } for abs 1e-5 lt", "true")
la("meigvec defective matrix: (1, 0) twice", "[[1 1][0 1]] mfromrows meigvec", [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0])
with localcontext() as c:
    c.prec = HP
    h2 = 1 / D(2).sqrt()
bna("meigvec bignums: largest component real and positive", f"{bnl([['0', -1], [1, 0]])} meigvec 0 get 1 get 0 get 0 get", h2, 28)
t("meigvec bignums: ... with imaginary part exactly 0", f"{bnl([['0', -1], [1, 0]])} meigvec 0 get 1 get 0 get 1 get bniszero", "true")
t("meigvec of a non-square matrix", "[[1 2 3][4 5 6]] mfromrows meigvec", "ERR:rangecheck")

section("Matrix.ps 1.4: matrix exponential", 30)
import math as _m
ma("mexp rotation", "[[0 -1][1 0]] mfromrows mexp", [[_m.cos(1), -_m.sin(1)], [_m.sin(1), _m.cos(1)]])
ma("mexp nilpotent", "[[0 1][0 0]] mfromrows mexp", [[1, 1], [0, 1]])
ra("mexp diagonal, large norm: e^5 relative", f"[[5 0][0 -3]] mfromrows mexp 1 1 mget {_m.exp(5):.10g} div", 1)
ra("mexp diagonal, large norm: e^-3", "[[5 0][0 -3]] mfromrows mexp 2 2 mget", _m.exp(-3))
ma("mexp of 0 is I", "[[0 0][0 0]] mfromrows mexp", [[1, 0], [0, 1]])
bna("mexp bignums: rotation cos 1", f"{bnl([['0', -1], [1, 0]])} mexp 1 1 mget", d_cos(1), 28)
bna("mexp bignums: rotation sin 1", f"{bnl([['0', -1], [1, 0]])} mexp 2 1 mget", d_sin(1), 28)
bna("mexp bignums: e^10", f"{bnl([['10', 0], [0, 1]])} mexp 1 1 mget", d_exp(10), 27)
with localcontext() as c:
    c.prec = HP + 20
    # e^[[a b][0 a]] = e^a [[1 b][0 1]]
    ref = d_exp(D("0.5")) * D("2.5")
bna("mexp bignums: Jordan block, off-diagonal", f"{bnl([['0.5', '2.5'], [0, '0.5']])} mexp 1 2 mget", ref, 28)
t("mexp(A) mexp(-A) = I, bignums",
  f"{bnl([['0.3', 1, '-0.2'], ['0.1', '-0.4', 2], [1, '0.5', '0.25']])} dup mexp exch -1 mscale mexp mmul 3 midentity tm_mdiff ({TOL}) tm_le", "true")
t("mexp of a non-square matrix", "[[1 2 3][4 5 6]] mfromrows mexp", "ERR:rangecheck")

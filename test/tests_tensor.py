# Tests of Tensor.ps, run by make_tests.py in its namespace (t, ra, la,
# section, fmt, F, D, ... come from there). References are computed here by
# brute force on flat Python lists.
import itertools as _it
import random as _random
from fractions import Fraction as _F

_rng = _random.Random(1414)


def _prod(xs):
    p = 1
    for x in xs:
        p *= x
    return p


def _strides(shape):
    st, acc = [0] * len(shape), 1
    for i in range(len(shape) - 1, -1, -1):
        st[i] = acc
        acc *= shape[i]
    return st


def _nested(shape, flat):
    if len(shape) == 1:
        return list(flat)
    step = _prod(shape[1:])
    return [_nested(shape[1:], flat[i * step:(i + 1) * step]) for i in range(shape[0])]


def _lit(x):  # Python value -> PostScript literal
    if isinstance(x, list):
        return "[" + " ".join(_lit(e) for e in x) + "]"
    if isinstance(x, str):
        return f"({x})"
    return str(x)


def _T(shape, flat):  # PostScript expression building the tensor
    return _lit(_nested(shape, flat)) + " tensor"


def _cvs(shape, flat, f=str):  # what tcvs prints
    if len(shape) == 1:
        return "[" + ", ".join(f(x) for x in flat) + "]"
    if len(shape) == 2:
        n = shape[1]
        return "[" + "; ".join(" ".join(f(x) for x in flat[i * n:(i + 1) * n]) for i in range(shape[0])) + "]"
    step = _prod(shape[1:])
    return "[" + ", ".join(_cvs(shape[1:], flat[i * step:(i + 1) * step], f) for i in range(shape[0])) + "]"


def _rand(shape, lo=-5, hi=9):
    return [_rng.randint(lo, hi) for _ in range(_prod(shape))]


def _get(shape, flat, idx):
    return flat[sum(i * s for i, s in zip(idx, _strides(shape)))]


def _einsum(ins, outs, ops):  # ops: list of (shape, flat); returns (shape, flat) or a scalar
    dims = {}
    for letters, (shape, _) in zip(ins, ops):
        for c, d in zip(letters, shape):
            dims[c] = d
    summed = sorted(set("".join(ins)) - set(outs))
    oshape = [dims[c] for c in outs]
    res = []
    for oi in _it.product(*[range(dims[c]) for c in outs]):
        acc = 0
        for si in _it.product(*[range(dims[c]) for c in summed]):
            val = dict(zip(outs, oi))
            val.update(zip(summed, si))
            p = 1
            for letters, (shape, flat) in zip(ins, ops):
                p *= _get(shape, flat, [val[c] for c in letters])
            acc += p
        res.append(acc)
    return res[0] if not outs else (oshape, res)


def _permute(shape, flat, p):  # result axis k is input axis p[k] (1-based)
    nshape = [shape[q - 1] for q in p]
    res = []
    for idx in _it.product(*[range(d) for d in nshape]):
        src = [0] * len(shape)
        for k, q in enumerate(p):
            src[q - 1] = idx[k]
        res.append(_get(shape, flat, src))
    return nshape, res


def _sign(p):
    if len(set(p)) < len(p):
        return 0
    s = 1
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                s = -s
    return s


def _flat(x):
    return [y for e in x for y in _flat(e)] if isinstance(x, list) else [x]


n = 20
TN = 0  # count of tensor tests, for the summary line


def tt(label, proc, expected):
    global TN
    TN += 1
    t(label, proc, expected)


def tla(label, proc, vals):
    global TN
    TN += 1
    la(label, proc, vals)


def tra(label, proc, val):
    global TN
    TN += 1
    ra(label, proc, val)


# ---------------------------------------------------------------- building
section("tensor: building", n)
tt("tensor rank 1", "[1 2 3] tensor tcvs", "[1, 2, 3]")
tt("tensor rank 2", "[[1 2 3] [4 5 6]] tensor tcvs", "[1 2 3; 4 5 6]")
S3 = [2, 3, 2]; D3 = _rand(S3)
tt("tensor rank 3", f"{_T(S3, D3)} tcvs", _cvs(S3, D3))
S4 = [2, 2, 2, 2]; D4 = list(range(16))
tt("tensor rank 4", f"{_T(S4, D4)} tcvs", _cvs(S4, D4))
tt("tshape", f"{_T(S3, D3)} tshape length", "3")
tt("tshape values", f"{_T(S3, D3)} tshape aload pop add add", "7")
tt("trank", f"{_T(S4, D4)} trank", "4")
tt("tsize", f"{_T(S3, D3)} tsize", "12")
tt("tolist round trip", f"{_T(S3, D3)} tolist tensor tcvs", _cvs(S3, D3))
tla("tolist values", f"{_T(S3, D3)} tolist", D3)
tt("tzeros", "[2 3] tzeros tcvs", "[0 0 0; 0 0 0]")
tt("tfill", "[3] 7 tfill tcvs", "[7, 7, 7]")
tt("tdelta", "3 tdelta tcvs", "[1 0 0; 0 1 0; 0 0 1]")
lev3 = [_sign(p) for p in _it.product(range(3), repeat=3)]
tt("tlevi 3", "3 tlevi tcvs", _cvs([3, 3, 3], lev3))
tt("tlevi 4 [2 1 3 4]", "4 tlevi [2 1 3 4] tget", "-1")
tt("tlevi 4 contracted with itself is 4!", "4 tlevi dup tinner", "24")
tt("tlevi 1", "1 tlevi tcvs", "[1]")
tt("tfrommatrix", "[[1 2] [3 4]] mfromrows tfrommatrix tcvs", "[1 2; 3 4]")
tt("ttomatrix", "[[1 2] [3 4]] tensor ttomatrix 1 2 mget", "2")
tt("ragged list", "[[1 2] [3]] tensor", "ERR:rangecheck")
tt("ragged deeper", "[[[1 2] [3 4]] [[5 6] [7]]] tensor", "ERR:rangecheck")
tt("empty list", "[] tensor", "ERR:rangecheck")
tt("not a list", "5 tensor", "ERR:typecheck")
tt("element of a wrong type", "[1 /a] tensor", "ERR:rangecheck")
tt("tzeros bad shape", "[2 0] tzeros", "ERR:rangecheck")
tt("tlevi 7", "7 tlevi", "ERR:rangecheck")
tt("ttomatrix of rank 3", f"{_T(S3, D3)} ttomatrix", "ERR:rangecheck")
tt("tolist of a list", "[1 2] tolist", "ERR:typecheck")

# ---------------------------------------------------------------- access
section("tensor: access", n)
for idx in ([1, 1, 1], [2, 3, 1], [1, 2, 2]):
    tt(f"tget {idx}", f"{_T(S3, D3)} {_lit(idx)} tget", str(_get(S3, D3, [i - 1 for i in idx])))
tt("tget out of range", f"{_T(S3, D3)} [3 1 1] tget", "ERR:rangecheck")
tt("tget wrong number of indices", f"{_T(S3, D3)} [1 1] tget", "ERR:rangecheck")
tt("tget of a list", "[1 2] [1] tget", "ERR:typecheck")
D3p = list(D3); D3p[_strides(S3)[0] * 1 + _strides(S3)[1] * 2 + 1] = 99
tt("tput", f"{_T(S3, D3)} [2 3 2] 99 tput tcvs", _cvs(S3, D3p))
tt("tput leaves the original", f"{_T(S3, D3)} dup [2 3 2] 99 tput pop tcvs", _cvs(S3, D3))
for ax in (1, 2, 3):
    k = 2
    shape2 = [d for i, d in enumerate(S3) if i != ax - 1]
    flat2 = [_get(S3, D3, list(idx[:ax - 1]) + [k - 1] + list(idx[ax - 1:]))
             for idx in _it.product(*[range(d) for d in shape2])]
    tt(f"tslice axis {ax}", f"{_T(S3, D3)} {ax} {k} tslice tcvs", _cvs(shape2, flat2))
tt("tslice rank 1", "[4 5 6] tensor 1 3 tslice", "6")
tt("tslice bad axis", f"{_T(S3, D3)} 4 1 tslice", "ERR:rangecheck")
tt("tslice bad index", f"{_T(S3, D3)} 2 4 tslice", "ERR:rangecheck")

# ---------------------------------------------------------------- algebra
section("tensor: algebra", n)
DA = _rand(S3); DB = _rand(S3)
tt("tadd", f"{_T(S3, DA)} {_T(S3, DB)} tadd tcvs", _cvs(S3, [a + b for a, b in zip(DA, DB)]))
tt("tsub", f"{_T(S3, DA)} {_T(S3, DB)} tsub tcvs", _cvs(S3, [a - b for a, b in zip(DA, DB)]))
tt("thadamard", f"{_T(S3, DA)} {_T(S3, DB)} thadamard tcvs", _cvs(S3, [a * b for a, b in zip(DA, DB)]))
tt("tscale", f"{_T(S3, DA)} -3 tscale tcvs", _cvs(S3, [-3 * a for a in DA]))
tt("tadd shapes differ", f"{_T(S3, DA)} [[1 2] [3 4]] tensor tadd", "ERR:rangecheck")
tt("tadd of a list", f"{_T(S3, DA)} [1 2] tadd", "ERR:typecheck")
tra("tnorm", f"{_T(S3, DA)} tnorm", sum(a * a for a in DA) ** 0.5)
SU = [2, 3]; DU = _rand(SU); SV = [2]; DV = _rand(SV)
tt("touter", f"{_T(SU, DU)} {_T(SV, DV)} touter tcvs",
   _cvs(SU + SV, [a * b for a in DU for b in DV]))
SM = [3, 4]; DM = _rand(SM); SN = [4, 2]; DN = _rand(SN)
r = _einsum(["ij", "jk"], "ik", [(SM, DM), (SN, DN)])
tt("tdot matrix product", f"{_T(SM, DM)} {_T(SN, DN)} [2] [1] tdot tcvs", _cvs(*r))
SP3 = [3, 4, 2]; DP3 = _rand(SP3)
r = _einsum(["ijk", "jk"], "i", [(SP3, DP3), (SN, DN)])
tt("tdot over two axes", f"{_T(SP3, DP3)} {_T(SN, DN)} [2 3] [1 2] tdot tcvs", _cvs(*r))
r = _einsum(["ijk", "lj"], "ikl", [(SP3, DP3), ([3, 4], DM)])
tt("tdot, B's axis 2", f"{_T(SP3, DP3)} {_T([3, 4], DM)} [2] [2] tdot tcvs", _cvs(*r))
tt("tdot empty axes is touter", f"{_T(SU, DU)} {_T(SV, DV)} [] [] tdot tcvs",
   _cvs(SU + SV, [a * b for a in DU for b in DV]))
tt("tdot all axes gives a number", f"{_T(SM, DM)} {_T(SM, DM)} [1 2] [1 2] tdot", str(sum(a * a for a in DM)))
tt("tdot dimensions differ", f"{_T(SM, DM)} {_T(SN, DN)} [1] [1] tdot", "ERR:rangecheck")
tt("tdot axis out of range", f"{_T(SM, DM)} {_T(SN, DN)} [3] [1] tdot", "ERR:rangecheck")
tt("tdot axis repeated", f"{_T([2, 2], [1, 2, 3, 4])} {_T([2, 2], [1, 2, 3, 4])} [1 1] [1 2] tdot", "ERR:rangecheck")
tt("tinner", f"{_T(S3, DA)} {_T(S3, DB)} tinner", str(sum(a * b for a, b in zip(DA, DB))))
SC = [3, 2, 3]; DC = _rand(SC)
for i, j, ins, outs in ((1, 3, "aba", "b"), (3, 1, "aba", "b")):
    r = _einsum([ins], outs, [(SC, DC)])
    tt(f"tcontract {i} {j}", f"{_T(SC, DC)} {i} {j} tcontract tcvs", _cvs(*r))
SC2 = [2, 2, 3]; DC2 = _rand(SC2)
r = _einsum(["aab"], "b", [(SC2, DC2)])
tt("tcontract 1 2", f"{_T(SC2, DC2)} 1 2 tcontract tcvs", _cvs(*r))
tt("tcontract of rank 2 gives a number", f"{_T([3, 3], D3[:9])} 1 2 tcontract", str(D3[0] + D3[4] + D3[8]))
tt("tcontract dimensions differ", f"{_T(SC, DC)} 1 2 tcontract", "ERR:rangecheck")
tt("tcontract i = j", f"{_T(SC, DC)} 2 2 tcontract", "ERR:rangecheck")
tt("ttrace rank 2", f"{_T([3, 3], D3[:9])} ttrace", str(D3[0] + D3[4] + D3[8]))
SR4 = [2, 2, 3, 3]; DR4 = _rand(SR4)
tt("ttrace rank 4", f"{_T(SR4, DR4)} ttrace", str(_einsum(["aabb"], "", [(SR4, DR4)])))
tt("ttrace odd rank", f"{_T(S3, D3)} ttrace", "ERR:rangecheck")
tt("ttrace not square", f"{_T(SM, DM)} ttrace", "ERR:rangecheck")
for p in _it.permutations([1, 2, 3]):
    p = list(p)
    tt(f"tpermute {p}", f"{_T(S3, D3)} {_lit(p)} tpermute tcvs", _cvs(*_permute(S3, D3, p)))
tt("tpermute not a permutation", f"{_T(S3, D3)} [1 1 2] tpermute", "ERR:rangecheck")
tt("tpermute wrong length", f"{_T(S3, D3)} [1 2] tpermute", "ERR:rangecheck")
tt("ttranspose rank 3", f"{_T(S3, D3)} ttranspose tcvs", _cvs(*_permute(S3, D3, [3, 2, 1])))
tt("ttranspose rank 2", "[[1 2 3] [4 5 6]] tensor ttranspose tcvs", "[1 4; 2 5; 3 6]")
SY = [3, 3, 3]; DY = _rand(SY)
perms = list(_it.permutations([1, 2, 3]))
sym = [sum(_permute(SY, DY, list(p))[1][k] for p in perms) / 6 for k in range(27)]
anti = [sum(_sign([q - 1 for q in p]) * _permute(SY, DY, list(p))[1][k] for p in perms) / 6 for k in range(27)]
tla("tsym rank 3", f"{_T(SY, DY)} tsym tolist", sym)
tla("tantisym rank 3", f"{_T(SY, DY)} tantisym tolist", anti)
tra("tantisym is a multiple of tlevi", f"{_T(SY, DY)} tantisym 3 tlevi tinner", 6 * anti[5])
tt("tsym dimensions differ", f"{_T(S3, D3)} tsym", "ERR:rangecheck")

# ---------------------------------------------------------------- einsum
section("tensor: teinsum", n)
r = _einsum(["ij", "jk"], "ik", [(SM, DM), (SN, DN)])
tt("teinsum (ij,jk->ik)", f"(ij,jk->ik) [{_T(SM, DM)} {_T(SN, DN)}] teinsum tcvs", _cvs(*r))
tt("teinsum implicit (ij,jk)", f"(ij,jk) [{_T(SM, DM)} {_T(SN, DN)}] teinsum tcvs", _cvs(*r))
tt("teinsum (ii)", f"(ii) [{_T([3, 3], D3[:9])}] teinsum", str(D3[0] + D3[4] + D3[8]))
tt("teinsum (ii->i) diagonal", f"(ii->i) [{_T([3, 3], D3[:9])}] teinsum tcvs", _cvs([3], [D3[0], D3[4], D3[8]]))
tt("teinsum (ij->ji)", f"(ij->ji) [{_T(SM, DM)}] teinsum tcvs", _cvs(*_permute(SM, DM, [2, 1])))
tt("teinsum (i,i)", "(i,i) [[1 2 3] tensor [4 5 6] tensor] teinsum", "32")
r = _einsum(["ij", "j"], "i", [(SM, DM), ([4], DM[:4])])
tt("teinsum (ij,j->i)", f"(ij,j->i) [{_T(SM, DM)} {_T([4], DM[:4])}] teinsum tcvs", _cvs(*r))
tt("teinsum (i,j->ij)", f"(i,j->ij) [{_T(SV, DV)} {_T([3], D3[:3])}] teinsum tcvs",
   _cvs([2, 3], [a * b for a in DV for b in D3[:3]]))
r = _einsum(["ijk", "jl"], "ikl", [(SP3, DP3), ([4, 3], DM)])
tt("teinsum (ijk,jl->ikl)", f"(ijk,jl->ikl) [{_T(SP3, DP3)} {_T([4, 3], DM)}] teinsum tcvs", _cvs(*r))
r = _einsum(["ij", "jk", "kl"], "il", [(SM, DM), (SN, DN), ([2, 3], DU)])
tt("teinsum three operands", f"(ij,jk,kl->il) [{_T(SM, DM)} {_T(SN, DN)} {_T([2, 3], DU)}] teinsum tcvs", _cvs(*r))
tt("teinsum implicit (ij,ji) gives a number",
   f"(ij,ji) [{_T(SM, DM)} {_T([4, 3], DM)}] teinsum", str(_einsum(["ij", "ji"], "", [(SM, DM), ([4, 3], DM)])))
tt("teinsum spaces", f"( i j , j k -> i k ) [{_T(SM, DM)} {_T(SN, DN)}] teinsum tcvs",
   _cvs(*_einsum(["ij", "jk"], "ik", [(SM, DM), (SN, DN)])))
tt("teinsum wrong operand count", f"(ij,jk) [{_T(SM, DM)}] teinsum", "ERR:rangecheck")
tt("teinsum rank mismatch", f"(ijk) [{_T(SM, DM)}] teinsum", "ERR:rangecheck")
tt("teinsum dimensions differ", f"(ij,jk) [{_T(SM, DM)} {_T(SM, DM)}] teinsum", "ERR:rangecheck")
tt("teinsum bad character", f"(i1) [{_T(SM, DM)}] teinsum", "ERR:rangecheck")
tt("teinsum output repeated", f"(ij->ii) [{_T(SM, DM)}] teinsum", "ERR:rangecheck")
tt("teinsum output not in inputs", f"(ij->k) [{_T(SM, DM)}] teinsum", "ERR:rangecheck")
tt("teinsum not a string", f"5 [{_T(SM, DM)}] teinsum", "ERR:typecheck")

# ---------------------------------------------------------------- vectors, metrics
section("tensor: vectors and metrics", n)
u, v, w = [1, 2, 3], [4, -5, 6], [2, 0, 7]
cr = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
tla("tcross lists", f"{_lit(u)} {_lit(v)} tcross", cr)
tt("tcross tensors", f"{_lit(u)} tensor {_lit(v)} tensor tcross tcvs", _cvs([3], cr))
tt("tcross mixed", f"{_lit(u)} {_lit(v)} tensor tcross tcvs", _cvs([3], cr))
tt("tcross equals tlevi contraction",
   f"(ijk,j,k->i) [3 tlevi {_lit(u)} tensor {_lit(v)} tensor] teinsum tcvs", _cvs([3], cr))
tt("ttriple", f"{_lit(u)} {_lit(v)} {_lit(w)} ttriple", str(sum(a * b for a, b in zip(w, cr))))
tt("tcross length 2", "[1 2] [3 4] tcross", "ERR:rangecheck")
G = [[2, 1], [1, 3]]
TG = [3, 5]
tla("tlower vector", f"{_lit(TG)} tensor {_lit(G)} mfromrows 1 tlower tolist",
    [G[0][0] * 3 + G[0][1] * 5, G[1][0] * 3 + G[1][1] * 5])
Ginv = [[_F(3, 5), _F(-1, 5)], [_F(-1, 5), _F(2, 5)]]
tla("traise vector", f"{_lit(TG)} tensor {_lit(G)} mfromrows 1 traise tolist",
    [float(Ginv[0][0] * 3 + Ginv[0][1] * 5), float(Ginv[1][0] * 3 + Ginv[1][1] * 5)])
tla("traise undoes tlower", f"{_lit(TG)} tensor {_lit(G)} tensor 1 tlower {_lit(G)} tensor 1 traise tolist", TG)
MT = [[1, 2], [3, 4]]
low2 = [sum(G[a][b] * MT[i][b] for b in range(2)) for i in range(2) for a in range(2)]
tla("tlower index 2 of a matrix", f"{_lit(MT)} tensor {_lit(G)} mfromrows 2 tlower tolist", low2)
tt("tlower bad index", f"{_lit(TG)} tensor {_lit(G)} mfromrows 2 tlower", "ERR:rangecheck")
tt("tlower metric of wrong size", f"{_lit(TG)} tensor 3 tdelta 1 tlower", "ERR:rangecheck")
tt("traise singular metric", f"{_lit(TG)} tensor [[1 2] [2 4]] mfromrows 1 traise", "ERR:undefinedresult")

# ---------------------------------------------------------------- bignums
section("tensor: bignums", n)
def _f(x): return fmt(D(x.numerator) / D(x.denominator), n) if isinstance(x, _F) else fmt(D(x), n)
BA = ["0.1", "0.2", "0.3", "0.4"]; BB = ["1.5", "-2", "0.25", "3"]
fa = [_F(x) for x in BA]; fb = [_F(x) for x in BB]
tt("tcvs of strings", f"{_T([2, 2], BA)} tcvs", _cvs([2, 2], fa, _f))
tt("tadd bignums", f"{_T([2, 2], BA)} {_T([2, 2], BB)} tadd tcvs", _cvs([2, 2], [a + b for a, b in zip(fa, fb)], _f))
tt("tadd mixed", f"{_T([2, 2], BA)} [[1 2] [3 4]] tensor tadd tcvs",
   _cvs([2, 2], [a + b for a, b in zip(fa, [1, 2, 3, 4])], _f))
tt("tscale by a string", f"{_T([2, 2], [1, 2, 3, 4])} (0.5) tscale tcvs", _cvs([2, 2], [_F(x, 2) for x in (1, 2, 3, 4)], _f))
r = _einsum(["ij", "jk"], "ik", [([2, 2], fa), ([2, 2], fb)])
tt("teinsum bignums", f"(ij,jk->ik) [{_T([2, 2], BA)} {_T([2, 2], BB)}] teinsum tcvs", _cvs(*r, f=_f))
tt("tinner bignums", f"{_T([2, 2], BA)} {_T([2, 2], BB)} tinner bncvs", _f(sum(a * b for a, b in zip(fa, fb))))
with localcontext() as _c:
    _c.prec = 60
    _nv = sum(D(x) ** 2 for x in BA).sqrt()
TN += 1
bna("tnorm bignums", f"{_T([2, 2], BA)} tnorm", _nv, 18)
cu = [_F("0.1"), _F("0.2"), _F("0.3")]; cv = [_F(1), _F("-0.5"), _F(2)]
ccr = [cu[1] * cv[2] - cu[2] * cv[1], cu[2] * cv[0] - cu[0] * cv[2], cu[0] * cv[1] - cu[1] * cv[0]]
tt("tcross bignums", "[(0.1) (0.2) (0.3)] tensor [1 (-0.5) 2] tcross tcvs", _cvs([3], ccr, _f))
SB = [2, 2]
symb = [(fa[i * 2 + j] + fa[j * 2 + i]) / 2 for i in range(2) for j in range(2)]
tt("tsym bignums", f"{_T(SB, BA)} tsym tcvs", _cvs(SB, symb, _f))
tt("tcontract bignums", f"{_T(SB, BA)} 1 2 tcontract bncvs", _f(fa[0] + fa[3]))
tt("tget keeps a string", f"{_T(SB, BA)} [2 1] tget", "0.3")
print(f"tensor tests: {TN}")

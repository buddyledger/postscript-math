# pst-numeric

Arbitrary precision arithmetic, matrices, complex numbers and numerical
methods for PSTricks.

**pst-numeric** is a library of PostScript procedures for PSTricks. Its
decimal numbers (*bignums*) carry as many significant digits as you ask for,
where PostScript's own reals have about seven. On top of that it has
matrices, complex numbers, roots of functions, integrals and polynomials,
each working on ordinary reals or on bignums. The calculations run in the
PostScript interpreter while the page is drawn, so they can feed plots
directly. The same library also runs on its own in Ghostscript, as a
calculator.

```latex
\usepackage[bignum,calc]{pst-numeric}
...
\psplot{0}{3}{\pstNumeric{[0.5 0 -1] x polyval}}
\begin{pspicture}(0,0)(8,0.4)
  \psNumericShow{30 setbnsize 2 setbn sqrtbn}  % prints +1.41421356237309504880168872421e0
\end{pspicture}
```

The [manual](doc/pst-numeric-doc.pdf) describes the package, with examples
and a reference of every procedure. The library has five parts, chosen by
the package options:

| Option | Source | What it does |
|---|---|---|
| `bignum` | `bignumlibrary.ps` | Decimal floating-point numbers with as many significant digits as you ask for: arithmetic, comparisons, sqrt, exp, powers, logarithms, trigonometric and hyperbolic functions and their inverses, pi, factorials |
| `trig` | `Trig.ps` | sin/cos/tan/atan for ordinary PostScript reals using the CORDIC algorithm |
| `matrix` | `Matrix.ps` | Matrices of reals or bignums: build, add, multiply, transpose, determinant, inverse, linear systems, least squares, symmetric eigenvalues |
| `complex` | `Complex.ps` | Complex numbers of reals or bignums: arithmetic, modulus and argument, sqrt, exp, ln, powers (loads `matrix`) |
| `calc` | `Numeric.ps` | Roots of functions, integrals, polynomials (values, roots, fitting), gcd and lcm (loads `matrix` and `complex`) |

With no option, all five are loaded. Matrices, complex numbers and `calc`
work on reals without `bignum`; load it too to use them with bignums.
Like every PSTricks package it needs the `latex`–`dvips` route (or `xelatex`).

## Files

| Folder | Contents | On CTAN |
|---|---|---|
| `tex/`, `latex/` | The package, `pst-numeric.tex`, and its LaTeX wrapper `pst-numeric.sty` | yes |
| `dvips/` | `pst-numeric-<part>.pro`, each part as a dvips header (generated), and `pst-numeric.pro`, the package's own helpers | yes |
| `doc/` | The manual: [`pst-numeric-doc.pdf`](doc/pst-numeric-doc.pdf), its source and bibliography | yes |
| `source/` | The library's PostScript files, `Load.ps` to load them all, `make_headers.py` to generate the headers, and `gs.bat` to run Ghostscript on Windows | yes, without `gs.bat` |
| `test/` | `test_bignum.ps` (581 tests of the library), `make_tests.py` that generates it, and `tex-test.sh` with `tex-test.tex` (tests of the package with latex and dvips) | no |
| `examples/` | [`showcase.pdf`](examples/showcase.pdf), every public procedure with a live result, with its source `showcase.ps` and `make_showcase.bat`; and `bignumfactorial.ps` | no |
| `tools/` | `make-doc.sh` builds the manual, `make-ctan.py` builds the CTAN archive | no |

`README` and `Changes` are the CTAN archive's readme and change log;
[RELEASING.md](RELEASING.md) describes how a version goes to CTAN.

## Building and testing

The manual and the package tests need TeX Live; its Docker image works
too. Run from the repository's top folder:

```bash
docker run --rm -v "$PWD:/pkg" texlive/texlive:latest bash /pkg/tools/make-doc.sh
```

```bash
docker run --rm -v "$PWD:/pkg:ro" texlive/texlive:latest bash /pkg/test/tex-test.sh
```

The dvips headers are generated from the `.ps` files, so don't edit them:
change the `.ps` file and run

```bash
python source/make_headers.py
```

A part header is its `.ps` file without the comment and blank lines (DSC
lines must not appear in a dvips header). `dvips/pst-numeric.pro` is written
by hand.

The library tests run in Ghostscript, from the top folder, against the
`.ps` files or, with `-dPSM_HEADERS`, against the headers (on Windows use
`gswin64c`):

```bash
gs -q -dNODISPLAY -dNOSAFER -dBATCH test/test_bignum.ps
```

```bash
gs -q -dNODISPLAY -dNOSAFER -dBATCH -dPSM_HEADERS test/test_bignum.ps
```

The file prints a line for each failure and ends with
`N passed, 0 failed / ALL TESTS PASSED`. To see every line, set
`/bnt_verbose true def` near the top. The first section checks that loading
adds only the library's dictionary to `userdict` and leaves the stacks as
they were. Expected values come from Python's `decimal` module, computed to
100 digits and rounded half away from zero, and from exact fractions
(`fractions` module) for the matrix and polynomial results.

`test_bignum.ps` is generated, so don't edit it by hand. To add or change
tests, edit the cases in `test/make_tests.py` and run it again
(`python test/make_tests.py`). The script writes the file itself; don't
redirect its output with `>`, which in Windows PowerShell 5.1 writes UTF-16.

`python tools/make-ctan.py` builds `build/pst-numeric.zip`, the archive for
CTAN, and checks it.

GitHub Actions runs all of these on every push: a check that the headers in
`dvips/` are up to date, the library tests both ways, the package tests, and
the CTAN archive.

## Using the library with Ghostscript

`source/Load.ps` loads all five parts from the current folder and opens the
library's dictionary, so after `(Load.ps) run` everything can be called
directly. In `source/`:

```bash
gs -dNODISPLAY -dNOSAFER Load.ps
```

On Windows, `source\gs.bat` calls Ghostscript 9.52
(`C:\Program Files\gs\gs9.52\bin\gswin64c.exe`) with `-dNODISPLAY -dNOSAFER`:
`gs.bat Load.ps` loads the library and waits at the `GS>` prompt, and
`gs.bat myfile.ps` runs a file (it can start with `(Load.ps) run`).

`-dNOSAFER` is required: since 9.50 Ghostscript runs in SAFER mode by
default, which stops `Load.ps` from `run`-ning the other files. It also means
any file run this way can read and write your files, so use it only for
PostScript you trust.

Every name the library defines is in one dictionary, `tx@NumericDict`, so
nothing clashes with other PostScript code or with your own names. Loading
adds only that one name to `userdict`. `Load.ps` leaves the dictionary open,
so anything you `def` at the top level then goes into it too; avoid
redefining its names. If you load a part on its own, or the dvips headers,
open the dictionary yourself:

```postscript
(Matrix.ps) run
tx@NumericDict begin
  [[1 2] [3 4]] mfromrows mdet =
end
```

[examples/showcase.pdf](examples/showcase.pdf) runs every public procedure
and typesets the code next to its result, with a note under each row. Red
results are errors raised on purpose, to show how each procedure rejects bad
input. It also compares the CORDIC functions with Ghostscript's built-in sin
and cos. To rebuild it after changing the library (about 50 seconds), run
`examples\make_showcase.bat`. `examples/bignumfactorial.ps` is a stand-alone
program, separate from the library, that computes 34! and draws it on the
page, so open it in a Ghostscript window.

## Reference

The manual has the reference for the package. This section has more detail
on each part of the library.

### bignumlibrary.ps

#### Quick example

```postscript
(Load.ps) run
30 setbnsize                       % 30 significant digits
(2) setbn lnbn bnPrint             % +6.93147180559945309417232121458e-1
1 setbn 3 setbn divbn bnPrint      % +3.33333333333333333333333333333e-1
pibn bnPrint                       % +3.14159265358979323846264338328e0
(1.5) setbn (1.25) setbn gtbn =    % true
```

#### Number format

A bignum is a three-element array `[sign digits exponent]`:

- `sign`: boolean, `true` for positive or zero, `false` for negative
- `digits`: a string of ASCII digits, `bnn` long, first digit non-zero unless the value is 0
- `exponent`: integer

The value is `digits × 10^exponent`, with the digits read as a whole number.
With `5 setbnsize`, 509 is stored as `[true (50900) -2]`.

`typchk` returns `(bignumtype)` for anything with this shape.

#### Precision and rounding

`n setbnsize` sets the number of significant digits (`bnn`). The default is
**20**. Every result is rounded to `bnn` digits, half away from zero.
Inputs are rounded too when `setbn` converts them.

- `addbn`, `subbn`, `mulbn`, `divbn`, `truncbn`, `roundbn` are exact
  before the final rounding, so their results are always correctly rounded.
- The functions (`sqrtbn`, `expbn`, `powbn`, `sinbn` and the rest, `pibn`,
  `factbn`, `binombn`) work with 6 extra digits and then round. Every test value is correct to the last digit, but
  correct rounding isn't proven for every input.

Precision doesn't change existing bignums. A bignum made at one precision
is re-rounded to the current `bnn` when it's used.

#### Procedures

Stack effects are shown as `inputs → outputs`. `bn` is a bignum.

**Conversion**

| Procedure | Stack | Notes |
|---|---|---|
| `setbnsize` | `n → –` | n ≥ 1, else `rangecheck` |
| `setbn` | `int\|real\|string\|bn → bn` | Strings: optional sign, digits, optional `.`, optional `e`/`E` exponent, e.g. `(-1.25e-3)`, `(.5)`, `(1E5)`. Anything else gives `syntaxerror`. **Pass strings for precise values.** A real keeps only the 6 digits Ghostscript prints for it (`3.14159265 setbn` gives 3.14159), and reals above about 3.4e38 can't be written at all, so write `(1e50)`, not `1e50` |
| `bncvs` | `bn → string` | e.g. `(+1.2500000000000000000e-3)` |
| `bnPrint` | `bn → –` | prints `bncvs` |
| `bncvr` | `bn → real` | limited to the range and precision of a real |

**Arithmetic**

| Procedure | Stack | Notes |
|---|---|---|
| `addbn` `subbn` `mulbn` | `a b → a±b, a×b` | |
| `divbn` | `a b → a÷b` | b = 0 gives `undefinedresult` |
| `negbn` `absbn` | `a → −a, \|a\|` | |
| `truncbn` | `a → integer part` | rounds toward zero |
| `roundbn` | `a → nearest integer` | halves round away from zero |

**Comparison**

| Procedure | Stack | Notes |
|---|---|---|
| `cmpbn` | `a b → -1\|0\|1` | |
| `eqbn` `nebn` `gtbn` `gebn` `ltbn` `lebn` | `a b → bool` | `a b gtbn` means a > b |
| `bniszero` | `a → bool` | 0 and −0 are equal |

**Functions**

| Procedure | Stack | Notes |
|---|---|---|
| `sinbn` `cosbn` `tanbn` | `x → bn` | x in radians. Any size: working precision grows with the size of x, so `(1e50) setbn sinbn` is accurate but slower |
| `lnbn` `log10bn` | `x → bn` | x ≤ 0 gives `rangecheck` |
| `sqrtbn` | `x → bn` | x < 0 gives `rangecheck` |
| `expbn` | `x → eˣ` | \|x\| ≥ 10⁹ gives `rangecheck` |
| `powbn` | `x y → xʸ` | whole-number y (below 10⁹) by repeated squaring, so negative x is allowed and results are exact when they fit; otherwise e^(y ln x), and x < 0 gives `rangecheck`. 0 to a negative power gives `undefinedresult`; 0⁰ = 1 |
| `atanbn` | `x → bn` | in (−π/2, π/2) |
| `asinbn` `acosbn` | `x → bn` | \|x\| > 1 gives `rangecheck` |
| `atan2bn` | `y x → bn` | angle of the point (x, y), in (−π, π]; 0 for (0, 0) |
| `sinhbn` `coshbn` `tanhbn` | `x → bn` | \|x\| ≥ 10⁹ gives `rangecheck` |
| `factbn` | `n → n!` | n an integer ≥ 0 |
| `binombn` | `n k → C(n, k)` | 0 when k < 0 or k > n |
| `pibn` | `– → bn` | |

pi, ln 2 and ln 10 are computed once per precision and cached.

**Other:** `mergestr` (`(ab) (cd) → (abcd)`), `typchk` (`any → (bignumtype)`,
`(complextype)`, `(matrixtype)` or the PostScript type name; a two-element
array of numbers or bignums counts as complex), `bnDebug` (set it `true` to
print each result of `setbn` and the arithmetic procedures).

Procedures whose names start with `bn_` are internal.

#### Errors

Errors are raised through `errordict`, the same way built-in operators raise
them, so `stopped` catches them and Ghostscript reports them as, for example,
`Error: /undefinedresult in /divbn`.

#### Speed

Arithmetic works one decimal digit at a time. At 20 digits each operation is
instant. At 100 digits, `pibn` takes about 5 s the first time (it's cached
after that) and `sinbn` about 2 s. The full test suite (581 tests) takes
about 30 seconds, mostly for bignum integrals and polynomial roots.

### Trig.ps

CORDIC functions for ordinary reals, accurate to about 6 significant digits
(40 iterations; PostScript reals limit the precision). CORDIC builds an angle
from the fixed steps atan(1), atan(1/2), atan(1/4), … using only additions
and halvings. The step angles and the length correction are computed when the
file loads. It works on its own and doesn't need Matrix.ps.

| Procedure | Stack |
|---|---|
| `corsin` `corcos` `cortan` `corcot` `corsec` `corcsc` | `x → real` (x in radians) |
| `coratan` | `x y → atan(y/x)` in [−π/2, π/2]; x = 0 gives ±π/2, and x = y = 0 gives `undefinedresult` |
| `cordiccossin` | `beta n → [[cos sin]]` (a 2×1 matrix in Matrix.ps layout, so `M 1 1 mget` is cos and `M 2 1 mget` is sin; n iterations, up to 64) |
| `cordicatan` | `x y n → atan(y/x)` (n iterations, up to 64) |

Also defines `pi` as a real.

### Matrix.ps

Matrices are arrays of columns, and indices start at 1. The easiest way to
write one is as a list of rows:

```postscript
/A [[1 2] [3 4]] mfromrows def
A mdet =                           % -2
A [[5] [6]] mfromrows msolve mPrint  % -4.0 / 4.5  (solves A x = [5; 6])
```

**Reals or bignums.** Every operation works on ordinary PostScript numbers.
If any element is a bignum, or a string such as `(0.1)`, the whole
calculation switches to bignum arithmetic at the current `bnn` (strings and
other numbers are converted with `setbn`). So
`[[(0.1) (0.2)] [(0.3) (0.4)]] mfromrows mdet` is exactly −0.02, where reals
give −0.0200000033. `mmul`, `mdet`, `minv` and `msolve` work with 6 extra
digits and then round. Bignum elements need `bignumlibrary.ps`; with reals
only, Matrix.ps works on its own.

| Procedure | Stack | Notes |
|---|---|---|
| `marray` | `m n → M` | m rows × n columns, zero-filled |
| `mfromrows` | `[[row] [row] …] → M` | rows must all be the same length, else `rangecheck` |
| `mtorows` | `M → [[row] [row] …]` | |
| `midentity` | `n → I` | n × n identity |
| `mcopy` | `M → copy` | independent of M |
| `mput` | `M i j value → –` | changes M in place |
| `mget` | `M i j → value` | |
| `msize` | `M → m n` | rows, then columns on top |
| `mtranspose` | `M → Mᵀ` | |
| `madd` `msub` | `A B → A±B` | sizes must match, else `rangecheck` |
| `mscale` | `M s → s·M` | s a number, bignum or string |
| `mmul` | `A B → A×B` | returns the string `(Nan)` if A's columns don't match B's rows (kept from the 2012 version) |
| `mdet` | `A → det` | A square. Singular gives 0; an all-integer matrix gives an integer |
| `minv` | `A → A⁻¹` | singular A gives `undefinedresult` |
| `msolve` | `A B → X` | solves A X = B for an n × n A and n × k B; singular A gives `undefinedresult` |
| `mlstsq` | `A B → X` | least squares: the X that minimises the size of A X − B, for an m × n A with m ≥ n (Householder QR). Linearly dependent columns give `undefinedresult` |
| `meigsym` | `A → [values] V` | A symmetric. Eigenvalues in ascending order, and V with the matching unit eigenvectors as columns (cyclic Jacobi). Not symmetric gives `rangecheck` |
| `mPrint` | `M → –` | prints one row per line |

`mdet`, `minv` and `msolve` use Gauss-Jordan elimination with partial
pivoting (row swaps). A pivot counts as zero when it is smaller than the
largest element of A times 10⁻⁵ for reals, or times 10^−(bnn+3) for bignums,
so rounding errors don't hide a singular matrix. With reals, results have
about 7 significant digits, and fewer for ill-conditioned matrices such as
Hilbert matrices. Use bignums when that matters.

The operations never change their arguments, except `mput`.

### Complex.ps

A complex number is the array `[re im]`. Wherever one is expected, a plain
number, bignum or string `x` counts as `[x 0]`. As in Matrix.ps, a bignum or
string part switches the calculation to bignums. Needs Matrix.ps.

```postscript
[1 2] [3 4] cmul cPrint          % -5 + 10i
[(0) 1] [0 1] cpow cPrint        % i^i = +2.0787957635076190855e-1 + 0.0...e0i
```

| Procedure | Stack | Notes |
|---|---|---|
| `cpx` | `re im → z` | |
| `cre` `cim` | `z → part` | |
| `cadd` `csub` `cmul` `cdiv` | `a b → z` | division by 0 gives `undefinedresult` |
| `cneg` `cconj` | `z → z` | |
| `cabs` | `z → \|z\|` | |
| `carg` | `z → angle` | in (−π, π] |
| `csqrt` | `z → √z` | the root with real part ≥ 0 |
| `cexp` | `z → eᶻ` | |
| `cln` | `z → ln z` | principal value; 0 gives `rangecheck` |
| `cpow` | `z w → zʷ` | whole-number w by repeated multiplication, otherwise e^(w ln z) |
| `ccvs` `cPrint` | `z → string`, `z → –` | `re + im i` |

Parts much smaller than the modulus can show rounding noise instead of 0, for
example `[0 pibn] cexp` gives −1 − 3.7e−20i because pibn is pi rounded to
`bnn` digits.

### Numeric.ps

Numerical methods for reals or bignums. Needs Matrix.ps; `polyroots` and a
complex `x` in `polyval` also need Complex.ps.

A function argument is a procedure `{f}` that takes x and returns f(x). If
the other arguments are bignums or strings, it receives bignums and should
return a bignum. It runs at 6 digits above `bnn`, so it shouldn't change
`bnn`.

```postscript
{ dup mulbn 2 setbn subbn } (1) (2) froot bnPrint   % +1.4142135623730950488e0
{ dup mul } 0 1 fintegrate =                         % 0.333333
[1 -6 11 -6] polyroots { cPrint } forall             % 1.0 + 0.0i  2.0 + 0.0i  3.0 + 0.0i
```

| Procedure | Stack | Notes |
|---|---|---|
| `gcd` `lcm` | `a b → n` | integers |
| `froot` | `{f} a b → x` | a root of f between a and b; f(a) and f(b) must differ in sign, else `rangecheck`. Illinois method |
| `fintegrate` | `{f} a b → ∫` | Gauss-Legendre with 16 and 32 points, halving the interval where they disagree |
| `polyval` | `p x → p(x)` | x a number, bignum, string or complex |
| `polyder` | `p → p′` | |
| `polyadd` `polymul` | `p q → p+q, p×q` | |
| `polyroots` | `p → [z …]` | all roots as complex numbers, sorted by real part (Durand-Kerner). All-zero p gives `rangecheck` |
| `polyfit` | `[x …] [y …] d → p` | least-squares polynomial of degree d, using `mlstsq` |

A polynomial is an array of coefficients, highest power first: `[1 0 -2]` is
x² − 2.

Limits:

- `fintegrate` is fast and accurate for smooth functions. Where the function
  or its slope is infinite at an end, as for √x at 0, it has to halve the
  interval many times: with reals that still gives full accuracy, but with
  bignums it is slow (over a minute) and the last few digits can be wrong.
  The first bignum integral at a given precision takes about 10 s extra to
  compute the rule's points and weights, which are then kept.
- `polyroots` finds a root of multiplicity m to only about 1/m of the digits,
  so a double root keeps about half of them.
- `froot` and `polyroots` stop after 500 iterations even if they haven't
  converged.

## License

Copyright 2012, 2026 Buddy Ledger.

This work may be distributed and/or modified under the conditions of the
[LaTeX Project Public License](https://www.latex-project.org/lppl/), either
version 1.3c of this license or (at your option) any later version. The full
text is in [LICENSE](LICENSE).

This work has the LPPL maintenance status `author-maintained`. The Current
Maintainer of this work is Buddy Ledger.

This work consists of the files `README`, `README.md`, `Changes`,
`RELEASING.md`, `tex/pst-numeric.tex`, `latex/pst-numeric.sty`,
`dvips/pst-numeric.pro`, `dvips/pst-numeric-bignum.pro`,
`dvips/pst-numeric-trig.pro`, `dvips/pst-numeric-matrix.pro`,
`dvips/pst-numeric-complex.pro`, `dvips/pst-numeric-calc.pro`,
`doc/pst-numeric-doc.tex`, `doc/pst-numeric-doc.bib`,
`doc/pst-numeric-doc.pdf`, `source/bignumlibrary.ps`, `source/Trig.ps`,
`source/Matrix.ps`, `source/Complex.ps`, `source/Numeric.ps`,
`source/Load.ps`, `source/make_headers.py`, `source/gs.bat`,
`test/test_bignum.ps`, `test/make_tests.py`, `test/tex-test.sh`,
`test/tex-test.tex`, `examples/showcase.ps`, `examples/showcase.pdf`,
`examples/make_showcase.bat`, `examples/bignumfactorial.ps`,
`tools/make-doc.sh` and `tools/make-ctan.py`.

The history of the changes is in [Changes](Changes).

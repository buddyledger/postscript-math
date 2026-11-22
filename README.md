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
and a reference of every procedure. The library has seven parts, chosen by
the package options:

| Option | Source | What it does |
|---|---|---|
| `bignum` | `bignumlibrary.ps` | Decimal floating-point numbers with as many significant digits as you ask for: arithmetic, comparisons, sqrt and n-th roots, exp, powers, logarithms, trigonometric and hyperbolic functions and their inverses, pi, e, factorials, integer division and remainder, modular powers, primality, factorization |
| `trig` | `Trig.ps` | sin/cos/tan/atan for ordinary PostScript reals using the CORDIC algorithm |
| `matrix` | `Matrix.ps` | Matrices of reals or bignums: build, add, multiply, transpose, determinant, inverse, linear systems, least squares, LU, Cholesky, QR and singular value decompositions, pseudo-inverse, null space, rank, norms, condition number, eigenvalues and eigenvectors, matrix exponential and powers, Kronecker product |
| `complex` | `Complex.ps` | Complex numbers of reals or bignums: arithmetic, modulus and argument, sqrt, exp, ln, powers, trigonometric and hyperbolic functions and their inverses (loads `matrix`) |
| `calc` | `Numeric.ps` | Roots of functions, integrals, polynomials (values, roots, fitting, interpolation), cubic splines, minima, derivatives, systems of equations, statistics, regression with confidence and prediction bands, differential equations, Fourier transform, Gauss-Legendre integration, random numbers, gcd and lcm (loads `matrix`, `complex` and `special`) |
| `special` | `Special.ps` | Gamma, beta, digamma, error, incomplete gamma and beta, and Bessel functions, binomial coefficients; the normal, t, chi-squared, F, exponential, binomial and Poisson distributions (loads `bignum`) |
| `tensor` | `Tensor.ps` | Tensors of any rank: outer products, contractions, Einstein summation, permutations, symmetric parts, Levi-Civita symbol, metrics (loads `matrix`) |

With no option, all seven are loaded. Matrices, tensors and complex numbers
work on reals without `bignum`; load it too to use them with bignums
(`calc` loads it, through `special`).
Like every PSTricks package it needs the `latex`–`dvips` route (or `xelatex`).

## Files

| Folder | Contents | On CTAN |
|---|---|---|
| `tex/`, `latex/` | The package, `pst-numeric.tex`, and its LaTeX wrapper `pst-numeric.sty` | yes |
| `dvips/` | `pst-numeric-<part>.pro`, each part as a dvips header (generated), and `pst-numeric.pro`, the package's own helpers | yes |
| `doc/` | The manual: [`pst-numeric-doc.pdf`](doc/pst-numeric-doc.pdf), its source and bibliography | yes |
| `source/` | The library's PostScript files, `Load.ps` to load them all, `make_headers.py` to generate the headers, and `gs.bat` to run Ghostscript on Windows | yes, without `gs.bat` |
| `test/` | `test_bignum.ps` (1524 tests of the library; more cases in `tests_*.py`), `make_tests.py` that generates it, and `tex-test.sh` with `tex-test.tex` (tests of the package with latex and dvips) | no |
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

## Presenting results in documents

`\psNumericShow[options]{code}` prints a result as text, and
`\psNumericMatrix[options]{code}` lays it out: a matrix with brackets and
columns aligned at the decimal point, a list as a column or row vector, a
tensor of rank 3 or 4 as its labelled slices. `\psNumericRegression` prints
the result of `regress` as the fitted equation and its statistics, much as
pst-fit's GLLSR did, and `\psNumericRegPlot` plots the fitted curve, the
confidence and prediction bands, the data or the residuals of a fit stored
once with `\psNumericDef{name}{code}`.

```latex
\psNumericDef{fit}{[1 2 3 4 5 6] [2.1 3.9 6.2 7.8 10.1 12.2] 1 regress}
\begin{pspicture}(0,-2)(12,2)
\rput[l](0,0){\psNumericMatrix[label=A^{-1},numFormat=fixed,numDigits=2]{[[1 2] [3 4]] mfromrows minv}}
\rput[l](6,1){\psNumericRegression[regShow=eq r2 s]{fit}}
\end{pspicture}
```

| Key | Values | Default |
|---|---|---|
| `numFormat` | `raw` (as computed), `auto` (like %g), `fixed`, `sci` | `raw` (`auto` for the layouts) |
| `numDigits` | significant digits (`auto`, `sci`) or decimals (`fixed`) | 6 |
| `numTrim` | drop trailing zeros | false |
| `numDecimal` | the decimal separator | `.` |
| `sciStyle` | `times` (1.5×10⁻³) or `e` (1.5e−3) | `times` |
| `numFont` `numFontSize` | font of `\psNumericShow` | Courier, 10 |
| `matrixFont` | font of the layouts | Times-Roman |
| `matrixDelim` | `bracket`, `paren`, `bar`, `dbar`, `none` | `bracket` |
| `matrixAlign` | `decimal`, `right`, `center`, `left` | `decimal` |
| `colSep` `rowSep` | column gap, row pitch (in font sizes) | 1, 1.4 |
| `vector` | `column` or `row` | `column` |
| `label` | text drawn before the result with “ = ” (`^{}` and `_{}` work) | empty |
| `tensorLabels` | slice labels such as (1,:,:) | true |
| `regShow` | lines of `\psNumericRegression`: `eq params coef r2 adjr2 s n dof tval sse` | `eq r2 s` |
| `regPlot` | `fit`, `ci`, `pi`, `data`, `residuals`, `stdresiduals` | `fit` |

Rounding works on the decimal digits, so a bignum is rounded correctly
whatever its length. In PostScript, `pstnum_fmtnum` formats a number with
the same settings.

## Using the library with Ghostscript

`source/Load.ps` loads all seven parts from the current folder and opens the
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
| `pibn` `ebn` | `– → bn` | π and e |
| `rootbn` | `x n → ⁿ√x` | n an integer ≥ 1; a negative x needs an odd n, else `rangecheck`. A last Newton step makes exact roots exact |
| `minbn` `maxbn` | `a b → bn` | the smaller, the larger |
| `idivbn` | `a b → ⌊a/b⌋` | exact while the quotient has at most `bnn` digits; b = 0 gives `undefinedresult` |
| `modbn` | `a b → a − b⌊a/b⌋` | the remainder, with the sign of b, exact for numbers of any size |
| `powmodbn` | `a b m → aᵇ mod m` | integers, b ≥ 0, m ≥ 1 (else `rangecheck`); the result in [0, m), exact, as a bignum with every digit |
| `isprime` | `n → bool` | trial division below 2³¹; above, trial division by the primes below 1000 and Miller–Rabin with the bases that make it deterministic below 3.3·10²⁴; larger n get a strong probable-prime test to the first 20 primes. n < 2 gives false; a fraction `rangecheck` |
| `factor` | `n → [p₁ p₂ …]` | the prime factors in ascending order with multiplicity; 1 gives []; n < 1 or a fraction `rangecheck`. Trial division by the primes below 10⁴, then Pollard's rho with Brent's cycle detection: a factor with up to about 9 digits beyond those is found in seconds; after 50000 steps without one, `limitcheck`. A number gives integers (bignums for factors of 2³¹ or more), a bignum or string gives bignums |

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
instant and a function takes a few hundredths of a second. At 100 digits,
`pibn` takes about 1.5 s the first time (it's cached after that) and `sinbn`
about 0.3 s. The full test suite (1524 tests) takes about four minutes, mostly for
bignum integrals, polynomial roots, the special functions, and the
distributions, matrix decompositions and regressions with bignums.

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
| `mtrace` | `A → trace` | sum of the diagonal; A square |
| `mnorm` `mnorm1` `mnorminf` | `A → norm` | Frobenius norm; largest column sum of \|aᵢⱼ\|; largest row sum |
| `mcond` | `A → κ` | condition number ‖A‖₁ ‖A⁻¹‖₁; singular A gives `undefinedresult` |
| `mrank` | `A → r` | Gaussian elimination with partial pivoting; a pivot below the zero tolerance (as for `mdet`) counts as 0 |
| `mlu` | `A → L U P` | P A = L U, L lower triangular with ones on the diagonal, U upper triangular, P a permutation matrix (partial pivoting) |
| `meig` | `A → [z …]` | every eigenvalue of a square matrix, as complex numbers sorted by real part: Hessenberg reduction, then QR steps in complex arithmetic with Wilkinson shifts |
| `mchol` | `A → L` | Cholesky: A = L Lᵀ, L lower triangular with a positive diagonal; `rangecheck` unless A is square, symmetric and positive definite |
| `mqr` | `A → Q R` | thin QR, A m×n with m ≥ n (else `rangecheck`): Q m×n with orthonormal columns, R n×n upper triangular with a positive diagonal (Gram-Schmidt, each column orthogonalised twice); dependent columns give `undefinedresult` |
| `msvd` | `A → U S V` | thin singular value decomposition A = U diag(S) Vᵀ, k = min(m, n): U m×k and V n×k with orthonormal columns, S the list of singular values, largest first (one-sided Jacobi). Values below the largest times the zero tolerance are given as 0 |
| `msingular` | `A → [σ …]` | the singular values, largest first |
| `mpinv` | `A → A⁺` | Moore-Penrose pseudo-inverse (n×m) from the SVD; singular values below the zero tolerance count as 0, so it also works for rank-deficient and zero matrices |
| `mnull` | `A → N` | the columns of N are an orthonormal basis of the null space {x : A x = 0}; the empty list `[]` if that is only x = 0 |
| `meigsymv` | `A → [λ …] V` | the same as `meigsym`: eigenvalues ascending, unit eigenvectors as the columns of V |
| `meigvec` | `A → [[z v] …]` | every eigenvalue z of a square matrix (as `meig` gives them) with an eigenvector v, a list of complex numbers `[re im]` of length 1 whose largest component is real and positive (inverse iteration in complex arithmetic). A repeated eigenvalue gets orthogonal vectors when it has that many independent ones; a defective matrix repeats the vector |
| `mexp` | `A → eᴬ` | matrix exponential, A square: scaling and squaring of the Taylor series |
| `mpow` | `A k → Aᵏ` | k an integer (else `typecheck`); k = 0 gives the identity, k < 0 uses the inverse (`undefinedresult` for a singular A) |
| `mkron` | `A B → A ⊗ B` | Kronecker product: block (i, j) is aᵢⱼ B |
| `mdiag` | `[d …] → D`, `M → [d …]` | a list gives the diagonal matrix, a matrix gives the list of its diagonal |
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
| `csin` `ccos` `ctan` | `z → z` | `ctan` at a pole gives `undefinedresult` |
| `csinh` `ccosh` `ctanh` | `z → z` | |
| `casin` `cacos` `catan` | `z → z` | principal values with the branch cuts of C99 and Python (asin 2 = π/2 + 1.317i); `catan` of ±i gives `rangecheck` |
| `casinh` `cacosh` `catanh` | `z → z` | `catanh` of ±1 gives `rangecheck` |

A real argument whose result is real (asin 0.5, atanh 0.5, acosh 2) gives a
real result with an exact zero imaginary part, computed with real functions.

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
| `polyinterp` | `[x …] [y …] → p` | the polynomial of lowest degree through the points (Newton's divided differences); equal x give `rangecheck` |
| `spline` | `[x …] [y …] → S` | natural cubic spline, x increasing; S is `[[x …] [y …] [y″ …]]` |
| `splineval` | `S x → y` | the spline at x; beyond the ends the end pieces continue |
| `fmin` | `{f} a b → x` | where f is smallest in [a, b] (Brent's method). x to about half the digits, f(x) to all of them |
| `fderiv` | `{f} x → f′(x)` | central differences extrapolated to step 0 (Ridders' method) |
| `fsolve` | `{F} [x0 …] → [x …]` | F(x) = 0 for a list of n unknowns, F mapping a list of n numbers to a list of n. Newton's method with a central-difference Jacobian and step halving; a singular Jacobian gives `undefinedresult` |
| `mean` `median` | `[x …] → number` | |
| `variance` `stddev` | `[x …] → number` | sample variance and standard deviation (n − 1); fewer than 2 values give `rangecheck` |
| `covariance` `correlation` | `[x …] [y …] → number` | sample covariance; Pearson's r (`undefinedresult` for a constant list) |
| `oderk4` | `{f} t0 y0 t1 n → [[t y] …]` | y′ = f(t, y) by n steps of the classical Runge-Kutta method, n + 1 points. y is a number or a list (a system); f takes `t y` and returns y′ of the same shape |
| `odesolve` | `{f} t0 y0 t1 n → [[t y] …]` | the same, each of the n steps solved to the working precision by Gragg-Bulirsch-Stoer extrapolation (a step that does not converge is halved) |
| `fft` `ifft` | `[z …] → [Z …]` | discrete Fourier transform Z(k) = Σ z(j) e^(−2πijk/n) and its inverse (with 1/n); radix 2 for a power of 2, otherwise the direct sum |
| `listmin` `listmax` | `[x …] → number` | the smallest, the largest; an empty list gives `rangecheck` |
| `listsum` | `[x …] → number` | the sum, 0 for an empty list |
| `mode` | `[x …] → number` | the most frequent value, the smallest of them on a tie |
| `wmean` | `[x …] [w …] → number` | weighted mean Σwx/Σw; weights adding up to 0 give `undefinedresult` |
| `skewness` `kurtosis` | `[x …] → number` | adjusted sample skewness G1 and excess kurtosis G2 (Excel's SKEW and KURT); at least 3 and 4 values, a constant list gives `undefinedresult` |
| `quantile` | `[x …] p → number` | R type 7 (Excel's PERCENTILE.INC): x₍ₕ₎ interpolated at h = (n − 1)p, 0 ≤ p ≤ 1; p = 0.5 is the median |
| `histogram` | `[x …] a b k → [c₁ … cₖ]` | counts in k equal bins on [a, b], the last bin closed; values outside are not counted |
| `regress` | `[x …] [y …] model → R` | linear least squares with statistics (GLLSR of pst-fit). model: an integer degree, `/linear`, a basis procedure `{ x → [b₁(x) … bₖ(x)] }`, `/power` (a xᵇ), `/exp` (a eᵇˣ), `/log10`, `/ln` (a + b log x), `/recip` (a + b/x), `/gauss` (A e^(−(x−μ)²/2σ²)), or a dictionary with `/model` and optional `/weights [w …]`, `/intercept c`, `/yoffset c` (fit y − c and add c back: y = c + a xᵇ, y = c + a eᵇˣ, a Gauss curve on a baseline; pst-fit's `Yint`), `/level p` (default 0.95). Householder QR; transforms are fitted in the transformed space. Invalid data for a transform, too few points, an unknown model give `rangecheck`; dependent columns and a `/gauss` without maximum give `undefinedresult` |
| `linreg` | `[x …] [y …] → R` | the straight line, `1 regress` |
| `regeval` | `R x → y` | the fitted curve at x, in the original coordinates |
| `regci` | `R x → [lo hi]` | confidence band of the mean response, ŷ ± t s √(b(x)ᵀ(XᵀWX)⁻¹b(x)), transformed back |
| `regpi` | `R x → [lo hi]` | prediction band for a new observation: the same with 1 + b(x)ᵀ(XᵀWX)⁻¹b(x) |
| `rngseed` | `n → –` | seeds the generator (any integer) |
| `rnguniform` | `– → real` | uniform in (0, 1): Park–Miller minimal standard with Schrage's method, the same on every interpreter |
| `rngnormal` | `– → real` | standard normal (Box–Muller) |
| `fgauss` | `{f} a b n → number` | n-point Gauss–Legendre rule, exact for polynomials of degree ≤ 2n − 1; n an integer ≥ 1 |

The result of `regress` is a dictionary. `/model` is the degree (an integer;
`/linear` becomes 1), the transform's name, or `/basis` (the procedure is
then in `/basis`); `/intercept` is null or the fixed constant term as given
(in the space of the fit, so for /power it fixes ln a; it matches pst-fit's
`Yint` only for polynomials without a constant term); `/yoffset` is null or
the offset as given;
`/x`, `/y` and `/weights` (null if none) hold the data as given. `/coef` are
the coefficients in the space of the fit, constant term first (with
`/intercept` it is the fixed value); `/params` is a dictionary of natural
parameters (`/a` `/b` for /power, /exp, /log10, /ln, /recip; `/A` `/mu`
`/sigma` for /gauss; `/coef` for polynomials and bases). `/se` are the
standard errors (0 for a fixed intercept), `/cov` the covariance matrix
s²(XᵀWX)⁻¹ as a matrix. `/n` points, `/k` fitted coefficients, `/dof` = n − k.
`/sse` = Σw e², `/sst` = Σw (Y − Ȳ)², `/ssr` = Σw (Ŷ − Ȳ)² (Y the data in
the space of the fit, Ȳ its weighted mean), `/r2` = 1 − sse/sst, `/adjr2` =
1 − (1 − r2)(n − 1)/dof, `/s` = √(sse/dof) (GLLSR's Syx). `/level` and
`/tval`, the (1 + level)/2 quantile of Student's t with dof degrees of
freedom (from `tinv`). `/fitted` and `/resid` are in the space of the fit;
`/stdresid` are internally studentized residuals √w e/(s√(1 − h)), h the
leverage. Keys starting with `n_` are internal.

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
- `regress` needs more points than fitted coefficients (n > k). With reals
  the coefficients carry about 6 digits; for high degrees or widely spaced
  x, use bignums.
- The random state lives in the dictionary; dvips restores it at the end of
  each page, so seed in the page that uses the numbers.
- With reals, `odesolve` and `fsolve` reach about 5 or 6 digits, the limit
  of single-precision reals; with bignums they reach the working precision.
  `oderk4` has an error that falls with the fourth power of the step.

### Special.ps

Special functions of a number, a bignum or a string. A number gives a real,
computed with bignums at 12 digits; a bignum or a string gives a bignum at
the current precision. Needs bignumlibrary.ps.

```postscript
(0.5) gamma bnPrint                  % +1.7724538509055160273e0   (sqrt pi)
(5) erfc bnPrint                     % +1.5374597944280348502e-12
0.975 norminv =                      % 1.95996
0 (1) besselj bnPrint                % +7.6519768655796655145e-1
```

| Procedure | Stack | Notes |
|---|---|---|
| `gamma` | `x → Γ(x)` | Stirling's series after shifting x up to the precision, reflection for x < 0; exact factorials for whole numbers. 0, −1, −2, … give `undefinedresult` |
| `lngamma` | `x → ln\|Γ(x)\|` | for arguments where Γ itself would be huge |
| `erf` `erfc` | `x → number` | a series of positive terms for small x, a continued fraction for large x; `erfc` keeps all its digits in the tail |
| `normpdf` `normcdf` | `x → number` | density and distribution function of the standard normal distribution |
| `norminv` | `p → x` | the quantile, 0 < p < 1 (else `rangecheck`): Newton's method on ln Φ from Acklam's approximation |
| `besselj` | `n x → Jₙ(x)` | Bessel function of the first kind, integer n (else `typecheck`), \|x\| < 10⁶; the power series with extra digits for the cancellation |
| `digamma` | `x → ψ(x)` | Γ′(x)/Γ(x): asymptotic series after shifting x up, reflection for x < 0; 0, −1, −2, … give `undefinedresult` |
| `betafn` | `a b → B(a,b)` | Γ(a)Γ(b)/Γ(a+b); exact products of factorials when 2a and 2b are whole numbers up to 2000; a or b at a pole gives `undefinedresult`, a + b at a pole gives 0 |
| `lnbeta` | `a b → ln\|B(a,b)\|` | for large arguments |
| `choose` | `n k → C(n,k)` | integers (numbers, bignums or strings of digits) give the exact integer, with every digit even beyond `bnn`; n < 0 by C(n,k) = (−1)ᵏ C(k−n−1,k); k must be below 10⁵ (else `rangecheck`). Other arguments: a product for an integer k, else Γ(n+1)/(Γ(k+1)Γ(n−k+1)) |
| `gammainc` `gammaincc` | `a x → P(a,x)`, `Q(a,x)` | regularized incomplete gamma functions, a > 0, x ≥ 0 (else `rangecheck`); a series for x < a+1, a continued fraction otherwise; Q keeps its digits in the tail |
| `betainc` | `x a b → Iₓ(a,b)` | regularized incomplete beta function, 0 ≤ x ≤ 1, a, b > 0; continued fraction with the symmetry Iₓ(a,b) = 1 − I₁₋ₓ(b,a) |
| `besseli` | `n x → Iₙ(x)` | modified Bessel function, integer n (else `typecheck`), \|x\| < 10⁴ |
| `besselk` | `n x → Kₙ(x)` | modified Bessel function of the second kind, 0 < x < 10⁶; the series (with extra digits for the cancellation) for moderate x, the asymptotic series for x above about 1.2 (bnn + 8); x = 0 gives `undefinedresult` |
| `bessely` | `n x → Yₙ(x)` | Bessel function of the second kind, 0 < x < 10⁶; series or Hankel's asymptotic series, as for `besselk` |
| `tpdf` `tcdf` | `t ν → number` | Student's t distribution, ν > 0 (need not be whole) |
| `tinv` | `p ν → t` | its quantile, 0 < p < 1; closed forms for ν = 1 and 2 |
| `chi2pdf` `chi2cdf` | `x k → number` | χ² distribution with k > 0 degrees of freedom |
| `chi2inv` | `p k → x` | its quantile |
| `fpdf` `fcdf` | `x d₁ d₂ → number` | F distribution |
| `finv` | `p d₁ d₂ → x` | its quantile |
| `exppdf` `expcdf` | `x λ → number` | exponential distribution with rate λ > 0; `expcdf` is accurate for small λx |
| `expinv` | `p λ → x` | −ln(1−p)/λ |
| `binompdf` `binomcdf` | `k n p → number` | binomial distribution: k and n integers, n ≥ 0, 0 ≤ p ≤ 1; the cdf through `betainc` |
| `binominv` | `q n p → k` | the smallest k with P(X ≤ k) ≥ q, an integer (n < 10⁹) |
| `poissonpdf` `poissoncdf` | `k λ → number` | Poisson distribution, λ > 0; the cdf is Q(k+1, λ) |
| `poissoninv` | `q λ → k` | the smallest k with P(X ≤ k) ≥ q, an integer |

Arguments: the argument first, then the parameters. A function gives a
bignum if any argument is a bignum or a string. With numbers only, the t,
χ², F and exponential distributions (density, distribution function and
quantile) and the binomial and Poisson quantiles work in real arithmetic:
about 6 digits (fewer for parameters in the hundreds and more, where
ln Γ is large), in a millisecond or so, fast enough for plots. The other
new functions with numbers give a real computed with bignums at 12 digits,
like gamma, erf and the other special functions. With bignums the quantiles bracket the
root, solve at 12 digits, then refine to `bnn` by Newton's method on the
logarithm of the distribution function (bisection when a step leaves the
bracket). A probability p for a quantile must satisfy 0 < p < 1, else
`rangecheck`; invalid parameters give `rangecheck` too.

Speed with bignums at 20 digits: a distribution function of the t, χ² or F
distribution takes 0.3–1 s (more when the parameters are not whole or
half-whole numbers, which need ln Γ by Stirling's series), a quantile 3–7 s.

A real argument costs about as much as a 20-digit bignum, so a plot of a
special function takes a few seconds rather than a fraction of one.

### Tensor.ps

Tensors of any rank, of reals or bignums. A tensor is a dictionary with
`/shape [d1 … dr]` and `/data`, its elements in row-major order (the last
index runs fastest). As with matrices, a tensor with any bignum or string
element is worked on with bignum arithmetic at the current precision, one of
plain numbers with reals. Indices count from 1; a result of rank 0 is a plain
number or bignum. Needs Matrix.ps; bignumlibrary.ps only for bignums.

```postscript
/A [[1 2] [3 4]] tensor def
/B [[5 6] [7 8]] tensor def
(ij,jk->ik) [A B] teinsum tcvs =     % [19 22; 43 50]
A B touter tshape ==                 % [2 2 2 2]
[1 0 0] [0 1 0] tcross ==            % [0 0 1]
3 tlevi [1 2 3] tget =               % 1
[[(0.1) (0.2)] [(0.3) 4]] tensor tnorm bnPrint   % +4.0174618853201333141e0
```

| Procedure | Stack | Notes |
|---|---|---|
| `tensor` | `[[…] …] → T` | from a nested list; the sublists at each level must have one length, else `rangecheck`. Elements are numbers, bignums or strings |
| `tzeros` | `[d1 … dr] → T` | all zeros |
| `tfill` | `[d1 … dr] x → T` | every element x |
| `tdelta` | `n → T` | n × n Kronecker delta (the identity) |
| `tlevi` | `n → T` | Levi-Civita symbol of rank n, every dimension n: the sign of the permutation, 0 if an index repeats; 1 ≤ n ≤ 6 |
| `tfrommatrix` `ttomatrix` | `M → T`, `T → M` | between matrices and rank-2 tensors; other ranks give `rangecheck` |
| `tolist` | `T → [[…] …]` | the nested list, the inverse of `tensor` |
| `tshape` `trank` `tsize` | `T → [d1 … dr]`, `T → r`, `T → n` | dimensions, rank, number of elements |
| `tget` | `T [i1 … ir] → x` | the element as stored (a string stays a string) |
| `tput` | `T [i1 … ir] x → T′` | a new tensor with that element replaced |
| `tslice` | `T axis k → T′` | index number axis fixed at k: rank r − 1 (a rank-1 tensor gives its k-th element) |
| `tadd` `tsub` `thadamard` | `A B → C` | element by element (sum, difference, product); the shapes must be equal |
| `tscale` | `T s → T′` | s times T |
| `tnorm` | `T → number` | Frobenius norm |
| `touter` | `A B → A⊗B` | outer product, rank rA + rB |
| `tdot` | `A B [a1 …] [b1 …] → C` | product summed over axis a1 of A with axis b1 of B and so on (numpy's tensordot); the remaining axes of A, then of B, form the result |
| `tinner` | `A B → number` | Σ A[i…] B[i…], same shapes |
| `tcontract` | `T i j → T′` | contraction over indices i ≠ j of equal dimension; rank 2 gives a number |
| `ttrace` | `T → number` | Σ T[i i j j …], the full contraction over consecutive pairs of indices of an even-rank tensor; for rank 2 the trace |
| `teinsum` | `(spec) [A B …] → C` | Einstein summation with one-letter indices, as numpy's einsum: `(ij,jk->ik)` matrix product, `(ii)` trace, `(i,i)` dot product, `(i,j->ij)` outer product. Without `->` the output is the indices that appear once, in alphabetical order; no output indices give a number |
| `tpermute` | `T [p1 … pr] → T′` | axis k of the result is axis pₖ of T |
| `ttranspose` | `T → T′` | all axes reversed |
| `tsym` `tantisym` | `T → T′` | symmetric and antisymmetric parts: the average over all permutations of the indices (with their signs for `tantisym`); all dimensions equal, rank at most 6 |
| `tcross` | `u v → u×v` | 3-vectors given as rank-1 tensors or lists of 3; a list if both are lists, else a tensor |
| `ttriple` | `u v w → u·(v×w)` | scalar triple product |
| `tlower` | `T g k → T′` | index k lowered with the metric g (a matrix or rank-2 tensor): T′[…a…] = Σ_b g[a b] T[…b…] |
| `traise` | `T g k → T′` | index k raised with g⁻¹ (`minv` gives `undefinedresult` for a singular g) |
| `tcvs` `tPrint` | `T → string`, `T → –` | rank 1 as `[a, b]`, rank 2 as `[a b; c d]`, higher ranks as the list of slices along the first index; `tPrint` prints a rank-2 tensor one row per line |

Errors: a non-tensor argument gives `typecheck`; a wrong index, axis or
shape gives `rangecheck`. The operations that sum (`teinsum`, `tdot`,
`tcontract`, `ttrace`, `tinner`, `tlower`, `traise`) go through one general
Einstein summation, which takes time proportional to the product of all the
dimensions involved: a product of two 3 × 3 matrices takes under a
millisecond, but one of two 10 × 10 × 10 tensors over one index (10⁵
multiplications) about a second.

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
`dvips/pst-numeric-complex.pro`, `dvips/pst-numeric-calc.pro`, `dvips/pst-numeric-special.pro`,
`doc/pst-numeric-doc.tex`, `doc/pst-numeric-doc.bib`,
`doc/pst-numeric-doc.pdf`, `source/bignumlibrary.ps`, `source/Trig.ps`,
`source/Matrix.ps`, `source/Complex.ps`, `source/Numeric.ps`, `source/Special.ps`,
`source/Load.ps`, `source/make_headers.py`, `source/gs.bat`,
`test/test_bignum.ps`, `test/make_tests.py`, `test/tex-test.sh`,
`test/tex-test.tex`, `examples/showcase.ps`, `examples/showcase.pdf`,
`examples/make_showcase.bat`, `examples/bignumfactorial.ps`,
`tools/make-doc.sh` and `tools/make-ctan.py`.

The history of the changes is in [Changes](Changes).

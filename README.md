# PostScript maths library

A small maths library written in PostScript and run with Ghostscript as a
calculator (no page output). It has five parts:

| File | What it does |
|---|---|
| `bignumlibrary.ps` | Decimal floating-point numbers with as many significant digits as you ask for: arithmetic, comparisons, sqrt, exp, powers, logarithms, trigonometric and hyperbolic functions and their inverses, pi, factorials |
| `Trig.ps` | sin/cos/tan/atan for ordinary PostScript reals using the CORDIC algorithm |
| `Matrix.ps` | Matrices of reals or bignums: build, add, multiply, transpose, determinant, inverse, linear systems, least squares, symmetric eigenvalues |
| `Complex.ps` | Complex numbers of reals or bignums: arithmetic, modulus and argument, sqrt, exp, ln, powers |
| `Numeric.ps` | Roots of functions, integrals, polynomials (values, roots, fitting), gcd and lcm |
| `Load.ps` | Loads all five and opens the library's dictionary |
| `dvips/*.pro` | Each part as a dvips header, for use from TeX (generated) |
| `make_headers.py` | Generates the headers in `dvips/` (Python 3, standard library only) |
| `test_bignum.ps` | Regression tests for all five files |
| `make_tests.py` | Generates `test_bignum.ps` (Python 3, standard library only) |
| [`showcase.pdf`](showcase.pdf) | Every public function with a live result, plus CORDIC plots (11 pages) |
| `showcase.ps`, `make_showcase.bat` | Source of the showcase and the script that builds it |

## Showcase

[showcase.pdf](showcase.pdf) runs every public procedure and typesets the code
next to its result, with a note under each row explaining what it shows. Red
results are errors raised on purpose, to show how each procedure rejects bad
input. It also has a table and plots that
compare the CORDIC functions with Ghostscript's built-in sin and cos. Each
code entry is executed as written while the PDF is built, so the document
always matches the library. To rebuild it after changing the library (about
50 seconds, mostly the bignum integral):

```bat
make_showcase.bat
```

`Examples/bignumfactorial.ps` is a stand-alone program, separate from the
library, that computes 34!. It draws the result on the page, so open it in a
Ghostscript window (`gswin64c Examples\bignumfactorial.ps`) rather than using
the launchers, which turn the page off.

## License

Copyright 2012, 2026 Buddy Ledger.

This work may be distributed and/or modified under the conditions of the
[LaTeX Project Public License](https://www.latex-project.org/lppl/), either
version 1.3c of this license or (at your option) any later version. The full
text is in [LICENSE](LICENSE).

This work has the LPPL maintenance status `author-maintained`. The Current
Maintainer of this work is Buddy Ledger.

This work consists of the files `bignumlibrary.ps`, `Trig.ps`, `Matrix.ps`,
`Complex.ps`, `Numeric.ps`, `Load.ps`, `gs.bat`, `runme.bat`, `test_bignum.ps`, `make_tests.py`,
`make_headers.py`, `dvips/postscript-math-bignum.pro`, `dvips/postscript-math-trig.pro`,
`dvips/postscript-math-matrix.pro`, `dvips/postscript-math-complex.pro`,
`dvips/postscript-math-numeric.pro`,
`showcase.ps`, `showcase.pdf`, `make_showcase.bat`,
`Examples/bignumfactorial.ps` and `README.md`.

## Running

The batch files call Ghostscript 9.52 (`C:\Program Files\gs\gs9.52\bin\gswin64c.exe`)
with `-dNODISPLAY -dNOSAFER`.

```bat
gs.bat Load.ps          :: load the library, then type at the GS> prompt
runme.bat myfile.ps     :: run a file (it can start with (Load.ps) run)
runme.bat test_bignum.ps
```

From PowerShell, use `.\gs.bat` and `.\runme.bat`.

`-dNOSAFER` is required: since 9.50 Ghostscript runs in SAFER mode by default,
which stops `Load.ps` from `run`-ning the other files. It also means any file
run through these launchers can read and write your files, so use them only
for PostScript you trust.

## The library's dictionary

Every name the library defines is in one dictionary, `tx@PostScriptMathDict`,
so nothing clashes with other PostScript code or with your own names. Loading
the library adds only that one name to `userdict`.

`Load.ps` leaves the dictionary open on the dictionary stack, so after
`(Load.ps) run` you can call everything directly, as in the examples below.
Anything you `def` at the top level then goes into the library's dictionary
too, so avoid redefining its names.

If you load a part on its own, or the dvips headers, open the dictionary
yourself:

```postscript
(Matrix.ps) run
tx@PostScriptMathDict begin
  [[1 2] [3 4]] mfromrows mdet =
end
```

## Using it from TeX: dvips headers

`dvips/` has each part as a separate dvips header, so a document loads only
the parts it uses:

| Header | Part | Load these first |
|---|---|---|
| `postscript-math-bignum.pro` | `bignumlibrary.ps` | |
| `postscript-math-trig.pro` | `Trig.ps` | |
| `postscript-math-matrix.pro` | `Matrix.ps` | bignum, for bignum matrices |
| `postscript-math-complex.pro` | `Complex.ps` | matrix; bignum, for bignums |
| `postscript-math-numeric.pro` | `Numeric.ps` | matrix and complex; bignum, for bignums |

A header is its `.ps` file without the comment and blank lines (DSC lines
must not appear in a dvips header). The headers are generated, so don't edit
them: change the `.ps` file and run

```bat
python make_headers.py
```

The test suite runs against the headers too (see [Tests](#tests)). The
`postscript-math-` file names are provisional, until the library has a name
as a TeX package.

## bignumlibrary.ps

### Quick example

```postscript
(Load.ps) run
30 setbnsize                       % 30 significant digits
(2) setbn lnbn bnPrint             % +6.93147180559945309417232121458e-1
1 setbn 3 setbn divbn bnPrint      % +3.33333333333333333333333333333e-1
pibn bnPrint                       % +3.14159265358979323846264338328e0
(1.5) setbn (1.25) setbn gtbn =    % true
```

### Number format

A bignum is a three-element array `[sign digits exponent]`:

- `sign`: boolean, `true` for positive or zero, `false` for negative
- `digits`: a string of ASCII digits, `bnn` long, first digit non-zero unless the value is 0
- `exponent`: integer

The value is `digits × 10^exponent`, with the digits read as a whole number.
With `5 setbnsize`, 509 is stored as `[true (50900) -2]`.

`typchk` returns `(bignumtype)` for anything with this shape.

### Precision and rounding

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

### Procedures

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

### Errors

Errors are raised through `errordict`, the same way built-in operators raise
them, so `stopped` catches them and Ghostscript reports them as, for example,
`Error: /undefinedresult in /divbn`.

### Speed

Arithmetic works one decimal digit at a time. At 20 digits each operation is
instant. At 100 digits, `pibn` takes about 5 s the first time (it's cached
after that) and `sinbn` about 2 s. The full test suite (581 tests) takes
about 30 seconds, mostly for bignum integrals and polynomial roots.

## Trig.ps

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

## Matrix.ps

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

## Complex.ps

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

## Numeric.ps

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

## Tests

```bat
runme.bat test_bignum.ps
```

The file prints a line for each failure and ends with
`N passed, 0 failed / ALL TESTS PASSED`. To see every line, set
`/bnt_verbose true def` near the top. Expected values come from Python's
`decimal` module, computed to 100 digits and rounded half away from zero,
and from exact fractions (`fractions` module) for the matrix and polynomial
results.

`test_bignum.ps` is generated, so don't edit it by hand. To add or change
tests, edit the cases in `make_tests.py` and run it again:

```bat
python make_tests.py
runme.bat test_bignum.ps
```

The script writes `test_bignum.ps` itself. Don't redirect its output with
`>`: in Windows PowerShell 5.1 that writes UTF-16, which Ghostscript can't
read.

The tests normally load the `.ps` files. To test the dvips headers instead,
run `make_headers.py` and then

```bat
"C:\Program Files\gs\gs9.52\bin\gswin64c.exe" -q -dNODISPLAY -dNOSAFER -dBATCH -dPSM_HEADERS test_bignum.ps
```

The first line of output says which were tested. The first section checks
that loading adds only the library's dictionary to `userdict` and leaves the
stacks as they were.

## Changes since version 1.1

- Every name is now defined in `tx@PostScriptMathDict` instead of `userdict`.
  `Load.ps` opens the dictionary, so code that starts with `(Load.ps) run`
  works unchanged.
- Each part is available as a dvips header in `dvips/`, built by
  `make_headers.py`.
- 6 new tests for the namespace (581 in all), and the suite can run against
  the headers.

## Changes in version 1.1 (November 2026)

**Matrix.ps** now stands on its own as a linear algebra library:

- Added `mfromrows`, `mtorows`, `mcopy`, `midentity`, `mtranspose`, `madd`,
  `msub`, `mscale`, `mdet`, `minv`, `msolve`, `mlstsq`, `meigsym` and
  `mPrint`.
- Every operation, including `mmul`, accepts bignum and decimal-string
  elements, for exact decimal results.

**bignumlibrary.ps**: added `sqrtbn`, `expbn`, `powbn`, `atanbn`, `asinbn`,
`acosbn`, `atan2bn`, `sinhbn`, `coshbn`, `tanhbn`, `factbn` and `binombn`.
`typchk` recognises complex numbers, and no longer calls a list of bignums a
matrix.

**New files**: `Complex.ps` (complex numbers) and `Numeric.ps` (roots,
integrals, polynomials, gcd and lcm), both working on reals or bignums.

**Tests and showcase**: 253 new tests (575 in all), and showcase sections for
every new procedure.

## Changes in version 1.0 (November 2026)

**bignumlibrary.ps** was rewritten using the same number format.

- Bugs fixed in 0.5:
  - `subbn` crashed with `rangecheck` and changed the sign of its second argument.
  - `mulbn` returned nothing.
  - `setbn` changed the string passed to it (`(12.5)` became `(1250)`) and left its working variables behind as globals.
  - `setbn` and `addbn` printed debug output on every call.
- Added `divbn`, the six comparisons and `cmpbn`, `negbn`, `absbn`, `truncbn`, `roundbn`, `bniszero`, `bncvs`, `bncvr`, `sinbn`, `cosbn`, `tanbn`, `lnbn`, `log10bn` and `pibn`.
- Default precision changed from 5 to 20 digits.
- `setbn` and the arithmetic procedures no longer print; set `bnDebug true` to see results.
- Removed `tencomp` (only used inside the old `addbn`) and the stray `showpage`.

**Trig.ps** was rewritten from the CORDIC algorithm, with the same procedure
names and results, so the whole work can be licensed under LPPL.

- Fixes the old version's bugs: `corcos` and `cortan` had the wrong sign in two
  of the four quadrants (`4 corcos` gave +0.654 instead of −0.654), and
  `coratan` crashed for x > 0, y < 0.
- `coratan` no longer prints its result, and handles x = 0.
- No longer needs Matrix.ps, and the recursion demos `K` and `Q` are gone.

**Matrix.ps**: removed a stray `showpage` at the end of the file, which added
a blank page to any document that loaded the library.

**Showcase**: added `showcase.ps` and the generated `showcase.pdf`.

**Licensing**: the work is now under LPPL 1.3c, with a notice in each file.

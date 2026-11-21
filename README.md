# PostScript maths library

A small maths library written in PostScript and run with Ghostscript as a
calculator (no page output). It has three parts:

| File | What it does |
|---|---|
| `bignumlibrary.ps` | Decimal floating-point numbers with as many significant digits as you ask for: arithmetic, comparisons, sin/cos/tan, ln/log10, pi |
| `Trig.ps` | sin/cos/tan/atan for ordinary PostScript reals using the CORDIC algorithm |
| `Matrix.ps` | Create matrices, get and set elements, multiply |
| `Load.ps` | Loads all three |
| `test_bignum.ps` | Regression tests for all three files |
| `make_tests.py` | Generates `test_bignum.ps` (Python 3, standard library only) |

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
`Load.ps`, `gs.bat`, `runme.bat`, `test_bignum.ps`, `make_tests.py`,
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
- `sinbn`, `cosbn`, `tanbn`, `lnbn`, `log10bn`, `pibn` work with 6 extra
  digits and then round. Every test value is correct to the last digit, but
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
| `pibn` | `– → bn` | |

pi, ln 2 and ln 10 are computed once per precision and cached.

**Other:** `mergestr` (`(ab) (cd) → (abcd)`), `typchk` (`any → (bignumtype)`,
`(matrixtype)` or the PostScript type name), `bnDebug` (set it `true` to
print each result of `setbn` and the arithmetic procedures).

Procedures whose names start with `bn_` are internal.

### Errors

Errors are raised through `errordict`, the same way built-in operators raise
them, so `stopped` catches them and Ghostscript reports them as, for example,
`Error: /undefinedresult in /divbn`.

### Speed

Arithmetic works one decimal digit at a time. At 20 digits each operation is
instant and the full test suite (322 tests) takes about 5 seconds. At 100 digits, `pibn`
takes about 5 s the first time (it's cached after that) and `sinbn` about 2 s.

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

Matrices are arrays of columns, and indices start at 1.

| Procedure | Stack |
|---|---|
| `marray` | `m n → M` (m rows × n columns, zero-filled) |
| `mput` | `M i j value → –` |
| `mget` | `M i j → value` |
| `msize` | `M → n m` |
| `mmul` | `A B → A×B` (or the string `(Nan)` if the sizes don't match) |

## Tests

```bat
runme.bat test_bignum.ps
```

The file prints a line for each failure and ends with
`N passed, 0 failed / ALL TESTS PASSED`. To see every line, set
`/bnt_verbose true def` near the top. Expected values come from Python's
`decimal` module, computed to 100 digits and rounded half away from zero.

`test_bignum.ps` is generated, so don't edit it by hand. To add or change
tests, edit the cases in `make_tests.py` and run it again:

```bat
python make_tests.py
runme.bat test_bignum.ps
```

The script writes `test_bignum.ps` itself. Don't redirect its output with
`>`: in Windows PowerShell 5.1 that writes UTF-16, which Ghostscript can't
read.

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

**Licensing**: the work is now under LPPL 1.3c, with a notice in each file.

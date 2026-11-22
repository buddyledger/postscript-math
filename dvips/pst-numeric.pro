%!
% pst-numeric.pro: PostScript helpers of the TeX interface of pst-numeric
% Copyright 2026 Buddy Ledger
% LaTeX Project Public License 1.3c or later, see LICENSE
% https://github.com/buddyledger/postscript-math
% The library itself is in pst-numeric-bignum.pro, -trig.pro, -matrix.pro,
% -complex.pro and -calc.pro, which pst-numeric.tex loads as needed.
/tx@NumericDict where { pop }{ /tx@NumericDict 600 dict def } ifelse
tx@NumericDict begin
% s1 s2 -> s1s2
/pstnum_cat {
	1 index length 1 index length add string
	dup 0 4 index putinterval dup 3 index length 3 index putinterval
	3 1 roll pop pop
} bind def
% [a b ...] (sep) -> (a sep b sep ...), each element through pstnum_cvs
/pstnum_join {
	exch () exch true exch {
		3 1 roll { }{ 2 index pstnum_cat } ifelse
		exch pstnum_cvs pstnum_cat false
	} forall
	pop exch pop
} bind def
% [a b ...] -> ([a, b, ...]), for a list that pstnum_cvs would take for a
% complex number or a matrix (a list of two numbers, a list of complex numbers)
/pstnum_list { (, ) pstnum_join ([) exch pstnum_cat (]) pstnum_cat } bind def
% any result -> string: a bignum as +d.ddd...e<exp>, a complex number as
% a + bi, a matrix as [a b; c d], a list as [a, b, c]; strings are kept
/pstnum_cvs {
	dup type /stringtype eq { }{
	/typchk where { pop dup typchk }{ () } ifelse
	dup (bignumtype) eq { pop bncvs }{
	dup (complextype) eq /ccvs where { pop true }{ false } ifelse and { pop ccvs }{
	(matrixtype) eq {
		mtorows [ exch { ( ) pstnum_join } forall ] (; ) pstnum_join
		([) exch pstnum_cat (]) pstnum_cat }{
	dup type /arraytype eq 1 index xcheck not and { pstnum_list }{
	60 string cvs } ifelse } ifelse } ifelse } ifelse } ifelse
} bind def
end

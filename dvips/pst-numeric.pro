%!
% pst-numeric.pro: PostScript helpers of the TeX interface of pst-numeric
% Copyright 2026 Buddy Ledger
% LaTeX Project Public License 1.3c or later, see LICENSE
% https://github.com/buddyledger/pst-numeric
% The library itself is in pst-numeric-bignum.pro, -trig.pro, -matrix.pro,
% -complex.pro and -calc.pro, which pst-numeric.tex loads as needed.
/tx@NumericDict where { pop }{ /tx@NumericDict 1000 dict def } ifelse
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
% a + bi, a matrix as [a b; c d], a list as [a, b, c], a tensor as tcvs
% gives it; strings are kept
/pstnum_cvs {
	dup type /stringtype eq { }{
	/typchk where { pop dup typchk }{ () } ifelse
	dup (tensortype) eq /tcvs where { pop true }{ false } ifelse and { pop tcvs }{
	dup (bignumtype) eq { pop bncvs }{
	dup (complextype) eq /ccvs where { pop true }{ false } ifelse and { pop ccvs }{
	(matrixtype) eq {
		mtorows [ exch { ( ) pstnum_join } forall ] (; ) pstnum_join
		([) exch pstnum_cat (]) pstnum_cat }{
	dup type /arraytype eq 1 index xcheck not and { pstnum_list }{
	60 string cvs } ifelse } ifelse } ifelse } ifelse } ifelse } ifelse
} bind def

% ---------------------------------------------------------------- formatting
% Settings, changed by the keys of the TeX interface (which define them in a
% small dictionary on top of tx@NumericDict for one picture):
%   pstnum_format  /raw (bncvs and cvs, as before), /auto (like %g),
%                  /fixed (pstnum_digits decimals), /sci (pstnum_digits
%                  significant digits, d.ddd e<exp>)
%   pstnum_digits  significant digits (auto, sci) or decimals (fixed)
%   pstnum_trim    drop trailing zeros after the decimal point
%   pstnum_dsep    the decimal separator, a one-character string
%   pstnum_sci     /e (1.5e-3) or /times (1.5 x 10 with a raised -3) when drawn
/pstnum_format /raw def /pstnum_digits 6 def /pstnum_trim false def
/pstnum_dsep (.) def /pstnum_sci /times def
/pstnum_font /Times-Roman def /pstnum_fsize 10 def /pstnum_mathminus true def
/pstnum_delim /bracket def /pstnum_align /decimal def /pstnum_colsep 1 def
/pstnum_rowsep 1.4 def /pstnum_vector /column def /pstnum_label () def
/pstnum_tlabels true def /pstnum_regshow (eq r2 s) def
% x -> real (a bignum or a numeric string becomes a real; for plotting)
/pstnum_real {
	dup type /stringtype eq { cvr }{
	dup type /arraytype eq { bncvr } if } ifelse
} bind def
% digits -> digits without trailing zeros (at least one digit kept)
/pstnum_rz {
	{ dup length 1 le { exit } if
	  dup dup length 1 sub get 48 ne { exit } if
	  0 1 index length 1 sub getinterval } loop
} bind def
% number or bignum or numeric string -> neg (d1d2d3...) e, the value being
% d1.d2d3... x 10^e; zero gives false (0) 0
/pstnum_split {
	6 dict begin
	dup type /stringtype eq /setbn where { pop true }{ false } ifelse and { setbn } if
	dup type /arraytype eq {
		bncvs /s exch def
		/ng s 0 get 45 eq def
		s (e) search pop exch pop /m exch def cvi /e exch def
		m 1 1 getinterval m 3 m length 3 sub getinterval pstnum_cat
		pstnum_rz /d exch def
		d (0) eq { /ng false def /e 0 def } if
		ng d e
	}{
	dup type /integertype eq {
		dup 0 lt /ng exch def abs 20 string cvs /d exch def
		/e d length 1 sub def d pstnum_rz /d exch def
		d (0) eq { /ng false def /e 0 def } if
		ng d e
	}{
		dup 0 eq { pop false (0) 0 }{
		dup 0 lt /ng exch def abs /x exch def
		/e x log floor cvi def
		x 10 e neg exp mul 1e6 mul round
		dup 1e7 ge { 10 div round /e e 1 add def } if
		dup 1e6 lt { 10 mul /e e 1 sub def } if
		cvi 10 string cvs pstnum_rz /d exch def
		ng d e } ifelse
	} ifelse } ifelse
	end
} bind def
% (digits) k -> (k digits, rounded half up) carry   (carry true: the result
% is 1 followed by zeros, one digit position higher)
/pstnum_rnd {
	4 dict begin /k exch def /d exch def
	k d length ge {
		k string dup 0 1 k 1 sub { 48 put dup } for pop
		dup 0 d putinterval false
	}{
		d 0 k getinterval k string copy /r exch def
		d k get 53 ge {
			/c true def
			k 1 sub -1 0 { /i exch def
				r i get 57 eq { r i 48 put }{ r i r i get 1 add put /c false def exit } ifelse
			} for
			c { r 0 49 put } if
			r c
		}{ r false } ifelse
	} ifelse
	end
} bind def
/pstnum_zeros { dup 0 le { pop () }{ string dup 0 1 2 index length 1 sub { 48 put dup } for pop } ifelse } bind def
% neg (int) (frac) -> string with sign, separator, optional trimming
/pstnum_join3 {
	pstnum_trim { pstnum_rz dup (0) eq { pop () } if } if
	dup length 0 gt { pstnum_dsep exch pstnum_cat } if pstnum_cat
	exch { (-) exch pstnum_cat } if
} bind def
% ng digits e q -> fixed notation with q decimals
/pstnum_fixed {
	6 dict begin /q exch def /e exch def /d exch def /ng exch def
	/k e 1 add q add def
	k 0 lt { /d (0) def /e 0 def }{
	k 0 eq { d 0 get 53 ge { /d (1) def /e e 1 add def }{ /d (0) def /e 0 def } ifelse }{
		d k pstnum_rnd { /e e 1 add def } if /d exch def } ifelse } ifelse
	d pstnum_rz (0) eq { /ng false def } if
	e 0 ge {
		d length e 1 add lt { d e 1 add d length sub pstnum_zeros pstnum_cat /d exch def } if
		d 0 e 1 add getinterval
		d e 1 add d length e 1 add sub getinterval
	}{ (0) e neg 1 sub pstnum_zeros d pstnum_cat } ifelse
	% fractional part to exactly q digits
	dup length q lt { q 1 index length sub pstnum_zeros pstnum_cat }{ 0 q getinterval } ifelse
	ng 3 1 roll pstnum_join3
	end
} bind def
% ng digits e p -> (d.ddd e<exp>) with p significant digits
/pstnum_scistr {
	5 dict begin /p exch def /e exch def /d exch def /ng exch def
	p 1 lt { /p 1 def } if
	d p pstnum_rnd { /e e 1 add def } if /d exch def
	d pstnum_rz (0) eq { /e 0 def /ng false def } if
	ng d 0 1 getinterval d 1 d length 1 sub getinterval pstnum_join3
	(e) pstnum_cat e 12 string cvs pstnum_cat
	end
} bind def
% number, bignum or numeric string -> string in the current format
/pstnum_fmtnum {
	pstnum_format /raw eq { pstnum_cvs }{
	pstnum_split
	pstnum_format /fixed eq { pstnum_digits pstnum_fixed }{
	pstnum_format /sci eq { pstnum_digits pstnum_scistr }{
		% auto: %g with pstnum_digits significant digits, trailing zeros dropped
		6 dict begin /e exch def /d exch def /ng exch def
		/p pstnum_digits 1 lt { 1 }{ pstnum_digits } ifelse def
		d p pstnum_rnd { /e e 1 add def } if pstnum_rz /d exch def
		/pstnum_trim true def
		e -4 lt e p ge or { ng d e p pstnum_scistr }{ ng d e p 1 sub e sub pstnum_fixed } ifelse
		end
	} ifelse } ifelse } ifelse
} bind def
% z -> string a + bi in the current format (a zero part is left out)
/pstnum_fmtc {
	aload pop 2 dict begin /im exch def /re exch def
	im pstnum_split pop pop /imneg exch def
	im pstnum_fmtnum dup (0) eq { pop () } if
	dup length 0 gt { imneg { 1 1 index length 1 sub getinterval } if (i) pstnum_cat } if
	/ims exch def
	re pstnum_fmtnum dup (0) eq ims length 0 gt and { pop () } if
	dup length 0 eq { pop ims imneg { (-) exch pstnum_cat } if dup length 0 eq { pop (0) } if }{
		ims length 0 gt { imneg { ( - ) }{ ( + ) } ifelse pstnum_cat ims pstnum_cat } if } ifelse
	end
} bind def
% any element (number, bignum, string, complex) -> string
/pstnum_fmtany {
	dup type /arraytype eq { dup length 2 eq }{ false } ifelse
	{ pstnum_fmtc }{ pstnum_fmtnum } ifelse
} bind def
% (1.5e-3) -> rich text for drawing: 1.5 x 10^{-3} when pstnum_sci is /times
% (an e counts only between a digit and an exponent, so words are kept)
/pstnum_scirich {
	pstnum_sci /times eq {
	6 dict begin /s exch def /o () def /i 0 def
	{ i s length ge { exit } if
	  /c s i get def
	  c 101 eq i 0 gt and { s i 1 sub get dup 48 ge exch 57 le and }{ false } ifelse {
		/j i 1 add def
		j s length lt { s j get 45 eq { /j j 1 add def } if } if
		/j0 j def
		{ j s length ge { exit } if s j get dup 48 ge exch 57 le and not { exit } if /j j 1 add def } loop
		j j0 gt {
			/o o (\001\26410^{) pstnum_cat s i 1 add j i sub 1 sub getinterval pstnum_cat (}) pstnum_cat def
			/i j def
		}{ /o o s i 1 getinterval pstnum_cat def /i i 1 add def } ifelse
	  }{ /o o s i 1 getinterval pstnum_cat def /i i 1 add def } ifelse
	} loop
	o end
	} if
} bind def

% ---------------------------------------------------------------- drawing
% Rich text: ^{...} raised, _{...} lowered (smaller, not nested), \001 c draws
% the character c from the Symbol font, - is drawn as a minus sign when
% pstnum_mathminus is true. (text) bool -> width; true draws at the current
% point and moves past the text, false only measures.
/pstnum_rich {
	8 dict begin /dr exch def /s exch def /w 0 def /i 0 def /sz 1 def /dy 0 def
	{ i s length ge { exit } if
	  /c s i get def /f pstnum_font def
	  c 94 eq c 95 eq or { i 1 add s length lt { s i 1 add get 123 eq }{ false } ifelse }{ false } ifelse {
		/sz 0.7 def /dy c 94 eq { 0.45 }{ -0.25 } ifelse def /i i 2 add def
	  }{
	  c 125 eq sz 1 ne and { /sz 1 def /dy 0 def /i i 1 add def }{
		c 1 eq i 1 add s length lt and { /f /Symbol def /i i 1 add def /c s i get def } if
		c 45 eq pstnum_mathminus and f /Symbol ne and { /f /Symbol def } if
		f findfont pstnum_fsize sz mul scalefont setfont
		( ) dup 0 c put
		dr { 0 dy pstnum_fsize mul rmoveto dup show 0 dy pstnum_fsize mul neg rmoveto } if
		stringwidth pop w add /w exch def
		/i i 1 add def
	  } ifelse } ifelse
	} loop
	w end
} bind def
% a formatted number -> rich text
/pstnum_r { pstnum_scirich } bind def
% rows (a list of lists of formatted strings) -> draws them as a matrix
% centred vertically on the math axis through the current point, with
% delimiters, and moves the current point past it
/pstnum_grid {
	28 dict begin /rows exch def
	/fs pstnum_fsize def /nr rows length def /nc 0 def
	rows { length dup nc gt { /nc exch def }{ pop } ifelse } forall
	/L nc array def /R nc array def
	0 1 nc 1 sub { dup L exch 0 put R exch 0 put } for
	% each cell -> [left right] in rich text; right is empty unless aligned at the separator
	/cells [ rows { [ exch { pstnum_r
		pstnum_align /decimal eq {
			/cs0 exch def
			cs0 pstnum_dsep search { 3 1 roll exch pstnum_cat }{ pop cs0 () } ifelse
		}{ () } ifelse
		2 array astore } forall ] } forall ] def
	0 1 nr 1 sub { /r exch def
		cells r get /row exch def
		0 1 row length 1 sub { /k exch def
			row k get aload pop
			false pstnum_rich dup R k get gt { R exch k exch put }{ pop } ifelse
			false pstnum_rich dup L k get gt { L exch k exch put }{ pop } ifelse
		} for
	} for
	/W [ 0 1 nc 1 sub { dup L exch get exch R exch get add } for ] def
	/h fs pstnum_rowsep mul def /H nr h mul def
	currentpoint /y0 exch def /x0 exch def
	/cy y0 fs 0.3 mul add def
	/top cy H 2 div add def /bot cy H 2 div sub def
	/dw pstnum_delim /none eq { 0 }{ fs 0.35 mul } ifelse def
	/gap pstnum_delim /none eq { 0 }{ fs 0.3 mul } ifelse def
	/cs fs pstnum_colsep mul def
	/xr x0 dw 2 mul add gap 2 mul add W { add } forall nc 1 sub 0 max cs mul add def
	gsave newpath fs 0.05 mul setlinewidth 1 setlinecap 0 setlinejoin
	pstnum_delim /bracket eq {
		x0 dw add top moveto x0 top lineto x0 bot lineto x0 dw add bot lineto stroke
		xr dw sub top moveto xr top lineto xr bot lineto xr dw sub bot lineto stroke } if
	pstnum_delim /paren eq {
		x0 dw add top moveto x0 dw 0.2 mul sub top H 0.25 mul sub x0 dw 0.2 mul sub bot H 0.25 mul add
		x0 dw add bot curveto stroke
		xr dw sub top moveto xr dw 0.2 mul add top H 0.25 mul sub xr dw 0.2 mul add bot H 0.25 mul add
		xr dw sub bot curveto stroke } if
	pstnum_delim /bar eq {
		x0 dw 2 div add top moveto 0 bot top sub rlineto stroke
		xr dw 2 div sub top moveto 0 bot top sub rlineto stroke } if
	pstnum_delim /dbar eq {
		x0 dw 0.2 mul add top moveto 0 bot top sub rlineto stroke
		x0 dw 0.7 mul add top moveto 0 bot top sub rlineto stroke
		xr dw 0.2 mul sub top moveto 0 bot top sub rlineto stroke
		xr dw 0.7 mul sub top moveto 0 bot top sub rlineto stroke } if
	grestore
	0 1 nr 1 sub { /r exch def
		/yb top r h mul sub h 2 div sub fs 0.33 mul sub def
		/xc x0 dw add gap add def
		cells r get /row exch def
		0 1 nc 1 sub { /k exch def
			k row length lt {
				row k get aload pop /rt exch def /lf exch def
				/wl lf false pstnum_rich def /wr rt false pstnum_rich def
				pstnum_align /decimal eq { xc L k get add wl sub }{
				pstnum_align /left eq { xc }{
				pstnum_align /center eq { xc W k get wl sub 2 div add }{
					xc W k get add wl sub } ifelse } ifelse } ifelse
				yb moveto lf true pstnum_rich pop rt true pstnum_rich pop
			} if
			/xc xc W k get add cs add def
		} for
	} for
	xr y0 moveto
	end
} bind def
% (label) -> draws "label = " at the current point, if the label is not empty
/pstnum_drawlabel {
	dup length 0 gt { ( = ) pstnum_cat true pstnum_rich pop }{ pop } ifelse
} bind def
% data offset nrows ncols -> rows of formatted strings (a slice of a tensor)
/pstnum_trows {
	5 dict begin /q exch def /p exch def /o exch def /dt exch def
	[ 0 1 p 1 sub { /i exch def
		[ 0 1 q 1 sub { dt exch o add i q mul add get pstnum_fmtany } for ] } for ]
	end
} bind def
% any result -> draws it at the current point and moves past it: a matrix
% or a tensor of rank 2 with delimiters, a list of numbers (or a tensor of
% rank 1) as a column or row vector, a tensor of rank 3 as its slices side
% by side, of rank 4 as a grid of slices, anything else as text
/pstnum_mdraw {
	20 dict begin /obj exch def
	pstnum_format /raw eq { /pstnum_format /auto def } if
	pstnum_label pstnum_drawlabel
	/typchk where { pop obj typchk }{ obj type 20 string cvs } ifelse /ty exch def
	ty (tensortype) eq {
		/sh obj /shape get def /dt obj /data get def
		sh length 1 eq { /ty (vector) def /obj dt def } if
		sh length 2 eq { dt 0 sh 0 get sh 1 get pstnum_trows pstnum_grid } if
		sh length 3 eq sh length 4 eq or {
			/p sh sh length 2 sub get def /q sh sh length 1 sub get def
			/n1 sh length 4 eq { sh 0 get }{ 1 } ifelse def
			/n2 sh length 4 eq { sh 1 get }{ sh 0 get } ifelse def
			/fs pstnum_fsize def
			/hh fs pstnum_rowsep mul p mul fs 2 mul add def
			currentpoint /ty0 exch def /tx0 exch def /txmax tx0 def
			1 1 n1 { /a exch def
				/yrow ty0 n1 1 add 2 div a sub hh mul add def
				tx0 yrow moveto
				1 1 n2 { /b exch def
					pstnum_tlabels {
						currentpoint
						gsave
						1 index yrow fs 0.3 mul add fs pstnum_rowsep mul p mul 2 div add fs 0.45 mul add moveto
						/pstnum_fsize fs 0.7 mul def
						sh length 4 eq { (\() a 3 string cvs pstnum_cat (,) pstnum_cat b 3 string cvs pstnum_cat (,:,:\)) pstnum_cat }
						{ (\() b 3 string cvs pstnum_cat (,:,:\)) pstnum_cat } ifelse
						true pstnum_rich pop
						/pstnum_fsize fs def
						grestore
						moveto
					} if
					dt a 1 sub n2 mul b 1 sub add p q mul mul p q pstnum_trows pstnum_grid
					fs 0.8 mul 0 rmoveto
				} for
				currentpoint pop dup txmax gt { /txmax exch def }{ pop } ifelse
			} for
			txmax ty0 moveto
		} if
		sh length 4 gt { obj pstnum_cvs true pstnum_rich pop } if
	} if
	ty (matrixtype) eq {
		[ obj mtorows { [ exch { pstnum_fmtany } forall ] } forall ] pstnum_grid
	} if
	ty (vector) eq ty (arraytype) eq obj type /arraytype eq and obj xcheck not and or {
		pstnum_vector /row eq { [ [ obj { pstnum_fmtany } forall ] ] }{ [ obj { [ exch pstnum_fmtany ] } forall ] } ifelse
		pstnum_grid
	} if
	ty (matrixtype) ne ty (tensortype) ne and ty (vector) ne and ty (arraytype) ne and {
		obj pstnum_fmtany pstnum_r true pstnum_rich pop } if
	end
} bind def
% a result -> draws it as text in the current format (rich text, so that
% 1.5e-3 is drawn as 1.5 x 10^-3 with pstnum_sci /times)
/pstnum_textdraw {
	pstnum_format /raw eq { pstnum_font findfont pstnum_fsize scalefont setfont pstnum_cvs show }{
		/typchk where { pop dup typchk }{ dup type 20 string cvs } ifelse
		dup (bignumtype) eq 1 index (complextype) eq or 1 index (stringtype) eq or
		1 index (integertype) eq or exch (realtype) eq or
		{ pstnum_fmtany }{ pstnum_cvs } ifelse
		pstnum_r true pstnum_rich pop
	} ifelse
} bind def
% ---------------------------------------------------------------- regression
% ys R -> x1 y1 x2 y2 ... as reals (R's x values with the given list), for
% \listplot
/pstnum_xy {
	3 dict begin /x get /xs exch def /ys exch def
	0 1 xs length 1 sub { dup xs exch get pstnum_real exch ys exch get pstnum_real } for
	end
} bind def
% (s) -> ( + s) or ( - s without its sign)
/pstnum_term {
	dup length 0 gt { dup 0 get 45 eq }{ false } ifelse
	{ 1 1 index length 1 sub getinterval ( - ) exch pstnum_cat }{ ( + ) exch pstnum_cat } ifelse
} bind def
% R -> the fitted equation as rich text
/pstnum_regeq {
	8 dict begin /R exch def /md R /model get def /cf R /coef get def
	/pr R /params known { R /params get }{ 0 dict } ifelse def
	/v { pstnum_fmtnum } def
	/pv { pr exch get v } def
	md type /integertype eq md /linear eq or {
		/dg md /linear eq { 1 }{ md } ifelse def
		(y = )
		0 1 cf length 1 sub { /j exch def
			/c cf j get v def
			/xp j 0 eq { () }{ j 1 eq { (x) }{ (x^{) j 3 string cvs pstnum_cat (}) pstnum_cat } ifelse } ifelse def
			j 0 gt c (1) eq and { /c () def } if
			j 0 gt c (-1) eq and { /c (-) def } if
			c (0) eq cf length 1 gt and { }{
				c xp pstnum_cat 1 index (y = ) eq { pstnum_cat }{ pstnum_term pstnum_cat } ifelse } ifelse
		} for
	}{
	md /power eq { (y = ) /a pv pstnum_cat (\001\327x^{) pstnum_cat /b pv pstnum_cat (}) pstnum_cat }{
	md /exp eq { (y = ) /a pv pstnum_cat (\001\327e^{) pstnum_cat /b pv pstnum_cat (x}) pstnum_cat }{
	md /log10 eq md /ln eq or md /recip eq or {
		(y = ) cf 0 get v pstnum_cat cf 1 get v
		md /log10 eq { ( log x) }{ md /ln eq { ( ln x) }{ (/x) } ifelse } ifelse pstnum_cat
		pstnum_term pstnum_cat }{
	md /gauss eq {
		(y = ) /A pv pstnum_cat (\001\327exp\(-\(x) pstnum_cat
		/mu pv dup length 0 gt { dup 0 get 45 eq }{ false } ifelse
		{ 1 1 index length 1 sub getinterval ( + ) exch pstnum_cat }{ ( - ) exch pstnum_cat } ifelse pstnum_cat
		(\)^{2}/) pstnum_cat
		pr /sigma get dup type /arraytype eq { dup mulbn (2) setbn mulbn }{ dup mul 2 mul } ifelse v pstnum_cat
		(\)) pstnum_cat }{
		(y = \001S c_{j} b_{j}\(x\)) } ifelse } ifelse } ifelse } ifelse } ifelse
	end
} bind def
% R -> draws the lines that pstnum_regshow names, one below the other,
% starting at the current point
/pstnum_regdraw {
	12 dict begin /R exch def
	pstnum_format /raw eq { /pstnum_format /auto def /pstnum_digits 4 def } if
	/v { pstnum_fmtnum pstnum_r } def
	/rs pstnum_regshow def
	/lines [
	{ rs length 0 eq { exit } if
	  rs ( ) search { exch pop exch /rs exch def }{ /rs () def } ifelse
	  /wd exch def
	  wd (eq) eq { R pstnum_regeq } if
	  wd (r2) eq { (r^{2} = ) R /r2 get v pstnum_cat } if
	  wd (adjr2) eq { (r^{2}_{adj} = ) R /adjr2 get v pstnum_cat } if
	  wd (s) eq { (s = ) R /s get v pstnum_cat } if
	  wd (n) eq { (n = ) R /n get v pstnum_cat } if
	  wd (dof) eq { (dof = ) R /dof get v pstnum_cat } if
	  wd (sse) eq { (SSE = ) R /sse get v pstnum_cat } if
	  wd (tval) eq { (t = ) R /tval get v pstnum_cat } if
	  wd (coef) eq {
		0 1 R /coef get length 1 sub { /j exch def
			(c_{) j 3 string cvs pstnum_cat (} = ) pstnum_cat R /coef get j get v pstnum_cat
			R /se known { ( \001\261 ) pstnum_cat R /se get j get v pstnum_cat } if
		} for } if
	  wd (params) eq { R /params get /pm exch def
		[ [/a (a)] [/b (b)] [/A (A)] [/mu (\001m)] [/sigma (\001s)] ] {
			aload pop exch dup pm exch known { pm exch get v exch ( = ) pstnum_cat exch pstnum_cat }{ pop pop } ifelse
		} forall } if
	} loop
	] def
	currentpoint /y0 exch def /x0 exch def
	0 1 lines length 1 sub { /j exch def
		x0 y0 j pstnum_fsize mul 1.4 mul sub moveto lines j get true pstnum_rich pop
	} for
	end
} bind def
end

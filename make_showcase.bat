@REM Copyright 2026 Buddy Ledger - LaTeX Project Public License 1.3c or later, see LICENSE
@REM Builds showcase.pdf from showcase.ps (takes about 15 seconds)
@"C:\Program Files\gs\gs9.52\bin\gswin64c.exe" -q -dNOSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=showcase.pdf showcase.ps

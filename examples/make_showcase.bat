@REM Copyright 2026 Buddy Ledger - LaTeX Project Public License 1.3c or later, see LICENSE
@REM Builds showcase.pdf from showcase.ps (takes about 50 seconds).
@REM Runs in source/, because Load.ps loads the parts from the current folder.
@pushd "%~dp0..\source"
@"C:\Program Files\gs\gs9.52\bin\gswin64c.exe" -q -dNOSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=../examples/showcase.pdf ../examples/showcase.ps
@popd

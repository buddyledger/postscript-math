#!/usr/bin/env python3
# Copyright 2026 Buddy Ledger
# LaTeX Project Public License 1.3c or later, see LICENSE
"""Builds build/pst-numeric.zip, the archive for CTAN.

    python tools/make-ctan.py

The archive has one top-level folder, pst-numeric/, with the files a TeX
distribution installs (tex/, latex/, dvips/), the manual (doc/), the sources
of the generated headers (source/), README and Changes. The tests, the
showcase and the repository's own files are left out.

It checks what CTAN checks too: the manual's PDF is there, no hidden or
temporary files, no file is empty, and the version in tex/pst-numeric.tex
agrees with latex/pst-numeric.sty and Changes. Exits with an error if not.
Needs only the Python standard library.
"""
import re
import sys
import zipfile
from pathlib import Path

PKG = "pst-numeric"
root = Path(__file__).resolve().parent.parent

FILES = [
    "README",
    "Changes",
    "doc/pst-numeric-doc.tex",
    "doc/pst-numeric-doc.bib",
    "doc/pst-numeric-doc.pdf",
    "dvips/pst-numeric.pro",
    "dvips/pst-numeric-bignum.pro",
    "dvips/pst-numeric-trig.pro",
    "dvips/pst-numeric-matrix.pro",
    "dvips/pst-numeric-complex.pro",
    "dvips/pst-numeric-calc.pro",
    "latex/pst-numeric.sty",
    "tex/pst-numeric.tex",
    "source/bignumlibrary.ps",
    "source/Trig.ps",
    "source/Matrix.ps",
    "source/Complex.ps",
    "source/Numeric.ps",
    "source/Load.ps",
    "source/make_headers.py",
]

errors = []


def check(ok, message):
    if not ok:
        errors.append(message)


for name in FILES:
    path = root / name
    check(path.is_file(), f"missing: {name}")
    if path.is_file():
        check(path.stat().st_size > 0, f"empty: {name}")

tex = (root / "tex/pst-numeric.tex").read_text(encoding="utf-8")
version = re.search(r"\\def\\fileversion\{([^}]*)\}", tex).group(1)
date = re.search(r"\\def\\filedate\{([^}]*)\}", tex).group(1)
sty = (root / "latex/pst-numeric.sty").read_text(encoding="utf-8")
check(f"[{date} v{version} " in sty,
      f"latex/pst-numeric.sty: \\ProvidesPackage should say [{date} v{version} ...]")
changes = (root / "Changes").read_text(encoding="utf-8")
check(re.search(rf"^{re.escape(version)}\b", changes, re.M) is not None,
      f"Changes has no entry for version {version}")
pdf = root / "doc/pst-numeric-doc.pdf"
if pdf.is_file() and (root / "doc/pst-numeric-doc.tex").is_file():
    check(pdf.read_bytes()[:5] == b"%PDF-", "doc/pst-numeric-doc.pdf is not a PDF")

if errors:
    for e in errors:
        print("error:", e)
    sys.exit(1)

out = root / "build" / f"{PKG}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name in FILES:
        info = zipfile.ZipInfo(f"{PKG}/{name}", date_time=tuple(int(x) for x in date.split("/")) + (0, 0, 0))
        info.external_attr = 0o644 << 16          # plain files, not executable
        info.compress_type = zipfile.ZIP_DEFLATED
        data = (root / name).read_bytes()
        if not name.endswith(".pdf"):
            data = data.replace(b"\r\n", b"\n")   # LF line ends, as CTAN prefers
        z.writestr(info, data)

print(f"wrote {out.relative_to(root).as_posix()} ({out.stat().st_size} bytes), "
      f"{PKG} {version} ({date}), {len(FILES)} files:")
for name in FILES:
    print(f"  {PKG}/{name}")

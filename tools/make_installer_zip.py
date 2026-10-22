#!/usr/bin/env python3
"""Pack the hosted installer into a .zip for the website download button.

Browsers (Chrome, Edge) often block or hide a bare .bat download; a .zip of the
same file gets through. The zip is byte-for-byte reproducible (fixed timestamp),
so rebuilding it from an unchanged .bat gives an identical file.

Run after copying a new Install-Prontera.bat into website/downloads/:
    python3 tools/make_installer_zip.py          -> website/downloads/Install-Prontera.zip
    python3 tools/make_installer_zip.py --check  -> exit 1 if the zip is missing or stale
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

DOWNLOADS = Path(__file__).resolve().parent.parent / "website" / "downloads"
BAT = DOWNLOADS / "Install-Prontera.bat"
ZIP = DOWNLOADS / "Install-Prontera.zip"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def build() -> bytes:
    info = zipfile.ZipInfo(BAT.name, date_time=FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(info, BAT.read_bytes(), compresslevel=9)
    return buf.getvalue()


def main() -> int:
    data = build()
    if "--check" in sys.argv[1:]:
        if not ZIP.exists() or ZIP.read_bytes() != data:
            print(f"{ZIP.name} is missing or out of date: run python3 tools/make_installer_zip.py")
            return 1
        print(f"{ZIP.name} matches {BAT.name}")
        return 0
    ZIP.write_bytes(data)
    print(f"wrote {ZIP} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

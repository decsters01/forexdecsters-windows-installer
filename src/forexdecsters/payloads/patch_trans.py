#!/usr/bin/env python3
"""Patch trans.sh so Windows setup disables account lockout."""

from __future__ import annotations

import sys
from pathlib import Path

NEEDLE = "download $confhome/windows.xml /tmp/autounattend.xml"
CALL = "    forexdecsters_apply_lockout"

FUNC = r"""
forexdecsters_apply_lockout() {
    f=/tmp/autounattend.xml
    [ -f "$f" ] || return 0
    grep -q 'lockoutthreshold' "$f" && return 0
    sed -i 's|<Path>reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ReserveManager /v ShippedWithReserves /t REG_DWORD /d 0 /f</Path>|<Path>cmd /c "net accounts /lockoutthreshold:0 \&amp; reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ReserveManager /v ShippedWithReserves /t REG_DWORD /d 0 /f"</Path>|' "$f"
}
"""


def patch_trans_script(text: str) -> str:
    if "forexdecsters_apply_lockout" in text:
        return text
    if NEEDLE not in text:
        raise ValueError("could not find windows.xml download in trans.sh")
    text = text.replace(NEEDLE, NEEDLE + "\n" + CALL, 1)
    lines = text.splitlines(True)
    insert_at = 1 if lines and lines[0].startswith("#!") else 0
    lines.insert(insert_at, FUNC + "\n")
    return "".join(lines)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_trans.py <trans.sh>")
    path = Path(sys.argv[1])
    original = path.read_text(encoding="utf-8", errors="replace")
    path.write_text(patch_trans_script(original), encoding="utf-8")


if __name__ == "__main__":
    main()

# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files

project = Path(SPECPATH)

datas = collect_data_files("forexdecsters")
binaries = []
hiddenimports = [
    "forexdecsters",
    "forexdecsters.cli",
    "forexdecsters.payloads",
    "forexdecsters.payloads.patch_trans",
]

for package in (
    "forexdecsters",
    "paramiko",
    "cryptography",
    "nacl",
    "bcrypt",
    "rich",
    "typer",
    "click",
    "shellingham",
):
    try:
        extra_datas, extra_binaries, extra_hidden = collect_all(package)
    except Exception:
        continue
    datas += extra_datas
    binaries += extra_binaries
    hiddenimports += extra_hidden

a = Analysis(
    [str(project / "src" / "forexdecsters" / "__main__.py")],
    pathex=[str(project / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="forexdecsters-windows-installer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

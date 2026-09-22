$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
py -3 -m pip install -e ".[dev]" pyinstaller
py -3 -m PyInstaller --noconfirm --clean forexdecsters.spec
Write-Host "exe: $(Resolve-Path .\dist\forexdecsters-windows-installer.exe)"

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_SSH_PORT = 22
DEFAULT_RDP_PORT = 3389
DEFAULT_WINDOWS_USERNAME = "Administrator"
IMAGE_NAME = "Windows Server 2019 ServerDatacenter"
REINSTALL_URL = "https://raw.githubusercontent.com/bin456789/reinstall/main/reinstall.sh"
MIN_RAM_MB = 1024
MIN_DISK_GB = 25


@dataclass(frozen=True)
class SshTarget:
    host: str
    port: int
    username: str
    password: str


@dataclass(frozen=True)
class WindowsAccount:
    username: str
    password: str
    rdp_port: int
    iso_url: str | None = None


@dataclass(frozen=True)
class InstallRequest:
    ssh: SshTarget
    windows: WindowsAccount
    dry_run: bool = False

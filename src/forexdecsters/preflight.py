from __future__ import annotations

from forexdecsters.models import MIN_DISK_GB, MIN_RAM_MB
from forexdecsters.ssh import RemoteError, RemoteSession

PREFLIGHT_SCRIPT = r"""
set -e
if command -v cmd.exe >/dev/null 2>&1 || [ -d /cygdrive ]; then
    echo 'ERR=target is Windows; this installer starts from Linux'
    exit 2
fi
arch=$(uname -m)
if [ "$arch" != "x86_64" ]; then
    echo "ERR=architecture $arch is not supported (need x86_64)"
    exit 2
fi
virt=unknown
if command -v systemd-detect-virt >/dev/null 2>&1; then
    virt=$(systemd-detect-virt || true)
fi
case "$virt" in
    openvz|lxc|docker|container-other)
        echo "ERR=virtualization $virt is not supported (need KVM/QEMU)"
        exit 2
        ;;
esac
if command -v hostnamectl >/dev/null 2>&1; then
    if hostnamectl | grep -qiE 'openvz|lxc'; then
        echo 'ERR=OpenVZ/LXC is not supported'
        exit 2
    fi
fi
uid=$(id -u)
ram_kb=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
ram_mb=$((ram_kb / 1024))
disk_b=$(lsblk -dbn -o SIZE,TYPE 2>/dev/null | awk '$2=="disk" {if ($1>max) max=$1} END {print max+0}')
disk_gb=$((disk_b / 1024 / 1024 / 1024))
disk_count=$(lsblk -dn -o TYPE 2>/dev/null | grep -c '^disk$' || true)
echo "ARCH=$arch"
echo "VIRT=$virt"
echo "UID=$uid"
echo "RAM_MB=$ram_mb"
echo "DISK_GB=$disk_gb"
echo "DISK_COUNT=$disk_count"
if ! command -v python3 >/dev/null 2>&1; then
    echo 'ERR=python3 is required on the VPS'
    exit 2
fi
if ! command -v curl >/dev/null 2>&1; then
    echo 'ERR=curl is required on the VPS'
    exit 2
fi
echo OK
"""


def run_preflight(session: RemoteSession) -> dict[str, str]:
    output = session.run(f"bash -s <<'FOREXDECSTERS_PREFLIGHT'\n{PREFLIGHT_SCRIPT}\nFOREXDECSTERS_PREFLIGHT")
    values: dict[str, str] = {}
    for line in output.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    if "ERR" in values:
        raise RemoteError(values["ERR"])
    if values.get("UID") != "0":
        raise RemoteError("SSH user is not root. Connect as root for this MVP.")
    ram_mb = int(values.get("RAM_MB") or "0")
    if ram_mb < MIN_RAM_MB:
        raise RemoteError(f"RAM {ram_mb} MB is below the {MIN_RAM_MB} MB minimum.")
    disk_gb = int(values.get("DISK_GB") or "0")
    if disk_gb < MIN_DISK_GB:
        raise RemoteError(f"Disk {disk_gb} GB is below the {MIN_DISK_GB} GB minimum.")
    if int(values.get("DISK_COUNT") or "0") > 1:
        raise RemoteError("Multiple disks found. Use a VPS with a single disk for the MVP.")
    return values

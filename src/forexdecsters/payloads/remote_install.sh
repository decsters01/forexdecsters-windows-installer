#!/bin/bash
# Runs on the Linux VPS. Downloads reinstall.sh, injects lockout disable, starts Windows install.
set -euo pipefail

ENV_FILE="${FOREXDECSTERS_ENV:-/tmp/forexdecsters.env}"
PATCH_TRANS="${FOREXDECSTERS_PATCH_TRANS:-/tmp/forexdecsters_patch_trans.py}"
REINSTALL_URL="${FOREXDECSTERS_REINSTALL_URL:-https://raw.githubusercontent.com/bin456789/reinstall/main/reinstall.sh}"
IMAGE_NAME="${FOREXDECSTERS_IMAGE_NAME:-Windows Server 2019 ServerDatacenter}"

if [ ! -f "$ENV_FILE" ]; then
    echo "forexdecsters: missing env file $ENV_FILE" >&2
    exit 1
fi
# shellcheck disable=SC1090
set -a
. "$ENV_FILE"
set +a

if [ -z "${FD_WIN_USER:-}" ] || [ -z "${FD_WIN_PASS:-}" ] || [ -z "${FD_RDP_PORT:-}" ]; then
    echo "forexdecsters: FD_WIN_USER, FD_WIN_PASS and FD_RDP_PORT are required" >&2
    exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
    echo "forexdecsters: must run as root" >&2
    exit 1
fi

echo "forexdecsters: downloading reinstall.sh"
curl -fsSL "$REINSTALL_URL" -o /tmp/reinstall.sh
chmod +x /tmp/reinstall.sh

python3 - <<'PY'
from pathlib import Path

path = Path("/tmp/reinstall.sh")
text = path.read_text(encoding="utf-8", errors="replace")
needle = "curl -Lo $initrd_dir/trans.sh $confhome/trans.sh"
hook = needle + '\npython3 /tmp/forexdecsters_patch_trans.py "$initrd_dir/trans.sh"'
if "forexdecsters_patch_trans.py" not in text:
    if needle not in text:
        raise SystemExit("could not find trans.sh download in reinstall.sh")
    path.write_text(text.replace(needle, hook, 1), encoding="utf-8")
print("forexdecsters: patched reinstall.sh to disable Windows lockout")
PY

if [ ! -f "$PATCH_TRANS" ]; then
    echo "forexdecsters: missing $PATCH_TRANS" >&2
    exit 1
fi

cmd=(bash /tmp/reinstall.sh windows
    --image-name "$IMAGE_NAME"
    --lang en
    --username "$FD_WIN_USER"
    --password "$FD_WIN_PASS"
    --rdp-port "$FD_RDP_PORT"
)
if [ -n "${FD_ISO_URL:-}" ]; then
    cmd+=(--iso "$FD_ISO_URL")
fi

echo "forexdecsters: starting Windows Server 2019 ServerDatacenter install"
"${cmd[@]}"

rm -f "$ENV_FILE"
echo "forexdecsters: reinstall prepared, rebooting"
sync
reboot

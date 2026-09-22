from __future__ import annotations

import re
import secrets
import string
import sys
from importlib.resources import files
from pathlib import Path

from forexdecsters.models import IMAGE_NAME, WindowsAccount

USERNAME_FORBIDDEN = set("/\\[]:|<>+=;,?*%@")
RANDOM_CHARS = string.ascii_lowercase + string.digits


def _payload_path(name: str) -> Path:
    try:
        resource = files("forexdecsters.payloads").joinpath(name)
        return Path(str(resource))
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        pass
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        frozen = Path(meipass) / "forexdecsters" / "payloads" / name
        if frozen.exists():
            return frozen
    return Path(__file__).resolve().parent / "payloads" / name


def load_payload(name: str) -> str:
    try:
        return files("forexdecsters.payloads").joinpath(name).read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        return _payload_path(name).read_text(encoding="utf-8")


def load_payload_bytes(name: str) -> bytes:
    try:
        return files("forexdecsters.payloads").joinpath(name).read_bytes()
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        return _payload_path(name).read_bytes()


def generate_random_username() -> str:
    return "fd" + "".join(secrets.choice(RANDOM_CHARS) for _ in range(8))


def generate_random_password(username: str = "", length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    blocked = username.lower()
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(ch.isupper() for ch in password)
            and any(ch.islower() for ch in password)
            and any(ch.isdigit() for ch in password)
            and (not blocked or blocked not in password.lower())
        ):
            return password


def resolve_windows_username(raw: str) -> str:
    value = raw.strip()
    if not value:
        return "Administrator"
    if value.lower() == "random":
        return generate_random_username()
    lowered = value.lower()
    if lowered == "none":
        raise ValueError("Username cannot be 'none'.")
    if any(ch in USERNAME_FORBIDDEN for ch in value):
        raise ValueError(
            "Username cannot contain: / \\ [ ] : | < > + = ; , ? * % @"
        )
    if len(value) > 20:
        raise ValueError("Username must be 20 characters or fewer.")
    return value


def validate_windows_password(password: str, username: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain a number.")
    if username and username.lower() in password.lower():
        raise ValueError("Password cannot contain the username.")


def build_reinstall_command(account: WindowsAccount) -> list[str]:
    command = [
        "bash",
        "/tmp/reinstall.sh",
        "windows",
        "--image-name",
        IMAGE_NAME,
        "--lang",
        "en",
        "--username",
        account.username,
        "--password",
        account.password,
        "--rdp-port",
        str(account.rdp_port),
    ]
    if account.iso_url:
        command.extend(["--iso", account.iso_url])
    return command


def patch_reinstall_script(
    text: str, patcher_path: str = "/tmp/forexdecsters_patch_trans.py"
) -> str:
    needle = "curl -Lo $initrd_dir/trans.sh $confhome/trans.sh"
    hook = needle + f'\npython3 {patcher_path} "$initrd_dir/trans.sh"'
    if "forexdecsters_patch_trans.py" in text:
        return text
    if needle not in text:
        raise ValueError("could not find trans.sh download in reinstall.sh")
    return text.replace(needle, hook, 1)


def format_env_file(account: WindowsAccount) -> str:
    iso = account.iso_url or ""
    return (
        f"FD_WIN_USER={_shell_single_quote(account.username)}\n"
        f"FD_WIN_PASS={_shell_single_quote(account.password)}\n"
        f"FD_RDP_PORT={account.rdp_port}\n"
        f"FD_ISO_URL={_shell_single_quote(iso)}\n"
    )


def _shell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"

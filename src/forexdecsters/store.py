from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from forexdecsters.models import WindowsAccount
from forexdecsters.windows import load_payload_bytes


def default_store_dir() -> Path:
    return Path.cwd()


def default_store_path() -> Path:
    return default_store_dir() / "installs.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    raise ValueError(f"invalid installs file: {path}")


def save_install(
    host: str,
    account: WindowsAccount,
    path: Path | None = None,
) -> Path:
    store_path = path or default_store_path()
    store_path.parent.mkdir(parents=True, exist_ok=True)
    records = load_records(store_path)
    endpoint = f"{host}:{account.rdp_port}"
    record = {
        "ip": endpoint,
        "username": account.username,
        "password": account.password,
        "saved_at": _now_iso(),
    }
    records = [item for item in records if item.get("ip") not in (host, endpoint)]
    records.append(record)
    store_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    destrave = store_path.parent / "destrave.bat"
    if not destrave.exists():
        destrave.write_bytes(load_payload_bytes("destrave.bat"))
    return store_path


def list_installs(path: Path | None = None) -> list[dict]:
    return load_records(path or default_store_path())


def show_install(host: str, path: Path | None = None) -> dict:
    wanted = host.strip()
    for record in list_installs(path):
        saved = str(record.get("ip", ""))
        if saved == wanted or saved.split(":", 1)[0] == wanted:
            return record
    raise KeyError(host)

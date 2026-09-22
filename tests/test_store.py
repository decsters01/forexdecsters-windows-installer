from pathlib import Path

from forexdecsters.models import WindowsAccount
from forexdecsters.store import list_installs, save_install, show_install


def test_save_list_show(tmp_path: Path) -> None:
    store = tmp_path / "installs.json"
    account = WindowsAccount(
        username="fdabc12345",
        password="Abcdefg1",
        rdp_port=3391,
    )
    save_install("203.0.113.10", account, path=store)
    records = list_installs(store)
    assert len(records) == 1
    assert records[0]["ip"] == "203.0.113.10:3391"
    assert records[0]["username"] == "fdabc12345"
    assert records[0]["password"] == "Abcdefg1"
    assert "rdp_port" not in records[0]
    shown = show_install("203.0.113.10", path=store)
    assert shown["password"] == "Abcdefg1"
    assert (tmp_path / "destrave.bat").exists()
    assert b"lockoutthreshold:0" in (tmp_path / "destrave.bat").read_bytes()


def test_save_replaces_same_ip(tmp_path: Path) -> None:
    store = tmp_path / "installs.json"
    first = WindowsAccount(username="one", password="Abcdefg1", rdp_port=3389)
    second = WindowsAccount(username="two", password="Abcdefg2", rdp_port=3389)
    save_install("10.0.0.1", first, path=store)
    save_install("10.0.0.1", second, path=store)
    records = list_installs(store)
    assert len(records) == 1
    assert records[0]["username"] == "two"

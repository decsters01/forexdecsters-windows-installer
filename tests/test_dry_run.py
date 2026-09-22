from forexdecsters.installer import dry_run_text, run_install
from forexdecsters.models import InstallRequest, SshTarget, WindowsAccount
from forexdecsters.ssh import RemoteSession


def _request() -> InstallRequest:
    return InstallRequest(
        ssh=SshTarget(
            host="203.0.113.8",
            port=22,
            username="root",
            password="ssh-secret",
        ),
        windows=WindowsAccount(
            username="Administrator",
            password="Abcdefg1",
            rdp_port=3389,
        ),
        dry_run=True,
    )


def test_dry_run_text_mentions_lockout_and_eval() -> None:
    text = dry_run_text(_request())
    assert "lockoutthreshold: 0" in text
    assert "Windows Server 2019 ServerDatacenter" in text
    assert "reinstall.sh" not in text or "forexdecsters-install.sh" in text


def test_dry_run_does_not_open_ssh(monkeypatch) -> None:
    def fail_init(*_args, **_kwargs):
        raise AssertionError("SSH must not be used in dry-run")

    monkeypatch.setattr(RemoteSession, "__init__", fail_init)
    logs: list[str] = []
    run_install(_request(), log=logs.append)
    assert logs
    assert "forexdecsters-install.sh" in logs[0]
    assert "reinstall.sh" not in "".join(logs) or "lockoutthreshold" in "".join(logs)

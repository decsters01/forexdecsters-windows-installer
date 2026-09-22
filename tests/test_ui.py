from forexdecsters.models import InstallRequest, SshTarget, WindowsAccount
from forexdecsters.ui import credentials_rows, request_credentials_panel


def test_credentials_rows_include_user_password_and_rdp() -> None:
    rows = dict(
        credentials_rows(
            host="203.0.113.8",
            rdp_port=3391,
            username="fdabc12345",
            password="Abcdefg1",
            ssh_user="root",
            ssh_port=22,
        )
    )
    assert rows["IP"] == "203.0.113.8"
    assert rows["RDP"] == "203.0.113.8:3391"
    assert rows["SSH"] == "root@203.0.113.8:22"
    assert rows["Username"] == "fdabc12345"
    assert rows["Password"] == "Abcdefg1"


def test_credentials_panel_renders_password() -> None:
    request = InstallRequest(
        ssh=SshTarget(host="10.1.2.3", port=22, username="root", password="ssh"),
        windows=WindowsAccount(
            username="Administrator",
            password="Abcdefg1",
            rdp_port=3389,
        ),
    )
    panel = request_credentials_panel(request, title="confira user e senha")
    assert panel is not None
    rows = dict(
        credentials_rows(
            host=request.ssh.host,
            rdp_port=request.windows.rdp_port,
            username=request.windows.username,
            password=request.windows.password,
            ssh_user=request.ssh.username,
            ssh_port=request.ssh.port,
        )
    )
    assert "Administrator" in rows["Username"]
    assert "Abcdefg1" in rows["Password"]

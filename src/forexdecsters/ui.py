from __future__ import annotations

from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from forexdecsters import __version__
from forexdecsters.models import InstallRequest
from forexdecsters.theme import BORDER


def banner_panel() -> Panel:
    title = Text()
    title.append("FOREXDECSTERS\n", style="brand")
    title.append("windows installer", style="accent")
    body = Text()
    body.append(title)
    body.append("\n")
    body.append(f"v{__version__}  ·  Server 2019 ServerDatacenter  ·  KVM\n", style="muted")
    body.append("apaga o disco do VPS  ·  RDP no final", style="muted")
    return Panel(
        Align.left(body),
        border_style=BORDER,
        title="[accent]fd[/accent]",
        title_align="left",
        padding=(1, 2),
    )


def format_access(host: str, port: int, username: str, password: str) -> str:
    return f"ip: {host}:{port}\nuser: {username}\npass: {password}"


def format_saved(record: dict) -> str:
    return (
        f"ip: {record.get('ip', '')}\n"
        f"user: {record.get('username', '')}\n"
        f"pass: {record.get('password', '')}"
    )


def credentials_rows(
    *,
    host: str,
    rdp_port: int,
    username: str,
    password: str,
    ssh_user: str | None = None,
    ssh_port: int | None = None,
) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [
        ("IP", host),
        ("RDP", f"{host}:{rdp_port}"),
        ("Username", username),
        ("Password", password),
    ]
    if ssh_user is not None and ssh_port is not None:
        rows.insert(1, ("SSH", f"{ssh_user}@{host}:{ssh_port}"))
    return rows


def credentials_panel(
    *,
    host: str,
    rdp_port: int,
    username: str,
    password: str,
    ssh_user: str | None = None,
    ssh_port: int | None = None,
    title: str = "dados da maquina",
    subtitle: str | None = None,
) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="field", min_width=10)
    table.add_column(style="value")
    for label, value in credentials_rows(
        host=host,
        rdp_port=rdp_port,
        username=username,
        password=password,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
    ):
        table.add_row(label, value)
    return Panel(
        table,
        title=f"[accent]{title}[/accent]",
        subtitle=f"[muted]{subtitle}[/muted]" if subtitle else None,
        border_style=BORDER,
        padding=(1, 2),
    )


def request_credentials_panel(request: InstallRequest, *, title: str) -> Panel:
    return credentials_panel(
        host=request.ssh.host,
        rdp_port=request.windows.rdp_port,
        username=request.windows.username,
        password=request.windows.password,
        ssh_user=request.ssh.username,
        ssh_port=request.ssh.port,
        title=title,
        subtitle="guarde user e senha Windows para o RDP",
    )


def log_line(message: str) -> Text:
    text = Text()
    text.append("│ ", style="brand")
    text.append(message, style="log")
    return text

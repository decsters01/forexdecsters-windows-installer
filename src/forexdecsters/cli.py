from __future__ import annotations

from typing import Optional

import typer
from rich.prompt import Confirm, Prompt
from rich.table import Table

from forexdecsters.installer import dry_run_text, run_install
from forexdecsters.models import (
    DEFAULT_RDP_PORT,
    DEFAULT_SSH_PORT,
    InstallRequest,
    SshTarget,
    WindowsAccount,
)
from forexdecsters.ssh import RemoteError
from forexdecsters.store import list_installs, show_install
from forexdecsters.theme import BORDER, console
from forexdecsters.ui import (
    banner_panel,
    credentials_panel,
    format_access,
    format_saved,
    log_line,
    request_credentials_panel,
)
from forexdecsters.windows import (
    generate_random_password,
    resolve_windows_username,
    validate_windows_password,
)

app = typer.Typer(
    add_completion=False,
    no_args_is_help=False,
    help="forexdecsters windows installer",
)


def _banner() -> None:
    console.print()
    console.print(banner_panel())
    console.print()


def _pause_before_close() -> None:
    console.print()
    console.print("[muted]Pressione Enter para fechar.[/muted]")
    try:
        input()
    except EOFError:
        return


def _ask_port(label: str, default: int) -> int:
    while True:
        raw = Prompt.ask(
            f"[prompt]{label}[/prompt]  [muted]Enter = {default}[/muted]",
            default=str(default),
            console=console,
        )
        try:
            port = int(raw)
        except ValueError:
            console.print("[danger]Porta tem que ser um numero.[/danger]")
            continue
        if 1 <= port <= 65535:
            return port
        console.print("[danger]Porta tem que ficar entre 1 e 65535.[/danger]")


def _ask_windows_password(username: str) -> str:
    while True:
        raw = Prompt.ask(
            "[prompt]Senha Windows[/prompt]  [muted]Enter = aleatoria · ou digite a sua[/muted]",
            default="",
            console=console,
            password=False,
        )
        if not raw.strip() or raw.strip().lower() == "random":
            password = generate_random_password(username)
            console.print(f"[muted]senha gerada[/muted]  [accent]{password}[/accent]")
            return password
        try:
            validate_windows_password(raw, username)
        except ValueError as exc:
            console.print(f"[danger]{exc}[/danger]")
            continue
        return raw


def _prompt_request(dry_run: bool, iso: Optional[str]) -> InstallRequest:
    console.print("[brand]VPS[/brand]  [muted]SSH agora[/muted]")
    host = Prompt.ask("[prompt]IP do VPS[/prompt]", console=console).strip()
    ssh_port = _ask_port("Porta SSH", DEFAULT_SSH_PORT)
    ssh_user = Prompt.ask(
        "[prompt]Usuario SSH[/prompt]  [muted]Enter = root[/muted]",
        default="root",
        console=console,
    ).strip()
    ssh_password = Prompt.ask(
        "[prompt]Senha SSH[/prompt]  [muted]nao e salva[/muted]",
        password=True,
        console=console,
    )

    console.print()
    console.print(
        "[brand]WINDOWS[/brand]  [muted]Server 2019 ServerDatacenter · depois do reboot, RDP[/muted]"
    )
    rdp_port = _ask_port("Porta RDP", DEFAULT_RDP_PORT)
    username_raw = Prompt.ask(
        "[prompt]Usuario Windows[/prompt]  [muted]Enter = Administrator · Random = nome fd… · ou um nome ate 20[/muted]",
        default="",
        console=console,
    )
    username = resolve_windows_username(username_raw)
    console.print(f"[muted]usuario que sera criado[/muted]  [accent]{username}[/accent]")
    password = _ask_windows_password(username)
    if iso is None:
        iso_raw = Prompt.ask(
            "[prompt]URL da ISO[/prompt]  [muted]Enter = busca automatica[/muted]",
            default="",
            console=console,
        ).strip()
        iso = iso_raw or None

    request = InstallRequest(
        ssh=SshTarget(
            host=host.strip(),
            port=ssh_port,
            username=ssh_user.strip(),
            password=ssh_password,
        ),
        windows=WindowsAccount(
            username=username,
            password=password,
            rdp_port=rdp_port,
            iso_url=iso,
        ),
        dry_run=dry_run,
    )
    console.print()
    console.print(
        request_credentials_panel(request, title="confira user e senha")
    )
    console.print(
        format_access(
            request.ssh.host,
            request.windows.rdp_port,
            request.windows.username,
            request.windows.password,
        )
    )
    console.print()
    console.print(
        "[danger]isso apaga o disco inteiro do VPS[/danger]\n"
        "[muted]Windows Server 2019 ServerDatacenter · lockoutthreshold=0[/muted]"
    )
    if Prompt.ask("[prompt]Digite o IP de novo[/prompt]", console=console) != host:
        raise typer.BadParameter("IP de confirmacao nao bate.")
    if not Confirm.ask("[prompt]Install?[/prompt]", default=False, console=console):
        raise typer.Abort()
    return request


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Mostra o comando remoto e nao executa o reinstall.",
    ),
    iso: Optional[str] = typer.Option(
        None,
        "--iso",
        help="URL opcional da ISO se a busca automatica falhar.",
    ),
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    _banner()
    request = _prompt_request(dry_run=dry_run, iso=iso)
    _execute(request)


@app.command()
def install(
    dry_run: bool = typer.Option(False, "--dry-run"),
    iso: Optional[str] = typer.Option(None, "--iso"),
    ip: Optional[str] = typer.Option(None, "--ip"),
    ssh_port: int = typer.Option(DEFAULT_SSH_PORT, "--ssh-port"),
    ssh_user: str = typer.Option("root", "--ssh-user"),
    ssh_password: Optional[str] = typer.Option(None, "--ssh-password"),
    rdp_port: int = typer.Option(DEFAULT_RDP_PORT, "--rdp-port"),
    username: str = typer.Option("", "--username"),
    password: Optional[str] = typer.Option(None, "--password"),
) -> None:
    """Instala Windows Server 2019 ServerDatacenter no VPS."""
    _banner()
    if ip and ssh_password is not None and password is not None:
        windows_user = resolve_windows_username(username)
        validate_windows_password(password, windows_user)
        request = InstallRequest(
            ssh=SshTarget(
                host=ip,
                port=ssh_port,
                username=ssh_user,
                password=ssh_password,
            ),
            windows=WindowsAccount(
                username=windows_user,
                password=password,
                rdp_port=rdp_port,
                iso_url=iso,
            ),
            dry_run=dry_run,
        )
        console.print(request_credentials_panel(request, title="confira user e senha"))
        console.print(
            format_access(
                request.ssh.host,
                request.windows.rdp_port,
                request.windows.username,
                request.windows.password,
            )
        )
        if not dry_run:
            console.print("[danger]isso apaga o disco inteiro do VPS[/danger]")
            if Prompt.ask("[prompt]Digite o IP de novo[/prompt]", console=console) != ip:
                raise typer.BadParameter("IP de confirmacao nao bate.")
            if not Confirm.ask("[prompt]Install?[/prompt]", default=False, console=console):
                raise typer.Abort()
        _execute(request)
        return
    request = _prompt_request(dry_run=dry_run, iso=iso)
    _execute(request)


@app.command("list")
def list_cmd() -> None:
    """Lista credenciais Windows salvas localmente."""
    _banner()
    records = list_installs()
    if not records:
        console.print("[muted]Nenhuma instalacao salva.[/muted]")
        return
    table = Table(
        title="[brand]instalacoes[/brand]",
        border_style=BORDER,
        header_style="accent",
    )
    table.add_column("IP", style="ice")
    table.add_column("Username", style="accent")
    table.add_column("Password", style="value")
    table.add_column("Salvo em", style="muted")
    for record in records:
        table.add_row(
            str(record.get("ip", "")),
            str(record.get("username", "")),
            str(record.get("password", "")),
            str(record.get("saved_at", "")),
        )
        console.print(format_saved(record))
    console.print(table)


@app.command()
def show(ip: str) -> None:
    """Mostra usuario e senha Windows salvos para um IP."""
    _banner()
    try:
        record = show_install(ip)
    except KeyError as exc:
        raise typer.BadParameter(f"Nenhum registro para {ip}") from exc
    console.print(format_saved(record))


def _execute(request: InstallRequest) -> None:
    if request.dry_run:
        console.print("[warn]Dry-run[/warn]  [muted]nada vai para o VPS[/muted]")
        console.print(request_credentials_panel(request, title="o que seria instalado"))
        console.print(f"[muted]{dry_run_text(request)}[/muted]")
        return
    try:
        run_install(request, log=lambda message: console.print(log_line(message)))
    except (RemoteError, ValueError) as exc:
        console.print(f"[danger]{exc}[/danger]")
        raise typer.Exit(code=1) from exc
    console.print()
    console.print(
        format_access(
            request.ssh.host,
            request.windows.rdp_port,
            request.windows.username,
            request.windows.password,
        )
    )
    console.print(
        "[ok]disparo concluido[/ok]  "
        "[muted]depois do reboot: mstsc /v:IP:porta[/muted]"
    )

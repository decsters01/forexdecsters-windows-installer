from __future__ import annotations

from collections.abc import Callable

from paramiko.ssh_exception import SSHException

from forexdecsters.models import IMAGE_NAME, InstallRequest
from forexdecsters.preflight import run_preflight
from forexdecsters.ssh import RemoteError, RemoteSession
from forexdecsters.store import save_install
from forexdecsters.windows import format_env_file, load_payload

LogFn = Callable[[str], None]


def dry_run_text(request: InstallRequest) -> str:
    command = [
        "bash /tmp/forexdecsters-install.sh",
        f"# image: {IMAGE_NAME}",
        f"# windows user: {request.windows.username}",
        f"# rdp port: {request.windows.rdp_port}",
        "# lockoutthreshold: 0 (embedded)",
    ]
    if request.windows.iso_url:
        command.append(f"# iso: {request.windows.iso_url}")
    return "\n".join(command)


def run_install(request: InstallRequest, log: LogFn | None = None) -> None:
    emit = log or (lambda _message: None)
    if request.dry_run:
        emit(dry_run_text(request))
        return

    saved = save_install(request.ssh.host, request.windows)
    emit(f"Windows credentials saved at {saved}")

    with RemoteSession(request.ssh, log=emit) as session:
        emit("SSH connected. Running preflight...")
        facts = run_preflight(session)
        emit(
            f"Preflight ok: virt={facts.get('VIRT')} ram={facts.get('RAM_MB')}MB "
            f"disk={facts.get('DISK_GB')}GB"
        )
        session.upload_text(
            "/tmp/forexdecsters.env",
            format_env_file(request.windows),
        )
        session.upload_text(
            "/tmp/forexdecsters_patch_trans.py",
            load_payload("patch_trans.py"),
        )
        session.upload_text(
            "/tmp/forexdecsters-install.sh",
            load_payload("remote_install.sh"),
        )
        session.run("chmod 600 /tmp/forexdecsters.env")
        session.run("chmod 755 /tmp/forexdecsters-install.sh /tmp/forexdecsters_patch_trans.py")
        emit("Starting remote installer (this wipes the VPS disk after reboot)...")
        saw_prepared = {"value": False}

        def capture(message: str) -> None:
            lowered = message.lower()
            if (
                "reinstall prepared" in lowered
                or "reboot to start the reinstallation" in lowered
                or "reiniciar" in lowered
            ):
                saw_prepared["value"] = True
            emit(message)

        session._log = capture
        try:
            code = session.stream("bash /tmp/forexdecsters-install.sh")
        except (RemoteError, OSError, SSHException) as exc:
            message = str(exc).lower()
            dropped = "reset" in message or "closed" in message or "timed out" in message
            if dropped and saw_prepared["value"]:
                emit("SSH dropped after reboot request. That is expected.")
                code = 0
            else:
                raise
        if code not in (0, -1):
            raise RemoteError(f"remote installer exited with status {code}")
        if code == -1 and not saw_prepared["value"]:
            raise RemoteError("remote installer ended without confirming the reinstall.")
        emit("RDP after the VPS finishes installing.")

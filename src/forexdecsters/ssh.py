from __future__ import annotations

import time
from collections.abc import Callable

import paramiko
from paramiko.ssh_exception import (
    AuthenticationException,
    SSHException,
)

from forexdecsters.models import SshTarget

LogFn = Callable[[str], None]


class RemoteError(RuntimeError):
    pass


class RemoteSession:
    def __init__(self, target: SshTarget, log: LogFn | None = None) -> None:
        self.target = target
        self._log = log or (lambda _message: None)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self) -> None:
        try:
            self.client.connect(
                hostname=self.target.host,
                port=self.target.port,
                username=self.target.username,
                password=self.target.password,
                timeout=30,
                allow_agent=False,
                look_for_keys=False,
            )
        except AuthenticationException as exc:
            raise RemoteError("SSH authentication failed. Check user and password.") from exc
        except SSHException as exc:
            raise RemoteError(f"SSH error: {exc}") from exc
        except OSError as exc:
            raise RemoteError(f"Could not reach {self.target.host}:{self.target.port}: {exc}") from exc

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> RemoteSession:
        self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def run(self, command: str, timeout: int = 120) -> str:
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        stdin.close()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        if code != 0:
            detail = (err or out).strip() or f"exit {code}"
            raise RemoteError(detail)
        return out

    def upload_text(self, remote_path: str, content: str) -> None:
        payload = content.encode("utf-8")
        with self.client.open_sftp() as sftp:
            with sftp.file(remote_path, "wb") as handle:
                handle.write(payload)

    def stream(self, command: str, timeout: int = 3600) -> int:
        transport = self.client.get_transport()
        if transport is None:
            raise RemoteError("SSH transport is not connected.")
        channel = transport.open_session()
        channel.settimeout(timeout)
        channel.get_pty()
        channel.exec_command(command)
        buffer = ""
        while True:
            if channel.recv_ready():
                chunk = channel.recv(4096).decode("utf-8", errors="replace")
                buffer += chunk
                self._flush_lines(buffer)
                buffer = _keep_partial(buffer)
            elif channel.exit_status_ready():
                break
            else:
                if channel.closed or not transport.is_active():
                    break
                time.sleep(0.05)
        try:
            leftover = channel.recv(4096).decode("utf-8", errors="replace")
        except OSError:
            leftover = ""
        if leftover:
            buffer += leftover
        if buffer.strip():
            self._log(buffer.rstrip("\n"))
        try:
            return channel.recv_exit_status()
        except OSError:
            return 0

    def _flush_lines(self, buffer: str) -> None:
        if "\n" not in buffer:
            return
        lines = buffer.split("\n")
        for line in lines[:-1]:
            self._log(line.rstrip("\r"))


def _keep_partial(buffer: str) -> str:
    if "\n" not in buffer:
        return buffer
    return buffer.split("\n")[-1]

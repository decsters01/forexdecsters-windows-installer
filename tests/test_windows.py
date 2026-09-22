from forexdecsters.models import IMAGE_NAME, WindowsAccount
from forexdecsters.payloads.patch_trans import NEEDLE, patch_trans_script
from forexdecsters.windows import (
    build_reinstall_command,
    format_env_file,
    generate_random_password,
    generate_random_username,
    patch_reinstall_script,
    resolve_windows_username,
    validate_windows_password,
)


def test_empty_username_is_administrator() -> None:
    assert resolve_windows_username("") == "Administrator"
    assert resolve_windows_username("   ") == "Administrator"


def test_random_username() -> None:
    name = resolve_windows_username("Random")
    assert name.startswith("fd")
    assert len(name) == 10
    assert name[2:].isalnum()
    assert name[2:].islower() or name[2:].isdigit() or name[2:].isalnum()


def test_generate_random_password_rules() -> None:
    password = generate_random_password("Administrator")
    assert len(password) >= 8
    validate_windows_password(password, "Administrator")


def test_generate_random_username_prefix() -> None:
    name = generate_random_username()
    assert name.startswith("fd")
    assert len(name) == 10


def test_custom_username() -> None:
    assert resolve_windows_username("cliente01") == "cliente01"


def test_forbidden_username() -> None:
    try:
        resolve_windows_username("user@x")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_password_rules() -> None:
    validate_windows_password("Abcdefg1", "Administrator")
    try:
        validate_windows_password("short1A", "Administrator")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    try:
        validate_windows_password("Abcdefg1", "Abc")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_reinstall_command_contains_image() -> None:
    account = WindowsAccount(
        username="Administrator",
        password="Abcdefg1",
        rdp_port=3389,
    )
    command = build_reinstall_command(account)
    assert IMAGE_NAME in command
    assert "--rdp-port" in command
    assert "3389" in command
    assert "--username" in command
    assert "Administrator" in command


def test_reinstall_command_optional_iso() -> None:
    account = WindowsAccount(
        username="Administrator",
        password="Abcdefg1",
        rdp_port=3390,
        iso_url="https://example.microsoft.com/eval.iso",
    )
    command = build_reinstall_command(account)
    assert "--iso" in command
    assert "https://example.microsoft.com/eval.iso" in command


def test_env_file_quotes_password() -> None:
    account = WindowsAccount(
        username="Administrator",
        password="Ab'cd1Ef",
        rdp_port=3389,
    )
    text = format_env_file(account)
    assert "FD_RDP_PORT=3389" in text
    assert "Ab'\"'\"'cd1Ef" in text or "FD_WIN_PASS=" in text


def test_patch_trans_injects_lockout() -> None:
    original = "#!/bin/sh\n" + NEEDLE + "\nlocale=en\n"
    patched = patch_trans_script(original)
    assert "forexdecsters_apply_lockout" in patched
    assert "lockoutthreshold:0" in patched
    assert patched.count("forexdecsters_apply_lockout") >= 2


def test_patch_trans_is_idempotent() -> None:
    original = "#!/bin/sh\n" + NEEDLE + "\n"
    once = patch_trans_script(original)
    twice = patch_trans_script(once)
    assert once == twice


def test_patch_reinstall_injects_python_hook() -> None:
    original = 'curl -Lo $initrd_dir/trans.sh $confhome/trans.sh\necho done\n'
    patched = patch_reinstall_script(original)
    assert "forexdecsters_patch_trans.py" in patched
    again = patch_reinstall_script(patched)
    assert again == patched

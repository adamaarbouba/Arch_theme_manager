from pathlib import Path
from types import SimpleNamespace
import socket

from arch_theme_manager.core.doctor import ThemeDoctor


def make_doctor(tmp_path: Path) -> ThemeDoctor:
    doctor = ThemeDoctor.__new__(ThemeDoctor)

    doctor.loader = None
    doctor.validator = None
    doctor.state = None

    doctor.home = tmp_path / "home"

    doctor.config_root = doctor.home / ".config"

    doctor.manager_config = doctor.config_root / "arch-theme-manager"

    doctor.generated_dir = doctor.manager_config / "generated"

    doctor.runtime_root = tmp_path / "runtime" / "arch-theme-manager"

    doctor.home.mkdir(parents=True)

    doctor.config_root.mkdir(parents=True)

    doctor.manager_config.mkdir(parents=True)

    doctor.generated_dir.mkdir(parents=True)

    doctor.runtime_root.mkdir(parents=True)

    return doctor


def write_file(
    path: Path,
    content: str = "test\n",
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content,
        encoding="utf-8",
    )


def setup_generated_files(
    doctor: ThemeDoctor,
) -> None:
    expected = [
        "waybar-theme.css",
        "swaync-theme.css",
        "hyprland-theme.lua",
        "kitty-theme.conf",
        "zsh-theme.zsh",
        "nvim-theme.lua",
        "hyprlock-theme.conf",
        "hyprtoolkit-theme.conf",
    ]

    for filename in expected:
        write_file(doctor.generated_dir / filename)


def setup_integrations(
    doctor: ThemeDoctor,
) -> None:
    hypr_dir = doctor.config_root / "hypr"

    waybar_dir = doctor.config_root / "waybar"

    swaync_dir = doctor.config_root / "swaync"

    kitty_dir = doctor.config_root / "kitty"

    nvim_dir = doctor.config_root / "nvim"

    manager_integrations = doctor.manager_config / "integrations"

    setup_generated_files(doctor)

    write_file(
        hypr_dir / "hyprland.lua",
        'require("theme")\n',
    )

    write_file(
        hypr_dir / "hyprlock.conf",
        ("source = $HOME/.config/arch-theme-manager/generated/hyprlock-theme.conf\n"),
    )

    write_file(
        kitty_dir / "kitty.conf",
        (
            "include theme.conf\n"
            "allow_remote_control "
            "socket-only\n"
            "listen_on "
            "unix:/tmp/"
            "kitty-theme-{kitty_pid}\n"
        ),
    )

    write_file(
        swaync_dir / "style.css",
        '@import "theme.css";\n',
    )

    write_file(
        waybar_dir / "style.css",
        '@import "theme.css";\n',
    )

    write_file(
        doctor.home / ".zshrc",
        (
            'source "${XDG_CONFIG_HOME:-'
            "$HOME/.config}/"
            "arch-theme-manager/"
            'integrations/zsh.zsh"\n'
        ),
    )

    write_file(manager_integrations / "zsh.zsh")

    write_file(manager_integrations / "nvim.lua")

    symlinks = [
        (
            waybar_dir / "theme.css",
            doctor.generated_dir / "waybar-theme.css",
        ),
        (
            swaync_dir / "theme.css",
            doctor.generated_dir / "swaync-theme.css",
        ),
        (
            hypr_dir / "theme.lua",
            doctor.generated_dir / "hyprland-theme.lua",
        ),
        (
            kitty_dir / "theme.conf",
            doctor.generated_dir / "kitty-theme.conf",
        ),
        (
            hypr_dir / "hyprtoolkit.conf",
            doctor.generated_dir / "hyprtoolkit-theme.conf",
        ),
        (
            nvim_dir / "plugin" / "arch-theme-manager.lua",
            manager_integrations / "nvim.lua",
        ),
    ]

    for link, target in symlinks:
        link.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        link.symlink_to(target)


def create_socket(
    path: Path,
) -> socket.socket:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    server = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    server.bind(str(path))

    return server


def test_generated_files_include_neovim(
    tmp_path,
):
    doctor = make_doctor(tmp_path)

    setup_generated_files(doctor)

    results = doctor._check_generated_files()

    assert (
        "OK",
        "Generated: nvim-theme.lua",
    ) in results


def test_missing_neovim_generated_file_fails(
    tmp_path,
):
    doctor = make_doctor(tmp_path)

    setup_generated_files(doctor)

    (doctor.generated_dir / "nvim-theme.lua").unlink()

    results = doctor._check_generated_files()

    assert (
        "FAIL",
        ("Missing generated file: nvim-theme.lua"),
    ) in results


def test_neovim_integration_is_installed(
    tmp_path,
):
    doctor = make_doctor(tmp_path)

    setup_integrations(doctor)

    results = doctor._check_integrations()

    assert (
        "OK",
        "Neovim integration file",
    ) in results

    assert (
        "OK",
        "Neovim integration",
    ) in results


def test_neovim_wrong_symlink_fails(
    tmp_path,
):
    doctor = make_doctor(tmp_path)

    setup_integrations(doctor)

    plugin = doctor.config_root / "nvim" / "plugin" / "arch-theme-manager.lua"

    plugin.unlink()

    wrong_target = tmp_path / "wrong.lua"

    write_file(wrong_target)

    plugin.symlink_to(wrong_target)

    results = doctor._check_integrations()

    assert any(
        status == "FAIL" and ("Neovim points to wrong target") in message
        for status, message in results
    )


def test_neovim_not_running_is_warning(
    tmp_path,
    monkeypatch,
):
    doctor = make_doctor(tmp_path)

    monkeypatch.setattr(
        "arch_theme_manager.core.doctor.shutil.which",
        lambda command: "/usr/bin/nvim" if command == "nvim" else None,
    )

    monkeypatch.setattr(
        doctor,
        "_process_running",
        lambda process: False,
    )

    results = doctor._check_neovim_runtime()

    assert (
        "WARN",
        ("Neovim is not currently running"),
    ) in results

    assert not any(status == "FAIL" for status, _ in results)


def test_running_neovim_without_socket_fails(
    tmp_path,
    monkeypatch,
):
    doctor = make_doctor(tmp_path)

    monkeypatch.setattr(
        "arch_theme_manager.core.doctor.shutil.which",
        lambda command: "/usr/bin/nvim" if command == "nvim" else None,
    )

    monkeypatch.setattr(
        doctor,
        "_process_running",
        lambda process: True,
    )

    results = doctor._check_neovim_runtime()

    assert (
        "FAIL",
        ("Neovim is running but Arch Theme Manager RPC directory is missing"),
    ) in results


def test_running_neovim_with_valid_rpc_socket(
    tmp_path,
    monkeypatch,
):
    doctor = make_doctor(tmp_path)

    socket_path = doctor.runtime_root / "nvim" / "12345.sock"

    server = create_socket(socket_path)

    try:
        monkeypatch.setattr(
            "arch_theme_manager.core.doctor.shutil.which",
            lambda command: "/usr/bin/nvim" if command == "nvim" else None,
        )

        monkeypatch.setattr(
            doctor,
            "_process_running",
            lambda process: True,
        )

        def fake_run(
            command,
            **kwargs,
        ):
            assert command == [
                "/usr/bin/nvim",
                "--server",
                str(socket_path),
                "--remote-expr",
                'execute("ArchThemeReload")',
            ]

            return SimpleNamespace(
                returncode=0,
                stdout="",
                stderr="",
            )

        monkeypatch.setattr(
            "arch_theme_manager.core.doctor.subprocess.run",
            fake_run,
        )

        results = doctor._check_neovim_runtime()

        assert (
            "OK",
            ("1 Neovim RPC instance(s) registered"),
        ) in results

        assert not any(status == "FAIL" for status, _ in results)

    finally:
        server.close()


def test_unresponsive_neovim_socket_fails(
    tmp_path,
    monkeypatch,
):
    doctor = make_doctor(tmp_path)

    socket_path = doctor.runtime_root / "nvim" / "12345.sock"

    server = create_socket(socket_path)

    try:
        monkeypatch.setattr(
            "arch_theme_manager.core.doctor.shutil.which",
            lambda command: "/usr/bin/nvim" if command == "nvim" else None,
        )

        monkeypatch.setattr(
            doctor,
            "_process_running",
            lambda process: True,
        )

        monkeypatch.setattr(
            "arch_theme_manager.core.doctor.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=1,
                stdout="",
                stderr="failed",
            ),
        )

        results = doctor._check_neovim_runtime()

        assert (
            "FAIL",
            ("No responsive Arch Theme Manager Neovim RPC instances were found"),
        ) in results

        assert (
            "WARN",
            ("1 unresponsive Neovim RPC socket(s) found"),
        ) in results

    finally:
        server.close()


def test_stale_socket_warns_when_neovim_closed(
    tmp_path,
    monkeypatch,
):
    doctor = make_doctor(tmp_path)

    socket_path = doctor.runtime_root / "nvim" / "12345.sock"

    server = create_socket(socket_path)

    try:
        monkeypatch.setattr(
            "arch_theme_manager.core.doctor.shutil.which",
            lambda command: "/usr/bin/nvim" if command == "nvim" else None,
        )

        monkeypatch.setattr(
            doctor,
            "_process_running",
            lambda process: False,
        )

        results = doctor._check_neovim_runtime()

        assert (
            "WARN",
            ("Neovim is not currently running"),
        ) in results

        assert (
            "WARN",
            ("1 stale Neovim RPC socket(s) may remain"),
        ) in results

        assert not any(status == "FAIL" for status, _ in results)

    finally:
        server.close()

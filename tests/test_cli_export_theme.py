import os
from pathlib import Path
import subprocess
import sys


def themectl_path():
    return (
        Path(sys.executable).parent
        / "themectl"
    )


def isolated_environment(tmp_path):
    env = os.environ.copy()

    env["XDG_CONFIG_HOME"] = str(
        tmp_path / "config"
    )

    env["XDG_STATE_HOME"] = str(
        tmp_path / "state"
    )

    env["XDG_RUNTIME_DIR"] = str(
        tmp_path / "runtime"
    )

    return env


def example_theme():
    return (
        Path(__file__).resolve()
        .parents[1]
        / "themes"
        / "example"
    )


def install_theme(
    env,
    name,
):
    return subprocess.run(
        [
            str(themectl_path()),
            "install-theme",
            str(example_theme()),
            "--name",
            name,
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )


def test_export_theme_help():
    result = subprocess.run(
        [
            str(themectl_path()),
            "export-theme",
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    assert result.returncode == 0

    assert (
        "Export an installed theme"
        in result.stdout
    )

    assert "destination" in result.stdout
    assert "--force" in result.stdout


def test_cli_exports_theme(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "portal",
    )

    assert installed.returncode == 0

    export_root = (
        tmp_path / "exports"
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "export-theme",
            "portal",
            str(export_root),
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    exported = (
        export_root
        / "portal"
    )

    assert exported.is_dir()

    assert (
        exported / "theme.json"
    ).is_file()

    assert (
        exported / "wallpaper.png"
    ).is_file()

    assert (
        "Exported theme "
        "'portal'"
        in result.stdout
    )


def test_cli_export_keeps_installed_theme(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "portal",
    )

    assert installed.returncode == 0

    export_root = (
        tmp_path / "exports"
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "export-theme",
            "portal",
            str(export_root),
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    installed_theme = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
        / "portal"
    )

    assert installed_theme.is_dir()

    assert (
        export_root
        / "portal"
    ).is_dir()


def test_cli_missing_theme_fails(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "export-theme",
            "missing",
            str(
                tmp_path / "exports"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 1

    assert (
        "does not exist"
        in result.stderr
    )


def test_cli_existing_export_fails(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "portal",
    )

    assert installed.returncode == 0

    export_root = (
        tmp_path / "exports"
    )

    command = [
        str(themectl_path()),
        "export-theme",
        "portal",
        str(export_root),
    ]

    first = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    second = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert first.returncode == 0
    assert second.returncode == 1

    assert (
        "already exists"
        in second.stderr
    )


def test_cli_force_replaces_export(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "portal",
    )

    assert installed.returncode == 0

    export_root = (
        tmp_path / "exports"
    )

    first = subprocess.run(
        [
            str(themectl_path()),
            "export-theme",
            "portal",
            str(export_root),
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert first.returncode == 0

    marker = (
        export_root
        / "portal"
        / "old-file.txt"
    )

    marker.write_text(
        "old",
        encoding="utf-8",
    )

    second = subprocess.run(
        [
            str(themectl_path()),
            "export-theme",
            "portal",
            str(export_root),
            "--force",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert second.returncode == 0

    assert not marker.exists()


def test_cli_export_creates_destination_root(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "portal",
    )

    assert installed.returncode == 0

    export_root = (
        tmp_path
        / "nested"
        / "exports"
    )

    assert not export_root.exists()

    result = subprocess.run(
        [
            str(themectl_path()),
            "export-theme",
            "portal",
            str(export_root),
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    assert (
        export_root
        / "portal"
    ).is_dir()

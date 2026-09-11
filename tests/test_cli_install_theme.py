import os
from pathlib import Path
import shutil
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


def test_install_theme_help():
    result = subprocess.run(
        [
            str(themectl_path()),
            "install-theme",
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    assert result.returncode == 0

    assert "Install a theme" in result.stdout
    assert "--name" in result.stdout
    assert "--force" in result.stdout


def test_cli_installs_theme(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "install-theme",
            str(example_theme()),
            "--name",
            "cli-test",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    assert (
        "Installed theme 'cli-test'."
        in result.stdout
    )

    installed = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
        / "cli-test"
    )

    assert (
        installed / "theme.json"
    ).is_file()

    assert (
        installed / "wallpaper.png"
    ).is_file()


def test_cli_duplicate_install_fails(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    command = [
        str(themectl_path()),
        "install-theme",
        str(example_theme()),
        "--name",
        "duplicate",
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


def test_cli_force_replaces_theme(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    source = (
        tmp_path
        / "source-theme"
    )

    shutil.copytree(
        example_theme(),
        source,
    )

    command = [
        str(themectl_path()),
        "install-theme",
        str(source),
        "--name",
        "replace-me",
    ]

    first = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert first.returncode == 0

    second = subprocess.run(
        command + ["--force"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert second.returncode == 0

    assert (
        "Installed theme 'replace-me'."
        in second.stdout
    )

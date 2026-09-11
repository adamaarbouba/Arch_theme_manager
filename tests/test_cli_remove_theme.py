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


def test_remove_theme_help():
    result = subprocess.run(
        [
            str(themectl_path()),
            "remove-theme",
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    assert result.returncode == 0
    assert "Remove an installed theme" in result.stdout
    assert "--force" in result.stdout


def test_cli_removes_theme(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "remove-me",
    )

    assert installed.returncode == 0

    result = subprocess.run(
        [
            str(themectl_path()),
            "remove-theme",
            "remove-me",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    assert (
        "Removed theme 'remove-me'."
        in result.stdout
    )

    theme_dir = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
        / "remove-me"
    )

    assert not theme_dir.exists()


def test_cli_missing_theme_fails(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "remove-theme",
            "missing",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 1
    assert "does not exist" in result.stderr


def test_cli_active_theme_requires_force(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "active-theme",
    )

    assert installed.returncode == 0

    state_dir = (
        tmp_path
        / "state"
        / "arch-theme-manager"
    )

    state_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        state_dir
        / "current.json"
    ).write_text(
        (
            '{"current": "active-theme", '
            '"previous": null}'
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "remove-theme",
            "active-theme",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 1
    assert "currently active" in result.stderr


def test_cli_force_removes_active_theme(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "active-theme",
    )

    assert installed.returncode == 0

    state_dir = (
        tmp_path
        / "state"
        / "arch-theme-manager"
    )

    state_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        state_dir
        / "current.json"
    ).write_text(
        (
            '{"current": "active-theme", '
            '"previous": null}'
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "remove-theme",
            "active-theme",
            "--force",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    assert (
        "Removed theme 'active-theme'."
        in result.stdout
    )

    assert not (
        state_dir
        / "current.json"
    ).exists()

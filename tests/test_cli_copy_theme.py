import json
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


def test_copy_theme_help():
    result = subprocess.run(
        [
            str(themectl_path()),
            "copy-theme",
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    assert result.returncode == 0

    assert (
        "Copy an installed theme"
        in result.stdout
    )

    assert "source" in result.stdout
    assert "new_name" in result.stdout


def test_cli_copies_theme(
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

    result = subprocess.run(
        [
            str(themectl_path()),
            "copy-theme",
            "portal",
            "portal-copy",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    assert (
        "Copied theme "
        "'portal' "
        "to 'portal-copy'."
        in result.stdout
    )

    themes_dir = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
    )

    assert (
        themes_dir
        / "portal"
    ).is_dir()

    assert (
        themes_dir
        / "portal-copy"
    ).is_dir()


def test_cli_copy_updates_manifest_name(
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

    result = subprocess.run(
        [
            str(themectl_path()),
            "copy-theme",
            "portal",
            "gateway",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    manifest = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
        / "gateway"
        / "theme.json"
    )

    data = json.loads(
        manifest.read_text(
            encoding="utf-8",
        )
    )

    assert (
        data["name"]
        == "gateway"
    )


def test_cli_copy_keeps_source(
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

    result = subprocess.run(
        [
            str(themectl_path()),
            "copy-theme",
            "portal",
            "gateway",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    themes_dir = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
    )

    assert (
        themes_dir
        / "portal"
    ).is_dir()

    assert (
        themes_dir
        / "gateway"
    ).is_dir()


def test_cli_missing_source_fails(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "copy-theme",
            "missing",
            "copy",
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


def test_cli_existing_destination_fails(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    first = install_theme(
        env,
        "portal",
    )

    second = install_theme(
        env,
        "gateway",
    )

    assert first.returncode == 0
    assert second.returncode == 0

    result = subprocess.run(
        [
            str(themectl_path()),
            "copy-theme",
            "portal",
            "gateway",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 1

    assert (
        "already exists"
        in result.stderr
    )

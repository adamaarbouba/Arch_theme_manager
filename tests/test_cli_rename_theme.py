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


def test_rename_theme_help():
    result = subprocess.run(
        [
            str(themectl_path()),
            "rename-theme",
            "--help",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    assert result.returncode == 0

    assert (
        "Rename an installed theme"
        in result.stdout
    )

    assert "old_name" in result.stdout
    assert "new_name" in result.stdout


def test_cli_renames_theme(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "old-name",
    )

    assert installed.returncode == 0

    result = subprocess.run(
        [
            str(themectl_path()),
            "rename-theme",
            "old-name",
            "new-name",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    assert (
        "Renamed theme "
        "'old-name' "
        "to 'new-name'."
        in result.stdout
    )

    themes = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
    )

    assert not (
        themes / "old-name"
    ).exists()

    assert (
        themes / "new-name"
    ).is_dir()


def test_cli_updates_manifest_name(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    installed = install_theme(
        env,
        "old-name",
    )

    assert installed.returncode == 0

    result = subprocess.run(
        [
            str(themectl_path()),
            "rename-theme",
            "old-name",
            "new-name",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    manifest_path = (
        tmp_path
        / "config"
        / "arch-theme-manager"
        / "themes"
        / "new-name"
        / "theme.json"
    )

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8",
        )
    )

    assert (
        manifest["name"]
        == "new-name"
    )


def test_cli_missing_theme_fails(
    tmp_path,
):
    env = isolated_environment(
        tmp_path
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "rename-theme",
            "missing",
            "new-name",
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
        "lucy",
    )

    assert first.returncode == 0
    assert second.returncode == 0

    result = subprocess.run(
        [
            str(themectl_path()),
            "rename-theme",
            "portal",
            "lucy",
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


def test_cli_rename_updates_current_state(
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

    state_dir = (
        tmp_path
        / "state"
        / "arch-theme-manager"
    )

    state_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    state_file = (
        state_dir
        / "current.json"
    )

    state_file.write_text(
        json.dumps(
            {
                "current": "portal",
                "previous": None,
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "rename-theme",
            "portal",
            "gateway",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    state_data = json.loads(
        state_file.read_text(
            encoding="utf-8",
        )
    )

    assert (
        state_data["current"]
        == "gateway"
    )


def test_cli_rename_updates_previous_state(
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

    state_dir = (
        tmp_path
        / "state"
        / "arch-theme-manager"
    )

    state_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    state_file = (
        state_dir
        / "current.json"
    )

    state_file.write_text(
        json.dumps(
            {
                "current": "lucy",
                "previous": "portal",
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            str(themectl_path()),
            "rename-theme",
            "portal",
            "gateway",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0

    state_data = json.loads(
        state_file.read_text(
            encoding="utf-8",
        )
    )

    assert (
        state_data["current"]
        == "lucy"
    )

    assert (
        state_data["previous"]
        == "gateway"
    )

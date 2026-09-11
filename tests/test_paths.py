import os
from pathlib import Path

from arch_theme_manager.paths import (
    config_home,
    ensure_runtime_dirs,
    generated_dir,
    runtime_home,
    state_dir,
    state_home,
    themes_dir,
)


def test_config_home_uses_xdg(
    monkeypatch,
    tmp_path,
):
    location = (
        tmp_path / "config"
    )

    monkeypatch.setenv(
        "XDG_CONFIG_HOME",
        str(location),
    )

    assert config_home() == (
        location
        / "arch-theme-manager"
    )


def test_state_home_uses_xdg(
    monkeypatch,
    tmp_path,
):
    location = (
        tmp_path / "state"
    )

    monkeypatch.setenv(
        "XDG_STATE_HOME",
        str(location),
    )

    assert state_home() == (
        location
        / "arch-theme-manager"
    )


def test_runtime_home_uses_xdg(
    monkeypatch,
    tmp_path,
):
    location = (
        tmp_path / "runtime"
    )

    monkeypatch.setenv(
        "XDG_RUNTIME_DIR",
        str(location),
    )

    assert runtime_home() == (
        location
        / "arch-theme-manager"
    )


def test_runtime_home_fallback(
    monkeypatch,
):
    monkeypatch.delenv(
        "XDG_RUNTIME_DIR",
        raising=False,
    )

    assert runtime_home() == Path(
        "/tmp"
    ) / (
        f"arch-theme-manager-"
        f"{os.getuid()}"
    )


def test_theme_directory(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "XDG_CONFIG_HOME",
        str(tmp_path),
    )

    assert themes_dir() == (
        tmp_path
        / "arch-theme-manager"
        / "themes"
    )


def test_generated_directory(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "XDG_CONFIG_HOME",
        str(tmp_path),
    )

    assert generated_dir() == (
        tmp_path
        / "arch-theme-manager"
        / "generated"
    )


def test_state_directory_alias(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv(
        "XDG_STATE_HOME",
        str(tmp_path),
    )

    assert state_dir() == (
        tmp_path
        / "arch-theme-manager"
    )


def test_ensure_runtime_dirs_creates_paths(
    monkeypatch,
    tmp_path,
):
    config = tmp_path / "config"
    state = tmp_path / "state"
    runtime = tmp_path / "runtime"

    monkeypatch.setenv(
        "XDG_CONFIG_HOME",
        str(config),
    )

    monkeypatch.setenv(
        "XDG_STATE_HOME",
        str(state),
    )

    monkeypatch.setenv(
        "XDG_RUNTIME_DIR",
        str(runtime),
    )

    ensure_runtime_dirs()

    assert config_home().is_dir()
    assert themes_dir().is_dir()
    assert generated_dir().is_dir()
    assert state_dir().is_dir()
    assert runtime_home().is_dir()

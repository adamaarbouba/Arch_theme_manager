import os
from pathlib import Path


APP_NAME = "arch-theme-manager"


def config_home() -> Path:
    base = Path(
        os.environ.get(
            "XDG_CONFIG_HOME",
            Path.home() / ".config",
        )
    )

    return base / APP_NAME


def state_home() -> Path:
    base = Path(
        os.environ.get(
            "XDG_STATE_HOME",
            Path.home() / ".local/state",
        )
    )

    return base / APP_NAME


def runtime_home() -> Path:
    value = os.environ.get("XDG_RUNTIME_DIR")

    if value:
        return (
            Path(value)
            / APP_NAME
        )

    return (
        Path("/tmp")
        / f"{APP_NAME}-{os.getuid()}"
    )


def themes_dir() -> Path:
    return config_home() / "themes"


def generated_dir() -> Path:
    return config_home() / "generated"


def state_dir() -> Path:
    return state_home()


def ensure_runtime_dirs() -> None:
    config_home().mkdir(
        parents=True,
        exist_ok=True,
    )

    themes_dir().mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_dir().mkdir(
        parents=True,
        exist_ok=True,
    )

    state_dir().mkdir(
        parents=True,
        exist_ok=True,
    )

    runtime_home().mkdir(
        parents=True,
        exist_ok=True,
    )

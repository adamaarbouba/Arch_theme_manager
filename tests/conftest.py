import json

import pytest


@pytest.fixture
def valid_theme(tmp_path):
    wallpaper = tmp_path / "wallpaper.png"
    wallpaper.touch()

    return {
        "name": "test",
        "_theme_name": "test",
        "_theme_dir": tmp_path,
        "wallpaper": "wallpaper.png",
        "colors": {
            "background": "#111827",
            "surface": "#1F2937",
            "foreground": "#F9FAFB",
            "primary": "#8B5CF6",
            "secondary": "#38BDF8",
            "accent": "#F472B6",
        },
        "hyprpaper": {
            "fit_mode": "cover",
        },
        "window": {
            "rounding": 10,
            "rounding_power": 2,
            "opacity": 0.96,
            "border_size": 2,
        },
    }


@pytest.fixture
def write_theme():
    def _write_theme(root, name, data):
        directory = root / name
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        manifest = directory / "theme.json"

        manifest.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

        return directory

    return _write_theme

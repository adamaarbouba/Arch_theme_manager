import pytest

from arch_theme_manager.core.loader import (
    ThemeError,
    ThemeLoader,
)


def test_lists_installed_themes(
    tmp_path,
    write_theme,
):
    write_theme(
        tmp_path,
        "portal",
        {},
    )

    write_theme(
        tmp_path,
        "lucy",
        {},
    )

    loader = ThemeLoader(tmp_path)

    themes = loader.list_themes()

    assert set(themes) == {
        "portal",
        "lucy",
    }


def test_hidden_base_theme_not_listed(
    tmp_path,
    write_theme,
):
    write_theme(
        tmp_path,
        "_base",
        {},
    )

    write_theme(
        tmp_path,
        "portal",
        {},
    )

    loader = ThemeLoader(tmp_path)

    themes = loader.list_themes()

    assert "_base" not in themes
    assert "portal" in themes


def test_directory_without_manifest_not_listed(
    tmp_path,
):
    directory = tmp_path / "broken"
    directory.mkdir()

    loader = ThemeLoader(tmp_path)

    assert (
        "broken"
        not in loader.list_themes()
    )


def test_loads_theme(
    tmp_path,
    write_theme,
):
    write_theme(
        tmp_path,
        "portal",
        {
            "wallpaper": "wallpaper.png",
            "colors": {
                "primary": "#123456",
            },
        },
    )

    loader = ThemeLoader(tmp_path)

    theme = loader.load("portal")

    assert theme["wallpaper"] == "wallpaper.png"
    assert theme["colors"]["primary"] == "#123456"
    assert theme["_theme_name"] == "portal"


def test_inherits_base_theme(
    tmp_path,
    write_theme,
):
    write_theme(
        tmp_path,
        "_base",
        {
            "colors": {
                "background": "#111111",
                "surface": "#222222",
                "primary": "#333333",
            },
            "window": {
                "rounding": 10,
                "opacity": 0.90,
            },
        },
    )

    write_theme(
        tmp_path,
        "portal",
        {
            "extends": "_base",
            "colors": {
                "primary": "#ABCDEF",
            },
            "window": {
                "opacity": 0.95,
            },
        },
    )

    loader = ThemeLoader(tmp_path)

    theme = loader.load("portal")

    assert (
        theme["colors"]["background"]
        == "#111111"
    )

    assert (
        theme["colors"]["surface"]
        == "#222222"
    )

    assert (
        theme["colors"]["primary"]
        == "#ABCDEF"
    )

    assert (
        theme["window"]["rounding"]
        == 10
    )

    assert (
        theme["window"]["opacity"]
        == 0.95
    )


def test_child_does_not_destroy_nested_base_values(
    tmp_path,
    write_theme,
):
    write_theme(
        tmp_path,
        "_base",
        {
            "colors": {
                "background": "#111111",
                "surface": "#222222",
                "foreground": "#FFFFFF",
            },
        },
    )

    write_theme(
        tmp_path,
        "child",
        {
            "extends": "_base",
            "colors": {
                "surface": "#333333",
            },
        },
    )

    loader = ThemeLoader(tmp_path)

    theme = loader.load("child")

    assert (
        theme["colors"]["background"]
        == "#111111"
    )

    assert (
        theme["colors"]["surface"]
        == "#333333"
    )

    assert (
        theme["colors"]["foreground"]
        == "#FFFFFF"
    )


def test_missing_theme_raises_error(
    tmp_path,
):
    loader = ThemeLoader(tmp_path)

    with pytest.raises(ThemeError):
        loader.load(
            "does-not-exist"
        )


def test_circular_inheritance_raises_error(
    tmp_path,
    write_theme,
):
    write_theme(
        tmp_path,
        "alpha",
        {
            "extends": "beta",
        },
    )

    write_theme(
        tmp_path,
        "beta",
        {
            "extends": "alpha",
        },
    )

    loader = ThemeLoader(tmp_path)

    with pytest.raises(ThemeError):
        loader.load("alpha")

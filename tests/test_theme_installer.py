import json

import pytest

from arch_theme_manager.core.theme_installer import (
    ThemeInstallError,
    ThemeInstaller,
)
from arch_theme_manager.core.validator import (
    ThemeValidator,
)


def create_theme(
    root,
    name="source-theme",
    *,
    primary="#8B5CF6",
):
    theme_dir = root / name

    theme_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    wallpaper = (
        theme_dir / "wallpaper.png"
    )

    wallpaper.write_bytes(b"test")

    manifest = {
        "name": name,
        "wallpaper": "wallpaper.png",
        "colors": {
            "background": "#111827",
            "surface": "#1F2937",
            "foreground": "#F9FAFB",
            "primary": primary,
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

    (
        theme_dir / "theme.json"
    ).write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    return theme_dir


def make_installer(tmp_path):
    themes_dir = (
        tmp_path / "installed"
    )

    return (
        ThemeInstaller(
            themes_dir,
            ThemeValidator(),
        ),
        themes_dir,
    )


def test_installs_valid_theme(
    tmp_path,
):
    source = create_theme(
        tmp_path / "source"
    )

    installer, themes_dir = (
        make_installer(tmp_path)
    )

    name = installer.install(source)

    assert name == "source-theme"

    installed = (
        themes_dir
        / "source-theme"
    )

    assert installed.is_dir()

    assert (
        installed / "theme.json"
    ).is_file()

    assert (
        installed / "wallpaper.png"
    ).is_file()


def test_custom_install_name(
    tmp_path,
):
    source = create_theme(
        tmp_path / "source"
    )

    installer, themes_dir = (
        make_installer(tmp_path)
    )

    name = installer.install(
        source,
        name="portal",
    )

    assert name == "portal"

    assert (
        themes_dir / "portal"
    ).is_dir()


def test_missing_source_fails(
    tmp_path,
):
    installer, _ = (
        make_installer(tmp_path)
    )

    with pytest.raises(
        ThemeInstallError
    ):
        installer.install(
            tmp_path / "missing"
        )


def test_missing_manifest_fails(
    tmp_path,
):
    source = (
        tmp_path
        / "broken-theme"
    )

    source.mkdir()

    installer, _ = (
        make_installer(tmp_path)
    )

    with pytest.raises(
        ThemeInstallError
    ):
        installer.install(source)


@pytest.mark.parametrize(
    "name",
    [
        "",
        "_private",
        "../escape",
        "bad name",
        "bad/name",
    ],
)
def test_invalid_names_fail(
    tmp_path,
    name,
):
    source = create_theme(
        tmp_path / "source"
    )

    installer, _ = (
        make_installer(tmp_path)
    )

    with pytest.raises(
        ThemeInstallError
    ):
        installer.install(
            source,
            name=name,
        )


def test_duplicate_theme_fails_without_force(
    tmp_path,
):
    source = create_theme(
        tmp_path / "source"
    )

    installer, _ = (
        make_installer(tmp_path)
    )

    installer.install(
        source,
        name="portal",
    )

    with pytest.raises(
        ThemeInstallError
    ):
        installer.install(
            source,
            name="portal",
        )


def test_force_replaces_existing_theme(
    tmp_path,
):
    first = create_theme(
        tmp_path / "first",
        primary="#111111",
    )

    second = create_theme(
        tmp_path / "second",
        primary="#ABCDEF",
    )

    installer, themes_dir = (
        make_installer(tmp_path)
    )

    installer.install(
        first,
        name="portal",
    )

    installer.install(
        second,
        name="portal",
        force=True,
    )

    manifest = json.loads(
        (
            themes_dir
            / "portal"
            / "theme.json"
        ).read_text(
            encoding="utf-8",
        )
    )

    assert (
        manifest["colors"]["primary"]
        == "#ABCDEF"
    )


def test_invalid_theme_is_not_installed(
    tmp_path,
):
    source = create_theme(
        tmp_path / "source",
        primary="not-a-color",
    )

    installer, themes_dir = (
        make_installer(tmp_path)
    )

    with pytest.raises(
        ThemeInstallError
    ):
        installer.install(
            source,
            name="broken",
        )

    assert not (
        themes_dir / "broken"
    ).exists()


def test_failed_force_keeps_existing_theme(
    tmp_path,
):
    valid = create_theme(
        tmp_path / "valid",
        primary="#123456",
    )

    invalid = create_theme(
        tmp_path / "invalid",
        primary="invalid",
    )

    installer, themes_dir = (
        make_installer(tmp_path)
    )

    installer.install(
        valid,
        name="portal",
    )

    with pytest.raises(
        ThemeInstallError
    ):
        installer.install(
            invalid,
            name="portal",
            force=True,
        )

    manifest = json.loads(
        (
            themes_dir
            / "portal"
            / "theme.json"
        ).read_text(
            encoding="utf-8",
        )
    )

    assert (
        manifest["colors"]["primary"]
        == "#123456"
    )


def test_no_staging_directory_left_after_install(
    tmp_path,
):
    source = create_theme(
        tmp_path / "source"
    )

    installer, themes_dir = (
        make_installer(tmp_path)
    )

    installer.install(source)

    leftovers = [
        path
        for path
        in themes_dir.iterdir()
        if path.name.startswith(
            "_install-"
        )
    ]

    assert leftovers == []

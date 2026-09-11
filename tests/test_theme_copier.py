import json

import pytest

from arch_theme_manager.core.theme_copier import (
    ThemeCopier,
    ThemeCopyError,
)
from arch_theme_manager.core.validator import (
    ThemeValidator,
)


def create_theme(
    root,
    name,
    *,
    primary="#8B5CF6",
):
    directory = (
        root / name
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        directory
        / "wallpaper.png"
    ).write_bytes(
        b"wallpaper"
    )

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
        directory
        / "theme.json"
    ).write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    return directory


def make_copier(tmp_path):
    themes_dir = (
        tmp_path
        / "themes"
    )

    copier = ThemeCopier(
        themes_dir,
        ThemeValidator(),
    )

    return (
        copier,
        themes_dir,
    )


def test_copies_theme(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    result = copier.copy(
        "portal",
        "gateway",
    )

    assert result == "gateway"

    assert (
        themes_dir
        / "portal"
    ).is_dir()

    assert (
        themes_dir
        / "gateway"
    ).is_dir()


def test_copy_updates_manifest_name(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    copier.copy(
        "portal",
        "gateway",
    )

    manifest = json.loads(
        (
            themes_dir
            / "gateway"
            / "theme.json"
        ).read_text(
            encoding="utf-8",
        )
    )

    assert (
        manifest["name"]
        == "gateway"
    )


def test_source_manifest_is_unchanged(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    copier.copy(
        "portal",
        "gateway",
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
        manifest["name"]
        == "portal"
    )


def test_wallpaper_is_copied(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    copier.copy(
        "portal",
        "gateway",
    )

    assert (
        themes_dir
        / "gateway"
        / "wallpaper.png"
    ).is_file()


def test_missing_source_fails(
    tmp_path,
):
    copier, _ = (
        make_copier(tmp_path)
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "missing",
            "new-theme",
        )


def test_existing_destination_fails(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    create_theme(
        themes_dir,
        "gateway",
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "portal",
            "gateway",
        )


def test_identical_names_fail(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "portal",
            "portal",
        )


@pytest.mark.parametrize(
    "name",
    [
        "",
        "_base",
        "../escape",
        "bad/name",
        "bad name",
    ],
)
def test_invalid_destination_names_fail(
    tmp_path,
    name,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "portal",
            name,
        )


def test_internal_source_is_refused(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "_base",
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "_base",
            "new-base",
        )


def test_missing_manifest_fails(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    (
        themes_dir
        / "broken"
    ).mkdir(
        parents=True,
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "broken",
            "copy",
        )


def test_symlinked_source_is_refused(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    real = create_theme(
        tmp_path,
        "real",
    )

    themes_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    link = (
        themes_dir
        / "linked"
    )

    link.symlink_to(
        real,
        target_is_directory=True,
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "linked",
            "copy",
        )

    assert link.is_symlink()
    assert real.is_dir()


def test_invalid_source_theme_is_not_copied(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "broken",
        primary="invalid-color",
    )

    with pytest.raises(
        ThemeCopyError
    ):
        copier.copy(
            "broken",
            "copy",
        )

    assert not (
        themes_dir
        / "copy"
    ).exists()


def test_no_staging_directory_left(
    tmp_path,
):
    copier, themes_dir = (
        make_copier(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    copier.copy(
        "portal",
        "gateway",
    )

    leftovers = [
        path
        for path
        in themes_dir.iterdir()
        if path.name.startswith(
            "_copy-"
        )
    ]

    assert leftovers == []

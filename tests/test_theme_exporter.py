import json

import pytest

from arch_theme_manager.core.theme_exporter import (
    ThemeExporter,
    ThemeExportError,
)
from arch_theme_manager.core.validator import (
    ThemeValidator,
)


def create_theme(
    root,
    name="portal",
    *,
    primary="#8B5CF6",
):
    directory = root / name

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


def make_exporter(tmp_path):
    themes_dir = (
        tmp_path
        / "themes"
    )

    exporter = ThemeExporter(
        themes_dir,
        ThemeValidator(),
    )

    return (
        exporter,
        themes_dir,
    )


def test_exports_theme(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    export_root = (
        tmp_path / "exports"
    )

    result = exporter.export(
        "portal",
        export_root,
    )

    assert result == (
        export_root / "portal"
    )

    assert result.is_dir()


def test_export_copies_manifest(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    result = exporter.export(
        "portal",
        tmp_path / "exports",
    )

    assert (
        result / "theme.json"
    ).is_file()


def test_export_copies_wallpaper(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    result = exporter.export(
        "portal",
        tmp_path / "exports",
    )

    assert (
        result / "wallpaper.png"
    ).is_file()


def test_source_is_unchanged(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    source = create_theme(
        themes_dir,
        "portal",
    )

    exporter.export(
        "portal",
        tmp_path / "exports",
    )

    assert source.is_dir()

    assert (
        source / "theme.json"
    ).is_file()


def test_missing_theme_fails(
    tmp_path,
):
    exporter, _ = (
        make_exporter(tmp_path)
    )

    with pytest.raises(
        ThemeExportError
    ):
        exporter.export(
            "missing",
            tmp_path / "exports",
        )


def test_existing_destination_fails(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    export_root = (
        tmp_path / "exports"
    )

    exporter.export(
        "portal",
        export_root,
    )

    with pytest.raises(
        ThemeExportError
    ):
        exporter.export(
            "portal",
            export_root,
        )


def test_force_replaces_existing_export(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    source = create_theme(
        themes_dir,
        "portal",
    )

    export_root = (
        tmp_path / "exports"
    )

    exporter.export(
        "portal",
        export_root,
    )

    marker = (
        export_root
        / "portal"
        / "old-file.txt"
    )

    marker.write_text(
        "old",
        encoding="utf-8",
    )

    (
        source / "new-file.txt"
    ).write_text(
        "new",
        encoding="utf-8",
    )

    exporter.export(
        "portal",
        export_root,
        force=True,
    )

    assert not marker.exists()

    assert (
        export_root
        / "portal"
        / "new-file.txt"
    ).is_file()


def test_invalid_theme_fails(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "broken",
        primary="invalid",
    )

    with pytest.raises(
        ThemeExportError
    ):
        exporter.export(
            "broken",
            tmp_path / "exports",
        )


def test_internal_theme_is_refused(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "_base",
    )

    with pytest.raises(
        ThemeExportError
    ):
        exporter.export(
            "_base",
            tmp_path / "exports",
        )


def test_symlinked_theme_is_refused(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
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
        themes_dir / "linked"
    )

    link.symlink_to(
        real,
        target_is_directory=True,
    )

    with pytest.raises(
        ThemeExportError
    ):
        exporter.export(
            "linked",
            tmp_path / "exports",
        )


def test_force_refuses_symlink_destination(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    export_root = (
        tmp_path / "exports"
    )

    export_root.mkdir()

    real = (
        tmp_path / "real"
    )

    real.mkdir()

    destination = (
        export_root / "portal"
    )

    destination.symlink_to(
        real,
        target_is_directory=True,
    )

    with pytest.raises(
        ThemeExportError
    ):
        exporter.export(
            "portal",
            export_root,
            force=True,
        )


def test_no_staging_files_remain(
    tmp_path,
):
    exporter, themes_dir = (
        make_exporter(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    export_root = (
        tmp_path / "exports"
    )

    exporter.export(
        "portal",
        export_root,
    )

    leftovers = [
        item
        for item in export_root.iterdir()
        if item.name.startswith(
            ".arch-theme-"
        )
    ]

    assert leftovers == []

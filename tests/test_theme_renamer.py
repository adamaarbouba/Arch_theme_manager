import json

import pytest

from arch_theme_manager.core.state import ThemeState
from arch_theme_manager.core.theme_renamer import (
    ThemeRenameError,
    ThemeRenamer,
)


def create_theme(
    root,
    name,
):
    theme_dir = root / name

    theme_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        theme_dir / "theme.json"
    ).write_text(
        json.dumps(
            {
                "name": name,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return theme_dir


def make_renamer(tmp_path):
    themes_dir = tmp_path / "themes"

    state = ThemeState(
        tmp_path / "state"
    )

    renamer = ThemeRenamer(
        themes_dir,
        state,
    )

    return (
        renamer,
        themes_dir,
        state,
    )


def test_renames_theme(tmp_path):
    renamer, themes_dir, _ = (
        make_renamer(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    result = renamer.rename(
        "portal",
        "gateway",
    )

    assert result == "gateway"

    assert not (
        themes_dir / "portal"
    ).exists()

    assert (
        themes_dir / "gateway"
    ).is_dir()


def test_updates_manifest_name(tmp_path):
    renamer, themes_dir, _ = (
        make_renamer(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    renamer.rename(
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


def test_updates_active_state(tmp_path):
    renamer, themes_dir, state = (
        make_renamer(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    state.save("portal")

    renamer.rename(
        "portal",
        "gateway",
    )

    assert state.current() == "gateway"


def test_updates_previous_state(tmp_path):
    renamer, themes_dir, state = (
        make_renamer(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    create_theme(
        themes_dir,
        "lucy",
    )

    state.save("portal")
    state.save("lucy")

    renamer.rename(
        "portal",
        "gateway",
    )

    assert state.current() == "lucy"
    assert state.previous() == "gateway"


def test_missing_theme_fails(tmp_path):
    renamer, _, _ = (
        make_renamer(tmp_path)
    )

    with pytest.raises(
        ThemeRenameError
    ):
        renamer.rename(
            "missing",
            "new-name",
        )


def test_destination_existing_fails(tmp_path):
    renamer, themes_dir, _ = (
        make_renamer(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    create_theme(
        themes_dir,
        "lucy",
    )

    with pytest.raises(
        ThemeRenameError
    ):
        renamer.rename(
            "portal",
            "lucy",
        )


def test_same_name_fails(tmp_path):
    renamer, themes_dir, _ = (
        make_renamer(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    with pytest.raises(
        ThemeRenameError
    ):
        renamer.rename(
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
def test_invalid_new_names_fail(
    tmp_path,
    name,
):
    renamer, themes_dir, _ = (
        make_renamer(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    with pytest.raises(
        ThemeRenameError
    ):
        renamer.rename(
            "portal",
            name,
        )


def test_missing_manifest_fails(tmp_path):
    renamer, themes_dir, _ = (
        make_renamer(tmp_path)
    )

    (
        themes_dir
        / "broken"
    ).mkdir(
        parents=True,
    )

    with pytest.raises(
        ThemeRenameError
    ):
        renamer.rename(
            "broken",
            "fixed",
        )


def test_symlink_theme_is_refused(tmp_path):
    renamer, themes_dir, _ = (
        make_renamer(tmp_path)
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
        ThemeRenameError
    ):
        renamer.rename(
            "linked",
            "renamed",
        )

    assert link.is_symlink()
    assert real.exists()

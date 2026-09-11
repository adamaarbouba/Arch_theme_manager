import json

import pytest

from arch_theme_manager.core.state import ThemeState
from arch_theme_manager.core.theme_remover import (
    ThemeRemoveError,
    ThemeRemover,
)


def create_theme(
    root,
    name="portal",
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
            }
        ),
        encoding="utf-8",
    )

    return theme_dir


def make_remover(tmp_path):
    themes_dir = (
        tmp_path / "themes"
    )

    state = ThemeState(
        tmp_path / "state"
    )

    remover = ThemeRemover(
        themes_dir,
        state,
    )

    return (
        remover,
        themes_dir,
        state,
    )


def test_removes_existing_theme(
    tmp_path,
):
    remover, themes_dir, _ = (
        make_remover(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    result = remover.remove(
        "portal"
    )

    assert result == "portal"

    assert not (
        themes_dir / "portal"
    ).exists()


def test_missing_theme_fails(
    tmp_path,
):
    remover, _, _ = (
        make_remover(tmp_path)
    )

    with pytest.raises(
        ThemeRemoveError
    ):
        remover.remove(
            "missing"
        )


def test_active_theme_cannot_be_removed(
    tmp_path,
):
    remover, themes_dir, state = (
        make_remover(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    state.save(
        "portal"
    )

    with pytest.raises(
        ThemeRemoveError
    ):
        remover.remove(
            "portal"
        )

    assert (
        themes_dir / "portal"
    ).is_dir()

    assert (
        state.current()
        == "portal"
    )


def test_force_removes_active_theme(
    tmp_path,
):
    remover, themes_dir, state = (
        make_remover(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    state.save(
        "portal"
    )

    remover.remove(
        "portal",
        force=True,
    )

    assert not (
        themes_dir / "portal"
    ).exists()

    assert state.current() is None
    assert state.previous() is None


def test_removing_inactive_theme_keeps_state(
    tmp_path,
):
    remover, themes_dir, state = (
        make_remover(tmp_path)
    )

    create_theme(
        themes_dir,
        "portal",
    )

    create_theme(
        themes_dir,
        "lucy",
    )

    state.save(
        "portal"
    )

    remover.remove(
        "lucy"
    )

    assert (
        state.current()
        == "portal"
    )


def test_internal_theme_cannot_be_removed(
    tmp_path,
):
    remover, themes_dir, _ = (
        make_remover(tmp_path)
    )

    create_theme(
        themes_dir,
        "_base",
    )

    with pytest.raises(
        ThemeRemoveError
    ):
        remover.remove(
            "_base"
        )

    assert (
        themes_dir / "_base"
    ).is_dir()


@pytest.mark.parametrize(
    "name",
    [
        "",
        "../portal",
        "bad/name",
        "bad name",
    ],
)
def test_invalid_names_fail(
    tmp_path,
    name,
):
    remover, _, _ = (
        make_remover(tmp_path)
    )

    with pytest.raises(
        ThemeRemoveError
    ):
        remover.remove(
            name
        )


def test_directory_without_manifest_fails(
    tmp_path,
):
    remover, themes_dir, _ = (
        make_remover(tmp_path)
    )

    broken = (
        themes_dir / "broken"
    )

    broken.mkdir(
        parents=True,
    )

    with pytest.raises(
        ThemeRemoveError
    ):
        remover.remove(
            "broken"
        )

    assert broken.exists()


def test_symlinked_theme_is_refused(
    tmp_path,
):
    remover, themes_dir, _ = (
        make_remover(tmp_path)
    )

    real_theme = create_theme(
        tmp_path,
        "real-theme",
    )

    themes_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    link = (
        themes_dir
        / "linked-theme"
    )

    link.symlink_to(
        real_theme,
        target_is_directory=True,
    )

    with pytest.raises(
        ThemeRemoveError
    ):
        remover.remove(
            "linked-theme"
        )

    assert link.is_symlink()
    assert real_theme.is_dir()

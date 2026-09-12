import pytest

from arch_theme_manager.core.orchestrator import (
    ThemeApplyError,
    ThemeOrchestrator,
)
from arch_theme_manager.core.state import (
    ThemeState,
)


class FakeLoader:
    def __init__(
        self,
        themes,
    ):
        self.themes = themes

    def load(
        self,
        name,
    ):
        return self.themes[name]


class FakeValidator:
    def __init__(self):
        self.validated = []

    def validate(
        self,
        theme,
    ):
        self.validated.append(theme["_theme_name"])


class FailingValidator:
    def validate(
        self,
        theme,
    ):
        raise ValueError("invalid theme")


class RecordingAdapter:
    def __init__(
        self,
        name,
        calls,
    ):
        self.name = name
        self.calls = calls

    def apply(
        self,
        theme,
    ):
        self.calls.append(
            (
                self.name,
                theme["_theme_name"],
            )
        )


class FailingAdapter:
    def __init__(
        self,
        name,
        calls,
    ):
        self.name = name
        self.calls = calls

    def apply(
        self,
        theme,
    ):
        self.calls.append(
            (
                self.name,
                theme["_theme_name"],
            )
        )

        raise RuntimeError("adapter failed")


def make_orchestrator(
    loader,
    validator,
    state,
):
    orchestrator = ThemeOrchestrator.__new__(ThemeOrchestrator)

    orchestrator.loader = loader
    orchestrator.validator = validator
    orchestrator.state = state
    orchestrator.adapters = []

    return orchestrator


def test_default_adapter_chain_includes_neovim(
    tmp_path,
):
    loader = FakeLoader({})
    validator = FakeValidator()

    state = ThemeState(tmp_path / "state")

    orchestrator = ThemeOrchestrator(
        loader=loader,
        validator=validator,
        state=state,
        generated_dir=(tmp_path / "generated"),
    )

    adapter_names = [adapter.__class__.__name__ for adapter in orchestrator.adapters]

    assert "NeovimAdapter" in (adapter_names)


def test_neovim_adapter_position_in_chain(
    tmp_path,
):
    loader = FakeLoader({})
    validator = FakeValidator()

    state = ThemeState(tmp_path / "state")

    orchestrator = ThemeOrchestrator(
        loader=loader,
        validator=validator,
        state=state,
        generated_dir=(tmp_path / "generated"),
    )

    adapter_names = [adapter.__class__.__name__ for adapter in orchestrator.adapters]

    assert adapter_names == [
        "HyprpaperAdapter",
        "WaybarAdapter",
        "SwayNCAdapter",
        "HyprlandAdapter",
        "KittyAdapter",
        "ZshAdapter",
        "NeovimAdapter",
        "HyprlockAdapter",
        "HyprtoolkitAdapter",
    ]


def test_apply_validates_theme_before_apply(
    tmp_path,
):
    theme = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": theme,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    applied = []

    orchestrator._apply_adapters = lambda loaded_theme: applied.append(
        loaded_theme["_theme_name"]
    )

    orchestrator.apply("portal")

    assert validator.validated == ["portal"]

    assert applied == ["portal"]


def test_successful_apply_saves_state(
    tmp_path,
):
    theme = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": theme,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    orchestrator._apply_adapters = lambda theme: None

    orchestrator.apply("portal")

    assert state.current() == "portal"


def test_failed_validation_does_not_apply(
    tmp_path,
):
    theme = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": theme,
        }
    )

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        FailingValidator(),
        state,
    )

    touched = []

    orchestrator._apply_adapters = lambda theme: touched.append(True)

    with pytest.raises(Exception):
        orchestrator.apply("portal")

    assert touched == []

    assert state.current() is None


def test_failed_apply_keeps_previous_state(
    tmp_path,
):
    portal = {
        "_theme_name": "portal",
    }

    lucy = {
        "_theme_name": "lucy",
    }

    loader = FakeLoader(
        {
            "portal": portal,
            "lucy": lucy,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    state.save("portal")

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    rollback_calls = []

    def fail_apply(
        theme,
    ):
        raise RuntimeError("adapter failed")

    orchestrator._apply_adapters = fail_apply

    orchestrator._rollback = lambda name: rollback_calls.append(name)

    with pytest.raises(ThemeApplyError):
        orchestrator.apply("lucy")

    assert state.current() == "portal"

    assert rollback_calls == ["portal"]


def test_previous_state_updates_after_success(
    tmp_path,
):
    themes = {
        "portal": {
            "_theme_name": "portal",
        },
        "lucy": {
            "_theme_name": "lucy",
        },
    }

    loader = FakeLoader(themes)

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    state.save("portal")

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    orchestrator._apply_adapters = lambda theme: None

    orchestrator.apply("lucy")

    assert state.current() == "lucy"

    assert state.previous() == "portal"


def test_apply_runs_every_adapter(
    tmp_path,
):
    theme = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": theme,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    calls = []

    orchestrator.adapters = [
        RecordingAdapter(
            "HyprlandAdapter",
            calls,
        ),
        RecordingAdapter(
            "KittyAdapter",
            calls,
        ),
        RecordingAdapter(
            "NeovimAdapter",
            calls,
        ),
    ]

    orchestrator.apply("portal")

    assert calls == [
        (
            "HyprlandAdapter",
            "portal",
        ),
        (
            "KittyAdapter",
            "portal",
        ),
        (
            "NeovimAdapter",
            "portal",
        ),
    ]


def test_neovim_participates_in_apply_chain(
    tmp_path,
):
    theme = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": theme,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    calls = []

    orchestrator.adapters = [
        RecordingAdapter(
            "NeovimAdapter",
            calls,
        ),
    ]

    orchestrator.apply("portal")

    assert calls == [
        (
            "NeovimAdapter",
            "portal",
        ),
    ]


def test_rollback_runs_every_adapter(
    tmp_path,
):
    portal = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": portal,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    calls = []

    orchestrator.adapters = [
        RecordingAdapter(
            "HyprlandAdapter",
            calls,
        ),
        RecordingAdapter(
            "KittyAdapter",
            calls,
        ),
        RecordingAdapter(
            "NeovimAdapter",
            calls,
        ),
    ]

    result = orchestrator._rollback("portal")

    assert calls == [
        (
            "HyprlandAdapter",
            "portal",
        ),
        (
            "KittyAdapter",
            "portal",
        ),
        (
            "NeovimAdapter",
            "portal",
        ),
    ]

    assert result == ("Rolled back successfully to 'portal'.")


def test_neovim_participates_in_rollback_chain(
    tmp_path,
):
    portal = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": portal,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    calls = []

    orchestrator.adapters = [
        RecordingAdapter(
            "NeovimAdapter",
            calls,
        ),
    ]

    result = orchestrator._rollback("portal")

    assert calls == [
        (
            "NeovimAdapter",
            "portal",
        ),
    ]

    assert result == ("Rolled back successfully to 'portal'.")


def test_rollback_continues_after_adapter_failure(
    tmp_path,
):
    portal = {
        "_theme_name": "portal",
    }

    loader = FakeLoader(
        {
            "portal": portal,
        }
    )

    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    calls = []

    orchestrator.adapters = [
        FailingAdapter(
            "KittyAdapter",
            calls,
        ),
        RecordingAdapter(
            "NeovimAdapter",
            calls,
        ),
        RecordingAdapter(
            "HyprlockAdapter",
            calls,
        ),
    ]

    result = orchestrator._rollback("portal")

    assert calls == [
        (
            "KittyAdapter",
            "portal",
        ),
        (
            "NeovimAdapter",
            "portal",
        ),
        (
            "HyprlockAdapter",
            "portal",
        ),
    ]

    assert "incomplete" in result

    assert "FailingAdapter" in result


def test_rollback_without_previous_theme(
    tmp_path,
):
    loader = FakeLoader({})
    validator = FakeValidator()

    state = ThemeState(tmp_path)

    orchestrator = make_orchestrator(
        loader,
        validator,
        state,
    )

    result = orchestrator._rollback(None)

    assert result == ("No previous active theme was available for rollback.")

import pytest

from arch_theme_manager.core.orchestrator import (
    ThemeApplyError,
    ThemeOrchestrator,
)
from arch_theme_manager.core.state import (
    ThemeState,
)


class FakeLoader:
    def __init__(self, themes):
        self.themes = themes

    def load(self, name):
        return self.themes[name]


class FakeValidator:
    def __init__(self):
        self.validated = []

    def validate(self, theme):
        self.validated.append(
            theme["_theme_name"]
        )


class FailingValidator:
    def validate(self, theme):
        raise ValueError(
            "invalid theme"
        )


def make_orchestrator(
    loader,
    validator,
    state,
):
    orchestrator = (
        ThemeOrchestrator.__new__(
            ThemeOrchestrator
        )
    )

    orchestrator.loader = loader
    orchestrator.validator = validator
    orchestrator.state = state

    return orchestrator


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

    orchestrator._apply_adapters = (
        lambda loaded_theme:
        applied.append(
            loaded_theme[
                "_theme_name"
            ]
        )
    )

    orchestrator.apply("portal")

    assert validator.validated == [
        "portal"
    ]

    assert applied == [
        "portal"
    ]


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

    orchestrator._apply_adapters = (
        lambda theme: None
    )

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

    orchestrator._apply_adapters = (
        lambda theme:
        touched.append(True)
    )

    with pytest.raises(Exception):
        orchestrator.apply(
            "portal"
        )

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

    def fail_apply(theme):
        raise RuntimeError(
            "adapter failed"
        )

    orchestrator._apply_adapters = (
        fail_apply
    )

    orchestrator._rollback = (
        lambda name:
        rollback_calls.append(name)
    )

    with pytest.raises(
        ThemeApplyError
    ):
        orchestrator.apply("lucy")

    assert state.current() == "portal"

    assert rollback_calls == [
        "portal"
    ]


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

    orchestrator._apply_adapters = (
        lambda theme: None
    )

    orchestrator.apply("lucy")

    assert state.current() == "lucy"
    assert state.previous() == "portal"

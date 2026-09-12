from pathlib import Path

from ..adapters.hyprland import HyprlandAdapter
from ..adapters.hyprlock import HyprlockAdapter
from ..adapters.hyprpaper import HyprpaperAdapter
from ..adapters.hyprtoolkit import HyprtoolkitAdapter
from ..adapters.kitty import KittyAdapter
from ..adapters.neovim import NeovimAdapter
from ..adapters.swaync import SwayNCAdapter
from ..adapters.waybar import WaybarAdapter
from ..adapters.zsh import ZshAdapter

from .loader import ThemeLoader
from .state import ThemeState
from .validator import ThemeValidator


class ThemeApplyError(Exception):
    pass


class ThemeOrchestrator:
    def __init__(
        self,
        loader: ThemeLoader,
        validator: ThemeValidator,
        state: ThemeState,
        generated_dir: Path,
    ):
        self.loader = loader
        self.validator = validator
        self.state = state

        self.adapters = [
            HyprpaperAdapter(),
            WaybarAdapter(generated_dir),
            SwayNCAdapter(generated_dir),
            HyprlandAdapter(generated_dir),
            KittyAdapter(generated_dir),
            ZshAdapter(generated_dir),
            NeovimAdapter(generated_dir),
            HyprlockAdapter(generated_dir),
            HyprtoolkitAdapter(generated_dir),
        ]

    def apply(
        self,
        theme_name: str,
    ) -> dict:
        # Theme currently known to be active.
        current_theme_name = self.state.current()

        # Load and validate before touching the desktop.
        theme = self.loader.load(theme_name)

        self.validator.validate(theme)

        try:
            self._apply_adapters(theme)

        except Exception as exc:
            rollback_message = self._rollback(current_theme_name)

            raise ThemeApplyError(
                f"Failed to apply theme '{theme_name}': {exc}. {rollback_message}"
            ) from exc

        # State is updated ONLY after every adapter succeeds.
        self.state.save(theme_name)

        return theme

    def _apply_adapters(
        self,
        theme: dict,
    ) -> None:
        for adapter in self.adapters:
            try:
                adapter.apply(theme)

            except Exception as exc:
                raise ThemeApplyError(f"{adapter.__class__.__name__}: {exc}") from exc

    def _rollback(
        self,
        theme_name: str | None,
    ) -> str:
        if theme_name is None:
            return "No previous active theme was available for rollback."

        try:
            theme = self.loader.load(theme_name)

            self.validator.validate(theme)

        except Exception as exc:
            return f"Rollback could not load theme '{theme_name}': {exc}"

        rollback_errors = []

        # Do not stop rollback because one adapter fails.
        # Restore everything that we still can.
        for adapter in self.adapters:
            try:
                adapter.apply(theme)

            except Exception as exc:
                rollback_errors.append(f"{adapter.__class__.__name__}: {exc}")

        if rollback_errors:
            errors = "; ".join(rollback_errors)

            return f"Rollback to '{theme_name}' was incomplete: {errors}"

        return f"Rolled back successfully to '{theme_name}'."

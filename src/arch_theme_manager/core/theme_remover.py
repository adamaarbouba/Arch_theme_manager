from pathlib import Path
import re
import shutil


class ThemeRemoveError(Exception):
    pass


class ThemeRemover:
    NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
    )

    def __init__(
        self,
        themes_dir: Path,
        state,
    ):
        self.themes_dir = themes_dir
        self.state = state

    def remove(
        self,
        name: str,
        force: bool = False,
    ) -> str:
        self._validate_name(name)

        target = (
            self.themes_dir
            / name
        )

        if target.is_symlink():
            raise ThemeRemoveError(
                f"Refusing to remove symlinked theme '{name}'"
            )

        if not target.is_dir():
            raise ThemeRemoveError(
                f"Theme '{name}' does not exist"
            )

        manifest = (
            target / "theme.json"
        )

        if not manifest.is_file():
            raise ThemeRemoveError(
                f"Theme '{name}' has no theme.json"
            )

        current = self.state.current()

        if current == name and not force:
            raise ThemeRemoveError(
                f"Theme '{name}' is currently active. "
                f"Use --force to remove it."
            )

        try:
            shutil.rmtree(target)

        except OSError as exc:
            raise ThemeRemoveError(
                f"Could not remove theme '{name}': {exc}"
            ) from exc

        if current == name:
            self.state.clear()

        return name

    def _validate_name(
        self,
        name: str,
    ) -> None:
        if not name:
            raise ThemeRemoveError(
                "Theme name cannot be empty"
            )

        if name.startswith("_"):
            raise ThemeRemoveError(
                "Internal themes cannot be removed "
                "with remove-theme"
            )

        if not self.NAME_PATTERN.fullmatch(
            name
        ):
            raise ThemeRemoveError(
                "Invalid theme name"
            )

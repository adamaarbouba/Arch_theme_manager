import json
from pathlib import Path
import re


class ThemeRenameError(Exception):
    pass


class ThemeRenamer:
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

    def rename(
        self,
        old_name: str,
        new_name: str,
    ) -> str:
        self._validate_name(old_name)
        self._validate_name(new_name)

        if old_name == new_name:
            raise ThemeRenameError(
                "Old and new theme names are identical"
            )

        source = (
            self.themes_dir
            / old_name
        )

        destination = (
            self.themes_dir
            / new_name
        )

        if source.is_symlink():
            raise ThemeRenameError(
                f"Refusing to rename symlinked theme "
                f"'{old_name}'"
            )

        if not source.is_dir():
            raise ThemeRenameError(
                f"Theme '{old_name}' does not exist"
            )

        if destination.exists():
            raise ThemeRenameError(
                f"Theme '{new_name}' already exists"
            )

        manifest_path = (
            source
            / "theme.json"
        )

        if not manifest_path.is_file():
            raise ThemeRenameError(
                f"Theme '{old_name}' has no theme.json"
            )

        try:
            original_manifest = (
                manifest_path.read_text(
                    encoding="utf-8",
                )
            )

            manifest = json.loads(
                original_manifest
            )

        except (
            OSError,
            json.JSONDecodeError,
        ) as exc:
            raise ThemeRenameError(
                f"Could not read theme manifest: {exc}"
            ) from exc

        if not isinstance(manifest, dict):
            raise ThemeRenameError(
                "Theme manifest must contain a JSON object"
            )

        manifest["name"] = new_name

        try:
            temporary = (
                manifest_path
                .with_suffix(".tmp")
            )

            temporary.write_text(
                json.dumps(
                    manifest,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            temporary.replace(
                manifest_path
            )

            source.rename(
                destination
            )

            self.state.rename_theme(
                old_name,
                new_name,
            )

        except Exception as exc:
            if destination.exists():
                try:
                    destination.rename(
                        source
                    )
                except OSError:
                    pass

            if source.is_dir():
                try:
                    (
                        source
                        / "theme.json"
                    ).write_text(
                        original_manifest,
                        encoding="utf-8",
                    )
                except OSError:
                    pass

            raise ThemeRenameError(
                f"Could not rename theme "
                f"'{old_name}' to '{new_name}': {exc}"
            ) from exc

        return new_name

    def _validate_name(
        self,
        name: str,
    ) -> None:
        if not name:
            raise ThemeRenameError(
                "Theme name cannot be empty"
            )

        if name.startswith("_"):
            raise ThemeRenameError(
                "Internal themes cannot be renamed"
            )

        if not self.NAME_PATTERN.fullmatch(name):
            raise ThemeRenameError(
                "Invalid theme name"
            )

import json
from pathlib import Path
import re
import shutil
import uuid

from .loader import ThemeLoader
from .validator import ThemeValidator


class ThemeCopyError(Exception):
    pass


class ThemeCopier:
    NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
    )

    def __init__(
        self,
        themes_dir: Path,
        validator: ThemeValidator,
    ):
        self.themes_dir = themes_dir
        self.validator = validator

    def copy(
        self,
        source_name: str,
        new_name: str,
    ) -> str:
        self._validate_name(
            source_name
        )

        self._validate_name(
            new_name
        )

        if source_name == new_name:
            raise ThemeCopyError(
                "Source and destination "
                "theme names are identical"
            )

        source = (
            self.themes_dir
            / source_name
        )

        destination = (
            self.themes_dir
            / new_name
        )

        if source.is_symlink():
            raise ThemeCopyError(
                f"Refusing to copy "
                f"symlinked theme "
                f"'{source_name}'"
            )

        if not source.is_dir():
            raise ThemeCopyError(
                f"Theme '{source_name}' "
                f"does not exist"
            )

        manifest = (
            source
            / "theme.json"
        )

        if not manifest.is_file():
            raise ThemeCopyError(
                f"Theme '{source_name}' "
                f"has no theme.json"
            )

        if destination.exists():
            raise ThemeCopyError(
                f"Theme '{new_name}' "
                f"already exists"
            )

        self.themes_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        staging_name = (
            f"_copy-"
            f"{uuid.uuid4().hex}"
        )

        staging = (
            self.themes_dir
            / staging_name
        )

        try:
            shutil.copytree(
                source,
                staging,
            )

            staging_manifest = (
                staging
                / "theme.json"
            )

            try:
                data = json.loads(
                    staging_manifest.read_text(
                        encoding="utf-8",
                    )
                )

            except (
                OSError,
                json.JSONDecodeError,
            ) as exc:
                raise ThemeCopyError(
                    f"Could not read theme "
                    f"manifest: {exc}"
                ) from exc

            if not isinstance(
                data,
                dict,
            ):
                raise ThemeCopyError(
                    "Theme manifest must "
                    "contain a JSON object"
                )

            data["name"] = new_name

            staging_manifest.write_text(
                json.dumps(
                    data,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            loader = ThemeLoader(
                self.themes_dir
            )

            copied_theme = loader.load(
                staging_name
            )

            self.validator.validate(
                copied_theme
            )

            staging.replace(
                destination
            )

        except Exception as exc:
            if staging.exists():
                shutil.rmtree(
                    staging,
                    ignore_errors=True,
                )

            if isinstance(
                exc,
                ThemeCopyError,
            ):
                raise

            raise ThemeCopyError(
                f"Could not copy theme "
                f"'{source_name}' to "
                f"'{new_name}': {exc}"
            ) from exc

        return new_name

    def _validate_name(
        self,
        name: str,
    ) -> None:
        if not name:
            raise ThemeCopyError(
                "Theme name cannot be empty"
            )

        if name.startswith("_"):
            raise ThemeCopyError(
                "Internal themes cannot "
                "be copied"
            )

        if not self.NAME_PATTERN.fullmatch(
            name
        ):
            raise ThemeCopyError(
                "Invalid theme name"
            )

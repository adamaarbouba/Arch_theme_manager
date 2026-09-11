from pathlib import Path
import re
import shutil
import uuid

from .loader import ThemeLoader
from .validator import ThemeValidator


class ThemeExportError(Exception):
    pass


class ThemeExporter:
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

    def export(
        self,
        theme_name: str,
        destination_root: Path,
        force: bool = False,
    ) -> Path:
        self._validate_name(
            theme_name
        )

        source = (
            self.themes_dir
            / theme_name
        )

        if source.is_symlink():
            raise ThemeExportError(
                f"Refusing to export "
                f"symlinked theme "
                f"'{theme_name}'"
            )

        if not source.is_dir():
            raise ThemeExportError(
                f"Theme '{theme_name}' "
                f"does not exist"
            )

        manifest = (
            source
            / "theme.json"
        )

        if not manifest.is_file():
            raise ThemeExportError(
                f"Theme '{theme_name}' "
                f"has no theme.json"
            )

        loader = ThemeLoader(
            self.themes_dir
        )

        try:
            theme = loader.load(
                theme_name
            )

            self.validator.validate(
                theme
            )

        except Exception as exc:
            raise ThemeExportError(
                f"Theme '{theme_name}' "
                f"is invalid: {exc}"
            ) from exc

        destination_root = (
            destination_root
            .expanduser()
            .resolve()
        )

        destination_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            destination_root
            / theme_name
        )

        if destination.exists():
            if not force:
                raise ThemeExportError(
                    f"Export destination "
                    f"already exists: "
                    f"{destination}"
                )

            if destination.is_symlink():
                raise ThemeExportError(
                    "Refusing to replace "
                    "a symlinked destination"
                )

        staging = (
            destination_root
            / (
                f".arch-theme-export-"
                f"{uuid.uuid4().hex}"
            )
        )

        backup = None

        try:
            shutil.copytree(
                source,
                staging,
            )

            if destination.exists():
                backup = (
                    destination_root
                    / (
                        f".arch-theme-backup-"
                        f"{uuid.uuid4().hex}"
                    )
                )

                destination.rename(
                    backup
                )

            staging.rename(
                destination
            )

            if (
                backup is not None
                and backup.exists()
            ):
                shutil.rmtree(
                    backup
                )

        except Exception as exc:
            if staging.exists():
                shutil.rmtree(
                    staging,
                    ignore_errors=True,
                )

            if (
                backup is not None
                and backup.exists()
                and not destination.exists()
            ):
                try:
                    backup.rename(
                        destination
                    )
                except OSError:
                    pass

            raise ThemeExportError(
                f"Could not export "
                f"theme '{theme_name}': "
                f"{exc}"
            ) from exc

        return destination

    def _validate_name(
        self,
        name: str,
    ) -> None:
        if not name:
            raise ThemeExportError(
                "Theme name cannot be empty"
            )

        if name.startswith("_"):
            raise ThemeExportError(
                "Internal themes cannot "
                "be exported"
            )

        if not self.NAME_PATTERN.fullmatch(
            name
        ):
            raise ThemeExportError(
                "Invalid theme name"
            )

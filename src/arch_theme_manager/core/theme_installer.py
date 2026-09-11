from pathlib import Path
import re
import shutil
import uuid

from .loader import ThemeLoader
from .validator import ThemeValidator


class ThemeInstallError(Exception):
    pass


class ThemeInstaller:
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

    def install(
        self,
        source: Path,
        name: str | None = None,
        force: bool = False,
    ) -> str:
        source = source.expanduser().resolve()

        if not source.is_dir():
            raise ThemeInstallError(
                f"Theme source is not a directory: {source}"
            )

        manifest = source / "theme.json"

        if not manifest.is_file():
            raise ThemeInstallError(
                f"Missing theme.json in {source}"
            )

        theme_name = (
            name
            if name is not None
            else source.name
        )

        self._validate_name(theme_name)

        self.themes_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            self.themes_dir
            / theme_name
        )

        if destination.exists() and not force:
            raise ThemeInstallError(
                f"Theme '{theme_name}' already exists"
            )

        staging_name = (
            f"_install-"
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

            loader = ThemeLoader(
                self.themes_dir
            )

            theme = loader.load(
                staging_name
            )

            self.validator.validate(
                theme
            )

            if destination.exists():
                shutil.rmtree(
                    destination
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
                ThemeInstallError,
            ):
                raise

            raise ThemeInstallError(
                f"Could not install "
                f"theme '{theme_name}': {exc}"
            ) from exc

        return theme_name

    def _validate_name(
        self,
        name: str,
    ) -> None:
        if not name:
            raise ThemeInstallError(
                "Theme name cannot be empty"
            )

        if name.startswith("_"):
            raise ThemeInstallError(
                "Installed theme names cannot "
                "start with '_'"
            )

        if not self.NAME_PATTERN.fullmatch(
            name
        ):
            raise ThemeInstallError(
                "Theme name may only contain "
                "letters, numbers, '.', '-' and '_'"
            )

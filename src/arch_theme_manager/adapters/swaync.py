from pathlib import Path
import subprocess


class SwayNCError(Exception):
    pass


class SwayNCAdapter:
    def __init__(self, generated_dir: Path):
        self.generated_dir = generated_dir

    def apply(self, theme: dict) -> None:
        colors = theme["colors"]

        css = f"""/* AUTO-GENERATED - DO NOT EDIT */

@define-color theme_background {colors["background"]};
@define-color theme_surface {colors["surface"]};
@define-color theme_foreground {colors["foreground"]};
@define-color theme_primary {colors["primary"]};
@define-color theme_secondary {colors["secondary"]};
@define-color theme_accent {colors["accent"]};
"""

        self.generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.generated_dir / "swaync-theme.css"
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            css,
            encoding="utf-8",
        )

        temporary.replace(target)

        self._reload()

    @staticmethod
    def _reload() -> None:
        result = subprocess.run(
            [
                "swaync-client",
                "--reload-css",
                "--skip-wait",
            ],
            capture_output=True,
            text=True,
        )

        # SwayNC may not currently be running.
        # Generated theme creation should still succeed.
        if result.returncode not in (0, 1):
            message = (
                result.stderr.strip()
                or result.stdout.strip()
            )

            raise SwayNCError(
                f"Failed to reload SwayNC CSS: {message}"
            )

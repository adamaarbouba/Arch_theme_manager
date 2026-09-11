from pathlib import Path
import subprocess


class WaybarError(Exception):
    pass


class WaybarAdapter:
    def __init__(self, generated_dir: Path):
        self.generated_dir = generated_dir

    def apply(self, theme: dict) -> None:
        colors = theme["colors"]

        css = f"""/* AUTO-GENERATED - DO NOT EDIT */

@define-color background {colors["background"]};
@define-color surface {colors["surface"]};
@define-color foreground {colors["foreground"]};
@define-color primary {colors["primary"]};
@define-color secondary {colors["secondary"]};
@define-color accent {colors["accent"]};
"""

        self.generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.generated_dir / "waybar-theme.css"
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            css,
            encoding="utf-8",
        )

        temporary.replace(target)

        self._reload_waybar()

    @staticmethod
    def _reload_waybar() -> None:
        result = subprocess.run(
            ["pkill", "-SIGUSR2", "waybar"],
            capture_output=True,
            text=True,
        )

        # pkill returns 1 if Waybar isn't running.
        # That's not a theme generation failure.
        if result.returncode not in (0, 1):
            raise WaybarError(
                result.stderr.strip()
                or "Failed to reload Waybar"
            )

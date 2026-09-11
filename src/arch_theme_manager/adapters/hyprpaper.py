from pathlib import Path
import subprocess


class HyprpaperError(Exception):
    pass


class HyprpaperAdapter:
    def apply(self, theme: dict) -> None:
        wallpaper = self._resolve_wallpaper(theme)

        config = theme.get("hyprpaper", {})
        monitor = config.get("monitor", "")
        fit_mode = config.get("fit_mode", "cover")

        target = f"{monitor}, {wallpaper}, {fit_mode}"

        result = subprocess.run(
            [
                "hyprctl",
                "hyprpaper",
                "wallpaper",
                target,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()

            raise HyprpaperError(
                f"Failed to apply wallpaper: {message}"
            )

    @staticmethod
    def _resolve_wallpaper(theme: dict) -> Path:
        wallpaper = Path(theme["wallpaper"]).expanduser()

        if not wallpaper.is_absolute():
            wallpaper = Path(theme["_theme_dir"]) / wallpaper

        return wallpaper.resolve()

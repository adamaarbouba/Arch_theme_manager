from pathlib import Path


class HyprlockAdapter:
    def __init__(self, generated_dir: Path):
        self.generated_dir = generated_dir

    def apply(self, theme: dict) -> None:
        colors = theme["colors"]

        theme_dir = Path(theme["_theme_dir"])
        wallpaper = (theme_dir / theme["wallpaper"]).resolve()

        content = f"""# AUTO-GENERATED - DO NOT EDIT

$theme_background = {self._rgba(colors["background"])}
$theme_surface = {self._rgba(colors["surface"])}
$theme_foreground = {self._rgba(colors["foreground"])}
$theme_primary = {self._rgba(colors["primary"])}
$theme_secondary = {self._rgba(colors["secondary"])}
$theme_accent = {self._rgba(colors["accent"])}

$theme_wallpaper = {wallpaper}
"""

        self.generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.generated_dir / "hyprlock-theme.conf"
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            content,
            encoding="utf-8",
        )

        temporary.replace(target)

    @staticmethod
    def _rgba(color: str) -> str:
        value = color.lstrip("#")

        if len(value) == 6:
            value += "ff"

        return f"rgba({value})"

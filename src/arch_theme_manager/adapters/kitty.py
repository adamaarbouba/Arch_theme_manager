from pathlib import Path
import subprocess


class KittyAdapter:
    def __init__(self, generated_dir: Path):
        self.generated_dir = generated_dir

    def apply(self, theme: dict) -> None:
        colors = theme["colors"]

        config = f"""# AUTO-GENERATED - DO NOT EDIT

background {colors["background"]}
foreground {colors["foreground"]}

selection_background {colors["primary"]}
selection_foreground {colors["background"]}

cursor {colors["accent"]}
cursor_text_color {colors["background"]}

url_color {colors["secondary"]}

active_border_color {colors["primary"]}
inactive_border_color {colors["surface"]}
bell_border_color {colors["accent"]}

active_tab_background {colors["primary"]}
active_tab_foreground {colors["background"]}

inactive_tab_background {colors["surface"]}
inactive_tab_foreground {colors["foreground"]}

tab_bar_background {colors["background"]}

color0 {colors["background"]}
color1 {colors["accent"]}
color2 {colors["secondary"]}
color3 {colors["primary"]}
color4 {colors["primary"]}
color5 {colors["accent"]}
color6 {colors["secondary"]}
color7 {colors["foreground"]}

color8 {colors["surface"]}
color9 {colors["accent"]}
color10 {colors["secondary"]}
color11 {colors["primary"]}
color12 {colors["primary"]}
color13 {colors["accent"]}
color14 {colors["secondary"]}
color15 {colors["foreground"]}
"""

        self.generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.generated_dir / "kitty-theme.conf"
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            config,
            encoding="utf-8",
        )

        temporary.replace(target)

        self._reload(target)

    @staticmethod
    def _reload(theme_file: Path) -> None:
        # Every Kitty OS process has its own socket:
        #
        # /tmp/kitty-theme-{kitty_pid}
        #
        # Stale sockets are harmless and are simply ignored.

        for socket in Path("/tmp").glob("kitty-theme-*"):
            subprocess.run(
                [
                    "kitten",
                    "@",
                    "--to",
                    f"unix:{socket}",
                    "set-colors",
                    "--all",
                    "--configured",
                    str(theme_file),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
            )

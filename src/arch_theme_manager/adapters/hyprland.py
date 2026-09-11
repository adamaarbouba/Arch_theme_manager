from pathlib import Path
import subprocess


class HyprlandError(Exception):
    pass


class HyprlandAdapter:
    def __init__(self, generated_dir: Path):
        self.generated_dir = generated_dir

    def apply(self, theme: dict) -> None:
        colors = theme["colors"]
        window = theme.get("window", {})

        background = self._to_rgba(colors["background"])
        surface = self._to_rgba(colors["surface"])
        primary = self._to_rgba(colors["primary"])
        secondary = self._to_rgba(colors["secondary"])

        rounding = window.get("rounding", 10)
        rounding_power = window.get("rounding_power", 2)
        opacity = window.get("opacity", 1.0)
        border_size = window.get("border_size", 2)

        lua = f"""-- AUTO-GENERATED - DO NOT EDIT

hl.config({{
    general = {{
        border_size = {border_size},

        col = {{
            active_border = {{
                colors = {{
                    "{primary}",
                    "{secondary}"
                }},
                angle = 45
            }},

            inactive_border = "{surface}",
        }},
    }},

    decoration = {{
        rounding = {rounding},
        rounding_power = {rounding_power},

        active_opacity = {opacity},
        inactive_opacity = {opacity},

        shadow = {{
            color = "{background}",
        }},
    }},
}})
"""

        self.generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.generated_dir / "hyprland-theme.lua"
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            lua,
            encoding="utf-8",
        )

        temporary.replace(target)

        self._reload()

    @staticmethod
    def _to_rgba(color: str) -> str:
        value = color.lstrip("#")

        if len(value) == 6:
            value += "ff"

        return f"rgba({value})"

    @staticmethod
    def _reload() -> None:
        result = subprocess.run(
            ["hyprctl", "reload"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = (
                result.stderr.strip()
                or result.stdout.strip()
            )

            raise HyprlandError(
                f"Failed to reload Hyprland: {message}"
            )

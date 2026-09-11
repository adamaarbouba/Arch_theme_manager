from pathlib import Path
import subprocess


class HyprtoolkitAdapter:
    def __init__(self, generated_dir: Path):
        self.generated_dir = generated_dir

    def apply(self, theme: dict) -> None:
        colors = theme["colors"]

        content = f"""# AUTO-GENERATED - DO NOT EDIT

background = {self._argb(colors["background"])}
base = {self._argb(colors["surface"])}
text = {self._argb(colors["foreground"])}

alternate_base = {self._argb(colors["background"])}
bright_text = {self._argb(colors["foreground"])}

accent = {self._argb(colors["primary"])}
accent_secondary = {self._argb(colors["secondary"])}
"""

        self.generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.generated_dir / "hyprtoolkit-theme.conf"
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            content,
            encoding="utf-8",
        )

        temporary.replace(target)

        self._reload_hyprlauncher()

    @staticmethod
    def _argb(color: str) -> str:
        value = color.lstrip("#")
        return f"0xFF{value}"

    @staticmethod
    def _reload_hyprlauncher() -> None:
        subprocess.run(
            ["pkill", "-x", "hyprlauncher"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        subprocess.Popen(
            ["hyprlauncher", "-d"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

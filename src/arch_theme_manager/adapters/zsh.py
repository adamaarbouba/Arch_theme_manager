from pathlib import Path
import os
import signal

from ..paths import runtime_home


class ZshAdapter:
    def __init__(self, generated_dir: Path):
        self.generated_dir = generated_dir

    def apply(self, theme: dict) -> None:
        colors = theme["colors"]

        content = f"""# AUTO-GENERATED - DO NOT EDIT

THEME_BACKGROUND="{colors["background"]}"
THEME_SURFACE="{colors["surface"]}"
THEME_FOREGROUND="{colors["foreground"]}"
THEME_PRIMARY="{colors["primary"]}"
THEME_SECONDARY="{colors["secondary"]}"
THEME_ACCENT="{colors["accent"]}"

PROMPT='%F{{{colors["primary"]}}}%n@%m%f %F{{{colors["secondary"]}}}%~%f %F{{{colors["accent"]}}}%#%f '
RPROMPT=''
"""

        self.generated_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        target = self.generated_dir / "zsh-theme.zsh"
        temporary = target.with_suffix(".tmp")

        temporary.write_text(
            content,
            encoding="utf-8",
        )

        temporary.replace(target)

        self._reload()

    @staticmethod
    def _reload() -> None:
        registry = runtime_home() / "zsh"

        if not registry.is_dir():
            return

        for pid_file in registry.iterdir():
            try:
                pid = int(pid_file.name)

            except ValueError:
                continue

            if not ZshAdapter._is_zsh_process(pid):
                try:
                    pid_file.unlink()

                except OSError:
                    pass

                continue

            try:
                os.kill(
                    pid,
                    signal.SIGUSR1,
                )

            except ProcessLookupError:
                try:
                    pid_file.unlink()

                except OSError:
                    pass

            except PermissionError:
                continue

    @staticmethod
    def _is_zsh_process(pid: int) -> bool:
        process_name = Path(
            f"/proc/{pid}/comm"
        )

        try:
            return (
                process_name.read_text(
                    encoding="utf-8",
                ).strip()
                == "zsh"
            )

        except OSError:
            return False

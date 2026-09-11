import json
from pathlib import Path


class ThemeState:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = state_dir / "current.json"

    def save(self, theme_name: str) -> None:
        self.state_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        previous = self.current()

        data = {
            "current": theme_name,
            "previous": previous,
        }

        temporary = self.state_file.with_suffix(".tmp")

        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        temporary.replace(self.state_file)

    def current(self) -> str | None:
        if not self.state_file.is_file():
            return None

        try:
            with self.state_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return data.get("current")

        except (json.JSONDecodeError, OSError):
            return None

    def previous(self) -> str | None:
        if not self.state_file.is_file():
            return None

        try:
            with self.state_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return data.get("previous")

        except (json.JSONDecodeError, OSError):
            return None


    def clear(self) -> None:
        try:
            self.state_file.unlink()

        except FileNotFoundError:
            pass

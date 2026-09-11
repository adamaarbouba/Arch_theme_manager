import json
from pathlib import Path


class ThemeState:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = state_dir / "current.json"

    def save(
        self,
        theme_name: str,
    ) -> None:
        self.state_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        previous = self.current()

        data = {
            "current": theme_name,
            "previous": previous,
        }

        temporary = (
            self.state_file
            .with_suffix(".tmp")
        )

        with temporary.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
            )

        temporary.replace(
            self.state_file
        )

    def current(self) -> str | None:
        if not self.state_file.is_file():
            return None

        try:
            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return data.get(
                "current"
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            return None

    def previous(self) -> str | None:
        if not self.state_file.is_file():
            return None

        try:
            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            return data.get(
                "previous"
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            return None

    def clear(self) -> None:
        try:
            self.state_file.unlink()

        except FileNotFoundError:
            pass

    def rename_theme(
        self,
        old_name: str,
        new_name: str,
    ) -> None:
        if not self.state_file.is_file():
            return

        try:
            data = json.loads(
                self.state_file.read_text(
                    encoding="utf-8",
                )
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return

        changed = False

        if data.get("current") == old_name:
            data["current"] = new_name
            changed = True

        if data.get("previous") == old_name:
            data["previous"] = new_name
            changed = True

        if not changed:
            return

        temporary = (
            self.state_file
            .with_suffix(".tmp")
        )

        temporary.write_text(
            json.dumps(
                data,
                indent=4,
            ),
            encoding="utf-8",
        )

        temporary.replace(
            self.state_file
        )

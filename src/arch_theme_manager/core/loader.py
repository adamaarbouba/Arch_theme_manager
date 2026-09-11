import json
from pathlib import Path


class ThemeError(Exception):
    pass


class ThemeLoader:
    def __init__(self, themes_dir: Path):
        self.themes_dir = themes_dir

    def list_themes(self) -> list[str]:
        if not self.themes_dir.exists():
            return []

        themes = []

        for path in self.themes_dir.iterdir():
            if not path.is_dir():
                continue

            if path.name.startswith("_"):
                continue

            if (path / "theme.json").is_file():
                themes.append(path.name)

        return sorted(themes)

    def load(self, name: str) -> dict:
        return self._load(name, seen=set())

    def _load(self, name: str, seen: set[str]) -> dict:
        if name in seen:
            raise ThemeError(
                f"Circular theme inheritance detected: {name}"
            )

        seen.add(name)

        theme_dir = self.themes_dir / name
        manifest = theme_dir / "theme.json"

        if not manifest.is_file():
            raise ThemeError(
                f"Theme '{name}' does not contain theme.json"
            )

        try:
            with manifest.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise ThemeError(
                f"Invalid JSON in {manifest}: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ThemeError(
                f"{manifest} must contain a JSON object"
            )

        parent_name = data.get("extends")

        if parent_name:
            parent = self._load(parent_name, seen)
            data = self._deep_merge(parent, data)

        data["_theme_name"] = name
        data["_theme_dir"] = str(theme_dir.resolve())

        return data

    def _deep_merge(self, base: dict, override: dict) -> dict:
        result = dict(base)

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(
                    result[key],
                    value
                )
            else:
                result[key] = value

        return result

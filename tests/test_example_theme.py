from pathlib import Path

from arch_theme_manager.core.loader import ThemeLoader
from arch_theme_manager.core.validator import ThemeValidator


def test_repository_example_theme_is_valid():
    themes_root = (
        Path(__file__).resolve()
        .parents[1]
        / "themes"
    )

    loader = ThemeLoader(themes_root)
    validator = ThemeValidator()

    theme = loader.load("example")

    validator.validate(theme)

    assert theme["_theme_name"] == "example"

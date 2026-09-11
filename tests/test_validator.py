import copy

import pytest

from arch_theme_manager.core.validator import (
    ThemeValidationError,
    ThemeValidator,
)


def test_valid_theme_passes(
    valid_theme,
):
    validator = ThemeValidator()

    validator.validate(
        valid_theme
    )


def test_missing_colors_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    del theme["colors"]

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


def test_missing_required_color_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    del theme["colors"]["accent"]

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


def test_invalid_hex_color_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme["colors"]["primary"] = (
        "purple"
    )

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


def test_short_hex_color_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme["colors"]["primary"] = (
        "#FFF"
    )

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


def test_eight_digit_hex_color_is_valid(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme["colors"]["primary"] = (
        "#112233AA"
    )

    validator = ThemeValidator()

    validator.validate(theme)


def test_negative_rounding_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme["window"]["rounding"] = -1

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


def test_zero_rounding_power_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme[
        "window"
    ][
        "rounding_power"
    ] = 0

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


@pytest.mark.parametrize(
    "opacity",
    [
        -0.1,
        1.1,
        2,
    ],
)
def test_invalid_opacity_fails(
    valid_theme,
    opacity,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme["window"]["opacity"] = (
        opacity
    )

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


@pytest.mark.parametrize(
    "opacity",
    [
        0,
        0.5,
        1,
    ],
)
def test_valid_opacity_passes(
    valid_theme,
    opacity,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme["window"]["opacity"] = (
        opacity
    )

    validator = ThemeValidator()

    validator.validate(theme)


def test_negative_border_size_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme[
        "window"
    ][
        "border_size"
    ] = -1

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


def test_float_border_size_fails(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme[
        "window"
    ][
        "border_size"
    ] = 1.5

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)


def test_monitor_must_be_string(
    valid_theme,
):
    theme = copy.deepcopy(
        valid_theme
    )

    theme["hyprpaper"]["monitor"] = 123

    validator = ThemeValidator()

    with pytest.raises(
        ThemeValidationError
    ):
        validator.validate(theme)
